"""
Météo en temps réel pour les 3 zones JOJ Dakar 2026.
Utilise Open-Meteo (gratuit, sans clé API).
Met à jour une entrée InfoLive par zone (pas de doublon).
"""
import logging
import urllib.request
import json
from datetime import datetime

logger = logging.getLogger(__name__)

ZONES = [
    {
        "id":       "dakar",
        "nom":      "Dakar",
        "emoji":    "🏙️",
        "lat":      14.6937,
        "lon":      -17.4441,
        "source":   "meteo:dakar",
    },
    {
        "id":       "diamniadio",
        "nom":      "Diamniadio",
        "emoji":    "🏗️",
        "lat":      14.7190,
        "lon":      -17.1640,
        "source":   "meteo:diamniadio",
    },
    {
        "id":       "saly",
        "nom":      "Saly",
        "emoji":    "🌊",
        "lat":      14.4661,
        "lon":      -17.0062,
        "source":   "meteo:saly",
    },
]

# Codes météo WMO → description française + emoji
WMO_CODES = {
    0:  ("☀️", "Ciel dégagé"),
    1:  ("🌤️", "Principalement dégagé"),
    2:  ("⛅", "Partiellement nuageux"),
    3:  ("☁️", "Couvert"),
    45: ("🌫️", "Brouillard"),
    48: ("🌫️", "Brouillard givrant"),
    51: ("🌦️", "Bruine légère"),
    53: ("🌦️", "Bruine modérée"),
    55: ("🌧️", "Bruine forte"),
    61: ("🌧️", "Pluie légère"),
    63: ("🌧️", "Pluie modérée"),
    65: ("🌧️", "Pluie forte"),
    71: ("❄️", "Neige légère"),
    73: ("❄️", "Neige modérée"),
    75: ("❄️", "Neige forte"),
    80: ("🌦️", "Averses légères"),
    81: ("🌧️", "Averses modérées"),
    82: ("⛈️", "Averses violentes"),
    95: ("⛈️", "Orage"),
    96: ("⛈️", "Orage avec grêle"),
    99: ("⛈️", "Orage violent avec grêle"),
}


def fetch_meteo(zone: dict) -> dict | None:
    """Interroge Open-Meteo pour une zone. Retourne les données ou None."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={zone['lat']}&longitude={zone['lon']}"
        f"&current=temperature_2m,apparent_temperature,weathercode,"
        f"windspeed_10m,relativehumidity_2m,precipitation"
        f"&wind_speed_unit=kmh&timezone=Africa%2FDakar"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JOJ-Dakar-2026/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        cur = data.get("current", {})
        return {
            "temp":      cur.get("temperature_2m"),
            "ressenti":  cur.get("apparent_temperature"),
            "code":      cur.get("weathercode", 0),
            "vent":      cur.get("windspeed_10m"),
            "humidite":  cur.get("relativehumidity_2m"),
            "pluie":     cur.get("precipitation", 0),
        }
    except Exception as e:
        logger.warning(f"[weather] Open-Meteo ECHEC pour {zone['nom']}: {e}")
        return None


def _build_contenu(zone: dict, m: dict) -> str:
    emoji_cond, desc_cond = WMO_CODES.get(int(m["code"]), ("🌡️", "Conditions inconnues"))
    lines = [
        f"{emoji_cond} {desc_cond}",
        f"🌡️ Température : {m['temp']:.1f}°C  (ressentie {m['ressenti']:.1f}°C)",
        f"💧 Humidité : {m['humidite']}%",
        f"💨 Vent : {m['vent']:.0f} km/h",
    ]
    if m["pluie"] and m["pluie"] > 0:
        lines.append(f"🌧️ Précipitations : {m['pluie']} mm")
    lines.append(f"\n📡 Source : Open-Meteo · Mise à jour {datetime.utcnow().strftime('%H:%M')} UTC")
    return "\n".join(lines)


def mettre_a_jour_meteo(app) -> int:
    """Récupère la météo des 3 zones et met à jour les entrées InfoLive."""
    updated = 0
    try:
        with app.app_context():
            from app import db
            from app.models.info_live import InfoLive

            for zone in ZONES:
                m = fetch_meteo(zone)
                if not m:
                    continue

                emoji_cond, desc_cond = WMO_CODES.get(int(m["code"]), ("🌡️", "Conditions"))
                titre   = f"{zone['emoji']} Météo {zone['nom']} — {emoji_cond} {m['temp']:.1f}°C"
                contenu = _build_contenu(zone, m)

                # Mise à jour si l'entrée existe déjà, sinon création
                existing = InfoLive.query.filter_by(source_url=zone["source"]).first()
                if existing:
                    existing.titre      = titre
                    existing.contenu    = contenu
                    existing.created_at = datetime.utcnow()
                else:
                    db.session.add(InfoLive(
                        titre      = titre,
                        contenu    = contenu,
                        categorie  = "meteo",
                        source_url = zone["source"],
                    ))
                updated += 1
                logger.info(f"[weather] {zone['nom']}: {m['temp']}°C {desc_cond}")

            if updated:
                db.session.commit()
                logger.info(f"[weather] ✅ Météo mise à jour pour {updated} zone(s).")
    except Exception as e:
        logger.error(f"[weather] CRASH: {e}")

    return updated
