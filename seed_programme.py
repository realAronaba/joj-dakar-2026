from datetime import datetime
from app import create_app, db
from app.models.site import Site
from app.models.epreuve import Epreuve

app = create_app()

# Helper
def dt(jour, heure):
    """Construit un datetime pour novembre 2026 (ou oct 31)."""
    mois = 10 if jour == 31 else 11
    j    = jour if jour == 31 else jour
    h, m = map(int, heure.split(":"))
    return datetime(2026, mois, j, h, m)

PROGRAMME = [
    # ── 31 octobre : Cérémonie d'ouverture ──────────────────────────
    ("Cérémonie d'ouverture des JOJ Dakar 2026",    "Cérémonie", "Cérémonie",     31, "19:00", "Stade Léopold Sédar Senghor"),

    # ── 1er novembre ────────────────────────────────────────────────
    ("Athlétisme — 100m haies (Q)",                 "Athlétisme","Qualifications",  1, "09:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m nage libre (Q)",              "Natation",  "Qualifications",  1, "10:00", "Piscine Olympique de Diamniadio"),
    ("Surf — Tour préliminaire",                    "Surf",      "Qualifications",  1, "07:30", "Plage de Ngor"),
    ("Basketball 3x3 — Phase de groupes",           "Basketball","Qualifications",  1, "14:00", "Dakar Arena"),
    ("Beach Volley — Phase de groupes",             "Beach Volley","Qualifications",1, "10:00", "Plage de Saly"),
    ("Voile — Course 1",                            "Voile",     "Qualifications",  1, "11:00", "Port de Saly"),

    # ── 2 novembre ──────────────────────────────────────────────────
    ("Athlétisme — 400m (Q)",                       "Athlétisme","Qualifications",  2, "09:30", "Stade Léopold Sédar Senghor"),
    ("Judo — Moins de 60 kg (Q)",                   "Judo",      "Qualifications",  2, "10:00", "Complexe Sportif de Diamniadio"),
    ("Natation — 200m dos (Q)",                     "Natation",  "Qualifications",  2, "10:00", "Piscine Olympique de Diamniadio"),
    ("Football — Phase de groupes (H)",             "Football",  "Qualifications",  2, "16:00", "Stade du Sénégal"),
    ("Handball — Phase de groupes (F)",             "Handball",  "Qualifications",  2, "15:00", "Palais des Sports de Diamniadio"),
    ("Golf — Tour 1",                               "Golf",      "Qualifications",  2, "08:00", "Club de Golf de Dakar"),

    # ── 3 novembre ──────────────────────────────────────────────────
    ("Boxe — Moins de 54 kg (Q)",                   "Boxe",      "Qualifications",  3, "11:00", "Complexe Sportif de Diamniadio"),
    ("Lutte — Catégorie 65 kg (Q)",                 "Lutte",     "Qualifications",  3, "14:00", "Complexe Sportif de Diamniadio"),
    ("Surf — Tour 2",                               "Surf",      "Qualifications",  3, "07:30", "Plage de Ngor"),
    ("Basketball 3x3 — Phase de groupes",           "Basketball","Qualifications",  3, "14:00", "Dakar Arena"),
    ("Équitation — Dressage (Q)",                   "Équitation","Qualifications",  3, "09:00", "Hippodrome de Saly"),

    # ── 4 novembre ──────────────────────────────────────────────────
    ("Athlétisme — 1500m (Q)",                      "Athlétisme","Qualifications",  4, "09:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m brasse (Q)",                  "Natation",  "Qualifications",  4, "10:00", "Piscine Olympique de Diamniadio"),
    ("Football — Phase de groupes (F)",             "Football",  "Qualifications",  4, "16:00", "Stade du Sénégal"),
    ("Voile — Course 2",                            "Voile",     "Qualifications",  4, "11:00", "Port de Saly"),
    ("Beach Volley — Phase de groupes",             "Beach Volley","Qualifications",4, "10:00", "Plage de Saly"),
    ("Golf — Tour 2",                               "Golf",      "Qualifications",  4, "08:00", "Club de Golf de Dakar"),

    # ── 5 novembre ──────────────────────────────────────────────────
    ("Judo — Moins de 70 kg (Q)",                   "Judo",      "Qualifications",  5, "10:00", "Complexe Sportif de Diamniadio"),
    ("Gymnastics — Artistique (Q)",                 "Gymnastique","Qualifications", 5, "10:00", "Dakar Arena"),
    ("Surf — Demi-finales",                         "Surf",      "Demi-finales",    5, "07:30", "Plage de Ngor"),
    ("Handball — Phase de groupes (H)",             "Handball",  "Qualifications",  5, "15:00", "Palais des Sports de Diamniadio"),

    # ── 6 novembre ──────────────────────────────────────────────────
    ("Athlétisme — 100m haies (Finale)",            "Athlétisme","Finale",          6, "18:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m nage libre (Finale)",         "Natation",  "Finale",          6, "17:00", "Piscine Olympique de Diamniadio"),
    ("Basketball 3x3 — Demi-finales",               "Basketball","Demi-finales",    6, "15:00", "Dakar Arena"),
    ("Boxe — Moins de 54 kg (Demi-finales)",        "Boxe",      "Demi-finales",    6, "14:00", "Complexe Sportif de Diamniadio"),

    # ── 7 novembre ──────────────────────────────────────────────────
    ("Football — Demi-finales (H)",                 "Football",  "Demi-finales",    7, "16:00", "Stade du Sénégal"),
    ("Lutte — Demi-finales",                        "Lutte",     "Demi-finales",    7, "14:00", "Complexe Sportif de Diamniadio"),
    ("Surf — Finale",                               "Surf",      "Finale",          7, "10:00", "Plage de Ngor"),
    ("Beach Volley — Demi-finales",                 "Beach Volley","Demi-finales",  7, "10:00", "Plage de Saly"),
    ("Voile — Course finale",                       "Voile",     "Finale",          7, "11:00", "Port de Saly"),

    # ── 8 novembre ──────────────────────────────────────────────────
    ("Judo — Finales toutes catégories",            "Judo",      "Finale",          8, "16:00", "Complexe Sportif de Diamniadio"),
    ("Gymnastics — Finale au sol",                  "Gymnastique","Finale",         8, "17:00", "Dakar Arena"),
    ("Golf — Tour final",                           "Golf",      "Finale",          8, "08:00", "Club de Golf de Dakar"),
    ("Équitation — Saut d'obstacles (Finale)",      "Équitation","Finale",          8, "14:00", "Hippodrome de Saly"),

    # ── 9 novembre ──────────────────────────────────────────────────
    ("Athlétisme — 400m (Finale)",                  "Athlétisme","Finale",          9, "18:30", "Stade Léopold Sédar Senghor"),
    ("Natation — 200m dos (Finale)",                "Natation",  "Finale",          9, "17:00", "Piscine Olympique de Diamniadio"),
    ("Basketball 3x3 — Finale",                     "Basketball","Finale",          9, "17:00", "Dakar Arena"),
    ("Handball — Demi-finales",                     "Handball",  "Demi-finales",    9, "15:00", "Palais des Sports de Diamniadio"),

    # ── 10 novembre ─────────────────────────────────────────────────
    ("Football — Finale (H)",                       "Football",  "Finale",         10, "17:00", "Stade du Sénégal"),
    ("Boxe — Finales",                              "Boxe",      "Finale",         10, "16:00", "Complexe Sportif de Diamniadio"),
    ("Beach Volley — Finale",                       "Beach Volley","Finale",       10, "15:00", "Plage de Saly"),

    # ── 11 novembre ─────────────────────────────────────────────────
    ("Athlétisme — 1500m (Finale)",                 "Athlétisme","Finale",         11, "18:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m brasse (Finale)",             "Natation",  "Finale",         11, "17:00", "Piscine Olympique de Diamniadio"),
    ("Lutte — Finales",                             "Lutte",     "Finale",         11, "15:00", "Complexe Sportif de Diamniadio"),
    ("Handball — Finale",                           "Handball",  "Finale",         11, "17:00", "Palais des Sports de Diamniadio"),

    # ── 12 novembre ─────────────────────────────────────────────────
    ("Football — Finale (F)",                       "Football",  "Finale",         12, "16:00", "Stade du Sénégal"),
    ("Athlétisme — Relais 4x100m (Finale)",         "Athlétisme","Finale",         12, "18:30", "Stade Léopold Sédar Senghor"),
    ("Gymnastics — Finale aux agrès",               "Gymnastique","Finale",        12, "15:00", "Dakar Arena"),

    # ── 13 novembre : Cérémonie de clôture ──────────────────────────
    ("Cérémonie de clôture des JOJ Dakar 2026",    "Cérémonie", "Cérémonie",      13, "20:00", "Stade Léopold Sédar Senghor"),
]

with app.app_context():
    # Créer la table si elle n'existe pas
    db.create_all()

    Epreuve.query.delete()
    db.session.commit()

    sites = {s.nom: s for s in Site.query.all()}
    inseres = 0

    for titre, sport, phase, jour, heure, nom_site in PROGRAMME:
        site = sites.get(nom_site)
        if not site:
            print(f"  Site introuvable : {nom_site}")
            continue
        db.session.add(Epreuve(
            titre=titre,
            sport=sport,
            phase=phase,
            date_heure=dt(jour, heure),
            site_id=site.id,
        ))
        inseres += 1

    db.session.commit()
    print(f"\n{inseres} épreuves insérées.\n")

    # Résumé par jour
    from collections import Counter
    compteur = Counter(e.date_heure.strftime("%d %b") for e in Epreuve.query.all())
    for jour in sorted(compteur):
        print(f"  {jour} — {compteur[jour]} épreuve(s)")
