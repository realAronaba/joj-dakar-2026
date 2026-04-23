"""Scheduler job : envoie les alertes email veille/matin."""
import json
from datetime import datetime, timedelta, time


def envoyer_alertes_email(app):
    with app.app_context():
        from app import db
        from app.models.email_subscription import EmailSubscription
        from app.models.epreuve import Epreuve
        from app.routes.email_notif import _send_email, ALERTE_HTML, EVENT_ITEM_HTML

        now     = datetime.utcnow()
        today   = now.date()
        demain  = today + timedelta(days=1)

        subs = EmailSubscription.query.filter_by(confirmed=True).all()
        if not subs:
            return

        for sub in subs:
            try:
                ids = json.loads(sub.agenda_ids or "[]")
                if not ids:
                    continue

                veille_sent = set(json.loads(sub.veille_sent or "[]"))
                matin_sent  = set(json.loads(sub.matin_sent  or "[]"))
                changed     = False

                # ── Alerte VEILLE (entre 17h00 et 19h30) ─────────────────────
                if sub.pref_veille and time(17, 0) <= now.time() <= time(19, 30):
                    epreuves_demain = [
                        e for e in Epreuve.query.filter(Epreuve.id.in_(ids)).all()
                        if e.date_heure.date() == demain and e.id not in veille_sent
                    ]
                    if epreuves_demain:
                        html = _build_alerte(epreuves_demain, sub.token,
                                             "Vos épreuves de demain",
                                             f"📅 Rappel : {len(epreuves_demain)} épreuve(s) demain",
                                             demain.strftime("%A %d %B"), app)
                        if _send_email(sub.email,
                                       f"🏅 JOJ Dakar 2026 — Vos épreuves de demain ({demain.strftime('%d %b')})",
                                       html, app):
                            veille_sent.update(e.id for e in epreuves_demain)
                            sub.veille_sent = json.dumps(list(veille_sent))
                            changed = True

                # ── Alerte MATIN (entre 07h30 et 09h30) ──────────────────────
                if sub.pref_matin and time(7, 30) <= now.time() <= time(9, 30):
                    epreuves_aujd = [
                        e for e in Epreuve.query.filter(Epreuve.id.in_(ids)).all()
                        if e.date_heure.date() == today and e.id not in matin_sent
                    ]
                    if epreuves_aujd:
                        html = _build_alerte(epreuves_aujd, sub.token,
                                             "Vos épreuves aujourd'hui",
                                             f"⏰ {len(epreuves_aujd)} épreuve(s) aujourd'hui",
                                             today.strftime("%A %d %B"), app)
                        if _send_email(sub.email,
                                       f"🏅 JOJ Dakar 2026 — Vos épreuves du jour ({today.strftime('%d %b')})",
                                       html, app):
                            matin_sent.update(e.id for e in epreuves_aujd)
                            sub.matin_sent = json.dumps(list(matin_sent))
                            changed = True

                if changed:
                    db.session.commit()

            except Exception as e:
                app.logger.error(f"Erreur alerte email sub#{sub.id}: {e}")


def _build_alerte(epreuves, token, subtitle, title, date_str, app):
    from flask import url_for
    from app.routes.email_notif import ALERTE_HTML, EVENT_ITEM_HTML

    items = []
    for e in sorted(epreuves, key=lambda x: x.date_heure):
        gmaps = (f"https://www.google.com/maps/dir/?api=1"
                 f"&destination={e.site.latitude},{e.site.longitude}")
        items.append(EVENT_ITEM_HTML % {
            "sport":  e.sport.split("/")[0].strip(),
            "heure":  e.date_heure.strftime("%H:%M"),
            "titre":  e.titre,
            "site":   f"{e.site.nom}, {e.site.zone}",
            "gmaps":  gmaps,
        })

    with app.app_context():
        unsub_url = url_for("email.unsubscribe", token=token, _external=True)
        app_url   = url_for("main.agenda", _external=True)

    return ALERTE_HTML % {
        "subtitle":    subtitle,
        "title":       title,
        "events_html": "".join(items),
        "app_url":     app_url,
        "unsub_url":   unsub_url,
    }
