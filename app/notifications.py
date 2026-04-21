import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def envoyer_notifications(app):
    with app.app_context():
        from app import db
        from app.models.push_subscription import PushSubscription
        from app.models.epreuve import Epreuve
        from config import Config
        from pywebpush import webpush, WebPushException

        if not Config.VAPID_PRIVATE_KEY or not Config.VAPID_PUBLIC_KEY:
            return

        maintenant = datetime.now()
        dans_2h    = maintenant + timedelta(hours=2)
        debut      = dans_2h - timedelta(minutes=5)
        fin        = dans_2h + timedelta(minutes=5)

        epreuves = Epreuve.query.filter(
            Epreuve.date_heure >= debut,
            Epreuve.date_heure <= fin,
        ).all()

        if not epreuves:
            return

        subscriptions = PushSubscription.query.all()
        a_supprimer   = []

        for epreuve in epreuves:
            for sub in subscriptions:
                ids = json.loads(sub.agenda_ids or "[]")
                if epreuve.id not in ids:
                    continue
                try:
                    webpush(
                        subscription_info = json.loads(sub.sub_json),
                        data = json.dumps({
                            "title": f"🏅 Dans 2h — {epreuve.sport}",
                            "body":  f"{epreuve.titre}\n⏰ {epreuve.date_heure.strftime('%H:%M')} · {epreuve.site.nom}",
                            "url":   "/agenda",
                            "tag":   f"epreuve-{epreuve.id}",
                        }),
                        vapid_private_key = Config.VAPID_PRIVATE_KEY,
                        vapid_claims      = {"sub": f"mailto:{Config.VAPID_CONTACT}"},
                    )
                    logger.info(f"Notification envoyée : {epreuve.titre} → {sub.user_token[:8]}")
                except WebPushException as e:
                    status = getattr(e.response, "status_code", 0) if e.response else 0
                    if status in (404, 410):
                        a_supprimer.append(sub.id)
                    else:
                        logger.error(f"Push error : {e}")

        for sid in set(a_supprimer):
            sub = PushSubscription.query.get(sid)
            if sub:
                db.session.delete(sub)
        if a_supprimer:
            db.session.commit()
