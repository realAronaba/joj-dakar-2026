import threading
from flask import Blueprint, request, jsonify, render_template, current_app
from app import db
from app.models.info_live import InfoLive, CATEGORIES

live_bp = Blueprint("live", __name__)


# ── API : lecture du fil ──────────────────────────────────────────────────────

@live_bp.route("/api/live/infos")
def get_infos():
    since_id = request.args.get("since_id", 0, type=int)
    limit    = request.args.get("limit", 30, type=int)
    if since_id:
        q = (InfoLive.query
             .filter(InfoLive.id > since_id)
             .order_by(InfoLive.created_at.asc()))
    else:
        q = InfoLive.query.order_by(InfoLive.created_at.desc())
    return jsonify([i.to_dict() for i in q.limit(limit).all()])


@live_bp.route("/api/live/ticker")
def ticker():
    infos = InfoLive.query.order_by(InfoLive.created_at.desc()).limit(8).all()
    return jsonify([i.to_dict() for i in infos])


# ── API : météo (refresh immédiat) ───────────────────────────────────────────

@live_bp.route("/api/live/meteo", methods=["POST"])
def refresh_meteo():
    app = current_app._get_current_object()
    def _run():
        from app.weather_fetcher import mettre_a_jour_meteo
        mettre_a_jour_meteo(app)
    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"started": True})


# ── API : rafraîchissement (public, rate-limité côté fetcher) ─────────────────

@live_bp.route("/api/live/refresh", methods=["POST"])
def refresh():
    """
    Déclenche un import en arrière-plan.
    Retourne immédiatement {started: true/false} sans attendre la fin.
    """
    app = current_app._get_current_object()

    def _run():
        from app.news_fetcher import importer_tout
        importer_tout(app)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return jsonify({"started": True, "total": InfoLive.query.count()})


# ── API : statut public (diagnostic sans secret) ─────────────────────────────

@live_bp.route("/api/live/status")
def live_status():
    import os
    from app.news_fetcher import _dernier_import, _derniere_erreur
    return jsonify({
        "total":          InfoLive.query.count(),
        "newsapi_key_ok": bool(os.getenv("NEWSAPI_KEY", "")),
        "dernier_import": _dernier_import.isoformat() if _dernier_import else None,
        "derniere_erreur": _derniere_erreur,
    })


# ── API : purge des articles non pertinents (admin) ──────────────────────────

@live_bp.route("/api/live/purge", methods=["POST"])
def purge_non_pertinents():
    token = current_app.config.get("LIVE_ADMIN_TOKEN", "")
    auth  = request.headers.get("X-Admin-Token", "") or request.args.get("token", "")
    if not token or auth != token:
        return jsonify({"error": "Non autorisé"}), 403

    from app.news_fetcher import est_pertinent
    supprimes = 0
    gardes    = 0
    for info in InfoLive.query.all():
        # Les entrées météo ont une source_url commençant par "meteo:" → garder
        if info.source_url and info.source_url.startswith("meteo:"):
            gardes += 1
            continue
        full = info.titre + " " + info.contenu
        if not est_pertinent(full):
            db.session.delete(info)
            supprimes += 1
        else:
            gardes += 1
    db.session.commit()
    return jsonify({"supprimes": supprimes, "gardes": gardes})


# ── API : diagnostic sources (admin) ─────────────────────────────────────────

@live_bp.route("/api/live/debug")
def debug_sources():
    token = current_app.config.get("LIVE_ADMIN_TOKEN", "")
    auth  = request.headers.get("X-Admin-Token", "") or request.args.get("token", "")
    if not token or auth != token:
        return jsonify({"error": "Non autorisé"}), 403
    from app.news_fetcher import tester_sources
    rapport = tester_sources(current_app._get_current_object())
    return jsonify(rapport)


# ── API : publication (admin) ─────────────────────────────────────────────────

@live_bp.route("/api/live/infos", methods=["POST"])
def post_info():
    token = current_app.config.get("LIVE_ADMIN_TOKEN", "")
    auth  = request.headers.get("X-Admin-Token", "") or request.args.get("token", "")
    if not token or auth != token:
        return jsonify({"error": "Non autorisé"}), 403

    data      = request.get_json() or {}
    titre     = (data.get("titre") or "").strip()
    contenu   = (data.get("contenu") or "").strip()
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
    # Déclenche un import en arrière-plan à chaque ouverture de la page
    app = current_app._get_current_object()

    def _bg():
        from app.news_fetcher import importer_si_necessaire
        importer_si_necessaire(app)

    threading.Thread(target=_bg, daemon=True).start()
    return render_template("live.html", categories=CATEGORIES)


@live_bp.route("/live/admin")
def page_admin():
    token = current_app.config.get("LIVE_ADMIN_TOKEN", "")
    auth  = request.args.get("token", "")
    if not token or auth != token:
        return "<h2 style='font-family:sans-serif;padding:2rem'>Accès refusé.</h2>", 403
    return render_template("live_admin.html", categories=CATEGORIES, token=auth)
