from datetime import datetime


SITES = [
    # ── DAKAR ─────────────────────────────────────────────────────────
    {"nom": "Stade Léopold Sédar Senghor", "zone": "Dakar",
     "sport": "Athlétisme / Cérémonie d'ouverture",
     "description": "Stade iconique de Dakar, rénové pour accueillir la cérémonie d'ouverture et les épreuves d'athlétisme des JOJ 2026.",
     "capacite": 60000, "latitude": 14.7232, "longitude": -17.4636},
    {"nom": "Dakar Arena", "zone": "Diamniadio",
     "sport": "Basketball / Gymnastique",
     "description": "Grande salle polyvalente de Diamniadio accueillant le basketball 3x3 et la gymnastique artistique.",
     "capacite": 15000, "latitude": 14.733883498357407, "longitude": -17.21248156380716},
    {"nom": "Plage de Ngor", "zone": "Dakar",
     "sport": "Surf / Triathlon",
     "description": "Plage emblématique de la presqu'île du Cap-Vert, cadre idéal pour le surf et la natation en eau libre.",
     "capacite": 5000, "latitude": 14.7506, "longitude": -17.5194},
    {"nom": "Club de Golf de Dakar", "zone": "Dakar",
     "sport": "Golf",
     "description": "Le plus ancien golf du Sénégal, situé aux Almadies, face à l'Atlantique.",
     "capacite": 3000, "latitude": 14.7381, "longitude": -17.5162},

    # ── DIAMNIADIO ────────────────────────────────────────────────────
    {"nom": "Stade du Sénégal", "zone": "Diamniadio",
     "sport": "Football / Athlétisme",
     "description": "Stade ultramoderne de 50 000 places construit à Diamniadio, vitrine sportive du Sénégal nouveau.",
     "capacite": 50000, "latitude": 14.7267, "longitude": -17.2014},
    {"nom": "Complexe Sportif de Diamniadio", "zone": "Diamniadio",
     "sport": "Boxe / Lutte / Judo",
     "description": "Complexe multi-sports intégré au pôle urbain de Diamniadio, regroupant plusieurs salles de combat.",
     "capacite": 8000, "latitude": 14.7240, "longitude": -17.1980},
    {"nom": "Piscine Olympique de Dakar", "zone": "Dakar",
     "sport": "Natation / Plongeon",
     "description": "Piscine olympique 50 m au Point E à Dakar, rénovée pour accueillir les épreuves de natation et plongeon des JOJ 2026.",
     "capacite": 5000, "latitude": 14.696194098675694, "longitude": -17.461359735496124},
    {"nom": "Palais des Sports de Diamniadio", "zone": "Diamniadio",
     "sport": "Handball / Volleyball",
     "description": "Salle couverte dédiée aux sports collectifs en salle, avec tribunes modulables.",
     "capacite": 10000, "latitude": 14.7280, "longitude": -17.2000},

    # ── SALY ──────────────────────────────────────────────────────────
    {"nom": "Plage de Saly", "zone": "Saly",
     "sport": "Beach Volley / Beach Soccer",
     "description": "Station balnéaire de la Petite Côte, ses plages de sable blanc accueilleront les sports de plage.",
     "capacite": 6000, "latitude": 14.4644, "longitude": -17.0167},
    {"nom": "Port de Saly", "zone": "Saly",
     "sport": "Voile / Aviron / Canoë-Kayak",
     "description": "Base nautique aménagée sur la Petite Côte pour les épreuves de voile et sports de pagaie.",
     "capacite": 2000, "latitude": 14.4612, "longitude": -17.0195},
    {"nom": "Hippodrome de Saly", "zone": "Saly",
     "sport": "Équitation",
     "description": "Site équestre de référence en Afrique de l'Ouest, rénové pour les épreuves d'équitation des JOJ.",
     "capacite": 4000, "latitude": 14.4700, "longitude": -17.0120},
]


def _dt(jour, heure):
    mois = 10 if jour == 31 else 11
    h, m = map(int, heure.split(":"))
    return datetime(2026, mois, jour, h, m)


PROGRAMME = [
    ("Cérémonie d'ouverture des JOJ Dakar 2026",  "Cérémonie",    "Cérémonie",      31, "19:00", "Stade Léopold Sédar Senghor"),
    ("Athlétisme — 100m haies (Q)",               "Athlétisme",   "Qualifications",  1, "09:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m nage libre (Q)",            "Natation",     "Qualifications",  1, "10:00", "Piscine Olympique de Diamniadio"),
    ("Surf — Tour préliminaire",                  "Surf",         "Qualifications",  1, "07:30", "Plage de Ngor"),
    ("Basketball 3x3 — Phase de groupes",         "Basketball",   "Qualifications",  1, "14:00", "Dakar Arena"),
    ("Beach Volley — Phase de groupes",           "Beach Volley", "Qualifications",  1, "10:00", "Plage de Saly"),
    ("Voile — Course 1",                          "Voile",        "Qualifications",  1, "11:00", "Port de Saly"),
    ("Athlétisme — 400m (Q)",                     "Athlétisme",   "Qualifications",  2, "09:30", "Stade Léopold Sédar Senghor"),
    ("Judo — Moins de 60 kg (Q)",                 "Judo",         "Qualifications",  2, "10:00", "Complexe Sportif de Diamniadio"),
    ("Natation — 200m dos (Q)",                   "Natation",     "Qualifications",  2, "10:00", "Piscine Olympique de Diamniadio"),
    ("Football — Phase de groupes (H)",           "Football",     "Qualifications",  2, "16:00", "Stade du Sénégal"),
    ("Handball — Phase de groupes (F)",           "Handball",     "Qualifications",  2, "15:00", "Palais des Sports de Diamniadio"),
    ("Golf — Tour 1",                             "Golf",         "Qualifications",  2, "08:00", "Club de Golf de Dakar"),
    ("Boxe — Moins de 54 kg (Q)",                 "Boxe",         "Qualifications",  3, "11:00", "Complexe Sportif de Diamniadio"),
    ("Lutte — Catégorie 65 kg (Q)",               "Lutte",        "Qualifications",  3, "14:00", "Complexe Sportif de Diamniadio"),
    ("Surf — Tour 2",                             "Surf",         "Qualifications",  3, "07:30", "Plage de Ngor"),
    ("Basketball 3x3 — Phase de groupes",         "Basketball",   "Qualifications",  3, "14:00", "Dakar Arena"),
    ("Équitation — Dressage (Q)",                 "Équitation",   "Qualifications",  3, "09:00", "Hippodrome de Saly"),
    ("Athlétisme — 1500m (Q)",                    "Athlétisme",   "Qualifications",  4, "09:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m brasse (Q)",                "Natation",     "Qualifications",  4, "10:00", "Piscine Olympique de Diamniadio"),
    ("Football — Phase de groupes (F)",           "Football",     "Qualifications",  4, "16:00", "Stade du Sénégal"),
    ("Voile — Course 2",                          "Voile",        "Qualifications",  4, "11:00", "Port de Saly"),
    ("Beach Volley — Phase de groupes",           "Beach Volley", "Qualifications",  4, "10:00", "Plage de Saly"),
    ("Golf — Tour 2",                             "Golf",         "Qualifications",  4, "08:00", "Club de Golf de Dakar"),
    ("Judo — Moins de 70 kg (Q)",                 "Judo",         "Qualifications",  5, "10:00", "Complexe Sportif de Diamniadio"),
    ("Gymnastique — Artistique (Q)",              "Gymnastique",  "Qualifications",  5, "10:00", "Dakar Arena"),
    ("Surf — Demi-finales",                       "Surf",         "Demi-finales",    5, "07:30", "Plage de Ngor"),
    ("Handball — Phase de groupes (H)",           "Handball",     "Qualifications",  5, "15:00", "Palais des Sports de Diamniadio"),
    ("Athlétisme — 100m haies (Finale)",          "Athlétisme",   "Finale",          6, "18:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m nage libre (Finale)",       "Natation",     "Finale",          6, "17:00", "Piscine Olympique de Diamniadio"),
    ("Basketball 3x3 — Demi-finales",             "Basketball",   "Demi-finales",    6, "15:00", "Dakar Arena"),
    ("Boxe — Moins de 54 kg (Demi-finales)",      "Boxe",         "Demi-finales",    6, "14:00", "Complexe Sportif de Diamniadio"),
    ("Football — Demi-finales (H)",               "Football",     "Demi-finales",    7, "16:00", "Stade du Sénégal"),
    ("Lutte — Demi-finales",                      "Lutte",        "Demi-finales",    7, "14:00", "Complexe Sportif de Diamniadio"),
    ("Surf — Finale",                             "Surf",         "Finale",          7, "10:00", "Plage de Ngor"),
    ("Beach Volley — Demi-finales",               "Beach Volley", "Demi-finales",    7, "10:00", "Plage de Saly"),
    ("Voile — Course finale",                     "Voile",        "Finale",          7, "11:00", "Port de Saly"),
    ("Judo — Finales toutes catégories",          "Judo",         "Finale",          8, "16:00", "Complexe Sportif de Diamniadio"),
    ("Gymnastique — Finale au sol",               "Gymnastique",  "Finale",          8, "17:00", "Dakar Arena"),
    ("Golf — Tour final",                         "Golf",         "Finale",          8, "08:00", "Club de Golf de Dakar"),
    ("Équitation — Saut d'obstacles (Finale)",    "Équitation",   "Finale",          8, "14:00", "Hippodrome de Saly"),
    ("Athlétisme — 400m (Finale)",                "Athlétisme",   "Finale",          9, "18:30", "Stade Léopold Sédar Senghor"),
    ("Natation — 200m dos (Finale)",              "Natation",     "Finale",          9, "17:00", "Piscine Olympique de Diamniadio"),
    ("Basketball 3x3 — Finale",                   "Basketball",   "Finale",          9, "17:00", "Dakar Arena"),
    ("Handball — Demi-finales",                   "Handball",     "Demi-finales",    9, "15:00", "Palais des Sports de Diamniadio"),
    ("Football — Finale (H)",                     "Football",     "Finale",         10, "17:00", "Stade du Sénégal"),
    ("Boxe — Finales",                            "Boxe",         "Finale",         10, "16:00", "Complexe Sportif de Diamniadio"),
    ("Beach Volley — Finale",                     "Beach Volley", "Finale",         10, "15:00", "Plage de Saly"),
    ("Athlétisme — 1500m (Finale)",               "Athlétisme",   "Finale",         11, "18:00", "Stade Léopold Sédar Senghor"),
    ("Natation — 100m brasse (Finale)",           "Natation",     "Finale",         11, "17:00", "Piscine Olympique de Diamniadio"),
    ("Lutte — Finales",                           "Lutte",        "Finale",         11, "15:00", "Complexe Sportif de Diamniadio"),
    ("Handball — Finale",                         "Handball",     "Finale",         11, "17:00", "Palais des Sports de Diamniadio"),
    ("Football — Finale (F)",                     "Football",     "Finale",         12, "16:00", "Stade du Sénégal"),
    ("Athlétisme — Relais 4x100m (Finale)",       "Athlétisme",   "Finale",         12, "18:30", "Stade Léopold Sédar Senghor"),
    ("Gymnastique — Finale aux agrès",            "Gymnastique",  "Finale",         12, "15:00", "Dakar Arena"),
    ("Cérémonie de clôture des JOJ Dakar 2026",  "Cérémonie",    "Cérémonie",      13, "20:00", "Stade Léopold Sédar Senghor"),
]


def seed_all(db):
    from app.models.site import Site
    from app.models.epreuve import Epreuve

    # Sites
    Site.query.delete()
    for data in SITES:
        db.session.add(Site(**data))
    db.session.commit()

    # Épreuves
    Epreuve.query.delete()
    db.session.commit()

    sites_map = {s.nom: s for s in Site.query.all()}
    for titre, sport, phase, jour, heure, nom_site in PROGRAMME:
        site = sites_map.get(nom_site)
        if site:
            db.session.add(Epreuve(
                titre=titre, sport=sport, phase=phase,
                date_heure=_dt(jour, heure), site_id=site.id,
            ))
    db.session.commit()
    print(f"Seed terminé : {Site.query.count()} sites, {Epreuve.query.count()} épreuves.")


def fix_sites(db):
    """Corrige les données incorrectes déjà en base (migrations légères)."""
    from app.models.site import Site
    changed = False

    # Dakar Arena → Diamniadio
    arena = Site.query.filter_by(nom="Dakar Arena").first()
    if arena and (arena.zone != "Diamniadio" or abs(arena.longitude - (-17.21248156380716)) > 0.001):
        arena.zone      = "Diamniadio"
        arena.latitude  = 14.733883498357407
        arena.longitude = -17.21248156380716
        arena.description = "Grande salle polyvalente de Diamniadio accueillant le basketball 3x3 et la gymnastique artistique."
        changed = True
        print("Fix : Dakar Arena déplacée à Diamniadio.")

    # Piscine Olympique renommée et déplacée au Point E, Dakar
    piscine = Site.query.filter(
        Site.nom.in_(["Piscine Olympique de Diamniadio", "Piscine Olympique de Dakar"])
    ).first()
    if piscine and (piscine.zone != "Dakar" or abs(piscine.latitude - 14.696194098675694) > 0.001):
        piscine.nom         = "Piscine Olympique de Dakar"
        piscine.zone        = "Dakar"
        piscine.latitude    = 14.696194098675694
        piscine.longitude   = -17.461359735496124
        piscine.description = "Piscine olympique 50 m au Point E à Dakar, rénovée pour accueillir les épreuves de natation et plongeon des JOJ 2026."
        changed = True
        print("Fix : Piscine Olympique déplacée au Point E, Dakar.")

    if changed:
        db.session.commit()
