import json
import uuid
from flask import Blueprint, request, jsonify, session, render_template_string, current_app, url_for
from app import db
from app.models.email_subscription import EmailSubscription

email_bp = Blueprint("email", __name__)


# ── Templates email inline ────────────────────────────────────────────────────

CONFIRMATION_HTML = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JOJ Dakar 2026 — Confirmez votre abonnement</title></head>
<body style="font-family:Arial,sans-serif;background:#f4f4f0;margin:0;padding:20px">
<div style="max-width:580px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;
            box-shadow:0 4px 20px rgba(0,0,0,.08)">
  <div style="background:#00853F;padding:28px;text-align:center">
    <p style="margin:0;font-size:2rem">🏅</p>
    <h1 style="color:#fff;margin:8px 0 4px;font-size:1.4rem">JOJ Dakar 2026</h1>
    <p style="color:#FDEF42;margin:0;font-size:.9rem">Alertes épreuves</p>
  </div>
  <div style="padding:32px">
    <h2 style="margin-top:0">Confirmez votre abonnement</h2>
    <p>Bonjour,</p>
    <p>Vous avez demandé à recevoir des alertes par email pour vos épreuves
       sélectionnées sur l'agenda JOJ Dakar 2026.</p>
    <p><strong>Préférences :</strong></p>
    <ul>%(prefs)s</ul>
    <p style="text-align:center;margin:32px 0">
      <a href="%(confirm_url)s"
         style="background:#00853F;color:#fff;padding:14px 28px;border-radius:8px;
                text-decoration:none;font-weight:700;display:inline-block;font-size:1rem">
        ✅ Confirmer mon abonnement
      </a>
    </p>
    <p style="color:#888;font-size:.82rem;border-top:1px solid #eee;padding-top:16px">
      Si vous n'avez pas effectué cette demande, ignorez simplement cet email.<br>
      Pour vous désabonner immédiatement :
      <a href="%(unsub_url)s" style="color:#c00">cliquez ici</a>
    </p>
  </div>
</div></body></html>"""

ALERTE_HTML = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JOJ Dakar 2026 — Rappel épreuves</title></head>
<body style="font-family:Arial,sans-serif;background:#f4f4f0;margin:0;padding:20px">
<div style="max-width:580px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;
            box-shadow:0 4px 20px rgba(0,0,0,.08)">
  <div style="background:#00853F;padding:24px;text-align:center">
    <p style="margin:0;font-size:1.8rem">🏅</p>
    <h1 style="color:#fff;margin:6px 0 4px;font-size:1.3rem">JOJ Dakar 2026</h1>
    <p style="color:#FDEF42;margin:0;font-size:.9rem">%(subtitle)s</p>
  </div>
  <div style="padding:28px">
    <h2 style="margin-top:0">%(title)s</h2>
    %(events_html)s
    <div style="text-align:center;margin:28px 0 0">
      <a href="%(app_url)s"
         style="background:#00853F;color:#fff;padding:12px 24px;border-radius:8px;
                text-decoration:none;font-weight:700;display:inline-block">
        📅 Voir mon agenda
      </a>
    </div>
    <p style="color:#aaa;font-size:.78rem;margin-top:24px;border-top:1px solid #eee;padding-top:12px">
      <a href="%(unsub_url)s" style="color:#aaa">Se désabonner</a>
    </p>
  </div>
</div></body></html>"""

EVENT_ITEM_HTML = """
<div style="border:1px solid #e5e5e5;border-radius:8px;padding:16px;margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
    <span style="background:#00853F22;color:#00853F;padding:3px 10px;border-radius:99px;
                 font-size:.78rem;font-weight:700">%(sport)s</span>
    <span style="color:#555;font-size:.85rem;font-weight:700">%(heure)s</span>
  </div>
  <p style="margin:4px 0;font-weight:700;font-size:.95rem">%(titre)s</p>
  <p style="margin:4px 0;color:#666;font-size:.85rem">📍 %(site)s</p>
  <a href="%(gmaps)s" style="display:inline-block;margin-top:8px;font-size:.82rem;
     color:#1a73e8;text-decoration:none">🗺️ Itinéraire Google Maps</a>
</div>"""

PAGE_CONFIRM_OK = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Abonnement confirmé — JOJ Dakar 2026</title>
<style>body{font-family:Arial,sans-serif;background:#f4f4f0;display:flex;
  align-items:center;justify-content:center;min-height:100vh;margin:0}
  .box{background:#fff;border-radius:12px;padding:40px;text-align:center;
  max-width:420px;box-shadow:0 4px 20px rgba(0,0,0,.08)}
  h1{color:#00853F} a{color:#00853F}</style></head>
<body><div class="box">
  <p style="font-size:3rem">✅</p>
  <h1>Abonnement confirmé !</h1>
  <p>Vous recevrez désormais vos alertes par email avant vos épreuves JOJ Dakar 2026.</p>
  <a href="/">← Retour à l'accueil</a>
</div></body></html>"""

PAGE_UNSUB_OK = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Désabonnement — JOJ Dakar 2026</title>
<style>body{font-family:Arial,sans-serif;background:#f4f4f0;display:flex;
  align-items:center;justify-content:center;min-height:100vh;margin:0}
  .box{background:#fff;border-radius:12px;padding:40px;text-align:center;
  max-width:420px;box-shadow:0 4px 20px rgba(0,0,0,.08)}
  a{color:#00853F}</style></head>
<body><div class="box">
  <p style="font-size:3rem">👋</p>
  <h2>Vous êtes désabonné(e)</h2>
  <p>Vous ne recevrez plus d'alertes email pour les JOJ Dakar 2026.</p>
  <a href="/">← Retour à l'accueil</a>
</div></body></html>"""


# ── Utilitaire envoi email ────────────────────────────────────────────────────

def _send_email(to, subject, html, app):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    server   = app.config.get("MAIL_SERVER", "")
    port     = int(app.config.get("MAIL_PORT", 587))
    username = app.config.get("MAIL_USERNAME", "")
    password = app.config.get("MAIL_PASSWORD", "")
    sender   = app.config.get("MAIL_SENDER", "JOJ Dakar 2026 <noreply@joj-dakar.sn>")

    if not server or not username:
        app.logger.warning("Email non configuré (MAIL_SERVER/MAIL_USERNAME manquant).")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = to
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP(server, port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        app.logger.error(f"Erreur envoi email à {to}: {e}")
        return False


# ── Routes ────────────────────────────────────────────────────────────────────

@email_bp.route("/api/email/subscribe", methods=["POST"])
def subscribe():
    data       = request.get_json() or {}
    email      = data.get("email", "").strip().lower()
    prefs      = data.get("prefs", {})
    user_token = session.get("user_token")
    agenda_ids = session.get("agenda", [])

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Email invalide"}), 400

    sub = EmailSubscription.query.filter_by(user_token=user_token).first()
    if not sub:
        sub = EmailSubscription(user_token=user_token)
        db.session.add(sub)

    sub.email        = email
    sub.token        = str(uuid.uuid4())
    sub.confirmed    = False
    sub.pref_veille  = bool(prefs.get("veille", True))
    sub.pref_matin   = bool(prefs.get("matin", False))
    sub.pref_changes = bool(prefs.get("changes", False))
    sub.agenda_ids   = json.dumps(agenda_ids)
    sub.veille_sent  = "[]"
    sub.matin_sent   = "[]"
    db.session.commit()

    confirm_url = url_for("email.confirm", token=sub.token, _external=True)
    unsub_url   = url_for("email.unsubscribe", token=sub.token, _external=True)

    prefs_items = []
    if sub.pref_veille:  prefs_items.append("<li>La veille de chaque épreuve</li>")
    if sub.pref_matin:   prefs_items.append("<li>Le matin même de chaque épreuve</li>")
    if sub.pref_changes: prefs_items.append("<li>En cas de changement important</li>")
    if not prefs_items:  prefs_items.append("<li>Veille de chaque épreuve</li>")

    html = CONFIRMATION_HTML % {
        "prefs":       "".join(prefs_items),
        "confirm_url": confirm_url,
        "unsub_url":   unsub_url,
    }
    _send_email(email, "✅ Confirmez vos alertes JOJ Dakar 2026", html, current_app._get_current_object())
    return jsonify({"ok": True})


@email_bp.route("/api/email/confirm/<token>")
def confirm(token):
    sub = EmailSubscription.query.filter_by(token=token).first_or_404()
    sub.confirmed = True
    db.session.commit()
    return PAGE_CONFIRM_OK


@email_bp.route("/api/email/unsubscribe/<token>")
def unsubscribe(token):
    sub = EmailSubscription.query.filter_by(token=token).first()
    if sub:
        db.session.delete(sub)
        db.session.commit()
    return PAGE_UNSUB_OK


@email_bp.route("/api/email/status")
def status():
    user_token = session.get("user_token")
    sub = EmailSubscription.query.filter_by(user_token=user_token).first()
    if sub and sub.confirmed:
        return jsonify({"subscribed": True, "email": sub.email})
    return jsonify({"subscribed": False})
