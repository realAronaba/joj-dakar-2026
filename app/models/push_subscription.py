from datetime import datetime
from app import db

class PushSubscription(db.Model):
    __tablename__ = "push_subscriptions"
    id         = db.Column(db.Integer, primary_key=True)
    user_token = db.Column(db.String(64), nullable=False, index=True)
    endpoint   = db.Column(db.Text, nullable=False, unique=True)
    sub_json   = db.Column(db.Text, nullable=False)
    agenda_ids = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
