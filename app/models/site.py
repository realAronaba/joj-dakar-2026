from app import db

class Site(db.Model):
    __tablename__ = "sites"

    id          = db.Column(db.Integer, primary_key=True)
    nom         = db.Column(db.String(100), nullable=False)
    zone        = db.Column(db.String(50),  nullable=False)   # Dakar | Diamniadio | Saly
    sport       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    capacite    = db.Column(db.Integer)
    latitude    = db.Column(db.Float, nullable=False)
    longitude   = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Site {self.nom} — {self.zone}>"

    def to_dict(self):
        return {
            "id":          self.id,
            "nom":         self.nom,
            "zone":        self.zone,
            "sport":       self.sport,
            "description": self.description,
            "capacite":    self.capacite,
            "latitude":    self.latitude,
            "longitude":   self.longitude,
        }
