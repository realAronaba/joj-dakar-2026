import uuid
import logging
import threading
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.models.site import Site                              # noqa: F401
    from app.models.epreuve import Epreuve                      # noqa: F401
    from app.models.push_subscription import PushSubscription   # noqa: F401
    from app.models.email_subscription import EmailSubscription  # noqa: F401
    from app.models.info_live import InfoLive                    # noqa: F401

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
    from app.routes.email_notif import email_bp
    from app.routes.live import live_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(push_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(live_bp)

    # Scheduler APScheduler (push + email)
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()

        if Config.VAPID_PRIVATE_KEY:
            from app.notifications import envoyer_notifications
            scheduler.add_job(
                func=envoyer_notifications, args=[app],
                trigger="interval", minutes=5,
                id="notif_job", replace_existing=True,
            )

        from app.email_alerts import envoyer_alertes_email
        scheduler.add_job(
            func=envoyer_alertes_email, args=[app],
            trigger="interval", minutes=30,
            id="email_alert_job", replace_existing=True,
        )

        from app.news_fetcher import importer_actualites
        scheduler.add_job(
            func=importer_actualites, args=[app],
            trigger="interval", minutes=15,
            id="news_fetch_job", replace_existing=True,
        )

        from app.weather_fetcher import mettre_a_jour_meteo
        scheduler.add_job(
            func=mettre_a_jour_meteo, args=[app],
            trigger="interval", hours=3,
            id="weather_job", replace_existing=True,
        )

        scheduler.start()
        # Imports au démarrage (threads séparés pour ne pas bloquer)
        threading.Thread(target=importer_actualites, args=[app], daemon=True).start()
        threading.Thread(target=mettre_a_jour_meteo, args=[app], daemon=True).start()
        logger.info("Scheduler démarré (push + email + météo).")
    except Exception as e:
        logger.error(f"Scheduler non démarré : {e}")

    return app
