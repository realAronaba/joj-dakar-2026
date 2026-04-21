import json
import logging
from flask import Blueprint, request, jsonify, session
from app import db
from app.models.push_subscription import PushSubscription
from config import Config

push_bp = Blueprint("push", __name__)
logger  = logging.getLogger(__name__)


@push_bp.route("/api/push/vapid-public-key")
def vapid_public_key():
    return jsonify({"key": Config.VAPID_PUBLIC_KEY})


@push_bp.route("/api/push/subscribe", methods=["POST"])
def subscribe():
    data       = request.get_json()
    sub_info   = data.get("subscription")
    user_token = session.get("user_token", "")
    agenda_ids = session.get("agenda", [])

    if not sub_info or not user_token:
        return jsonify({"error": "données manquantes"}), 400

    endpoint = sub_info.get("endpoint", "")
    existing = PushSubscription.query.filter_by(endpoint=endpoint).first()

    if existing:
        existing.sub_json   = json.dumps(sub_info)
        existing.agenda_ids = json.dumps(agenda_ids)
        existing.user_token = user_token
    else:
        db.session.add(PushSubscription(
            user_token = user_token,
            endpoint   = endpoint,
            sub_json   = json.dumps(sub_info),
            agenda_ids = json.dumps(agenda_ids),
        ))
    db.session.commit()
    return jsonify({"status": "ok"})


@push_bp.route("/api/push/unsubscribe", methods=["POST"])
def unsubscribe():
    user_token = session.get("user_token", "")
    if user_token:
        PushSubscription.query.filter_by(user_token=user_token).delete()
        db.session.commit()
    return jsonify({"status": "ok"})


@push_bp.route("/api/push/sync-agenda", methods=["POST"])
def sync_agenda():
    user_token = session.get("user_token", "")
    agenda_ids = session.get("agenda", [])
    if user_token:
        sub = PushSubscription.query.filter_by(user_token=user_token).first()
        if sub:
            sub.agenda_ids = json.dumps(agenda_ids)
            db.session.commit()
    return jsonify({"status": "ok"})
