"""
Job APScheduler : agrège les actualités JOJ Dakar 2026 depuis des flux RSS
et les publie automatiquement dans le fil Live.
Fréquence recommandée : toutes les 2 heures.
"""
import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re

logger = logging.getLogger(__name__)

# ── Sources RSS ───────────────────────────────────────────────────────────────

SOURCES = [
    {
        "name": "Google News — JOJ Dakar 2026",
        "url":  "https://news.google.com/rss/search?q=JOJ+Dakar+2026&hl=fr&gl=SN&ceid=SN:fr",
    },
    {
        "name": "Google News — Jeux Olympiques Jeunesse Dakar",
        "url":  "https://news.google.com/rss/search?q=%22Jeux+Olympiques+de+la+Jeunesse%22+Dakar&hl=fr&gl=SN&ceid=SN:fr",
    },
    {
        "name": "Google News — COJOJ travaux",
        "url":  "https://news.google.com/rss/search?q=COJOJ+Dakar+2026&hl=fr&gl=SN&ceid=SN:fr",
    },
    {
        "name": "APS Sénégal",
        "url":  "https://www.aps.sn/feed",
    },
    {
        "name": "Seneweb",
        "url":  "https://www.seneweb.com/news/rss/",
    },
]

# ── Mots-clés de pertinence ───────────────────────────────────────────────────

KEYWORDS_PERTINENTS = [
    "joj", "joj 2026", "dakar 2026", "cojoj",
    "jeux olympiques de la jeunesse", "jeux de la jeunesse",
    "olympic youth games", "youth olympic",
    "iba mar diop", "dakar arena", "diamniadio",
    "saly beach", "tour de l'œuf", "abdoulaye wade",
    "jeux africains dakar", "athlétisme dakar 2026",
    "natation dakar 2026", "basketball dakar 2026",
]

# ── Détection de catégorie par contenu ───────────────────────────────────────

CAT_KEYWORDS = {
    "travaux":     ["travaux", "chantier", "construction", "infrastructure",
                    "rénovation", "bâtiment", "aménagement", "génie civil",
                    "livraison", "inauguration"],
    "site":        ["site", "arena", "piscine", "stade", "vélodrome",
                    "salle", "complexe sportif", "village olympique"],
    "competition": ["médaille", "résultat", "finale", "podium", "champion",
                    "victoire", "athlète", "épreuve", "compétition",
                    "record", "performance", "sélection"],
    "meteo":       ["météo", "pluie", "chaleur", "température", "climat",
                    "harmattan", "vent", "saison"],
    "programme":   ["programme", "horaire", "calendrier", "report",
                    "annulé", "modifié", "cérémonie", "ouverture",
                    "clôture", "tirage"],
}


def deviner_categorie(texte: str) -> str:
    t = texte.lower()
    for cat, mots in CAT_KEYWORDS.items():
        if any(m in t for m in mots):
            return cat
    return "annonce"


def est_pertinent(texte: str) -> bool:
    t = texte.lower()
    return any(kw in t for kw in KEYWORDS_PERTINENTS)


def nettoyer(texte: str) -> str:
    texte = html.unescape(texte or "")
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()


# ── Lecture RSS ───────────────────────────────────────────────────────────────

def fetch_rss(url: str, timeout: int = 15) -> list:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "JOJ-Dakar-2026-App/1.0 (+https://joj-dakar-2026.onrender.com)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()

        root = ET.fromstring(data)
        items = []

        # RSS 2.0
        for item in root.findall(".//item"):
            titre = nettoyer(item.findtext("title") or "")
            desc  = nettoyer(item.findtext("description") or "")
            link  = (item.findtext("link") or "").strip()
            if titre and link:
                items.append({"titre": titre, "desc": desc, "link": link})

        # Atom
        if not items:
            ns = "http://www.w3.org/2005/Atom"
            for entry in root.findall(f"{{{ns}}}entry"):
                titre = nettoyer(entry.findtext(f"{{{ns}}}title") or "")
                desc  = nettoyer(entry.findtext(f"{{{ns}}}summary") or "")
                link_el = entry.find(f"{{{ns}}}link")
                link    = (link_el.get("href", "") if link_el is not None else "").strip()
                if titre and link:
                    items.append({"titre": titre, "desc": desc, "link": link})

        return items

    except Exception as e:
        logger.warning(f"[news_fetcher] Échec RSS {url}: {e}")
        return []


# ── Job principal ─────────────────────────────────────────────────────────────

def importer_actualites(app):
    with app.app_context():
        from app import db
        from app.models.info_live import InfoLive
        from sqlalchemy import text

        # Migration douce : ajouter source_url si absent
        try:
            db.session.execute(
                text("ALTER TABLE infos_live ADD COLUMN source_url VARCHAR(500)")
            )
            db.session.commit()
        except Exception:
            db.session.rollback()

        imported = 0

        for source in SOURCES:
            articles = fetch_rss(source["url"])
            for art in articles:
                texte_complet = art["titre"] + " " + art["desc"]

                if not est_pertinent(texte_complet):
                    continue

                # Déduplications par URL
                existe = InfoLive.query.filter_by(source_url=art["link"]).first()
                if existe:
                    continue

                contenu = art["desc"][:600].strip() or art["titre"]
                if len(art["desc"]) > 600:
                    contenu += "…"
                contenu += f"\n\n📰 Source : {source['name']}"

                info = InfoLive(
                    titre      = art["titre"][:200],
                    contenu    = contenu,
                    categorie  = deviner_categorie(texte_complet),
                    source_url = art["link"],
                )
                db.session.add(info)
                imported += 1

        if imported:
            db.session.commit()
            logger.info(f"[news_fetcher] {imported} article(s) importé(s).")
        else:
            logger.debug("[news_fetcher] Aucun nouvel article JOJ trouvé.")
