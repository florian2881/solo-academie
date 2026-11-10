import re, os, json, html, shutil, datetime
from PIL import Image

ROOT = "/home/claude"
OUT = f"{ROOT}/web/dist"
BASE = "https://florian2881.github.io/solo-academie"
TODAY = datetime.date.today().isoformat()
STORE = "https://payhip.com/SoloAcademie"
PACK_URL = ""  # lien Payhip du pack, à remplir quand il existe

THEMES = [
    {"id": "sport", "nom": "Sport & bien-être", "court": "Sport",
     "titre_seo": "Apprendre un sport seul : programmes de sport en autodidacte",
     "intro": "Courir, te muscler ou gagner en souplesse sans coach ni abonnement. Chaque programme part de zéro, avancé semaine par semaine, avec des tests pour mesurer tes progrès.",
     "ids": ["courir", "muscu", "souplesse"]},
    {"id": "langues", "nom": "Langues", "court": "Langues",
     "titre_seo": "Apprendre une langue seul : coréen, japonais, espagnol, anglais",
     "intro": "Des programmes courts pour poser des bases solides dans une nouvelle langue, à raison de 15 à 20 minutes par jour : prononciation, phrases utiles, grammaire essentielle et exercices corrigés.",
     "ids": ["coreen", "japonais", "espagnol", "anglais"]},
    {"id": "arts-loisirs", "nom": "Arts & loisirs", "court": "Arts & loisirs",
     "titre_seo": "Apprendre la guitare, le dessin, la photo ou les échecs seul",
     "intro": "Jouer tes premières chansons, dessiner d'observation, réussir tes photos ou progresser aux échecs : des méthodes progressives pour apprendre un loisir en autodidacte.",
     "ids": ["guitare", "dessin", "photo", "echecs"]},
    {"id": "numerique-carriere", "nom": "Numérique & carrière", "court": "Numérique",
     "titre_seo": "Apprendre Excel, créer un site web et trouver ses premiers clients",
     "intro": "Des compétences utiles au travail et pour lancer une activité : Excel, HTML et CSS, et une méthode concrète pour trouver ton premier client en freelance.",
     "ids": ["excel", "siteweb", "freelance"]},
]

C = {
 "courir": dict(md="01-courir-5km", slug="courir-5km-debutant", titre="Courir 5 km en 8 semaines", seo="Courir 5 km en 8 semaines quand on débute", prix=19, duree="8 semaines", rythme="3 séances par semaine", niveau="Débutant complet", pages=8,
   url="https://payhip.com/b/6bZx9", accroche="Du canapé à 30 minutes de course sans t'arrêter, en alternant marche et course.",
   skills=["Courir 30 minutes sans t'arrêter (environ 5 km)", "Courir à la bonne allure sans t'épuiser", "Renforcer genoux et chevilles en 10 minutes", "Reconnaître et éviter les blessures courantes"]),
 "coreen": dict(md="02-coreen-30-jours", slug="apprendre-le-coreen", titre="Le coréen en 30 jours", seo="Apprendre le coréen seul en 30 jours", prix=24, duree="30 jours", rythme="20 minutes par jour", niveau="Débutant complet", pages=8,
   url="https://payhip.com/b/HWTLa", accroche="Lis le hangeul en une semaine, présente-toi et débrouille-toi au restaurant et dans les transports.", skills=None),
 "muscu": dict(md="03-muscu-maison", slug="musculation-maison-poids-du-corps", titre="Muscu maison au poids du corps", seo="Programme de musculation à la maison sans matériel", prix=19, duree="12 semaines", rythme="3 séances de 35 minutes par semaine", niveau="Débutant à intermédiaire", pages=9,
   url="https://payhip.com/b/2s7uB", accroche="12 semaines pour te muscler sans salle ni matériel, avec 5 niveaux par exercice.",
   skills=["Faire pompes, squats, rowings et dips avec une bonne technique", "Progresser sans matériel grâce à 5 niveaux par exercice", "Suivre un programme structuré de 12 semaines", "Mesurer tes progrès avec des tests"]),
 "anglais": dict(md="04-anglais-oral", slug="anglais-oral-oser-parler", titre="Débloque ton anglais oral", seo="Débloquer son anglais oral : oser parler en 60 jours", prix=24, duree="60 jours", rythme="15 minutes par jour", niveau="Tu comprends un peu mais tu bloques à l'oral", pages=7,
   url="https://payhip.com/b/Y5U8j", accroche="Arrête de traduire dans ta tête et ose enfin parler anglais, même avec ton accent.",
   skills=["Utiliser 60 blocs de phrases sans traduire", "Éviter les 5 erreurs typiques des francophones", "Parler 3 minutes sans t'arrêter sur un sujet du quotidien", "Tenir une vraie conversation avec un natif"]),
 "freelance": dict(md="05-premier-client-freelance", slug="trouver-premier-client-freelance", titre="Ton premier client freelance", seo="Trouver son premier client en freelance", prix=29, duree="30 jours", rythme="À ton rythme", niveau="Débutant", pages=9,
   url="https://payhip.com/b/Z41Xe", accroche="Une méthode concrète pour vendre une compétence que tu as déjà. Aucune promesse de revenus.", skills=None),
 "guitare": dict(md="06-guitare-30-jours", slug="apprendre-la-guitare-seul", titre="Guitare en autodidacte", seo="Apprendre la guitare seul en 30 jours", prix=19, duree="30 jours", rythme="15 minutes par jour", niveau="Débutant complet", pages=7,
   url="https://payhip.com/b/q8D1x", accroche="4 accords, 2 rythmes et tes premières chansons en un mois.", skills=None),
 "espagnol": dict(md="07-espagnol-30-jours", slug="apprendre-l-espagnol", titre="L'espagnol en 30 jours", seo="Apprendre l'espagnol seul en 30 jours", prix=24, duree="30 jours", rythme="20 minutes par jour", niveau="Débutant complet", pages=12,
   url="https://payhip.com/b/OLsoa", accroche="Prononciation, présent, ser et estar, phrases de voyage : les vraies bases.", skills=None),
 "japonais": dict(md="08-japonais-kana", slug="apprendre-hiragana-katakana", titre="Japonais : hiragana et katakana", seo="Apprendre les hiragana et katakana en 21 jours", prix=24, duree="21 jours", rythme="20 minutes par jour", niveau="Débutant complet", pages=9,
   url="https://payhip.com/b/8ZwbK", accroche="Les deux alphabets japonais, des exercices de lecture corrigés et tes premières phrases.", skills=None),
 "echecs": dict(md="09-echecs", slug="apprendre-les-echecs", titre="Les échecs en autodidacte", seo="Apprendre à jouer aux échecs seul", prix=24, duree="6 semaines", rythme="30 minutes par jour", niveau="Débutant complet", pages=8,
   url="https://payhip.com/b/1WwUr", accroche="Des règles complètes à tes premières victoires, avec un plan de progression.", skills=None),
 "dessin": dict(md="10-dessin-30-jours", slug="apprendre-a-dessiner", titre="Apprendre à dessiner en 30 jours", seo="Apprendre à dessiner seul en 30 jours", prix=19, duree="30 jours", rythme="25 minutes par jour", niveau="Débutant complet", pages=8,
   url="https://payhip.com/b/VINA4", accroche="Le dessin d'observation pas à pas, même si tu penses ne pas savoir dessiner.", skills=None),
 "souplesse": dict(md="11-souplesse", slug="souplesse-mobilite", titre="Souplesse et mobilité", seo="Gagner en souplesse : programme d'étirements en 6 semaines", prix=19, duree="6 semaines", rythme="15 minutes par jour", niveau="Tous niveaux, même très raide", pages=7,
   url="https://payhip.com/b/sTDEi", accroche="Moins raide, mieux dans ton corps, avec 10 exercices et des tests de progrès.",
   skills=["Faire 10 étirements essentiels correctement", "Suivre une routine de 15 minutes par jour", "Gagner en mobilité active", "Soulager les raideurs du travail assis en 5 minutes"]),
 "excel": dict(md="12-excel", slug="apprendre-excel-bases", titre="Excel : les bases indispensables", seo="Apprendre Excel seul : formules, tableaux et graphiques", prix=24, duree="4 semaines", rythme="25 minutes par jour", niveau="Débutant complet", pages=9,
   url="https://payhip.com/b/jVriX", accroche="Formules, tableaux et graphiques pour le travail et ton budget.", skills=None),
 "siteweb": dict(md="13-site-web-html-css", slug="creer-son-site-web-html-css", titre="Crée ton premier site web", seo="Créer son premier site web en HTML et CSS", prix=29, duree="30 jours", rythme="30 minutes par jour", niveau="Aucune connaissance en code", pages=10,
   url="https://payhip.com/b/rt4hs", accroche="HTML et CSS de zéro, jusqu'à ton site en ligne et lisible sur téléphone.", skills=None),
 "photo": dict(md="14-photo-smartphone", slug="photo-smartphone", titre="La photo au smartphone", seo="Apprendre la photo au smartphone", prix=19, duree="21 jours", rythme="15 minutes par jour", niveau="Débutant", pages=7,
   url="https://payhip.com/b/Ji7wc", accroche="Composition, lumière et retouche pour des photos qui sortent du lot.", skills=None),
}
THEME_OF = {cid: t for t in THEMES for cid in t["ids"]}

def strip_md(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s.strip()

def parse(md):
    s = open(f"{ROOT}/formations/{md}.md", encoding="utf-8").read()
    body = s.split("---", 2)[2]
    m = re.search(r"# Bienvenue[^\n]*\n\n(.+?)\n\n", body, re.S)
    intro = strip_md(m.group(1)) if m else ""
    m2 = re.search(r"# Bienvenue[^\n]*\n\n.+?\n\n(.+?)\n\n", body, re.S)
    intro2 = strip_md(m2.group(1)) if m2 and not m2.group(1).startswith(("**", "-", ">", "|", "#", "1.")) else ""
    modules, cur = [], None
    for line in body.splitlines():
        if line.startswith("# Module"):
            t = re.sub(r"^Module \d+ — ", "", line[2:].strip())
            cur = {"titre": t, "parts": []}; modules.append(cur)
        elif line.startswith("# "):
            cur = None
        elif line.startswith("## ") and cur is not None:
            cur["parts"].append(strip_md(line[3:]))
    skills = [strip_md(x) for x in re.findall(r"^- \[ \] (.+)$", body, re.M)]
    return intro, intro2, modules, skills

for cid, c in C.items():
    intro, intro2, modules, skills = parse(c["md"])
    c["intro"], c["intro2"], c["modules"] = intro, intro2, modules
    if not c["skills"]:
        c["skills"] = skills[:6]
    c["id"] = cid
    c["theme"] = THEME_OF[cid]
    c["path"] = f"formations/{c['slug']}.html"

E = html.escape

def head(title, desc, path, depth, extra_ld=None, og_img="assets/og.jpg"):
    pre = "../" * depth
    canon = f"{BASE}/{path}" if path != "index.html" else f"{BASE}/"
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (extra_ld or []))
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Solo Académie">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#17352b">
<meta name="google-site-verification" content="e4r3uuOzoxMJQv6gyVcO5iTqb2DGRmkEAErruzMM8QU">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{pre}assets/style.css">
{lds}
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="nav"><div class="wrap nav-in">
  <a class="logo" href="{pre}index.html" aria-label="Solo Académie, accueil">Solo<span>.</span>Académie</a>
  <nav aria-label="Thèmes">
    {''.join(f'<a href="{pre}themes/{t["id"]}.html">{E(t["court"])}</a>' for t in THEMES)}
  </nav>
  <a class="btn btn-sm" href="{pre}index.html#catalogue">Catalogue</a>
</div></header>
<main id="contenu">
"""

def foot(depth):
    pre = "../" * depth
    cols = "".join(f'<div><h3>{E(t["nom"])}</h3><ul>' + "".join(f'<li><a href="{pre}{C[i]["path"]}">{E(C[i]["titre"])}</a></li>' for i in t["ids"]) + "</ul></div>" for t in THEMES)
    return f"""</main>
<footer class="foot"><div class="wrap">
  <div class="foot-top">
    <div class="foot-brand"><a class="logo" href="{pre}index.html">Solo<span>.</span>Académie</a>
      <p>Des programmes complets pour apprendre seul, à ton rythme. Paiement sécurisé et livraison immédiate du PDF par email.</p>
      <a class="foot-store" href="{STORE}" rel="noopener">Voir la boutique →</a></div>
    {cols}
  </div>
  <div class="foot-bot"><span>© {datetime.date.today().year} Solo Académie</span><span>Paiement sécurisé par Payhip · PayPal et carte bancaire</span></div>
</div></footer>
</body>
</html>"""

def card(c, depth):
    pre = "../" * depth
    return f"""<article class="card">
  <a class="card-img" href="{pre}{c['path']}" tabindex="-1" aria-hidden="true"><img src="{pre}assets/covers/{c['id']}.jpg" alt="" width="520" height="735" loading="lazy"></a>
  <div class="card-body">
    <div class="card-meta"><span>{E(c['duree'])}</span><span>{E(c['niveau'].split(',')[0])}</span></div>
    <h3><a href="{pre}{c['path']}">{E(c['titre'])}</a></h3>
    <p>{E(c['accroche'])}</p>
    <div class="card-foot"><span class="price">{c['prix']} €</span><a class="link" href="{pre}{c['path']}">Voir le programme <span aria-hidden="true">→</span></a></div>
  </div>
</article>"""

FAQ = [
    ("Sous quelle forme je reçois la formation ?", "Un fichier PDF, envoyé par email juste après le paiement. Tu peux le lire sur ton téléphone, ta tablette ou ton ordinateur, ou l'imprimer pour remplir les exercices."),
    ("Faut-il un niveau de départ ?", "Non. Chaque formation indique son niveau, et la plupart partent de zéro."),
    ("Combien de temps faut-il y consacrer ?", "Entre 15 et 30 minutes par jour selon la formation, sur 3 à 12 semaines. Le rythme est indiqué sur chaque page."),
    ("Le paiement est-il sécurisé ?", "Oui. Le paiement est géré par Payhip, qui accepte PayPal et la carte bancaire, et qui envoie automatiquement le fichier après l'achat."),
    ("La formation freelance garantit-elle des revenus ?", "Non, et aucune formation honnête ne peut le faire. Elle donne une méthode concrète pour proposer un service et trouver des clients ; le résultat dépend de ta compétence et de ton travail."),
]

def faq_html(items):
    return '<div class="faq">' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in items) + "</div>"

def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def course_ld(c):
    return {"@context": "https://schema.org", "@type": "Course", "name": c["titre"], "description": c["intro"] or c["accroche"],
            "inLanguage": "fr", "url": f"{BASE}/{c['path']}", "image": f"{BASE}/assets/covers/{c['id']}.jpg",
            "provider": {"@type": "Organization", "name": "Solo Académie", "url": f"{BASE}/"},
            "educationalLevel": c["niveau"], "teaches": c["skills"],
            "offers": {"@type": "Offer", "category": "Paid", "price": f"{c['prix']}.00", "priceCurrency": "EUR", "url": c["url"], "availability": "https://schema.org/InStock"},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Online", "courseWorkload": c["rythme"]}}

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def write(path, content):
    full = f"{OUT}/{path}"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(f"{OUT}/assets/covers")
    shutil.copy(f"{ROOT}/web/style.css", f"{OUT}/assets/style.css")
    shutil.copy(f"{ROOT}/web/favicon.svg", f"{OUT}/assets/favicon.svg")
    shutil.copy(f"{ROOT}/web/og.jpg", f"{OUT}/assets/og.jpg")
    for cid, c in C.items():
        im = Image.open(f"{ROOT}/covers/Solo-Academie-{c['md']}-couverture.png").convert("RGB")
        im.thumbnail((520, 1000))
        im.save(f"{OUT}/assets/covers/{cid}.jpg", quality=82, optimize=True)

    # ---------- accueil ----------
    allc = list(C.values())
    total = sum(c["prix"] for c in allc)
    sections = ""
    for t in THEMES:
        cards = "".join(card(C[i], 0) for i in t["ids"])
        sections += f"""<section class="theme" id="{t['id']}" aria-labelledby="h-{t['id']}"><div class="wrap">
  <div class="theme-head"><div><p class="eyebrow">{len(t['ids'])} formations</p><h2 id="h-{t['id']}">{E(t['nom'])}</h2></div>
  <p>{E(t['intro'])}</p></div>
  <div class="grid g{len(t['ids'])}">{cards}</div>
  <a class="link" href="themes/{t['id']}.html">Tout le thème {E(t['nom'])} <span aria-hidden="true">→</span></a>
</div></section>"""
    pack = ""
    if PACK_URL:
        pack = f"""<section class="pack"><div class="wrap pack-in">
  <div><p class="eyebrow on-dark">Pack complet</p><h2>Les {len(allc)} formations en un seul achat</h2><p>Pour tout essayer, ou offrir un objectif à quelqu'un.</p></div>
  <div class="pack-price"><s>{total} €</s><strong>149 €</strong><a class="btn" href="{PACK_URL}" rel="noopener">Prendre le pack</a></div>
</div></section>"""
    itemlist = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{BASE}/{c['path']}", "name": c["titre"]} for i, c in enumerate(allc)]}
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Solo Académie", "url": f"{BASE}/", "logo": f"{BASE}/assets/favicon.svg"}
    home = head("Solo Académie — Apprendre seul : sport, langues, musique, numérique",
                f"{len(allc)} formations complètes pour apprendre seul : courir, muscu, coréen, japonais, espagnol, anglais, guitare, dessin, échecs, Excel, création de site web. Programme jour par jour en PDF, dès 19 €.",
                "index.html", 0, [org, itemlist, faq_ld(FAQ)])
    home += f"""<section class="hero"><div class="wrap hero-in">
  <div class="hero-txt">
    <p class="eyebrow on-dark">Formations pour autodidactes</p>
    <h1>Apprends seul.<br><em>Pour de vrai.</em></h1>
    <p class="lead">Des programmes complets pour apprendre un sport, une langue ou une compétence, sans prof et à ton rythme. Un plan jour par jour, des exercices corrigés, et rien d'autre à acheter.</p>
    <div class="hero-cta"><a class="btn" href="#catalogue">Voir les {len(allc)} formations</a><a class="btn btn-ghost" href="#methode">Comment ça marche</a></div>
  </div>
  <div class="hero-stack" aria-hidden="true">
    <img src="assets/covers/coreen.jpg" alt="" width="520" height="735">
    <img src="assets/covers/courir.jpg" alt="" width="520" height="735">
    <img src="assets/covers/guitare.jpg" alt="" width="520" height="735">
  </div>
</div>
<div class="wrap facts">
  <div><b>{len(allc)}</b><span>formations complètes</span></div>
  <div><b>15–30 min</b><span>par jour suffisent</span></div>
  <div><b>dès 19 €</b><span>paiement unique, PDF à vie</span></div>
  <div><b>Immédiat</b><span>envoyé par email après l'achat</span></div>
</div></section>

<section id="catalogue" class="catalogue"><div class="wrap">
  <p class="eyebrow">Catalogue</p><h2 class="h-xl">Choisis ce que tu veux apprendre</h2>
  <nav class="theme-chips" aria-label="Aller à un thème">
    {''.join(f'<a href="#{t["id"]}">{E(t["nom"])} <span>{len(t["ids"])}</span></a>' for t in THEMES)}
  </nav>
</div></section>
{sections}
{pack}
<section id="methode" class="method"><div class="wrap">
  <p class="eyebrow">La méthode</p><h2 class="h-xl">Un programme, pas un tas de vidéos</h2>
  <ol class="steps">
    <li><h3>Un objectif précis</h3><p>Courir 5 km, lire le hangeul, jouer 4 accords : chaque formation vise un résultat concret, atteignable en quelques semaines.</p></li>
    <li><h3>Un plan jour par jour</h3><p>Tu sais exactement quoi faire chaque jour, en 15 à 30 minutes. Pas besoin de chercher ni de trier des contenus.</p></li>
    <li><h3>Des preuves de progrès</h3><p>Exercices corrigés, journaux de suivi et bilans à cocher te montrent où tu en es à chaque étape.</p></li>
  </ol>
</div></section>
<section class="faq-sec"><div class="wrap narrow">
  <p class="eyebrow">Questions</p><h2 class="h-xl">Avant d'acheter</h2>
  {faq_html(FAQ)}
</div></section>
"""
    home += foot(0)
    write("index.html", home)

    # ---------- pages thème ----------
    for t in THEMES:
        cs = [C[i] for i in t["ids"]]
        p = f"themes/{t['id']}.html"
        pg = head(f"{t['titre_seo']} | Solo Académie", t["intro"], p, 1,
                  [crumbs_ld([("Accueil", f"{BASE}/"), (t["nom"], f"{BASE}/{p}")])])
        pg += f"""<section class="page-hero"><div class="wrap">
  <nav class="crumbs" aria-label="Fil d'Ariane"><a href="../index.html">Accueil</a><span>/</span><span>{E(t['nom'])}</span></nav>
  <h1>{E(t['nom'])}</h1><p class="lead">{E(t['intro'])}</p>
</div></section>
<section class="theme"><div class="wrap"><div class="grid g{len(cs)}">{''.join(card(c, 1) for c in cs)}</div></div></section>
<section class="other-themes"><div class="wrap"><h2>Les autres thèmes</h2><div class="theme-chips">
  {''.join(f'<a href="{o["id"]}.html">{E(o["nom"])} <span>{len(o["ids"])}</span></a>' for o in THEMES if o is not t)}
</div></div></section>"""
        pg += foot(1)
        write(p, pg)

    # ---------- pages formation ----------
    for c in allc:
        t = c["theme"]
        mods = "".join(f"""<li><div class="mod-n">{i+1}</div><div><h3>{E(m['titre'])}</h3>{('<ul>' + ''.join(f'<li>{E(x)}</li>' for x in m['parts']) + '</ul>') if m['parts'] else ''}</div></li>""" for i, m in enumerate(c["modules"]))
        skills = "".join(f"<li>{E(s)}</li>" for s in c["skills"])
        rel = [C[i] for i in t["ids"] if i != c["id"]][:3]
        cfaq = [
            ("Pour qui est cette formation ?", f"Niveau : {c['niveau']}. Elle est pensée pour apprendre seul, sans prof ni matériel compliqué."),
            ("Combien de temps faut-il ?", f"{c['duree']}, à raison de {c['rythme'].lower()}."),
            ("Comment je reçois la formation ?", f"Un PDF de {c['pages']} pages, envoyé par email juste après le paiement sécurisé (PayPal ou carte bancaire)."),
        ]
        pg = head(f"{c['seo']} — Programme PDF | Solo Académie", f"{c['accroche']} {c['duree']}, {c['rythme'].lower()}. Programme complet en PDF, {c['prix']} €.",
                  c["path"], 1, [course_ld(c), crumbs_ld([("Accueil", f"{BASE}/"), (t["nom"], f"{BASE}/themes/{t['id']}.html"), (c["titre"], f"{BASE}/{c['path']}")]), faq_ld(cfaq)],
                  og_img=f"assets/covers/{c['id']}.jpg")
        intro2 = f"<p>{E(c['intro2'])}</p>" if c["intro2"] else ""
        pg += f"""<section class="page-hero course-hero"><div class="wrap course-top">
  <div class="course-txt">
    <nav class="crumbs" aria-label="Fil d'Ariane"><a href="../index.html">Accueil</a><span>/</span><a href="../themes/{t['id']}.html">{E(t['nom'])}</a></nav>
    <h1>{E(c['titre'])}</h1>
    <p class="lead">{E(c['intro'])}</p>
    {intro2}
    <dl class="course-facts">
      <div><dt>Durée</dt><dd>{E(c['duree'])}</dd></div>
      <div><dt>Rythme</dt><dd>{E(c['rythme'])}</dd></div>
      <div><dt>Niveau</dt><dd>{E(c['niveau'])}</dd></div>
      <div><dt>Format</dt><dd>PDF, {c['pages']} pages</dd></div>
    </dl>
  </div>
  <aside class="buy-box" aria-label="Acheter">
    <img src="../assets/covers/{c['id']}.jpg" alt="Couverture de la formation {E(c['titre'])}" width="520" height="735">
    <div class="buy-in">
      <div class="price-lg">{c['prix']} €</div>
      <p>Paiement unique · PDF envoyé par email immédiatement</p>
      <a class="btn btn-block" href="{c['url']}" rel="noopener">Acheter la formation</a>
      <p class="secure">Paiement sécurisé par Payhip · PayPal ou carte</p>
    </div>
  </aside>
</div></section>
<section class="course-body"><div class="wrap course-grid">
  <div class="course-main">
    <h2>À la fin, tu sauras</h2>
    <ul class="checks">{skills}</ul>
    <h2>Le programme complet</h2>
    <ol class="modules">{mods}</ol>
    <h2>Questions fréquentes</h2>
    {faq_html(cfaq)}
  </div>
</div></section>
<section class="related"><div class="wrap">
  <h2>Dans le même thème</h2>
  <div class="grid">{''.join(card(r, 1) for r in rel)}</div>
</div></section>
<div class="sticky-buy"><span>{E(c['titre'])} · <b>{c['prix']} €</b></span><a class="btn btn-sm" href="{c['url']}" rel="noopener">Acheter</a></div>
"""
        pg += foot(1)
        write(c["path"], pg)

    # ---------- 404, robots, sitemap ----------
    nf = head("Page introuvable | Solo Académie", "Cette page n'existe pas.", "404.html", 0)
    nf = nf.replace('href="assets/', f'href="{BASE}/assets/').replace('href="index.html', f'href="{BASE}/index.html').replace('href="themes/', f'href="{BASE}/themes/')
    nf += f"""<section class="page-hero"><div class="wrap"><h1>Page introuvable</h1><p class="lead">Cette page n'existe pas ou a changé d'adresse.</p><p><a class="btn" href="{BASE}/">Retour à l'accueil</a></p></div></section>"""
    nf += foot(0).replace('href="index.html', f'href="{BASE}/index.html').replace('href="formations/', f'href="{BASE}/formations/')
    write("404.html", nf)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    urls = [f"{BASE}/"] + [f"{BASE}/themes/{t['id']}.html" for t in THEMES] + [f"{BASE}/{c['path']}" for c in allc]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    write(".nojekyll", "")
    print("pages:", len(urls), "+ 404")

if __name__ == "__main__":
    build()
