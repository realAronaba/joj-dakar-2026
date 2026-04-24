"""
Agrégateur d'actualités JOJ Dakar 2026.
- RSS (presse sénégalaise / africaine) + NewsAPI.org optionnel
- Filtre par mots-clés, détecte la catégorie, déduplique par URL
- Thread-safe : verrou + cooldown MIN_INTERVAL_MIN
"""
import json
import logging
import threading
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime

logger = logging.getLogger(__name__)

_lock            = threading.Lock()
_dernier_import  = None
MIN_INTERVAL_MIN = 5


# ── Sources RSS ───────────────────────────────────────────────────────────────
# Google News bloque les IPs de datacenter → priorité aux médias sénégalais

SOURCES_RSS = [
    {"name": "APS Sénégal",  "url": "https://www.aps.sn/feed"},
    {"name": "RFM Sénégal",  "url": "https://www.rfmsn.com/feed/"},
    {"name": "Senenews",     "url": "https://www.senenews.com/feed/"},
    {"name": "PressAfrik",   "url": "https://www.pressafrik.com/feed/"},
    {"name": "Leral.net",    "url": "https://www.leral.net/feed/"},
    {"name": "DakarActu",    "url": "https://www.dakaractu.com/feed/"},
    {"name": "RFI Afrique",  "url": "https://www.rfi.fr/fr/rss/rss_afrique.xml"},
    # Google News conservé en dernier (souvent bloqué depuis un datacenter)
    {"name": "Google News",  "url": "https://news.google.com/rss/search?q=JOJ+Dakar+2026&hl=fr&gl=SN&ceid=SN:fr"},
    {"name": "Google News",  "url": "https://news.google.com/rss/search?q=COJOJ+Dakar&hl=fr&gl=SN&ceid=SN:fr"},
]


# ── Mots-clés de pertinence ───────────────────────────────────────────────────

KEYWORDS = [
    "joj", "dakar 2026", "cojoj",
    "jeux olympiques de la jeunesse", "jeux de la jeunesse",
    "olympic youth", "youth olympic games",
    "iba mar diop", "dakar arena", "diamniadio 2026",
    "saly beach", "tour de l'œuf",
    "village olympique dakar", "athlètes dakar",
    "mascotte joj", "ayo dakar",
    "jeux de la jeunesse dakar", "dakar youth",
    "stade léopold sédar senghor", "arena dakae",
]

CAT_KEYWORDS = {
    "travaux":     ["travaux", "chantier", "construction", "infrastructure",
                    "rénovation", "bâtiment", "aménagement", "livraison",
                    "inauguration", "génie civil", "ouvriers"],
    "site":        ["site", "arena", "piscine", "stade", "vélodrome",
                    "salle", "complexe sportif", "village olympique", "sapco"],
    "competition": ["médaille", "résultat", "finale", "podium", "champion",
                    "victoire", "athlète", "épreuve", "compétition",
                    "record", "sélection", "qualification", "discipline"],
    "meteo":       ["météo", "pluie", "chaleur", "température", "climat",
                    "harmattan", "vent", "hivernage"],
    "programme":   ["programme", "horaire", "calendrier", "report",
                    "annulé", "modifié", "cérémonie", "ouverture",
                    "clôture", "tirage au sort", "compte à rebours"],
}


def deviner_categorie(texte: str) -> str:
    t = texte.lower()
    for cat, mots in CAT_KEYWORDS.items():
        if any(m in t for m in mots):
            return cat
    return "annonce"


def est_pertinent(texte: str) -> bool:
    t = texte.lower()
    return any(kw in t for kw in KEYWORDS)


def nettoyer(texte: str) -> str:
    texte = html.unescape(texte or "")
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()


# ── Lecture RSS ───────────────────────────────────────────────────────────────

def fetch_rss(url: str, timeout: int = 15) -> list:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept":          "application/rss+xml, application/xml, text/xml, */*",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()

        root  = ET.fromstring(data)
        items = []

        for item in root.findall(".//item"):
            titre = nettoyer(item.findtext("title") or "")
            desc  = nettoyer(item.findtext("description") or "")
            link  = (item.findtext("link") or "").strip()
            if titre and link:
                items.append({"titre": titre, "desc": desc, "link": link})

        if not items:
            ns = "http://www.w3.org/2005/Atom"
            for entry in root.findall(f"{{{ns}}}entry"):
                titre   = nettoyer(entry.findtext(f"{{{ns}}}title") or "")
                desc    = nettoyer(entry.findtext(f"{{{ns}}}summary") or "")
                link_el = entry.find(f"{{{ns}}}link")
                link    = (link_el.get("href", "") if link_el is not None else "").strip()
                if titre and link:
                    items.append({"titre": titre, "desc": desc, "link": link})

        logger.info(f"[news_fetcher] RSS {url[:55]}… → {len(items)} articles")
        return items

    except Exception as e:
        logger.warning(f"[news_fetcher] RSS ECHEC {url[:55]}… — {e}")
        return []


# ── NewsAPI.org (optionnel) ───────────────────────────────────────────────────

def fetch_newsapi(api_key: str) -> list:
    """
    Interroge NewsAPI.org (100 req/jour en gratuit).
    Retourne une liste de {titre, desc, link, source_name}.
    """
    queries = [
        "JOJ Dakar 2026",
        "Youth Olympic Games Dakar",
        "COJOJ Dakar 2026",
    ]
    results = []
    for q in queries:
        try:
            params = urllib.parse.urlencode({
                "q":        q,
                "language": "fr",
                "sortBy":   "publishedAt",
                "pageSize": 20,
                "apiKey":   api_key,
            })
            url = f"https://newsapi.org/v2/everything?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "JOJ-Dakar-2026/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            for art in data.get("articles", []):
                titre = nettoyer(art.get("title") or "")
                desc  = nettoyer(art.get("description") or "")
                link  = (art.get("url") or "").strip()
                src   = art.get("source", {}).get("name", "NewsAPI")
                if titre and link:
                    results.append({"titre": titre, "desc": desc, "link": link, "source_name": src})

            logger.info(f"[news_fetcher] NewsAPI '{q}' → {len(data.get('articles', []))} articles")
        except Exception as e:
            logger.warning(f"[news_fetcher] NewsAPI ECHEC '{q}' — {e}")

    return results


# ── Diagnostic (appelé par /api/live/debug) ───────────────────────────────────

def tester_sources(app) -> list:
    """Teste chaque source RSS et retourne un rapport."""
    rapport = []
    for src in SOURCES_RSS:
        articles = fetch_rss(src["url"])
        pertinents = [a for a in articles if est_pertinent(a["titre"] + " " + a["desc"])]
        rapport.append({
            "source":     src["name"],
            "url":        src["url"],
            "total":      len(articles),
            "pertinents": len(pertinents),
            "ok":         len(articles) > 0,
        })
    return rapport


# ── Import principal ──────────────────────────────────────────────────────────

def importer_actualites(app) -> int:
    """Importe les nouveaux articles depuis toutes les sources. Retourne le nombre ajoutés."""
    global _dernier_import

    with app.app_context():
        from app import db
        from app.models.info_live import InfoLive
        from sqlalchemy import text

        # Migration douce : ajout de source_url si manquant
        try:
            db.session.execute(text(
                "ALTER TABLE infos_live ADD COLUMN source_url VARCHAR(500)"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

        imported = 0

        # ── RSS ──────────────────────────────────────────────────────────────
        for source in SOURCES_RSS:
            articles = fetch_rss(source["url"])
            for art in articles:
                full = art["titre"] + " " + art["desc"]
                if not est_pertinent(full):
                    continue
                if InfoLive.query.filter_by(source_url=art["link"]).first():
                    continue

                contenu = art["desc"][:600].strip() or art["titre"]
                if len(art["desc"]) > 600:
                    contenu += "…"
                contenu += f"\n\n📰 Source : {source['name']}"

                db.session.add(InfoLive(
                    titre      = art["titre"][:200],
                    contenu    = contenu,
                    categorie  = deviner_categorie(full),
                    source_url = art["link"],
                ))
                imported += 1

        # ── NewsAPI (si clé configurée) ───────────────────────────────────────
        import os
        newsapi_key = os.getenv("NEWSAPI_KEY", "")
        if newsapi_key:
            articles = fetch_newsapi(newsapi_key)
            for art in articles:
                full = art["titre"] + " " + art["desc"]
                if not est_pertinent(full):
                    continue
                if InfoLive.query.filter_by(source_url=art["link"]).first():
                    continue

                contenu = art["desc"][:600].strip() or art["titre"]
                if len(art["desc"]) > 600:
                    contenu += "…"
                src_name = art.get("source_name", "NewsAPI")
                contenu += f"\n\n📰 Source : {src_name}"

                db.session.add(InfoLive(
                    titre      = art["titre"][:200],
                    contenu    = contenu,
                    categorie  = deviner_categorie(full),
                    source_url = art["link"],
                ))
                imported += 1

        if imported:
            db.session.commit()
            logger.info(f"[news_fetcher] ✅ {imported} nouvel(s) article(s) importé(s).")
        else:
            logger.info("[news_fetcher] Aucun nouvel article pertinent trouvé.")

        _dernier_import = datetime.utcnow()
        return imported


def importer_si_necessaire(app) -> int:
    """Thread-safe : importe seulement si le cooldown est écoulé."""
    global _dernier_import

    if not _lock.acquire(blocking=False):
        return 0

    try:
        if _dernier_import:
            elapsed = (datetime.utcnow() - _dernier_import).total_seconds()
            if elapsed < MIN_INTERVAL_MIN * 60:
                return 0
        return importer_actualites(app)
    finally:
        _lock.release()
