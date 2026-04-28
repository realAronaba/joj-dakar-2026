import os
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

MAX_HISTORY = 10  # messages conservés en session


def build_system_prompt():
    """Construit le prompt système avec les données réelles de la BD."""
    sports = sorted({e.sport for e in Epreuve.query.all()})
    sites  = Site.query.order_by(Site.zone, Site.nom).all()

    par_zone = {}
    for s in sites:
        par_zone.setdefault(s.zone, []).append(s.nom)

    sports_txt = ", ".join(sports) if sports else "programme à venir"
    zones_txt  = "\n".join(
        f"  - {z} : {', '.join(noms)}" for z, noms in par_zone.items()
    )

    return f"""Tu es l'assistant officieux de l'application JOJ Dakar 2026, une app citoyenne (non officielle) dédiée aux Jeux Olympiques de la Jeunesse qui se tiennent à Dakar, Sénégal.

=== INFORMATIONS CLÉS ===
- Événement : Jeux Olympiques de la Jeunesse (JOJ) Dakar 2026
- Dates : 31 octobre – 13 novembre 2026
- Lieu : Dakar, Sénégal — première édition africaine de l'histoire des JOJ
- Site officiel : olympics.com/fr/dakar-2026

=== SPORTS AU PROGRAMME ===
{sports_txt}

=== ZONES ET SITES DE COMPÉTITION ===
{zones_txt}

=== TRANSPORT ===
- Dakar : BRT (Bus Rapid Transit), petits taxis (tarif à négocier), Yango/InDrive (VTC)
- Diamniadio (30 km de Dakar) : TER (Train Express Régional) depuis la gare de Dakar en ~30 min, bus Dakar Dem Dikk, navettes JOJ prévues
- Saly (80 km de Dakar) : voiture sur autoroute à péage (~1h30), bus Dakar Dem Dikk direction Mbour, navettes JOJ prévues

=== MÉTÉO EN NOVEMBRE ===
- Dakar : 26–30°C, ensoleillé, fin de saison des pluies, brise marine agréable
- Diamniadio : légèrement plus chaud (~32°C), moins humide
- Saly : 27–30°C, bord de mer, brise fraîche

=== BILLETS ===
Les billets seront disponibles sur olympics.com/fr/dakar-2026. Certaines épreuves pourraient être en accès libre. Restez connectés pour les annonces.

=== HÉBERGEMENT ===
- Dakar : hôtels sur le Plateau, aux Almadies, à Mermoz (réservez tôt)
- Diamniadio : hôtels modernes en développement près des sites
- Saly : station balnéaire avec nombreux hôtels et résidences

=== SÉCURITÉ / URGENCES ===
- Police : 17
- SAMU : 15
- Restez dans les zones balisées JOJ, hydratez-vous (chaleur ~28°C)

=== FONCTIONNALITÉS DE L'APPLICATION ===
- Accueil : vue d'ensemble, message de bienvenue
- Programme : toutes les épreuves filtrées par jour et par sport
- Sites : infos détaillées sur chaque site de compétition
- Carte : carte interactive pour localiser les sites
- Mon Agenda ⭐ : sauvegardez vos épreuves favorites, recevez des rappels email, exportez en .ics
- Live 🔴 : actualités JOJ en temps réel, météo des 3 zones, mis à jour toutes les 15 min

=== TON ET COMPORTEMENT ===
- Réponds toujours en français, de façon amicale, claire et concise
- Tu peux aussi comprendre les questions en anglais ou wolof et répondre en français
- Si tu ne sais pas quelque chose de précis, oriente vers olympics.com/fr/dakar-2026
- N'invente pas de données (horaires précis, prix exacts, etc.) qui ne sont pas dans ce contexte
- Mentionne les pages de l'app quand c'est pertinent (Programme, Carte, Live, Mon Agenda)
- Tes réponses font au maximum 4-5 phrases sauf si une liste est vraiment nécessaire
"""


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"response": "L'assistant IA n'est pas encore configuré. Contactez l'administrateur.", "suggestions": SUGGESTIONS[:4]})

    data    = request.get_json() or {}
    msg     = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"response": "Bonjour ! 👋 Comment puis-je vous aider ?", "suggestions": SUGGESTIONS[:4]})

    # Historique de conversation en session
    history = session.get("chat_history", [])

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        system_prompt = build_system_prompt()

        # Construit les messages pour l'API
        messages = history[-MAX_HISTORY:] + [{"role": "user", "content": msg}]

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            messages=messages,
        )

        reply = response.content[0].text

        # Met à jour l'historique
        history.append({"role": "user",      "content": msg})
        history.append({"role": "assistant", "content": reply})
        session["chat_history"] = history[-MAX_HISTORY:]
        session.modified = True

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"response": f"Une erreur est survenue : {str(e)[:100]}"})


@chat_bp.route("/api/chat/reset", methods=["POST"])
def chat_reset():
    session.pop("chat_history", None)
    return jsonify({"ok": True})


@chat_bp.route("/api/chat/suggestions")
def suggestions():
    return jsonify(SUGGESTIONS)
