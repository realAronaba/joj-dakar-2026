import os
import json
import urllib.request
from flask import Blueprint, request, jsonify, session
from app.models.site import Site
from app.models.epreuve import Epreuve

chat_bp = Blueprint("chat", __name__)

SUGGESTIONS = [
    "Quels sports sont au programme ?",
    "Comment aller à Diamniadio ?",
    "Quelle météo en novembre à Dakar ?",
    "Comment utiliser Mon Agenda ?",
    "Quels sont les sites de compétition ?",
    "Y a-t-il des navettes officielles ?",
]

MAX_HISTORY = 10


def build_system_prompt():
    sports = sorted({e.sport for e in Epreuve.query.all()})
    sites  = Site.query.order_by(Site.zone, Site.nom).all()

    par_zone = {}
    for s in sites:
        par_zone.setdefault(s.zone, []).append(s.nom)

    sports_txt = ", ".join(sports) if sports else "programme à venir"
    zones_txt  = "\n".join(
        f"  - {z} : {', '.join(noms)}" for z, noms in par_zone.items()
    )

    return f"""Tu es l'assistant de l'application JOJ Dakar 2026, une app citoyenne (non officielle) dédiée aux Jeux Olympiques de la Jeunesse.

=== INFORMATIONS CLÉS ===
- Événement : Jeux Olympiques de la Jeunesse (JOJ) Dakar 2026
- Dates : 31 octobre – 13 novembre 2026
- Lieu : Dakar, Sénégal — première édition africaine des JOJ
- Site officiel : olympics.com/fr/dakar-2026

=== SPORTS AU PROGRAMME ===
{sports_txt}

=== ZONES ET SITES ===
{zones_txt}

=== TRANSPORT ===
- Dakar : BRT, petits taxis, Yango/InDrive
- Diamniadio (30 km) : TER depuis gare de Dakar en ~30 min, bus Dakar Dem Dikk, navettes JOJ
- Saly (80 km) : voiture ou bus direction Mbour (~1h30), navettes JOJ prévues

=== MÉTÉO NOVEMBRE ===
- Dakar : 26–30°C, ensoleillé, brise marine
- Diamniadio : ~32°C, moins humide
- Saly : 27–30°C, bord de mer

=== BILLETS ===
Disponibles sur olympics.com/fr/dakar-2026. Certaines épreuves en accès libre.

=== HÉBERGEMENT ===
- Dakar : hôtels Plateau, Almadies, Mermoz
- Diamniadio : hôtels modernes près des sites
- Saly : station balnéaire, hôtels et résidences

=== URGENCES ===
Police : 17 — SAMU : 15

=== FONCTIONNALITÉS APP ===
- Programme : épreuves par jour et sport
- Sites : infos sur chaque site
- Carte : localisation interactive
- Mon Agenda ⭐ : favoris, rappels email, export .ics
- Live 🔴 : actualités et météo en temps réel

=== COMPORTEMENT ===
- Réponds en français, de façon amicale et concise (3-4 phrases max sauf liste nécessaire)
- Si tu ne sais pas, oriente vers olympics.com/fr/dakar-2026
- N'invente pas de prix ou horaires précis non mentionnés ici
- Mentionne les pages de l'app quand c'est utile (Programme, Carte, Live, Mon Agenda)
"""


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return jsonify({
            "response": "L'assistant n'est pas encore configuré (clé GROQ manquante).",
            "suggestions": SUGGESTIONS[:4]
        })

    data = request.get_json() or {}
    msg  = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"response": "Bonjour ! 👋 Comment puis-je vous aider ?"})

    history = session.get("chat_history", [])

    messages = [{"role": "system", "content": build_system_prompt()}]
    messages += history[-MAX_HISTORY:]
    messages.append({"role": "user", "content": msg})

    payload = json.dumps({
        "model":       "llama-3.1-8b-instant",
        "messages":    messages,
        "max_tokens":  512,
        "temperature": 0.7,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        reply = result["choices"][0]["message"]["content"].strip()

        history.append({"role": "user",      "content": msg})
        history.append({"role": "assistant", "content": reply})
        session["chat_history"] = history[-MAX_HISTORY:]
        session.modified = True

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"response": "Désolé, une erreur est survenue. Réessayez dans un instant."})


@chat_bp.route("/api/chat/reset", methods=["POST"])
def chat_reset():
    session.pop("chat_history", None)
    return jsonify({"ok": True})


@chat_bp.route("/api/chat/suggestions")
def suggestions():
    return jsonify(SUGGESTIONS)
