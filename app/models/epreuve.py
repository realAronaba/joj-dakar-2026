from app import db

class Epreuve(db.Model):
    __tablename__ = "epreuves"

    id          = db.Column(db.Integer, primary_key=True)
    titre       = db.Column(db.String(150), nullable=False)
    sport       = db.Column(db.String(100), nullable=False)
    phase       = db.Column(db.String(50),  nullable=False)   # Qualifications | Demi-finales | Finale | Cérémonie
    date_heure  = db.Column(db.DateTime,    nullable=False)
    site_id     = db.Column(db.Integer, db.ForeignKey("sites.id"), nullable=False)
    site        = db.relationship("Site", backref="epreuves")

    def __repr__(self):
        return f"<Epreuve {self.titre} — {self.date_heure:%d/%m %H:%M}>"

    def to_dict(self):
        return {
            "id":        self.id,
            "titre":     self.titre,
            "sport":     self.sport,
            "phase":     self.phase,
            "date":      self.date_heure.strftime("%Y-%m-%d"),
            "heure":     self.date_heure.strftime("%H:%M"),
            "site":      self.site.nom,
            "zone":      self.site.zone,
            "site_id":   self.site_id,
        }
