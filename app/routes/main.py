from datetime import timedelta
from flask import Blueprint, render_template, jsonify, session, Response, request
from app.models.site import Site
from app.models.epreuve import Epreuve
from collections import defaultdict

main_bp = Blueprint("main", __name__)

ZONES = ["Dakar", "Diamniadio", "Saly"]

@main_bp.route("/")
def index():
    zones_data = []
    for zone in ZONES:
        sites = Site.query.filter_by(zone=zone).order_by(Site.nom).all()
        sports = sorted({s.sport for s in sites})
        zones_data.append({
            "nom": zone,
            "nb_sites": len(sites),
            "sports": sports,
            "noms_sites": [s.nom for s in sites],
        })
    return render_template("index.html", zones=zones_data)

@main_bp.route("/sites")
def sites():
    sites_par_zone = {
        zone: Site.query.filter_by(zone=zone).order_by(Site.nom).all()
        for zone in ZONES
    }
    return render_template("sites.html", sites_par_zone=sites_par_zone, zones=ZONES)

@main_bp.route("/programme")
def programme():
    epreuves = Epreuve.query.order_by(Epreuve.date_heure).all()

    par_jour = defaultdict(list)
    for e in epreuves:
        par_jour[e.date_heure.date()].append(e)

    jours   = sorted(par_jour.keys())
    sports  = sorted({e.sport for e in epreuves})
    agenda  = set(session.get("agenda", []))

    return render_template("programme.html",
                           par_jour=par_jour,
                           jours=jours,
                           sports=sports,
                           agenda=agenda)

@main_bp.route("/api/agenda/toggle/<int:epreuve_id>", methods=["POST"])
def agenda_toggle(epreuve_id):
    agenda = set(session.get("agenda", []))
    if epreuve_id in agenda:
        agenda.discard(epreuve_id)
        action = "retrait"
    else:
        epreuve = Epreuve.query.get_or_404(epreuve_id)  # noqa: F841
        agenda.add(epreuve_id)
        action = "ajout"
    session.permanent = True
    session["agenda"] = list(agenda)

    # Sync push subscription si l'utilisateur en a une
    user_token = session.get("user_token")
    if user_token:
        from app.models.push_subscription import PushSubscription
        sub = PushSubscription.query.filter_by(user_token=user_token).first()
        if sub:
            import json
            sub.agenda_ids = json.dumps(list(agenda))
            from app import db
            db.session.commit()

    return jsonify({"action": action, "total": len(agenda)})

@main_bp.route("/agenda")
def agenda():
    ids     = session.get("agenda", [])
    epreuves = (Epreuve.query
                .filter(Epreuve.id.in_(ids))
                .order_by(Epreuve.date_heure)
                .all()) if ids else []

    par_jour = defaultdict(list)
    for e in epreuves:
        par_jour[e.date_heure.date()].append(e)

    jours = sorted(par_jour.keys())
    return render_template("agenda.html", par_jour=par_jour, jours=jours, total=len(epreuves))

@main_bp.route("/api/epreuves/<int:epreuve_id>/ics")
def epreuve_ics(epreuve_id):
    e       = Epreuve.query.get_or_404(epreuve_id)
    fmt     = "%Y%m%dT%H%M%SZ"
    fin     = e.date_heure + timedelta(hours=2)
    lat, lon = e.site.latitude, e.site.longitude
    lieu    = f"{e.site.nom}, {e.site.zone}, Sénégal"
    gmaps   = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
    app_url = request.host_url.rstrip("/") + "/programme"
    desc    = (
        f"Sport: {e.sport}\\n"
        f"Phase: {e.phase}\\n"
        f"Site: {e.site.nom}\\n"
        f"Itinéraire: {gmaps}\\n"
        f"Programme: {app_url}"
    )
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//JOJ Dakar 2026//FR\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "BEGIN:VEVENT\r\n"
        f"DTSTART:{e.date_heure.strftime(fmt)}\r\n"
        f"DTEND:{fin.strftime(fmt)}\r\n"
        f"SUMMARY:{e.titre}\r\n"
        f"DESCRIPTION:{desc}\r\n"
        f"LOCATION:{lieu}\r\n"
        f"GEO:{lat};{lon}\r\n"
        f"URL:{gmaps}\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    return Response(
        ics,
        mimetype="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="joj-epreuve-{epreuve_id}.ics"'},
    )

@main_bp.route("/carte")
def carte():
    return render_template("carte.html")

@main_bp.route("/api/sites")
def api_sites():
    sites = Site.query.order_by(Site.zone, Site.nom).all()
    return jsonify([s.to_dict() for s in sites])

@main_bp.route("/api/sites/<int:site_id>")
def api_site_detail(site_id):
    site = Site.query.get_or_404(site_id)
    epreuves = (Epreuve.query
                .filter_by(site_id=site_id)
                .order_by(Epreuve.date_heure)
                .all())
    return jsonify({
        **site.to_dict(),
        "epreuves": [
            {
                "id":         e.id,
                "titre":      e.titre,
                "sport":      e.sport,
                "phase":      e.phase,
                "date_heure": e.date_heure.strftime("%d %b · %H:%M"),
                "jour":       e.date_heure.strftime("%A %d %B").capitalize(),
            }
            for e in epreuves
        ]
    })
