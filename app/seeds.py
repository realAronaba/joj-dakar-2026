from datetime import datetime


# ── Sites officiels JOJ Dakar 2026 ────────────────────────────────────────────
# Source : olympics.com/ioc/dakar-2026-venues + COJOJ
SITES = [
    # ── DAKAR ─────────────────────────────────────────────────────────
    {"nom": "Tour de l'Œuf",
     "zone": "Dakar",
     "sport": "Basketball 3x3 / Baseball5 / Breaking / Skateboard / Natation",
     "description": "Piscine olympique historique surnommée la Tour de l'Œuf, rue PE 17, Point E, Dakar. "
                    "Rénovée pour les JOJ 2026, elle accueille la natation, le basketball 3x3, le breaking et le skateboard.",
     "capacite": 5000,
     "latitude": 14.695919, "longitude": -17.461832},

    {"nom": "Stade Iba Mar Diop",
     "zone": "Dakar",
     "sport": "Athlétisme / Boxe / Futsal / Rugby à 7",
     "description": "Stade historique de la Médina à Dakar, en réfection pour accueillir l'athlétisme, "
                    "la boxe, le futsal et le rugby à 7 des JOJ 2026.",
     "capacite": 10000,
     "latitude": 14.679911, "longitude": -17.446512},

    {"nom": "Corniche Ouest",
     "zone": "Dakar",
     "sport": "Surf / Golf / Cyclisme / Sports d'engagement",
     "description": "Parcours urbain longeant la côte atlantique de Dakar, cadre du départ/arrivée du cyclisme "
                    "sur route et de 10 sports d'engagement (surf, golf, escalade, karaté, tennis…).",
     "capacite": 8000,
     "latitude": 14.678981, "longitude": -17.459454},

    # ── DIAMNIADIO ────────────────────────────────────────────────────
    {"nom": "Stade Me Abdoulaye Wade",
     "zone": "Diamniadio",
     "sport": "Tir à l'arc / Cérémonie d'ouverture",
     "description": "Stade ultramoderne de 50 000 places inauguré en 2022, sur l'axe autoroutier A1 à Diamniadio. "
                    "Cadre de la cérémonie d'ouverture des JOJ 2026 et des épreuves de tir à l'arc.",
     "capacite": 50000,
     "latitude": 14.732541, "longitude": -17.200935},

    {"nom": "Dakar Arena",
     "zone": "Diamniadio",
     "sport": "Badminton / Futsal",
     "description": "Grande salle polyvalente de Diamniadio sur l'axe autoroutier A1, "
                    "accueillant le badminton et le futsal des JOJ 2026.",
     "capacite": 15000,
     "latitude": 14.733759, "longitude": -17.212460},

    {"nom": "Dakar Expo Center (CICAD)",
     "zone": "Diamniadio",
     "sport": "Gymnastique / Escrime / Judo / Tennis de table / Taekwondo / Wushu",
     "description": "Centre International de Conférences Abdou Diouf à Diamniadio. "
                    "Accueille les sports de combat et de précision : escrime, judo, taekwondo, wushu, "
                    "tennis de table et gymnastique artistique.",
     "capacite": 8000,
     "latitude": 14.739777, "longitude": -17.198358},

    {"nom": "Centre Équestre de Diamniadio",
     "zone": "Diamniadio",
     "sport": "Équitation",
     "description": "Infrastructure équestre construite spécialement pour les JOJ 2026 à Diamniadio, "
                    "dédiée aux épreuves de saut d'obstacles.",
     "capacite": 3000,
     "latitude": 14.725000, "longitude": -17.190000},

    # ── SALY ──────────────────────────────────────────────────────────
    {"nom": "Saly Beach West",
     "zone": "Saly",
     "sport": "Beach Handball / Beach Volley / Beach Wrestling / Aviron côtier / Voile / Triathlon",
     "description": "Site balnéaire sur la Petite Côte (Petite Côte, Mbour, Région de Thiès), "
                    "à ~80 km au sud de Dakar. Installations temporaires pour les sports de plage et nautiques.",
     "capacite": 6000,
     "latitude": 14.431302, "longitude": -17.000165},
]


def _dt(jour, heure):
    mois = 10 if jour == 31 else 11
    h, m = map(int, heure.split(":"))
    return datetime(2026, mois, jour, h, m)


# ── Programme officiel — sites remappés ───────────────────────────────────────
PROGRAMME = [
    # 31 octobre — Cérémonie d'ouverture
    ("Cérémonie d'ouverture des JOJ Dakar 2026",  "Cérémonie",    "Cérémonie",      31, "19:00", "Stade Me Abdoulaye Wade"),

    # 1er novembre
    ("Athlétisme — 100m haies (Q)",               "Athlétisme",   "Qualifications",  1, "09:00", "Stade Iba Mar Diop"),
    ("Natation — 100m nage libre (Q)",            "Natation",     "Qualifications",  1, "10:00", "Tour de l'Œuf"),
    ("Surf — Tour préliminaire",                  "Surf",         "Qualifications",  1, "07:30", "Corniche Ouest"),
    ("Basketball 3x3 — Phase de groupes",         "Basketball",   "Qualifications",  1, "14:00", "Tour de l'Œuf"),
    ("Beach Volley — Phase de groupes",           "Beach Volley", "Qualifications",  1, "10:00", "Saly Beach West"),
    ("Voile — Course 1",                          "Voile",        "Qualifications",  1, "11:00", "Saly Beach West"),

    # 2 novembre
    ("Athlétisme — 400m (Q)",                     "Athlétisme",   "Qualifications",  2, "09:30", "Stade Iba Mar Diop"),
    ("Judo — Moins de 60 kg (Q)",                 "Judo",         "Qualifications",  2, "10:00", "Dakar Expo Center (CICAD)"),
    ("Natation — 200m dos (Q)",                   "Natation",     "Qualifications",  2, "10:00", "Tour de l'Œuf"),
    ("Football — Phase de groupes (H)",           "Football",     "Qualifications",  2, "16:00", "Stade Me Abdoulaye Wade"),
    ("Handball — Phase de groupes (F)",           "Handball",     "Qualifications",  2, "15:00", "Dakar Expo Center (CICAD)"),
    ("Golf — Tour 1",                             "Golf",         "Qualifications",  2, "08:00", "Corniche Ouest"),

    # 3 novembre
    ("Boxe — Moins de 54 kg (Q)",                 "Boxe",         "Qualifications",  3, "11:00", "Stade Iba Mar Diop"),
    ("Lutte — Catégorie 65 kg (Q)",               "Lutte",        "Qualifications",  3, "14:00", "Stade Iba Mar Diop"),
    ("Surf — Tour 2",                             "Surf",         "Qualifications",  3, "07:30", "Corniche Ouest"),
    ("Basketball 3x3 — Phase de groupes",         "Basketball",   "Qualifications",  3, "14:00", "Tour de l'Œuf"),
    ("Équitation — Dressage (Q)",                 "Équitation",   "Qualifications",  3, "09:00", "Centre Équestre de Diamniadio"),

    # 4 novembre
    ("Athlétisme — 1500m (Q)",                    "Athlétisme",   "Qualifications",  4, "09:00", "Stade Iba Mar Diop"),
    ("Natation — 100m brasse (Q)",                "Natation",     "Qualifications",  4, "10:00", "Tour de l'Œuf"),
    ("Football — Phase de groupes (F)",           "Football",     "Qualifications",  4, "16:00", "Stade Me Abdoulaye Wade"),
    ("Voile — Course 2",                          "Voile",        "Qualifications",  4, "11:00", "Saly Beach West"),
    ("Beach Volley — Phase de groupes",           "Beach Volley", "Qualifications",  4, "10:00", "Saly Beach West"),
    ("Golf — Tour 2",                             "Golf",         "Qualifications",  4, "08:00", "Corniche Ouest"),

    # 5 novembre
    ("Judo — Moins de 70 kg (Q)",                 "Judo",         "Qualifications",  5, "10:00", "Dakar Expo Center (CICAD)"),
    ("Gymnastique — Artistique (Q)",              "Gymnastique",  "Qualifications",  5, "10:00", "Dakar Expo Center (CICAD)"),
    ("Surf — Demi-finales",                       "Surf",         "Demi-finales",    5, "07:30", "Corniche Ouest"),
    ("Handball — Phase de groupes (H)",           "Handball",     "Qualifications",  5, "15:00", "Dakar Expo Center (CICAD)"),

    # 6 novembre
    ("Athlétisme — 100m haies (Finale)",          "Athlétisme",   "Finale",          6, "18:00", "Stade Iba Mar Diop"),
    ("Natation — 100m nage libre (Finale)",       "Natation",     "Finale",          6, "17:00", "Tour de l'Œuf"),
    ("Basketball 3x3 — Demi-finales",             "Basketball",   "Demi-finales",    6, "15:00", "Tour de l'Œuf"),
    ("Boxe — Moins de 54 kg (Demi-finales)",      "Boxe",         "Demi-finales",    6, "14:00", "Stade Iba Mar Diop"),

    # 7 novembre
    ("Football — Demi-finales (H)",               "Football",     "Demi-finales",    7, "16:00", "Stade Me Abdoulaye Wade"),
    ("Lutte — Demi-finales",                      "Lutte",        "Demi-finales",    7, "14:00", "Stade Iba Mar Diop"),
    ("Surf — Finale",                             "Surf",         "Finale",          7, "10:00", "Corniche Ouest"),
    ("Beach Volley — Demi-finales",               "Beach Volley", "Demi-finales",    7, "10:00", "Saly Beach West"),
    ("Voile — Course finale",                     "Voile",        "Finale",          7, "11:00", "Saly Beach West"),

    # 8 novembre
    ("Judo — Finales toutes catégories",          "Judo",         "Finale",          8, "16:00", "Dakar Expo Center (CICAD)"),
    ("Gymnastique — Finale au sol",               "Gymnastique",  "Finale",          8, "17:00", "Dakar Expo Center (CICAD)"),
    ("Golf — Tour final",                         "Golf",         "Finale",          8, "08:00", "Corniche Ouest"),
    ("Équitation — Saut d'obstacles (Finale)",    "Équitation",   "Finale",          8, "14:00", "Centre Équestre de Diamniadio"),

    # 9 novembre
    ("Athlétisme — 400m (Finale)",                "Athlétisme",   "Finale",          9, "18:30", "Stade Iba Mar Diop"),
    ("Natation — 200m dos (Finale)",              "Natation",     "Finale",          9, "17:00", "Tour de l'Œuf"),
    ("Basketball 3x3 — Finale",                   "Basketball",   "Finale",          9, "17:00", "Tour de l'Œuf"),
    ("Handball — Demi-finales",                   "Handball",     "Demi-finales",    9, "15:00", "Dakar Expo Center (CICAD)"),

    # 10 novembre
    ("Football — Finale (H)",                     "Football",     "Finale",         10, "17:00", "Stade Me Abdoulaye Wade"),
    ("Boxe — Finales",                            "Boxe",         "Finale",         10, "16:00", "Stade Iba Mar Diop"),
    ("Beach Volley — Finale",                     "Beach Volley", "Finale",         10, "15:00", "Saly Beach West"),

    # 11 novembre
    ("Athlétisme — 1500m (Finale)",               "Athlétisme",   "Finale",         11, "18:00", "Stade Iba Mar Diop"),
    ("Natation — 100m brasse (Finale)",           "Natation",     "Finale",         11, "17:00", "Tour de l'Œuf"),
    ("Lutte — Finales",                           "Lutte",        "Finale",         11, "15:00", "Stade Iba Mar Diop"),
    ("Handball — Finale",                         "Handball",     "Finale",         11, "17:00", "Dakar Expo Center (CICAD)"),

    # 12 novembre
    ("Football — Finale (F)",                     "Football",     "Finale",         12, "16:00", "Stade Me Abdoulaye Wade"),
    ("Athlétisme — Relais 4x100m (Finale)",       "Athlétisme",   "Finale",         12, "18:30", "Stade Iba Mar Diop"),
    ("Gymnastique — Finale aux agrès",            "Gymnastique",  "Finale",         12, "15:00", "Dakar Expo Center (CICAD)"),

    # 13 novembre — Cérémonie de clôture
    ("Cérémonie de clôture des JOJ Dakar 2026",  "Cérémonie",    "Cérémonie",      13, "20:00", "Stade Me Abdoulaye Wade"),
]


def seed_all(db):
    from app.models.site import Site
    from app.models.epreuve import Epreuve

    Site.query.delete()
    for data in SITES:
        db.session.add(Site(**data))
    db.session.commit()

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
