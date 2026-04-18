from flask import Blueprint, render_template, jsonify, session
from app.models.site import Site
from app.models.epreuve import Epreuve
from collections import defaultdict

main_bp = Blueprint("main", __name__)

ZONES = ["Dakar", "Diamniadio", "Saly"]

@main_bp.route("/")
def index():
    return render_template("index.html")

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

@main_bp.route("/carte")
def carte():
    return render_template("carte.html")

@main_bp.route("/api/sites")
def api_sites():
    sites = Site.query.order_by(Site.zone, Site.nom).all()
    return jsonify([s.to_dict() for s in sites])
