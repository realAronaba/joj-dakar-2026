"""
Agrégateur d'actualités JOJ Dakar 2026.
Sources :
  - RSS presse sénégalaise / africaine (toutes les 15 min)
  - The Guardian API  (toutes les 2h, clé test gratuite sans inscription)
  - NewsAPI.org       (toutes les 2h, 100 req/jour — optionnel via NEWSAPI_KEY)
Thread-safe : verrou + cooldown par canal.
"""
import json
import logging
import os
import threading
import traceback
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# ── État global ───────────────────────────────────────────────────────────────
_lock_rss        = threading.Lock()
_lock_api        = threading.Lock()
_dernier_rss     = None
_derniere_api    = None
_dernier_import  = None   # tous canaux confondus (pour /api/live/status)
_derniere_erreur = None

MIN_RSS_MIN  = 10   # cooldown RSS en minutes
MIN_API_MIN  = 90   # cooldown API (Guardian + NewsAPI) en minutes


# ── Sources RSS (presse sénégalaise/africaine) ────────────────────────────────
SOURCES_RSS = [
    {"name": "APS Sénégal",  "url": "https://www.aps.sn/feed"},
    {"name": "RFM Sénégal",  "url": "https://www.rfmsn.com/feed/"},
    {"name": "Senenews",     "url": "https://www.senenews.com/feed/"},
    {"name": "PressAfrik",   "url": "https://www.pressafrik.com/feed/"},
    {"name": "Leral.net",    "url": "https://www.leral.net/feed/"},
    {"name": "DakarActu",    "url": "https://www.dakaractu.com/feed/"},
    {"name": "RFI Afrique",  "url": "https://www.rfi.fr/fr/rss/rss_afrique.xml"},
    {"name": "Bing News",    "url": "https://www.bing.com/news/search?q=JOJ+Dakar+2026&format=rss&setlang=fr"},
    {"name": "Bing News",    "url": "https://www.bing.com/news/search?q=Dakar+2026+Jeux+Olympiques+Jeunesse&format=rss"},
    {"name": "Google News",  "url": "https://news.google.com/rss/search?q=JOJ+Dakar+2026&hl=fr&gl=SN&ceid=SN:fr"},
]

# ── Mots-clés de pertinence (RSS uniquement — API déjà ciblée) ───────────────
KEYWORDS = [
    # Français
    "joj", "dakar 2026", "cojoj",
    "jeux olympiques de la jeunesse", "jeux de la jeunesse",
    "jo de la jeunesse", "jeunesse 2026",
    "iba mar diop", "dakar arena", "diamniadio 2026",
    "saly beach", "tour de l'œuf",
    "village olympique dakar", "athlètes dakar",
    "mascotte joj", "ayo dakar",
    "jeux jeunesse dakar", "olympique jeunesse dakar",
    # Anglais
    "youth olympic games", "olympic youth",
    "youth olympic 2026", "dakar 2026 youth",
    "youth games dakar", "dakar olympic 2026",
    "dakar 2026 games", "senegal olympic 2026",
    "khaby lame joj", "khaby lame olympic",
]

CAT_KEYWORDS = {
    "travaux":     ["travaux", "chantier", "construction", "infrastructure",
                    "rénovation", "bâtiment", "aménagement", "livraison",
                    "inauguration", "génie civil", "ouvriers"],
    "site":        ["site", "arena", "piscine", "stade", "vélodrome",
                    "salle", "complexe sportif", "village olympique", "sapco"],
    "competition": ["médaille", "résultat", "finale", "podium", "champion",
                    "victoire", "athlète", "épreuve", "compétition",
                    "record", "sélection", "qualification", "discipline",
                    "athlete", "medal", "champion", "competition"],
    "meteo":       ["météo", "pluie", "chaleur", "température", "climat",
                    "harmattan", "vent", "hivernage"],
    "programme":   ["programme", "horaire", "calendrier", "report",
                    "annulé", "modifié", "cérémonie", "ouverture",
                    "clôture", "tirage au sort", "compte à rebours",
                    "schedule", "ceremony", "opening"],
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
    return texte.strip()[:800]


# ── Lecture RSS ───────────────────────────────────────────────────────────────

def fetch_rss(url: str, timeout: int = 15) -> list:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
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

        logger.info(f"[RSS] {url[:50]}… → {len(items)} articles")
        return items
    except Exception as e:
        logger.warning(f"[RSS] ECHEC {url[:50]}… — {e}")
        return []


# ── The Guardian API (gratuit, clé test sans inscription) ─────────────────────

GUARDIAN_QUERIES = [
    "\"youth olympic games\" dakar 2026",
    "\"dakar 2026\" olympic",
    "JOJ dakar 2026",
    "\"youth olympic\" senegal 2026",
]


def fetch_guardian() -> list:
    """Interroge The Guardian avec la clé test (gratuite, pas d'inscription)."""
    results = []
    seen    = set()
    for q in GUARDIAN_QUERIES:
        try:
            params = urllib.parse.urlencode({
                "q":           q,
                "api-key":     "test",
                "page-size":   50,
                "show-fields": "trailText",
                "order-by":    "newest",
            })
            url = f"https://content.guardianapis.com/search?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "JOJ-Dakar-2026/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            arts = data.get("response", {}).get("results", [])
            for art in arts:
                link  = art.get("webUrl", "").strip()
                titre = nettoyer(art.get("webTitle") or "")
                desc  = nettoyer(
                    (art.get("fields") or {}).get("trailText") or art.get("webTitle") or ""
                )
                if link and link not in seen:
                    seen.add(link)
                    results.append({"titre": titre, "desc": desc, "link": link,
                                    "source_name": "The Guardian"})
            logger.info(f"[Guardian] '{q}' → {len(arts)} articles")
        except Exception as e:
            logger.warning(f"[Guardian] ECHEC '{q}' — {e}")
    return results


# ── NewsAPI.org (optionnel, 100 req/jour) ─────────────────────────────────────

NEWSAPI_QUERIES = [
    "JOJ Dakar 2026",
    "Youth Olympic Games Dakar 2026",
    "Jeux Olympiques Jeunesse Dakar",
    "COJOJ Dakar 2026",
    "Dakar 2026 Olympics",
]


def fetch_newsapi(api_key: str) -> list:
    results = []
    seen    = set()
    for q in NEWSAPI_QUERIES:
        try:
            params = urllib.parse.urlencode({
                "q":        q,
                "sortBy":   "publishedAt",
                "pageSize": 30,
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
                if titre and link and link not in seen:
                    seen.add(link)
                    results.append({"titre": titre, "desc": desc, "link": link,
                                    "source_name": src})
            logger.info(f"[NewsAPI] '{q}' → {len(data.get('articles', []))} articles")
        except Exception as e:
            logger.warning(f"[NewsAPI] ECHEC '{q}' — {e}")
    return results


# ── Sauvegarde d'articles en base ─────────────────────────────────────────────

def _sauvegarder(articles: list, source_name_default: str, filtrer: bool, db, InfoLive) -> int:
    """Sauvegarde une liste d'articles en base. Retourne le nombre ajoutés."""
    added = 0
    for art in articles:
        full = art["titre"] + " " + art["desc"]
        if filtrer and not est_pertinent(full):
            continue
        link = art["link"]
        if InfoLive.query.filter_by(source_url=link).first():
            continue

        contenu = art["desc"][:600].strip() or art["titre"]
        if len(art.get("desc", "")) > 600:
            contenu += "…"
        src = art.get("source_name", source_name_default)
        contenu += f"\n\n📰 Source : {src}"

        db.session.add(InfoLive(
            titre      = art["titre"][:200],
            contenu    = contenu,
            categorie  = deviner_categorie(full),
            source_url = link,
        ))
        added += 1
    return added


# ── Import RSS (toutes les 15 min) ────────────────────────────────────────────

def importer_actualites(app) -> int:
    """Import RSS. Appelé par le scheduler toutes les 15 min."""
    global _dernier_rss, _dernier_import, _derniere_erreur

    if not _lock_rss.acquire(blocking=False):
        return 0

    try:
        elapsed = (_now() - _dernier_rss).total_seconds() if _dernier_rss else None
        if elapsed is not None and elapsed < MIN_RSS_MIN * 60:
            return 0

        imported = 0
        try:
            with app.app_context():
                from app import db
                from app.models.info_live import InfoLive
                from sqlalchemy import text

                try:
                    db.session.execute(text(
                        "ALTER TABLE infos_live ADD COLUMN source_url VARCHAR(500)"
                    ))
                    db.session.commit()
                except Exception:
                    db.session.rollback()

                for source in SOURCES_RSS:
                    try:
                        arts = fetch_rss(source["url"])
                        n = _sauvegarder(arts, source["name"], filtrer=True, db=db, InfoLive=InfoLive)
                        if n:
                            db.session.commit()
                            imported += n
                    except Exception as e:
                        logger.warning(f"[RSS] source {source['name']}: {e}")
                        db.session.rollback()

                if imported:
                    logger.info(f"[RSS] ✅ {imported} nouveaux articles RSS.")
                else:
                    logger.info("[RSS] Aucun nouvel article RSS pertinent.")

                _derniere_erreur = None
        except Exception:
            tb = traceback.format_exc()
            logger.error(f"[RSS] CRASH:\n{tb}")
            _derniere_erreur = tb

        _dernier_rss    = _now()
        _dernier_import = _now()
        return imported
    finally:
        _lock_rss.release()


# ── Import API (Guardian + NewsAPI, toutes les 2h) ────────────────────────────

def importer_depuis_apis(app) -> int:
    """Import Guardian + NewsAPI. Appelé par le scheduler toutes les 2h."""
    global _derniere_api, _dernier_import, _derniere_erreur

    if not _lock_api.acquire(blocking=False):
        return 0

    try:
        elapsed = (_now() - _derniere_api).total_seconds() if _derniere_api else None
        if elapsed is not None and elapsed < MIN_API_MIN * 60:
            return 0

        imported = 0
        try:
            with app.app_context():
                from app import db
                from app.models.info_live import InfoLive

                # The Guardian
                arts = fetch_guardian()
                n = _sauvegarder(arts, "The Guardian", filtrer=True, db=db, InfoLive=InfoLive)
                if n:
                    db.session.commit()
                    imported += n
                    logger.info(f"[Guardian] ✅ {n} nouveaux articles.")

                # NewsAPI
                newsapi_key = os.getenv("NEWSAPI_KEY", "")
                if newsapi_key:
                    arts = fetch_newsapi(newsapi_key)
                    n = _sauvegarder(arts, "NewsAPI", filtrer=False, db=db, InfoLive=InfoLive)
                    if n:
                        db.session.commit()
                        imported += n
                        logger.info(f"[NewsAPI] ✅ {n} nouveaux articles.")

                logger.info(f"[API] ✅ Total : {imported} nouveaux articles via APIs.")
                _derniere_erreur = None
        except Exception:
            tb = traceback.format_exc()
            logger.error(f"[API] CRASH:\n{tb}")
            _derniere_erreur = tb

        _derniere_api   = _now()
        _dernier_import = _now()
        return imported
    finally:
        _lock_api.release()


# ── Import complet (RSS + API, appelé au démarrage ou refresh manuel) ─────────

def importer_tout(app) -> int:
    """Lance RSS + API sans tenir compte des cooldowns. Pour démarrage et refresh."""
    global _dernier_rss, _derniere_api, _dernier_import, _derniere_erreur

    imported = 0
    try:
        with app.app_context():
            from app import db
            from app.models.info_live import InfoLive
            from sqlalchemy import text

            try:
                db.session.execute(text(
                    "ALTER TABLE infos_live ADD COLUMN source_url VARCHAR(500)"
                ))
                db.session.commit()
            except Exception:
                db.session.rollback()

            # RSS
            for source in SOURCES_RSS:
                try:
                    arts = fetch_rss(source["url"])
                    n = _sauvegarder(arts, source["name"], filtrer=True, db=db, InfoLive=InfoLive)
                    if n:
                        db.session.commit()
                        imported += n
                except Exception as e:
                    logger.warning(f"[RSS] {source['name']}: {e}")
                    db.session.rollback()

            # The Guardian
            try:
                arts = fetch_guardian()
                n = _sauvegarder(arts, "The Guardian", filtrer=True, db=db, InfoLive=InfoLive)
                if n:
                    db.session.commit()
                    imported += n
            except Exception as e:
                logger.warning(f"[Guardian] {e}")
                db.session.rollback()

            # NewsAPI
            newsapi_key = os.getenv("NEWSAPI_KEY", "")
            if newsapi_key:
                try:
                    arts = fetch_newsapi(newsapi_key)
                    n = _sauvegarder(arts, "NewsAPI", filtrer=False, db=db, InfoLive=InfoLive)
                    if n:
                        db.session.commit()
                        imported += n
                except Exception as e:
                    logger.warning(f"[NewsAPI] {e}")
                    db.session.rollback()

            logger.info(f"[importer_tout] ✅ {imported} nouveaux articles au total.")
            _derniere_erreur = None
    except Exception:
        tb = traceback.format_exc()
        logger.error(f"[importer_tout] CRASH:\n{tb}")
        _derniere_erreur = tb

    now = _now()
    _dernier_rss    = now
    _derniere_api   = now
    _dernier_import = now
    return imported


# ── Diagnostic ────────────────────────────────────────────────────────────────

def tester_sources(app) -> list:
    rapport = []
    for src in SOURCES_RSS:
        articles   = fetch_rss(src["url"])
        pertinents = [a for a in articles if est_pertinent(a["titre"] + " " + a["desc"])]
        rapport.append({
            "source":     src["name"],
            "url":        src["url"],
            "total":      len(articles),
            "pertinents": len(pertinents),
            "ok":         len(articles) > 0,
        })
    return rapport


# ── Compatibilité ascendante (appelé par __init__.py scheduler) ───────────────

def importer_si_necessaire(app) -> int:
    return importer_actualites(app)


def _now():
    return datetime.utcnow()
