from app import create_app, db
from app.models.site import Site

app = create_app()

SITES = [
    # ── DAKAR ──────────────────────────────────────────────────────────
    {
        "nom":         "Stade Léopold Sédar Senghor",
        "zone":        "Dakar",
        "sport":       "Athlétisme / Cérémonie d'ouverture",
        "description": "Stade iconique de Dakar, rénové pour accueillir la cérémonie d'ouverture et les épreuves d'athlétisme des JOJ 2026.",
        "capacite":    60000,
        "latitude":    14.7232,
        "longitude":   -17.4636,
    },
    {
        "nom":         "Dakar Arena",
        "zone":        "Dakar",
        "sport":       "Basketball / Gymnastique",
        "description": "Grande salle polyvalente de Dakar accueillant le basketball 3x3 et la gymnastique artistique.",
        "capacite":    15000,
        "latitude":    14.7284,
        "longitude":   -17.4573,
    },
    {
        "nom":         "Plage de Ngor",
        "zone":        "Dakar",
        "sport":       "Surf / Triathlon",
        "description": "Plage emblématique de la presqu'île du Cap-Vert, cadre idéal pour le surf et la natation en eau libre.",
        "capacite":    5000,
        "latitude":    14.7506,
        "longitude":   -17.5194,
    },
    {
        "nom":         "Club de Golf de Dakar",
        "zone":        "Dakar",
        "sport":       "Golf",
        "description": "Le plus ancien golf du Sénégal, situé aux Almadies, face à l'Atlantique.",
        "capacite":    3000,
        "latitude":    14.7381,
        "longitude":   -17.5162,
    },

    # ── DIAMNIADIO ────────────────────────────────────────────────────
    {
        "nom":         "Stade du Sénégal",
        "zone":        "Diamniadio",
        "sport":       "Football / Athlétisme",
        "description": "Stade ultramoderne de 50 000 places construit à Diamniadio, vitrine sportive du Sénégal nouveau.",
        "capacite":    50000,
        "latitude":    14.7267,
        "longitude":   -17.2014,
    },
    {
        "nom":         "Complexe Sportif de Diamniadio",
        "zone":        "Diamniadio",
        "sport":       "Boxe / Lutte / Judo",
        "description": "Complexe multi-sports intégré au pôle urbain de Diamniadio, regroupant plusieurs salles de combat.",
        "capacite":    8000,
        "latitude":    14.7240,
        "longitude":   -17.1980,
    },
    {
        "nom":         "Piscine Olympique de Diamniadio",
        "zone":        "Diamniadio",
        "sport":       "Natation / Plongeon",
        "description": "Infrastructure aquatique aux normes olympiques, première piscine 50 m homologuée FINA au Sénégal.",
        "capacite":    5000,
        "latitude":    14.7255,
        "longitude":   -17.2030,
    },
    {
        "nom":         "Palais des Sports de Diamniadio",
        "zone":        "Diamniadio",
        "sport":       "Handball / Volleyball",
        "description": "Salle couverte dédiée aux sports collectifs en salle, avec tribunes modulables.",
        "capacite":    10000,
        "latitude":    14.7280,
        "longitude":   -17.2000,
    },

    # ── SALY ──────────────────────────────────────────────────────────
    {
        "nom":         "Plage de Saly",
        "zone":        "Saly",
        "sport":       "Beach Volley / Beach Soccer",
        "description": "Station balnéaire de la Petite Côte, ses plages de sable blanc accueilleront les sports de plage.",
        "capacite":    6000,
        "latitude":    14.4644,
        "longitude":   -17.0167,
    },
    {
        "nom":         "Port de Saly",
        "zone":        "Saly",
        "sport":       "Voile / Aviron / Canoë-Kayak",
        "description": "Base nautique aménagée sur la Petite Côte pour les épreuves de voile et sports de pagaie.",
        "capacite":    2000,
        "latitude":    14.4612,
        "longitude":   -17.0195,
    },
    {
        "nom":         "Hippodrome de Saly",
        "zone":        "Saly",
        "sport":       "Équitation",
        "description": "Site équestre de référence en Afrique de l'Ouest, rénové pour les épreuves d'équitation des JOJ.",
        "capacite":    4000,
        "latitude":    14.4700,
        "longitude":   -17.0120,
    },
]

with app.app_context():
    Site.query.delete()
    for data in SITES:
        db.session.add(Site(**data))
    db.session.commit()
    total = Site.query.count()
    print(f"{total} sites insérés avec succès.")
    for s in Site.query.order_by(Site.zone, Site.nom).all():
        print(f"  [{s.zone:12}] {s.nom}")
