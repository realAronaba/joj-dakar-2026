from flask import Blueprint, request, jsonify
from app.models.site import Site
from app.models.epreuve import Epreuve

chat_bp = Blueprint("chat", __name__)

SUGGESTIONS = [
    "Quels sports sont au programme ?",
    "Quels sont les sites ?",
    "Comment aller à Diamniadio ?",
    "Quelles sont les dates ?",
    "Météo à Dakar en novembre ?",
    "Comment utiliser l'agenda ?",
]

REPONSES = {
    "greeting": (
        "Bonjour ! 👋 Je suis votre assistant JOJ Dakar 2026.\n"
        "Je peux vous aider sur le programme, les sites, les transports et bien plus.\n"
        "Que voulez-vous savoir ?"
    ),
    "dates": (
        "📅 Les Jeux Olympiques de la Jeunesse Dakar 2026 se déroulent du "
        "**31 octobre au 13 novembre 2026**.\n"
        "C'est la première édition africaine de l'histoire des JOJ !"
    ),
    "zones": (
        "Les compétitions se tiennent dans **3 zones** :\n"
        "🏙️ **Dakar** — le cœur historique\n"
        "🏗️ **Diamniadio** — la cité du futur (à 30 km de Dakar)\n"
        "🌊 **Saly** — la perle de l'Atlantique (à 80 km de Dakar)"
    ),
    "transport_diamniadio": (
        "🚆 Pour **Diamniadio** depuis Dakar :\n"
        "• Train Express Régional (TER) — départ gare de Dakar, ~30 min\n"
        "• Bus Dakar Dem Dikk sur l'autoroute à péage\n"
        "• Taxi ou VTC (~45 min selon trafic)\n"
        "• Des navettes officielles JOJ seront disponibles"
    ),
    "transport_saly": (
        "🌊 Pour **Saly** depuis Dakar :\n"
        "• Voiture sur l'autoroute à péage Dakar–Mbour (~1h30)\n"
        "• Bus Dakar Dem Dikk direction Mbour\n"
        "• Des navettes officielles JOJ seront prévues\n"
        "• Taxi collectif depuis Mbour"
    ),
    "transport_dakar": (
        "🏙️ Pour les sites de **Dakar** :\n"
        "• BRT (Bus Rapid Transit) — ligne principale\n"
        "• Petits taxis (tarif négocié ou compteur)\n"
        "• Yango / InDrive (VTC)\n"
        "• Consultez la carte pour localiser chaque site"
    ),
    "transport_general": (
        "🚌 Transport vers les sites :\n"
        "• **Diamniadio** : TER (Train Express Régional) depuis Dakar ~30 min\n"
        "• **Saly** : Voiture / bus ~1h30 depuis Dakar\n"
        "• **Dakar** : BRT, taxi, VTC\n"
        "• Des navettes officielles JOJ seront organisées\n\n"
        "Consultez la 🗺️ Carte pour localiser tous les sites."
    ),
    "tickets": (
        "🎟️ Les informations sur les billets seront publiées sur le site officiel :\n"
        "**olympics.com/fr/dakar-2026**\n\n"
        "Certaines épreuves pourraient être en accès libre. Restez connectés !"
    ),
    "agenda": (
        "⭐ **Mon Agenda** vous permet de :\n"
        "• Sauvegarder vos épreuves favorites\n"
        "• Recevoir des rappels par email\n"
        "• Exporter en calendrier (.ics)\n\n"
        "Cliquez sur ⭐ à côté de n'importe quelle épreuve dans le Programme."
    ),
    "live": (
        "🔴 La page **Live** affiche en temps réel :\n"
        "• Actualités et résultats JOJ\n"
        "• Météo des 3 zones (Dakar, Diamniadio, Saly)\n"
        "• Infos pratiques du jour\n\n"
        "Les données sont actualisées toutes les 15 minutes."
    ),
    "meteo": (
        "🌤️ **Météo en novembre à Dakar** :\n"
        "• Température : 26–30°C\n"
        "• Temps chaud et ensoleillé, fin de saison des pluies\n"
        "• Humidité modérée, brise marine agréable\n\n"
        "La météo en direct des 3 zones est disponible sur la page Live."
    ),
    "carte": (
        "🗺️ La **Carte interactive** vous permet de :\n"
        "• Localiser tous les sites de compétition\n"
        "• Voir les épreuves de chaque site\n"
        "• Planifier votre itinéraire\n\n"
        "Accessible depuis le menu → Carte."
    ),
    "hebergement": (
        "🏨 **Hébergement à Dakar et environs** :\n"
        "• Dakar : nombreux hôtels (Plateau, Almadies, Mermoz)\n"
        "• Diamniadio : hôtels modernes près des sites\n"
        "• Saly : station balnéaire avec hôtels et résidences\n\n"
        "Réservez tôt, la demande sera forte pendant les JOJ !"
    ),
    "securite": (
        "🔒 **Sécurité et conseils pratiques** :\n"
        "• Restez dans les zones balisées JOJ\n"
        "• Gardez vos affaires en sécurité dans les transports\n"
        "• Hydratez-vous bien (chaleur ~28°C)\n"
        "• Portez votre accréditation visible à tout moment\n"
        "• Numéro d'urgence Sénégal : **17** (Police), **15** (SAMU)"
    ),
    "app": (
        "📱 **Comment utiliser cette application** :\n"
        "• 🏠 **Accueil** : vue d'ensemble et accès rapides\n"
        "• 📅 **Programme** : toutes les épreuves par jour et sport\n"
        "• 🏟️ **Sites** : infos sur chaque lieu de compétition\n"
        "• 🗺️ **Carte** : localisation interactive\n"
        "• ⭐ **Mon Agenda** : vos épreuves favorites\n"
        "• 🔴 **Live** : actualités et météo en direct"
    ),
    "default": (
        "Je n'ai pas bien compris votre question. 😊\n"
        "Voici les sujets sur lesquels je peux vous aider :\n"
        "• 📅 Dates et programme des épreuves\n"
        "• 🏟️ Sites de compétition\n"
        "• 🚌 Transport et accès\n"
        "• 🌤️ Météo des 3 zones\n"
        "• 🎟️ Billets et accréditations\n"
        "• ⭐ Mon Agenda personnel\n"
        "• 🔴 Infos en direct"
    ),
}

LIENS = {
    "dates":    "/programme",
    "agenda":   "/agenda",
    "live":     "/live",
    "carte":    "/carte",
    "zones":    "/sites",
    "app":      "/programme",
    "transport_general": "/carte",
    "transport_dakar":   "/carte",
    "transport_diamniadio": "/carte",
    "transport_saly":    "/carte",
}


def detecter_intention(msg):
    m = msg.lower()
    if any(w in m for w in ["bonjour", "salut", "hello", "hi", "bonsoir", "aide", "aider", "dalal"]):
        return "greeting"
    if any(w in m for w in ["date", "quand", "durée", "combien de temps", "novembre", "octobre", "jours"]):
        return "dates"
    if "diamniadio" in m:
        return "transport_diamniadio"
    if "saly" in m and any(w in m for w in ["aller", "transport", "bus", "accès", "comment"]):
        return "transport_saly"
    if "dakar" in m and any(w in m for w in ["aller", "transport", "bus", "taxi", "accès", "comment"]):
        return "transport_dakar"
    if any(w in m for w in ["transport", "bus", "taxi", "train", "ter", "aller", "accès", "navette", "déplacer", "comment aller", "comment se rendre"]):
        return "transport_general"
    if any(w in m for w in ["sport", "discipline", "quels sport", "épreuve", "jeux"]):
        return "sports"
    if any(w in m for w in ["site", "stade", "arène", "salle", "piscine", "complexe", "lieu", "où se"]):
        return "sites"
    if any(w in m for w in ["zone", "ville", "région", "dakar", "diamniadio", "saly"]):
        return "zones"
    if any(w in m for w in ["billet", "ticket", "entrée", "prix", "coût", "tarif", "gratuit", "accrédit"]):
        return "tickets"
    if any(w in m for w in ["agenda", "favori", "sauvegarder", "étoile", "rappel", "notification"]):
        return "agenda"
    if any(w in m for w in ["live", "direct", "résultat", "score", "temps réel", "actualité"]):
        return "live"
    if any(w in m for w in ["météo", "temps", "température", "climat", "pluie", "chaud", "froid", "chaleur"]):
        return "meteo"
    if any(w in m for w in ["carte", "map", "localisation", "où", "plan", "itinéraire"]):
        return "carte"
    if any(w in m for w in ["hôtel", "hébergement", "loger", "dormir", "auberge", "logement"]):
        return "hebergement"
    if any(w in m for w in ["sécurité", "danger", "urgence", "police", "médecin", "samu", "sûr"]):
        return "securite"
    if any(w in m for w in ["application", "app", "utiliser", "fonctionner", "comment ça", "menu"]):
        return "app"
    return "default"


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    msg  = (data.get("message") or "").strip()

    if not msg:
        return jsonify({"response": REPONSES["greeting"], "suggestions": SUGGESTIONS[:4]})

    intention = detecter_intention(msg)

    if intention == "sports":
        sports = sorted({e.sport for e in Epreuve.query.all()})
        if sports:
            liste = "\n".join(f"• {s}" for s in sports)
            reponse = f"🏅 **{len(sports)} sports** sont au programme :\n{liste}"
        else:
            reponse = "Le programme des sports sera bientôt disponible."
        return jsonify({"response": reponse, "link": "/programme", "link_label": "Voir le programme"})

    if intention == "sites":
        sites = Site.query.order_by(Site.zone, Site.nom).all()
        if sites:
            par_zone = {}
            for s in sites:
                par_zone.setdefault(s.zone, []).append(s.nom)
            emojis = {"Dakar": "🏙️", "Diamniadio": "🏗️", "Saly": "🌊"}
            lignes = []
            for zone, noms in par_zone.items():
                lignes.append(f"{emojis.get(zone,'📍')} **{zone}** : {', '.join(noms)}")
            reponse = "🏟️ Sites de compétition :\n" + "\n".join(lignes)
        else:
            reponse = "Consultez la page Sites pour la liste complète."
        return jsonify({"response": reponse, "link": "/sites", "link_label": "Voir les sites"})

    reponse = REPONSES.get(intention, REPONSES["default"])
    result  = {"response": reponse}
    if intention in LIENS:
        labels = {
            "dates": "Voir le programme", "agenda": "Mon agenda",
            "live": "Page Live", "carte": "Carte interactive",
            "zones": "Les sites", "app": "Programme",
            "transport_general": "Carte", "transport_dakar": "Carte",
            "transport_diamniadio": "Carte", "transport_saly": "Carte",
        }
        result["link"]       = LIENS[intention]
        result["link_label"] = labels.get(intention, "En savoir plus")

    return jsonify(result)


@chat_bp.route("/api/chat/suggestions")
def suggestions():
    return jsonify(SUGGESTIONS)
