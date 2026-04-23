"""
Agrégateur d'actualités JOJ Dakar 2026.
- Interroge Google News RSS + APS + sources officielles
- Filtre par mots-clés, détecte la catégorie, déduplique par URL
- Thread-safe : ne se relance pas si un import est déjà en cours
  ou si moins de MIN_INTERVAL_MINUTES se sont écoulés.
"""
import logging
import threading
import urllib.request
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ── Verrou + horodatage pour éviter les imports simultanés ────────────────────
_lock            = threading.Lock()
_dernier_import  = None
MIN_INTERVAL_MIN = 5   # minutes minimum entre deux imports


# ── Sources RSS ───────────────────────────────────────────────────────────────

SOURCES = [
    # Google News — plusieurs requêtes ciblées
    {
        "name": "Google News",
        "url":  "https://news.google.com/rss/search?q=JOJ+Dakar+2026&hl=fr&gl=SN&ceid=SN:fr",
    },
    {
        "name": "Google News",
        "url":  "https://news.google.com/rss/search?q=%22Jeux+Olympiques+de+la+Jeunesse%22+Dakar+2026&hl=fr&gl=SN&ceid=SN:fr",
    },
    {
        "name": "Google News",
        "url":  "https://news.google.com/rss/search?q=COJOJ+Dakar&hl=fr&gl=SN&ceid=SN:fr",
    },
    {
        "name": "Google News",
        "url":  "https://news.google.com/rss/search?q=Dakar+2026+infrastructure+travaux&hl=fr&gl=SN&ceid=SN:fr",
    },
    {
        "name": "Google News",
        "url":  "https://news.google.com/rss/search?q=JOJ+2026+sport+athletes&hl=en&gl=SN&ceid=SN:en",
    },
    # Presse sénégalaise
    {
        "name": "APS Sénégal",
        "url":  "https://www.aps.sn/feed",
    },
    {
        "name": "RFM Sénégal",
        "url":  "https://www.rfmsn.com/feed/",
    },
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
]

# ── Détection de catégorie ────────────────────────────────────────────────────

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

def fetch_rss(url: str, timeout: int = 12) -> list:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; JOJ-Dakar-2026/1.0)",
            "Accept":     "application/rss+xml, application/xml, text/xml",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()

        root = ET.fromstring(data)
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

        return items

    except Exception as e:
        logger.debug(f"[news_fetcher] RSS {url[:60]}… — {e}")
        return []


# ── Import principal ──────────────────────────────────────────────────────────

def importer_actualites(app) -> int:
    """Importe les nouveaux articles. Retourne le nombre ajoutés."""
    global _dernier_import

    with app.app_context():
        from app import db
        from app.models.info_live import InfoLive
        from sqlalchemy import text

        # Migration douce
        try:
            db.session.execute(text(
                "ALTER TABLE infos_live ADD COLUMN source_url VARCHAR(500)"
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

        imported = 0
        for source in SOURCES:
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

        if imported:
            db.session.commit()
            logger.info(f"[news_fetcher] {imported} nouvel(s) article(s) importé(s).")

        _dernier_import = datetime.utcnow()
        return imported


def importer_si_necessaire(app) -> int:
    """
    Importe seulement si MIN_INTERVAL_MIN minutes se sont écoulées
    depuis le dernier import. Thread-safe.
    Retourne le nombre d'articles ajoutés (0 si trop tôt).
    """
    global _dernier_import

    if not _lock.acquire(blocking=False):
        return 0  # un import est déjà en cours

    try:
        if _dernier_import:
            elapsed = (datetime.utcnow() - _dernier_import).total_seconds()
            if elapsed < MIN_INTERVAL_MIN * 60:
                return 0
        return importer_actualites(app)
    finally:
        _lock.release()
