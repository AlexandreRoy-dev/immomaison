#!/usr/bin/env python3
"""Generate SEO landing pages for all Estrie municipalities."""

import json
import os
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "estrie"
BASE_URL = "https://immobiliermaison.com"
TODAY = "2026-06-14"

MRCS = [
    {
        "name": "Brome-Missisquoi",
        "slug": "brome-missisquoi",
        "chef_lieu": "Cowansville",
        "municipalities": [
            ("Abercorn", "village"),
            ("Bedford", "ville", "bedford"),
            ("Bedford", "canton", "bedford-canton"),
            ("Bolton-Ouest", "municipalite"),
            ("Brigham", "municipalite"),
            ("Brome", "village"),
            ("Bromont", "ville"),
            ("Cowansville", "ville"),
            ("Dunham", "ville"),
            ("East Farnham", "municipalite"),
            ("Farnham", "ville"),
            ("Frelighsburg", "municipalite"),
            ("Lac-Brome", "ville"),
            ("Notre-Dame-de-Stanbridge", "municipalite"),
            ("Pike River", "municipalite"),
            ("Saint-Armand", "municipalite"),
            ("Saint-Ignace-de-Stanbridge", "municipalite"),
            ("Sainte-Sabine", "municipalite"),
            ("Stanbridge East", "municipalite"),
            ("Stanbridge Station", "municipalite"),
            ("Sutton", "ville"),
        ],
    },
    {
        "name": "Coaticook",
        "slug": "coaticook",
        "chef_lieu": "Coaticook",
        "municipalities": [
            ("Barnston-Ouest", "municipalite"),
            ("Coaticook", "ville"),
            ("Compton", "municipalite"),
            ("Dixville", "municipalite"),
            ("East Hereford", "municipalite"),
            ("Martinville", "municipalite"),
            ("Saint-Herménégilde", "municipalite"),
            ("Saint-Malo", "municipalite"),
            ("Saint-Venant-de-Paquette", "municipalite"),
            ("Sainte-Edwidge-de-Clifton", "canton"),
            ("Stanstead-Est", "municipalite"),
            ("Waterville", "ville"),
        ],
    },
    {
        "name": "La Haute-Yamaska",
        "slug": "haute-yamaska",
        "chef_lieu": "Granby",
        "municipalities": [
            ("Granby", "ville"),
            ("Roxton Pond", "municipalite"),
            ("Saint-Alphonse-de-Granby", "municipalite"),
            ("Saint-Joachim-de-Shefford", "municipalite"),
            ("Sainte-Cécile-de-Milton", "municipalite"),
            ("Shefford", "canton"),
            ("Warden", "village"),
            ("Waterloo", "ville"),
        ],
    },
    {
        "name": "Le Granit",
        "slug": "granit",
        "chef_lieu": "Lac-Mégantic",
        "municipalities": [
            ("Audet", "municipalite"),
            ("Frontenac", "municipalite"),
            ("Lac-Drolet", "municipalite"),
            ("Lac-Mégantic", "ville"),
            ("Lambton", "municipalite"),
            ("Marston", "canton"),
            ("Milan", "municipalite"),
            ("Nantes", "municipalite"),
            ("Notre-Dame-des-Bois", "municipalite"),
            ("Piopolis", "municipalite"),
            ("Saint-Augustin-de-Woburn", "paroisse"),
            ("Saint-Ludger", "municipalite"),
            ("Saint-Robert-Bellarmin", "municipalite"),
            ("Saint-Romain", "municipalite"),
            ("Saint-Sébastien", "municipalite"),
            ("Sainte-Cécile-de-Whitton", "municipalite"),
            ("Stornoway", "municipalite"),
            ("Stratford", "canton"),
            ("Val-Racine", "municipalite"),
        ],
    },
    {
        "name": "Le Haut-Saint-François",
        "slug": "haut-saint-francois",
        "chef_lieu": "Cookshire-Eaton",
        "municipalities": [
            ("Ascot Corner", "municipalite"),
            ("Bury", "municipalite"),
            ("Chartierville", "municipalite"),
            ("Cookshire-Eaton", "ville"),
            ("Dudswell", "municipalite"),
            ("East Angus", "ville"),
            ("Hampden", "canton"),
            ("La Patrie", "municipalite"),
            ("Lingwick", "canton"),
            ("Newport", "municipalite"),
            ("Saint-Isidore-de-Clifton", "municipalite"),
            ("Scotstown", "ville"),
            ("Weedon", "municipalite"),
            ("Westbury", "canton"),
        ],
    },
    {
        "name": "Le Val-Saint-François",
        "slug": "val-saint-francois",
        "chef_lieu": "Richmond",
        "municipalities": [
            ("Bonsecours", "municipalite"),
            ("Cleveland", "canton"),
            ("Kingsbury", "village"),
            ("Lawrenceville", "village"),
            ("Maricourt", "municipalite"),
            ("Melbourne", "canton"),
            ("Racine", "municipalite"),
            ("Richmond", "ville"),
            ("Saint-Claude", "municipalite"),
            ("Saint-Denis-de-Brompton", "municipalite"),
            ("Saint-François-Xavier-de-Brompton", "municipalite"),
            ("Sainte-Anne-de-la-Rochelle", "municipalite"),
            ("Stoke", "municipalite"),
            ("Ulverton", "municipalite"),
            ("Val-Joli", "municipalite"),
            ("Valcourt", "canton", "valcourt-canton"),
            ("Valcourt", "ville", "valcourt"),
            ("Windsor", "ville"),
        ],
    },
    {
        "name": "Les Sources",
        "slug": "sources",
        "chef_lieu": "Val-des-Sources",
        "municipalities": [
            ("Danville", "ville"),
            ("Ham-Sud", "municipalite"),
            ("Saint-Adrien", "municipalite"),
            ("Saint-Camille", "canton"),
            ("Saint-Georges-de-Windsor", "municipalite"),
            ("Val-des-Sources", "ville"),
            ("Wotton", "municipalite"),
        ],
    },
    {
        "name": "Memphrémagog",
        "slug": "memphremagog",
        "chef_lieu": "Magog",
        "municipalities": [
            ("Austin", "municipalite"),
            ("Ayer's Cliff", "village"),
            ("Bolton-Est", "municipalite"),
            ("Eastman", "municipalite"),
            ("Hatley", "municipalite", "hatley"),
            ("Hatley", "canton", "hatley-canton"),
            ("Magog", "ville"),
            ("North Hatley", "village"),
            ("Ogden", "municipalite"),
            ("Orford", "canton"),
            ("Potton", "canton"),
            ("Saint-Benoît-du-Lac", "municipalite"),
            ("Saint-Étienne-de-Bolton", "municipalite"),
            ("Sainte-Catherine-de-Hatley", "municipalite"),
            ("Stanstead", "canton", "stanstead-canton"),
            ("Stanstead", "ville", "stanstead"),
            ("Stukely-Sud", "village"),
        ],
    },
    {
        "name": "Sherbrooke",
        "slug": "sherbrooke",
        "chef_lieu": "Sherbrooke",
        "municipalities": [
            ("Sherbrooke", "ville"),
        ],
        "boroughs": [
            ("Brompton–Rock Forest–Saint-Élie–Deauville", "arrondissement", "brompton-rock-forest-saint-elie-deauville"),
            ("Fleurimont", "arrondissement", "fleurimont"),
            ("Lennoxville", "arrondissement", "lennoxville"),
            ("Des Nations", "arrondissement", "des-nations"),
        ],
    },
]

TYPE_LABELS = {
    "ville": "Ville",
    "village": "Municipalité de village",
    "canton": "Municipalité de canton",
    "municipalite": "Municipalité",
    "paroisse": "Municipalité de paroisse",
    "arrondissement": "Arrondissement de Sherbrooke",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def make_slug(name: str, typ: str, custom: str | None = None) -> str:
    if custom:
        return custom
    base = slugify(name)
    if typ in ("canton", "village", "paroisse") and base not in (
        "bedford", "hatley", "stanstead", "valcourt"
    ):
        return f"{base}-{typ}" if typ != "municipalite" else base
    return base


def collect_all_entries():
    entries = []
    for mrc in MRCS:
        for item in mrc["municipalities"]:
            name, typ = item[0], item[1]
            custom = item[2] if len(item) > 2 else None
            slug = make_slug(name, typ, custom)
            entries.append(
                {
                    "name": name,
                    "type": typ,
                    "slug": slug,
                    "mrc_name": mrc["name"],
                    "mrc_slug": mrc["slug"],
                    "is_borough": False,
                }
            )
        for item in mrc.get("boroughs", []):
            name, typ = item[0], item[1]
            custom = item[2] if len(item) > 2 else None
            slug = make_slug(name, typ, custom)
            entries.append(
                {
                    "name": name,
                    "type": typ,
                    "slug": slug,
                    "mrc_name": mrc["name"],
                    "mrc_slug": mrc["slug"],
                    "is_borough": True,
                    "parent_city": "Sherbrooke",
                }
            )
    return entries


def nearby(entries, current, limit=4):
    same = [e for e in entries if e["mrc_slug"] == current["mrc_slug"] and e["slug"] != current["slug"]]
    return same[:limit]


def intro_paragraph(entry):
    name = entry["name"]
    mrc = entry["mrc_name"]
    typ = TYPE_LABELS.get(entry["type"], "Municipalité")

    if entry.get("is_borough"):
        return (
            f"Vous souhaitez vendre ou acheter une propriété de prestige dans l'arrondissement {name} à Sherbrooke ? "
            f"L'Équipe Chiasson de Francesco, courtiers immobiliers RE/MAX D'ABORD, connaît intimement le marché "
            f"immobilier de ce secteur sherbrookois. De la mise en marché haut de gamme à la négociation stratégique, "
            f"nous maximisons la valeur de votre patrimoine dans l'un des arrondissements les plus recherchés de l'Estrie."
        )

    if entry["type"] == "ville":
        return (
            f"Le marché immobilier à {name} exige une expertise locale et une mise en marché irréprochable. "
            f"Basés à Sherbrooke et actifs dans toute la MRC {mrc}, les courtiers de l'Équipe Chiasson de Francesco "
            f"accompagnent vendeurs et acheteurs de propriétés résidentielles et commerciales à {name} avec rigueur, "
            f"transparence et un service de prestige."
        )

    return (
        f"Que vous possédiez une résidence, un chalet ou un terrain à {name}, la vente d'une propriété en Estrie "
        f"demande un courtier qui comprend les réalités du marché de la MRC {mrc}. L'Équipe Chiasson de Francesco "
        f"offre une évaluation immobilière gratuite, une stratégie de mise en marché sur mesure et un accompagnement "
        f"personnalisé pour chaque transaction à {name}."
    )


def market_paragraph(entry):
    name = entry["name"]
    mrc = entry["mrc_name"]
    location = f"{name}, Sherbrooke" if entry.get("is_borough") else name
    return (
        f"En tant que {TYPE_LABELS.get(entry['type'], 'municipalité').lower()} de la MRC {mrc}, {location} fait partie "
        f"du dynamisme immobilier de l'Estrie. Notre équipe maîtrise les tendances du marché local — prix, délais de "
        f"vente, profil des acheteurs — pour positionner votre propriété au bon prix et attirer les bonnes offres. "
        f"Appuyés par le réseau mondial RE/MAX, nous offrons une visibilité exceptionnelle à chaque inscription."
    )


def render_page(entry, all_entries, page_kind="municipality"):
    name = entry["name"]
    slug = entry["slug"]
    mrc = entry["mrc_name"]
    mrc_slug = entry["mrc_slug"]
    typ_label = TYPE_LABELS.get(entry["type"], "Municipalité")

    if entry.get("is_borough"):
        title = f"Courtier immobilier {name} Sherbrooke | Immobilier Estrie — immobiliermaison.com"
        h1 = f"Courtier immobilier — {name}, Sherbrooke"
        geo_name = f"{name}, Sherbrooke"
        canonical = f"{BASE_URL}/estrie/{slug}/"
        breadcrumb_mid = ("Sherbrooke", f"{BASE_URL}/estrie/sherbrooke/")
    else:
        title = f"Courtier immobilier {name} | Vendre sa maison en Estrie — immobiliermaison.com"
        h1 = f"Courtier immobilier à {name}"
        geo_name = name
        canonical = f"{BASE_URL}/estrie/{slug}/"
        breadcrumb_mid = (mrc, f"{BASE_URL}/estrie/mrc-{mrc_slug}/")

    description = (
        f"Courtiers immobiliers RE/MAX à {geo_name}, Estrie. Équipe Chiasson de Francesco — évaluation gratuite, "
        f"vente et achat de propriétés de prestige. MRC {mrc}. Appelez (819) 919-4631."
    )
    keywords = (
        f"courtier immobilier {name}, vendre maison {name}, immobilier {name}, immobilier Estrie, "
        f"équipe chiasson de francesco, RE/MAX {name}, évaluation immobilière {name}, MRC {mrc}"
    )

    neighbors = nearby(all_entries, entry)
    neighbor_links = "\n".join(
        f'                    <a href="{BASE_URL}/estrie/{n["slug"]}/" class="text-sm text-gray-500 hover:text-remaxRed transition-colors">{n["name"]}</a>'
        for n in neighbors
    )

    intro = intro_paragraph(entry)
    market = market_paragraph(entry)

    schema_area = geo_name
    if entry.get("is_borough"):
        schema_area = f"{name}, Sherbrooke, QC"

    return f"""<!DOCTYPE html>
<html lang="fr-CA" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <meta name="author" content="Équipe Chiasson de Francesco">
    <meta name="geo.region" content="CA-QC">
    <meta name="geo.placename" content="{geo_name}">
    <meta name="theme-color" content="#0A1128">
    <link rel="canonical" href="{canonical}">
    <link rel="alternate" hreflang="fr-CA" href="{canonical}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta property="og:site_name" content="Immobiliermaison.com">
    <meta property="og:title" content="Courtier immobilier {name} | Équipe Chiasson de Francesco">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?ixlib=rb-4.0.3&amp;auto=format&amp;fit=crop&amp;w=1200&amp;q=80">
    <meta property="og:locale" content="fr_CA">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Courtier immobilier {name} | immobiliermaison.com">
    <meta name="twitter:description" content="{description}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://api.leadconnectorhq.com">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{ remaxRed: '#E11B22', luxuryDark: '#0A1128', luxuryLight: '#FDFDFD', accentGold: '#D4AF37' }},
                    fontFamily: {{ sans: ['Montserrat', 'sans-serif'], serif: ['Playfair Display', 'serif'] }},
                    boxShadow: {{ glass: '0 8px 32px 0 rgba(0,0,0,0.3)', floating: '0 20px 40px -10px rgba(0,0,0,0.08)' }}
                }}
            }}
        }}
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@graph": [
            {{
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {{ "@type": "ListItem", "position": 1, "name": "Accueil", "item": "{BASE_URL}/" }},
                    {{ "@type": "ListItem", "position": 2, "name": "Estrie", "item": "{BASE_URL}/estrie/" }},
                    {{ "@type": "ListItem", "position": 3, "name": "{breadcrumb_mid[0]}", "item": "{breadcrumb_mid[1]}" }},
                    {{ "@type": "ListItem", "position": 4, "name": "{name}", "item": "{canonical}" }}
                ]
            }},
            {{
                "@type": "RealEstateAgent",
                "name": "Équipe Chiasson de Francesco — {name}",
                "url": "{canonical}",
                "telephone": "+1-819-919-4631",
                "email": "info@immobiliermaison.com",
                "areaServed": {{ "@type": "City", "name": "{schema_area}" }},
                "parentOrganization": {{ "@type": "Organization", "name": "RE/MAX D'ABORD" }},
                "address": {{
                    "@type": "PostalAddress",
                    "streetAddress": "157 boul. Jacques-Cartier Sud",
                    "addressLocality": "Sherbrooke",
                    "addressRegion": "QC",
                    "postalCode": "J1J 2Z4",
                    "addressCountry": "CA"
                }}
            }}
        ]
    }}
    </script>
    <style>
        .form-iframe-wrapper {{ min-height: 624px; border-radius: 8px; overflow: hidden; background: rgba(255,255,255,0.95); }}
        .form-iframe-wrapper iframe {{ display: block; width: 100%; min-height: 624px; border: none; border-radius: 8px; }}
    </style>
</head>
<body class="font-sans text-gray-800 bg-luxuryLight antialiased">
    <header class="fixed w-full top-0 z-50 bg-white/90 backdrop-blur-lg border-b border-gray-100 py-4">
        <div class="max-w-7xl mx-auto px-6 lg:px-12 flex justify-between items-center">
            <a href="{BASE_URL}/" class="font-serif text-2xl font-bold text-luxuryDark uppercase">Immobilier<span class="text-remaxRed">maison</span></a>
            <nav class="hidden md:flex items-center gap-8 text-xs font-semibold uppercase tracking-widest text-gray-500">
                <a href="{BASE_URL}/estrie/" class="hover:text-luxuryDark">Estrie</a>
                <a href="{BASE_URL}/estrie/municipalites/" class="hover:text-luxuryDark">Municipalités</a>
                <a href="tel:+18199194631" class="border border-luxuryDark/20 px-5 py-2 hover:bg-luxuryDark hover:text-white transition">(819) 919-4631</a>
            </nav>
        </div>
    </header>

    <main class="pt-24">
        <section class="bg-luxuryDark text-white py-20">
            <div class="max-w-7xl mx-auto px-6 lg:px-12">
                <nav class="text-xs uppercase tracking-widest text-gray-400 mb-6" aria-label="Fil d'Ariane">
                    <a href="{BASE_URL}/" class="hover:text-white">Accueil</a>
                    <span class="mx-2">/</span>
                    <a href="{BASE_URL}/estrie/" class="hover:text-white">Estrie</a>
                    <span class="mx-2">/</span>
                    <a href="{breadcrumb_mid[1]}" class="hover:text-white">{breadcrumb_mid[0]}</a>
                    <span class="mx-2">/</span>
                    <span class="text-white">{name}</span>
                </nav>
                <p class="text-remaxRed text-xs font-bold uppercase tracking-widest mb-4">{typ_label} · MRC {mrc} · Estrie</p>
                <h1 class="font-serif text-4xl md:text-6xl leading-tight mb-6">{h1}</h1>
                <p class="text-gray-300 font-light text-lg max-w-3xl leading-relaxed">{intro}</p>
            </div>
        </section>

        <section class="py-20">
            <div class="max-w-7xl mx-auto px-6 lg:px-12 grid lg:grid-cols-2 gap-16 items-start">
                <div>
                    <h2 class="font-serif text-3xl text-luxuryDark mb-6">Immobilier de prestige à {geo_name}</h2>
                    <p class="text-gray-500 font-light leading-relaxed mb-6">{market}</p>
                    <p class="text-gray-500 font-light leading-relaxed mb-8">
                        Pierre-Olivier Chiasson et Marco De Francesco, courtiers immobiliers résidentiels et commerciaux chez RE/MAX D'ABORD,
                        vous accompagnent à chaque étape : évaluation privée gratuite, photographie professionnelle, marketing numérique ciblé,
                        qualification des acheteurs et négociation jusqu'à l'acte notarié. <strong class="font-medium text-luxuryDark">immobiliermaison.com</strong>
                        est votre porte d'entrée vers un service immobilier haut de gamme en Estrie.
                    </p>
                    <ul class="space-y-3 text-sm text-gray-600">
                        <li class="flex gap-3"><span class="text-remaxRed">✓</span> Évaluation immobilière gratuite et confidentielle</li>
                        <li class="flex gap-3"><span class="text-remaxRed">✓</span> Mise en marché haut de gamme (photo, vidéo, drone)</li>
                        <li class="flex gap-3"><span class="text-remaxRed">✓</span> Réseau RE/MAX — visibilité locale et internationale</li>
                        <li class="flex gap-3"><span class="text-remaxRed">✓</span> Avis Google 5 étoiles — Équipe Chiasson de Francesco</li>
                    </ul>
                </div>
                <div id="contact" class="bg-white p-6 shadow-floating border border-gray-100">
                    <h2 class="font-serif text-2xl text-luxuryDark mb-2">Évaluation privée — {name}</h2>
                    <p class="text-sm text-gray-500 mb-4 font-light">Recevez une analyse confidentielle de la valeur de votre propriété à {geo_name}.</p>
                    <div class="form-iframe-wrapper">
                        <iframe src="https://api.leadconnectorhq.com/widget/form/fZigX6fPzGLkOM4sNUWJ" style="width:100%;height:100%;border:none;border-radius:8px" id="inline-fZigX6fPzGLkOM4sNUWJ" data-form-name="immobiliermaison" data-height="624" title="Formulaire immobiliermaison — {name}"></iframe>
                    </div>
                </div>
            </div>
        </section>

        <section class="py-16 bg-white border-y border-gray-100">
            <div class="max-w-7xl mx-auto px-6 lg:px-12">
                <h2 class="font-serif text-2xl text-luxuryDark mb-6">Autres municipalités — MRC {mrc}</h2>
                <div class="flex flex-wrap gap-4">
{neighbor_links}
                </div>
                <p class="mt-8 text-sm text-gray-400"><a href="{BASE_URL}/estrie/municipalites/" class="text-remaxRed hover:underline">Voir toutes les municipalités de l'Estrie →</a></p>
            </div>
        </section>
    </main>

    <footer class="bg-luxuryDark text-white py-12 border-t-4 border-remaxRed">
        <div class="max-w-7xl mx-auto px-6 lg:px-12 flex flex-col md:flex-row justify-between gap-8 text-sm text-gray-400 font-light">
            <div>
                <p class="font-serif text-xl text-white mb-2">Immobilier<span class="text-remaxRed">maison</span></p>
                <p>Équipe Chiasson de Francesco · RE/MAX D'ABORD · Sherbrooke</p>
            </div>
            <div class="space-y-1">
                <p><a href="tel:+18199194631" class="hover:text-white">(819) 919-4631</a></p>
                <p><a href="mailto:info@immobiliermaison.com" class="hover:text-white">info@immobiliermaison.com</a></p>
            </div>
            <div class="space-y-1">
                <p><a href="{BASE_URL}/" class="hover:text-white">Accueil</a></p>
                <p><a href="{BASE_URL}/estrie/" class="hover:text-white">Immobilier Estrie</a></p>
                <p><a href="https://chiassondefrancesco.ca/" class="hover:text-white">chiassondefrancesco.ca</a></p>
            </div>
        </div>
    </footer>
    <script src="https://link.msgsndr.com/js/form_embed.js"></script>
</body>
</html>
"""


def render_mrc_hub(mrc, entries):
    name = mrc["name"]
    slug = mrc["slug"]
    canonical = f"{BASE_URL}/estrie/mrc-{slug}/"
    muni_entries = [e for e in entries if e["mrc_slug"] == slug]
    links = "\n".join(
        f'                <a href="{BASE_URL}/estrie/{e["slug"]}/" class="p-4 border border-gray-100 hover:border-remaxRed/30 hover:shadow-floating transition block"><span class="font-serif text-lg text-luxuryDark">{e["name"]}</span><span class="block text-xs text-gray-400 mt-1">{TYPE_LABELS.get(e["type"], "")}</span></a>'
        for e in sorted(muni_entries, key=lambda x: x["name"])
    )
    return f"""<!DOCTYPE html>
<html lang="fr-CA">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Courtier immobilier MRC {name} | Estrie — immobiliermaison.com</title>
    <meta name="description" content="Courtiers immobiliers RE/MAX dans la MRC {name}, Estrie. {len(muni_entries)} municipalités desservies par l'Équipe Chiasson de Francesco. Évaluation gratuite.">
    <link rel="canonical" href="{canonical}">
    <meta name="robots" content="index, follow">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config={{theme:{{extend:{{colors:{{remaxRed:'#E11B22',luxuryDark:'#0A1128'}},fontFamily:{{serif:['Playfair Display','serif'],sans:['Montserrat','sans-serif']}}}}}}}}</script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-sans bg-[#FDFDFD] text-gray-800">
    <header class="bg-luxuryDark text-white py-6"><div class="max-w-7xl mx-auto px-6"><a href="{BASE_URL}/" class="font-serif text-2xl font-bold uppercase">Immobilier<span class="text-remaxRed">maison</span></a></div></header>
    <main class="max-w-7xl mx-auto px-6 py-16">
        <nav class="text-sm text-gray-400 mb-6"><a href="{BASE_URL}/estrie/">Estrie</a> / MRC {name}</nav>
        <h1 class="font-serif text-4xl md:text-5xl text-luxuryDark mb-6">Courtier immobilier — MRC {name}</h1>
        <p class="text-gray-500 font-light text-lg max-w-3xl mb-12">L'Équipe Chiasson de Francesco dessert l'ensemble de la MRC {name} en Estrie. Chef-lieu : {mrc["chef_lieu"]}. Sélectionnez votre municipalité pour une évaluation immobilière gratuite.</p>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{links}</div>
    </main>
    <footer class="bg-luxuryDark text-gray-400 text-center py-8 text-sm"><a href="{BASE_URL}/estrie/municipalites/" class="hover:text-white">Toutes les municipalités de l'Estrie</a></footer>
</body>
</html>
"""


def render_estrie_hub(entries, mrcs):
    by_mrc = {}
    for e in entries:
        by_mrc.setdefault(e["mrc_slug"], []).append(e)

    mrc_sections = ""
    for mrc in mrcs:
        muni_links = "\n".join(
            f'<li><a href="{BASE_URL}/estrie/{e["slug"]}/" class="hover:text-remaxRed">{e["name"]}</a></li>'
            for e in sorted(by_mrc.get(mrc["slug"], []), key=lambda x: x["name"])
        )
        mrc_sections += f"""
        <section class="mb-12">
            <h2 class="font-serif text-2xl text-luxuryDark mb-2"><a href="{BASE_URL}/estrie/mrc-{mrc["slug"]}/" class="hover:text-remaxRed">MRC {mrc["name"]}</a></h2>
            <p class="text-sm text-gray-400 mb-4">Chef-lieu : {mrc["chef_lieu"]} · {len(by_mrc.get(mrc["slug"], []))} municipalités</p>
            <ul class="grid sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-2 text-sm text-gray-600">{muni_links}</ul>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="fr-CA">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Courtier immobilier Estrie | Cantons-de-l'Est — immobiliermaison.com</title>
    <meta name="description" content="Courtiers immobiliers RE/MAX dans toute l'Estrie (Cantons-de-l'Est). {len(entries)} municipalités desservies. Équipe Chiasson de Francesco — évaluation gratuite, vente et achat immobilier de prestige.">
    <meta name="keywords" content="courtier immobilier Estrie, immobilier Cantons-de-l'Est, vendre maison Estrie, RE/MAX Estrie, équipe chiasson de francesco">
    <link rel="canonical" href="{BASE_URL}/estrie/">
    <meta name="robots" content="index, follow">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config={{theme:{{extend:{{colors:{{remaxRed:'#E11B22',luxuryDark:'#0A1128'}},fontFamily:{{serif:['Playfair Display','serif'],sans:['Montserrat','sans-serif']}}}}}}}}</script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
    <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"Courtier immobilier Estrie","description":"Pages SEO par municipalité en Estrie","url":"{BASE_URL}/estrie/"}}</script>
</head>
<body class="font-sans bg-[#FDFDFD]">
    <header class="bg-luxuryDark text-white py-8"><div class="max-w-7xl mx-auto px-6 lg:px-12"><a href="{BASE_URL}/" class="font-serif text-3xl font-bold uppercase">Immobilier<span class="text-remaxRed">maison</span></a><p class="text-gray-400 text-sm mt-2">Équipe Chiasson de Francesco · RE/MAX D'ABORD</p></div></header>
    <main class="max-w-7xl mx-auto px-6 lg:px-12 py-16">
        <h1 class="font-serif text-4xl md:text-6xl text-luxuryDark mb-6">Courtier immobilier en Estrie</h1>
        <p class="text-gray-500 font-light text-lg max-w-3xl mb-4">L'Estrie — aussi connue sous le nom des Cantons-de-l'Est — compte 9 MRC et {len(entries)} municipalités. L'Équipe Chiasson de Francesco, basée à Sherbrooke, dessert l'ensemble du territoire pour la vente et l'achat de propriétés résidentielles, commerciales et de prestige.</p>
        <p class="mb-12"><a href="{BASE_URL}/estrie/municipalites/" class="text-remaxRed font-semibold text-sm uppercase tracking-widest hover:underline">Index alphabétique complet →</a></p>
        {mrc_sections}
    </main>
    <footer class="bg-luxuryDark text-gray-400 text-center py-8 text-sm">&copy; 2026 <a href="{BASE_URL}/" class="hover:text-white">immobiliermaison.com</a></footer>
</body>
</html>
"""


def render_municipalities_index(entries):
    alpha = sorted(entries, key=lambda x: x["name"].lower())
    links = "\n".join(
        f'<li><a href="{BASE_URL}/estrie/{e["slug"]}/" class="hover:text-remaxRed">{e["name"]}</a> <span class="text-gray-400 text-xs">({e["mrc_name"]})</span></li>'
        for e in alpha
    )
    return f"""<!DOCTYPE html>
<html lang="fr-CA">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toutes les municipalités de l'Estrie | immobiliermaison.com</title>
    <meta name="description" content="Index de {len(entries)} pages SEO — courtier immobilier par municipalité en Estrie. Équipe Chiasson de Francesco, RE/MAX.">
    <link rel="canonical" href="{BASE_URL}/estrie/municipalites/">
    <meta name="robots" content="index, follow">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config={{theme:{{extend:{{colors:{{remaxRed:'#E11B22',luxuryDark:'#0A1128'}},fontFamily:{{serif:['Playfair Display','serif'],sans:['Montserrat','sans-serif']}}}}}}}}</script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-sans bg-[#FDFDFD]">
    <header class="bg-luxuryDark text-white py-6"><div class="max-w-7xl mx-auto px-6"><a href="{BASE_URL}/estrie/" class="text-gray-400 text-sm hover:text-white">← Estrie</a><h1 class="font-serif text-3xl mt-2">Municipalités de l'Estrie</h1></div></header>
    <main class="max-w-7xl mx-auto px-6 py-12"><ul class="grid sm:grid-cols-2 lg:grid-cols-3 gap-2 text-sm">{links}</ul></main>
</body>
</html>
"""


def write_sitemap(entries):
    urls = [f"  <url><loc>{BASE_URL}/</loc><priority>1.0</priority></url>"]
    urls.append(f"  <url><loc>{BASE_URL}/estrie/</loc><priority>0.9</priority></url>")
    urls.append(f"  <url><loc>{BASE_URL}/estrie/municipalites/</loc><priority>0.8</priority></url>")
    for mrc in MRCS:
        urls.append(f"  <url><loc>{BASE_URL}/estrie/mrc-{mrc['slug']}/</loc><priority>0.7</priority></url>")
    for e in entries:
        urls.append(f"  <url><loc>{BASE_URL}/estrie/{e['slug']}/</loc><priority>0.6</priority></url>")

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(content, encoding="utf-8")


def main():
    entries = collect_all_entries()
    if OUT.exists():
        import shutil
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for entry in entries:
        dest = OUT / entry["slug"]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(render_page(entry, entries), encoding="utf-8")

    for mrc in MRCS:
        dest = OUT / f"mrc-{mrc['slug']}"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(render_mrc_hub(mrc, entries), encoding="utf-8")

    (OUT / "index.html").write_text(render_estrie_hub(entries, MRCS), encoding="utf-8")
    (OUT / "municipalites").mkdir(exist_ok=True)
    (OUT / "municipalites" / "index.html").write_text(render_municipalities_index(entries), encoding="utf-8")

    manifest = [{"name": e["name"], "slug": e["slug"], "mrc": e["mrc_name"], "type": e["type"]} for e in entries]
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "municipalities.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    write_sitemap(entries)
    print(f"Generated {len(entries)} municipality pages + {len(MRCS)} MRC hubs + 2 index pages")
    print(f"Sitemap updated with {len(entries) + len(MRCS) + 3} URLs")


if __name__ == "__main__":
    main()
