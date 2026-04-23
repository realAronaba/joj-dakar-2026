from datetime import datetime
from app import db

CATEGORIES = {
    "competition": {"label": "Compétitions", "emoji": "🏅"},
    "site":        {"label": "Sites",         "emoji": "🏟️"},
    "travaux":     {"label": "Travaux",        "emoji": "🚧"},
    "annonce":     {"label": "Annonces",       "emoji": "📢"},
    "meteo":       {"label": "Météo",          "emoji": "🌤️"},
    "programme":   {"label": "Programme",      "emoji": "🔄"},
}


class InfoLive(db.Model):
    __tablename__ = "infos_live"

    id         = db.Column(db.Integer, primary_key=True)
    titre      = db.Column(db.String(200), nullable=False)
    contenu    = db.Column(db.Text, nullable=False)
    categorie  = db.Column(db.String(50), default="annonce")
    source_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        cat = CATEGORIES.get(self.categorie, {"label": self.categorie, "emoji": "📌"})
        delta = datetime.utcnow() - self.created_at
        if delta.seconds < 60 and delta.days == 0:
            age = "à l'instant"
        elif delta.days == 0 and delta.seconds < 3600:
            age = f"il y a {delta.seconds // 60} min"
        elif delta.days == 0:
            age = f"il y a {delta.seconds // 3600} h"
        else:
            age = self.created_at.strftime("%d %b à %H:%M")
        return {
            "id":         self.id,
            "titre":      self.titre,
            "contenu":    self.contenu,
            "categorie":  self.categorie,
            "cat_label":  cat["label"],
            "cat_emoji":  cat["emoji"],
            "age":        age,
            "created_at": self.created_at.strftime("%d %b %H:%M"),
            "source_url": self.source_url or "",
        }
