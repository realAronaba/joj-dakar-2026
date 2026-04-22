import uuid
import logging
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.models.site import Site                          # noqa: F401
    from app.models.epreuve import Epreuve                   # noqa: F401
    from app.models.push_subscription import PushSubscription # noqa: F401

    with app.app_context():
        db.create_all()
        from app.seeds import SITES, seed_all
        expected = {s["nom"] for s in SITES}
        actual   = {s.nom for s in Site.query.all()}
        if not actual or expected != actual:
            from app.models.epreuve import Epreuve
            Epreuve.query.delete()
            Site.query.delete()
            db.session.commit()
            seed_all(db)

    # Token anonyme persistant par utilisateur
    @app.before_request
    def assigner_token():
        if "user_token" not in session:
            session.permanent = True
            session["user_token"] = str(uuid.uuid4())

    from app.routes.main import main_bp
    from app.routes.push import push_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(push_bp)

    # Scheduler de notifications (toutes les 5 min)
    if Config.VAPID_PRIVATE_KEY:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from app.notifications import envoyer_notifications
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                func     = envoyer_notifications,
                args     = [app],
                trigger  = "interval",
                minutes  = 5,
                id       = "notif_job",
                replace_existing = True,
            )
            scheduler.start()
            logger.info("Scheduler de notifications démarré.")
        except Exception as e:
            logger.error(f"Scheduler non démarré : {e}")

    return app
