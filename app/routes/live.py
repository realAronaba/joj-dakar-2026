import json
from flask import Blueprint, request, jsonify, render_template_string, current_app
from app import db
from app.models.info_live import InfoLive, CATEGORIES

live_bp = Blueprint("live", __name__)


# ── API : lecture du fil ──────────────────────────────────────────────────────

@live_bp.route("/api/live/infos")
def get_infos():
    since_id = request.args.get("since_id", 0, type=int)
    limit    = request.args.get("limit", 30, type=int)
    q = InfoLive.query.order_by(InfoLive.created_at.desc())
    if since_id:
        q = InfoLive.query.filter(InfoLive.id > since_id).order_by(InfoLive.created_at.asc())
    infos = q.limit(limit).all()
    return jsonify([i.to_dict() for i in infos])


@live_bp.route("/api/live/ticker")
def ticker():
    infos = InfoLive.query.order_by(InfoLive.created_at.desc()).limit(8).all()
    return jsonify([i.to_dict() for i in infos])


# ── API : publication (admin) ─────────────────────────────────────────────────

@live_bp.route("/api/live/infos", methods=["POST"])
def post_info():
    token = current_app.config.get("LIVE_ADMIN_TOKEN", "")
    auth  = request.headers.get("X-Admin-Token", "") or request.args.get("token", "")
    if not token or auth != token:
        return jsonify({"error": "Non autorisé"}), 403

    data = request.get_json() or {}
    titre    = (data.get("titre") or "").strip()
    contenu  = (data.get("contenu") or "").strip()
    categorie = data.get("categorie", "annonce")

    if not titre or not contenu:
        return jsonify({"error": "titre et contenu requis"}), 400
    if categorie not in CATEGORIES:
        return jsonify({"error": "catégorie invalide"}), 400

    info = InfoLive(titre=titre, contenu=contenu, categorie=categorie)
    db.session.add(info)
    db.session.commit()
    return jsonify(info.to_dict()), 201


@live_bp.route("/api/live/infos/<int:info_id>", methods=["DELETE"])
def delete_info(info_id):
    token = current_app.config.get("LIVE_ADMIN_TOKEN", "")
    auth  = request.headers.get("X-Admin-Token", "") or request.args.get("token", "")
    if not token or auth != token:
        return jsonify({"error": "Non autorisé"}), 403
    info = InfoLive.query.get_or_404(info_id)
    db.session.delete(info)
    db.session.commit()
    return jsonify({"ok": True})


# ── Pages ─────────────────────────────────────────────────────────────────────

@live_bp.route("/live")
def page_live():
    from flask import render_template
    return render_template("live.html", categories=CATEGORIES)


@live_bp.route("/live/admin")
def page_admin():
    token = current_app.config.get("LIVE_ADMIN_TOKEN", "")
    auth  = request.args.get("token", "")
    if not token or auth != token:
        return "<h2 style='font-family:sans-serif;padding:2rem'>Accès refusé.</h2>", 403
    from flask import render_template
    return render_template("live_admin.html", categories=CATEGORIES, token=auth)
