import uuid
from datetime import datetime
from app import db


class EmailSubscription(db.Model):
    __tablename__ = "email_subscriptions"

    id           = db.Column(db.Integer, primary_key=True)
    user_token   = db.Column(db.String(64), nullable=False, index=True)
    email        = db.Column(db.String(255), nullable=False)
    token        = db.Column(db.String(64), unique=True, nullable=False,
                             default=lambda: str(uuid.uuid4()))
    confirmed    = db.Column(db.Boolean, default=False)
    pref_veille  = db.Column(db.Boolean, default=True)
    pref_matin   = db.Column(db.Boolean, default=False)
    pref_changes = db.Column(db.Boolean, default=False)
    agenda_ids   = db.Column(db.Text, default="[]")
    veille_sent  = db.Column(db.Text, default="[]")
    matin_sent   = db.Column(db.Text, default="[]")
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
