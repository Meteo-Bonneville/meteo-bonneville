import json
import urllib.request
from datetime import datetime

VIGICRUES_URL = (
    "https://www.vigicrues.gouv.fr/services/1/"
    "InfoVigiCru.geojson"
)

COULEURS = {
    1: ("🟢", "Vigilance verte"),
    2: ("🟡", "Vigilance jaune"),
    3: ("🟠", "Vigilance orange"),
    4: ("🔴", "Vigilance rouge"),
}

def lire_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "meteo-bonneville/1.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def vigilance_arve():
    data = lire_json(VIGICRUES_URL)

    for feature in data["features"]:
        props = feature["properties"]

        if props.get("CdEntCru") == "AN43":
            niveau = int(props.get("NivInfViCr", 0))

            if niveau in COULEURS:
                return COULEURS[niveau]

    return ("⚪", "Vigilance indisponible")

symbole, texte = vigilance_arve()

METEO_URL = (
    "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "weatherref-france-vigilance-meteo-departement/records"
    "?limit=100&refine=domain_id%3A%2274%22"
)

NOMS_PHENOMENES = {
    "1": "Vent",
    "2": "Pluie-inondation",
    "3": "Orages",
    "4": "Crues",
    "5": "Neige-verglas",
    "6": "Canicule",
    "7": "Grand froid",
    "8": "Avalanches",
}

COULEURS_METEO = {
    "green": ("🟢", "verte"),
    "yellow": ("🟡", "jaune"),
    "orange": ("🟠", "orange"),
    "red": ("🔴", "rouge"),
    "vert": ("🟢", "verte"),
    "jaune": ("🟡", "jaune"),
    "rouge": ("🔴", "rouge"),
}

def vigilance_meteo_74():
    data = lire_json(METEO_URL)
    alertes = []

    for ligne in data.get("results", []):
        phenomene = str(ligne.get("phenomenon", ""))
        couleur = str(ligne.get("color", "")).lower()

        if couleur in COULEURS_METEO and couleur not in ("green", "vert"):
            emoji, nom_couleur = COULEURS_METEO[couleur]
            nom = NOMS_PHENOMENES.get(phenomene, phenomene)

            texte = f"{emoji} {nom} — Vigilance {nom_couleur}"
            if texte not in alertes:
                alertes.append(texte)

    if not alertes:
        alertes.append("🟢 Aucune vigilance particulière")

    return alertes

symbole, texte = vigilance_arve()
alertes_meteo = vigilance_meteo_74()

resultat = {
    "meteo": {
        "departement": "Haute-Savoie (74)",
        "alertes": alertes_meteo
    },
    "vigicrues": {
        "secteur": "Arve aval / Bonneville",
        "symbole": symbole,
        "texte": texte
    },
    "mise_a_jour": datetime.now().strftime("%d/%m/%Y %H:%M")
}

with open("vigilance.json", "w", encoding="utf-8") as f:
    json.dump(resultat, f, ensure_ascii=False, indent=2)

print(symbole, texte)

