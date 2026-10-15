#!/usr/bin/env python3
"""Gera a pasta public/ (site pronto para o Render) a partir de recovered-deployment/.

A cópia recuperada é idêntica ao site que estava no ar. Este script só mexe no
<head> de cada página (título, descrição, canonical, Open Graph, JSON-LD) e cria
robots.txt, sitemap.xml, favicons e a imagem de compartilhamento.
Uso: python3 scripts/build_public.py
"""
import json, re, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "recovered-deployment"
OUT = ROOT / "public"
SITE = "https://livrosquetransformam.pcgdigital.com.br"
AUTOR = "Pe. Pedro de Celso Gardini"
NOME = "Gestão Pastoral — Livros do Pe. Pedro de Celso Gardini"
CLUB = "https://clubedeautores.com.br/cart"
IMG_GESTAO = "/manus-storage/capa-gestao-pastoral_4021fa04.jpg"
IMG_ESS = "/manus-storage/capa_essencial_rosa_serena_subtitulo_reforcado_9fd5d091.png"

# Enquanto o servidor de códigos/e-mails não existe, as ferramentas ficam "em breve".
# Quando o servidor estiver pronto: TOOLS_LIVE = True
TOOLS_LIVE = False

PAGES = [
    dict(path="/", title="Gestão Pastoral — Livros e ferramentas para a paróquia | Pe. Pedro Gardini",
         desc="Livros do Pe. Pedro de Celso Gardini para servir, organizar e acolher: Gestão Pastoral e O Essencial é Invisível aos Olhos. Ferramentas práticas para a paróquia.",
         sitemap=True, prio="1.0"),
    dict(path="/gestao-pastoral", title="Gestão Pastoral — livro de ferramentas para uma Igreja viva e organizada",
         desc="Gestão Pastoral, do Pe. Pedro de Celso Gardini: ferramentas práticas para planejar, acolher, formar equipes e transformar boas intenções em passos concretos. Leia o primeiro capítulo grátis.",
         og=IMG_GESTAO, sitemap=True, prio="0.9", ld="gestao"),
    dict(path="/o-essencial", title="O Essencial é Invisível aos Olhos — guia para o secretário(a) paroquial",
         desc="Um guia para quem trabalha na secretaria paroquial, inspirado n’O Pequeno Príncipe: escuta, delicadeza e cuidado com cada pessoa que chega. Do Pe. Pedro de Celso Gardini.",
         og=IMG_ESS, sitemap=True, prio="0.8", ld="essencial"),
    dict(path="/o-essencial/primeiro-capitulo", title="Cativar é criar laços — primeiro encontro na secretaria paroquial | O Essencial é Invisível aos Olhos",
         desc="Leia o primeiro encontro de O Essencial é Invisível aos Olhos: como o acolhimento na secretaria paroquial cria laços. Trecho do livro do Pe. Pedro de Celso Gardini.",
         og=IMG_ESS, sitemap=True, prio="0.6"),
    dict(path="/leia-o-primeiro-capitulo", title="A acolhida como primeira evangelização — primeiro capítulo grátis de Gestão Pastoral",
         desc="Leia grátis o Capítulo 1 de Gestão Pastoral: “A acolhida como primeira evangelização” e o fundamento de toda gestão pastoral. Do Pe. Pedro de Celso Gardini.",
         og=IMG_GESTAO, sitemap=True, prio="0.8"),
    dict(path="/ferramentas", title="Ferramentas de gestão pastoral — Roda da Vida, SWOT, 5W2H, Eisenhower",
         desc="Ferramentas gratuitas para preencher, visualizar e imprimir: Roda da Vida pastoral, Metas SMART, Análise SWOT, Matriz de Eisenhower, Plano 5W2H e Checklist de Acolhida.",
         sitemap=True, prio="0.7", tools=True),
    dict(path="/relatorio-financeiro", title="Relatório financeiro paroquial — modelo para imprimir",
         desc="Modelo de relatório financeiro paroquial para preencher e imprimir.",
         noindex=True, sitemap=False),
]

def esc(s): return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")

def jsonld(page):
    g = [{"@context": "https://schema.org", "@type": "Person", "@id": SITE + "/#autor",
          "name": AUTOR, "url": SITE + "/", "image": SITE + "/manus-storage/retrato_pe_pedro_limpo_535a3d64.png",
          "sameAs": ["https://instagram.com/pegardini", "https://youtube.com/@pedrogardini",
                     "https://linkedin.com/in/pedro-de-celso-gardini-ba8baa22"]}]
    if page["path"] == "/":
        g.append({"@context": "https://schema.org", "@type": "WebSite", "name": "Gestão Pastoral — Livros e ferramentas",
                  "url": SITE + "/", "inLanguage": "pt-BR", "author": {"@id": SITE + "/#autor"}})
    if page.get("ld") == "gestao":
        g.append({"@context": "https://schema.org", "@type": "Book", "name": "Gestão Pastoral",
                  "alternateName": "Gestão Pastoral: ferramentas práticas para uma Igreja viva e organizada",
                  "author": {"@id": SITE + "/#autor"}, "inLanguage": "pt-BR", "bookFormat": "https://schema.org/Paperback",
                  "image": SITE + IMG_GESTAO, "url": SITE + "/gestao-pastoral",
                  "description": page["desc"],
                  "offers": {"@type": "Offer", "price": "42.68", "priceCurrency": "BRL",
                             "availability": "https://schema.org/PreOrder", "url": CLUB}})
    if page.get("ld") == "essencial":
        g.append({"@context": "https://schema.org", "@type": "Book", "name": "O Essencial é Invisível aos Olhos",
                  "author": {"@id": SITE + "/#autor"}, "inLanguage": "pt-BR",
                  "image": SITE + IMG_ESS, "url": SITE + "/o-essencial", "description": page["desc"]})
    return "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>" for x in g)

def make_head_html(src_html, page):
    url = SITE + page["path"] if page["path"] != "/" else SITE + "/"
    og = SITE + "/og-image.jpg" if not page.get("og") else SITE + "/og-image.jpg"
    h = src_html
    # No Render, o CSS pedido com `crossorigin` responde 503/404; sem o atributo carrega normalmente.
    h = h.replace('<link rel="stylesheet" crossorigin href=', '<link rel="stylesheet" href=')
    h = h.replace('<html lang="en">', '<html lang="pt-BR">')
    # remove metadados antigos do Manus
    h = re.sub(r'<title>.*?</title>', '', h, count=1, flags=re.S)
    h = re.sub(r'\s*<meta property="og:[^>]*>', '', h)
    h = re.sub(r'\s*<meta name="twitter:[^>]*>', '', h)
    h = re.sub(r'<link rel="canonical"[^>]*>', '', h)
    # estatísticas do Manus (conta dele) saem junto com o site
    h = re.sub(r'<script\s+defer\s+src="https://manus-analytics\.com/umami"[^>]*></script>', '', h)
    h = re.sub(r'<script\s+defer\s+data-domain="manus\.space".*?</script>\s*<script>.*?</script>', '', h, flags=re.S)
    h = re.sub(r'<link rel="manifest"[^>]*>', '<link rel="manifest" href="/manifest.webmanifest" />', h)
    robots = "noindex, nofollow" if page.get("noindex") else "index, follow, max-image-preview:large"
    meta = f'''<title>{esc(page["title"])}</title>
<meta name="description" content="{esc(page["desc"])}" />
<meta name="robots" content="{robots}" />
{"" if page["path"]=="/404" else f'<link rel="canonical" href="{url}" />'}
<meta name="theme-color" content="#173467" />
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Gestão Pastoral — Pe. Pedro de Celso Gardini" />
<meta property="og:locale" content="pt_BR" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{esc(page["title"])}" />
<meta property="og:description" content="{esc(page["desc"])}" />
<meta property="og:image" content="{og}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(page["title"])}" />
<meta name="twitter:description" content="{esc(page["desc"])}" />
<meta name="twitter:image" content="{og}" />
{jsonld(page)}
'''
    h = h.replace("</head>", meta + "</head>", 1)
    return h

def font(size, bold=False):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "/usr/share/fonts/opentype/inter/Inter-Regular.otf"]:
        if Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def build_images():
    # imagem de compartilhamento 1200x630 com as duas capas
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "#173467")
    d = ImageDraw.Draw(im)
    for x in range(W):  # leve degradê
        c = int(23 + 14 * x / W); d.line([(x, 0), (x, H)], fill=(c, 52 + int(18 * x / W), 103 + int(20 * x / W)))
    d.text((60, 120), "Gestão Pastoral", font=font(66, True), fill="#ffffff")
    d.text((60, 228), "Livros e ferramentas para servir,", font=font(34), fill="#e9c76e")
    d.text((60, 275), "organizar e acolher a paróquia", font=font(34), fill="#e9c76e")
    d.text((60, 520), AUTOR, font=font(30, True), fill="#dbeafe")
    d.line([(62, 206), (300, 206)], fill="#e9c76e", width=4)
    for i, f in enumerate(["capa-gestao-pastoral_4021fa04.jpg", "capa_essencial_rosa_serena_subtitulo_reforcado_9fd5d091.png"]):
        c = Image.open(SRC / "manus-storage" / f).convert("RGB")
        c.thumbnail((250, 400)); x = 700 + i * 230; y = 110 + i * 40
        d.rectangle([x - 6, y - 6, x + c.width + 6, y + c.height + 6], fill="#ffffff")
        im.paste(c, (x, y))
    im.save(OUT / "og-image.jpg", quality=88)
    # favicon: livro dourado sobre azul
    def icon(size):
        S = size * 4
        a = Image.new("RGBA", (S, S), "#173467"); g = ImageDraw.Draw(a)
        m = S * 0.2
        g.rounded_rectangle([m, m * 0.9, S - m, S - m * 0.9], radius=S * 0.05, fill="#e9c76e")
        g.rectangle([S * 0.5 - S * 0.015, m * 0.9, S * 0.5 + S * 0.015, S - m * 0.9], fill="#173467")
        g.rectangle([S * 0.5 - S * 0.012 - S * 0.16, S * 0.36, S * 0.5 - S * 0.04, S * 0.385], fill="#173467")
        g.rectangle([S * 0.5 + S * 0.04, S * 0.36, S * 0.5 + S * 0.012 + S * 0.16, S * 0.385], fill="#173467")
        g.rectangle([S * 0.5 - S * 0.012 - S * 0.16, S * 0.46, S * 0.5 - S * 0.04, S * 0.485], fill="#173467")
        g.rectangle([S * 0.5 + S * 0.04, S * 0.46, S * 0.5 + S * 0.012 + S * 0.16, S * 0.485], fill="#173467")
        return a.resize((size, size), Image.LANCZOS).convert("RGB")
    icon(180).save(OUT / "apple-touch-icon.png"); icon(32).save(OUT / "favicon-32.png")
    icon(192).save(OUT / "icon-192.png"); icon(512).save(OUT / "icon-512.png")
    icon(64).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

EM_BREVE = ('()=>b.jsxs("main",{style:{minHeight:"100vh",display:"grid",placeItems:"center",background:"#fffdf8",padding:"40px 20px",textAlign:"center",fontFamily:"Inter,sans-serif"},'
            'children:[b.jsxs("div",{style:{maxWidth:560},children:[b.jsx("p",{style:{color:"#a87a21",fontWeight:700,letterSpacing:".2em",textTransform:"uppercase",fontSize:12},children:"Em breve"}),'
            'b.jsx("h1",{style:{color:"#173467",fontFamily:"Playfair Display,serif",fontSize:"2.2rem",margin:"12px 0"},children:"Ferramentas pastorais"}),'
            'b.jsx("p",{style:{color:"#64748b",lineHeight:1.7},children:"Estamos preparando o novo acesso às ferramentas do livro Gestão Pastoral. Volte em breve."}),'
            'b.jsx("a",{href:"/",style:{display:"inline-block",marginTop:18,background:"#173467",color:"white",padding:"12px 20px",borderRadius:10,fontWeight:600,textDecoration:"none"},children:"Voltar para o site"})]})]})')

def hide_tools():
    js = next((OUT / "assets").glob("index-*.js"))
    t = js.read_text(encoding="utf8")
    for route, comp in (("/ferramentas", "Rce"), ("/relatorio-financeiro", "Mce")):
        old = f'path:"{route}",component:{comp}}}'
        assert t.count(old) == 1, old
        t = t.replace(old, f'path:"{route}",component:{EM_BREVE}}}')
    js.write_text(t, encoding="utf8")

def optimize_images():
    # Reduz as imagens grandes de manus-storage mantendo nome e formato (os HTML/JS apontam para esses nomes).
    # Original: ~7,3 MB; fica em ~1,1 MB. Os arquivos originais continuam em recovered-deployment/.
    for f in (OUT / "manus-storage").iterdir():
        im = Image.open(f).convert("RGB")
        if f.suffix.lower() == ".png":
            im.thumbnail((900, 1200), Image.LANCZOS)
            im.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f, optimize=True)
        else:
            im.thumbnail((800, 1400), Image.LANCZOS)
            im.save(f, quality=82, optimize=True, progressive=True)

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    optimize_images()
    (OUT / "__manus").exists() and shutil.rmtree(OUT / "__manus")  # manifesto passa a ser /manifest.webmanifest
    build_images()
    if not TOOLS_LIVE: hide_tools()
    manifest = {"name": "Gestão Pastoral - Recursos Complementares", "short_name": "Gestão Pastoral", "start_url": "/",
                "display": "standalone", "background_color": "#fffdf8", "theme_color": "#173467",
                "description": "Livros para servir, organizar e acolher.",
                "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
    (OUT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf8")
    base = (SRC / "index.html").read_text(encoding="utf8")
    pages = [dict(q, noindex=True, sitemap=False, title="Ferramentas pastorais — em breve | Gestão Pastoral",
                  desc="Estamos preparando o novo acesso às ferramentas do livro Gestão Pastoral.")
             if q.get("tools") and not TOOLS_LIVE else q for q in PAGES]
    for p in pages:
        html = make_head_html(base, p)
        dest = OUT / "index.html" if p["path"] == "/" else OUT / p["path"].strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_text(html, encoding="utf8")
    # página 404 real (mantém noindex)
    nf = make_head_html(base, dict(path="/404", title="Página não encontrada | Gestão Pastoral", desc="Página não encontrada.", noindex=True))
    (OUT / "404.html").write_text(nf, encoding="utf8")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        if p.get("sitemap"):
            sm.append(f'  <url><loc>{SITE}{p["path"] if p["path"] != "/" else "/"}</loc><priority>{p["prio"]}</priority></url>')
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /relatorio-financeiro\n{"" if TOOLS_LIVE else "Disallow: /ferramentas" + chr(10)}\nSitemap: {SITE}/sitemap.xml\n", encoding="utf8")
    print("ok:", sum(1 for _ in OUT.rglob("*") if _.is_file()), "arquivos em", OUT)

main()
