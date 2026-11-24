#!/usr/bin/env python3
"""Gera a pasta public/ (site pronto para o Render) a partir de recovered-deployment/.

A cópia recuperada é idêntica ao site que estava no ar. Este script só mexe no
<head> de cada página (título, descrição, canonical, Open Graph, JSON-LD) e cria
robots.txt, sitemap.xml, favicons e a imagem de compartilhamento.
Uso: python3 scripts/build_public.py
"""
import hashlib, json, re, shutil
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
TOOLS_LIVE = True

# Acesso às ferramentas sem servidor (ver scripts/tools-access.template.js).
# Código impresso no livro (único para todos os exemplares); só a impressão digital vai para o site.
TOOLS_CODE = "GESTAO-PASTORAL-2026"
# Formulário público do Brevo (lista "Livros - ferramentas", dupla confirmação). Endereço público por natureza.
BREVO_FORM_URL = "https://dbd3de88.sibforms.com/serve/MUIFAGnvsWDRw2HUAW1rW3ckEaQHXk2-GObhhT3KcJx2c8ehac54PBf1S2qkLSRXC2agyojUQWJKEYAiAw9QSX6waKEF8ttkJDy43LTTLJQrfqmvc_QvMmzC1XTrp-MvfRH6_qMu4XgjXeeNkgarfKG2js5mcBLUu0rYN_CG_hcLljPQiSZi0hYBd4alNuoBC_rWfO-hwjHKy4wRYQ=="

def write_tools_access():
    t = (ROOT / "scripts" / "tools-access.template.js").read_text(encoding="utf8")
    h = hashlib.sha256(TOOLS_CODE.upper().replace(" ", "").encode()).hexdigest()
    (OUT / "tools-access.js").write_text(t.replace("__CODE_HASH__", h).replace("__BREVO_URL__", BREVO_FORM_URL), encoding="utf8")


PRIVACIDADE_HTML = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Privacidade | Gestão Pastoral — Pe. Pedro de Celso Gardini</title>
<meta name="description" content="Como tratamos os dados de quem usa as ferramentas do livro Gestão Pastoral e aceita receber novidades.">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<style>
body{margin:0;background:#fdfbf7;color:#334155;font:17px/1.65 Georgia,'Times New Roman',serif}
main{max-width:720px;margin:0 auto;padding:32px 20px 64px}
h1{color:#173467;font-size:2rem;line-height:1.2;margin:.6em 0 .2em}
h2{color:#173467;font-size:1.2rem;margin:1.8em 0 .3em}
a{color:#173467} .meta{color:#64748b;font-size:.9rem} .voltar{font:600 .95rem system-ui,sans-serif;text-decoration:none}
</style></head><body><main>
<a class="voltar" href="/">← Voltar ao site</a>
<h1>Privacidade</h1>
<p class="meta">Atualizado em 15/10/2026</p>
<p>Esta página explica, sem rodeios, o que acontece com os seus dados quando você usa as ferramentas do livro <em>Gestão Pastoral</em> neste site.</p>

<h2>Quem cuida dos dados</h2>
<p>Pe. Pedro de Celso Gardini, autor do livro e responsável por este site. Dúvidas, pedidos e reclamações: <a href="mailto:contato@pcgdigital.com.br">contato@pcgdigital.com.br</a>.</p>

<h2>Quem tem o código do livro</h2>
<p>Se você digita o código impresso no livro, a conferência acontece no seu próprio navegador. Nenhum dado seu é enviado ou guardado por nós. O site apenas anota, no seu navegador, que o acesso foi liberado, para você não digitar de novo.</p>

<h2>Quem escolhe “Quero conhecer as ferramentas”</h2>
<p>Você informa nome e e-mail para liberar o acesso. Esses dados <strong>só saem do seu navegador se você marcar a caixa</strong> “Quero receber novidades por e-mail”. Sem marcar, você usa as ferramentas normalmente e nada é guardado.</p>
<p>Se marcar, enviamos <strong>apenas o e-mail</strong> para a nossa lista de contatos no Brevo, serviço de e-mail de uma empresa francesa que atua como operadora dos dados. O nome digitado não é guardado. Antes de entrar na lista, você recebe uma mensagem para confirmar o cadastro (dupla confirmação).</p>
<ul>
<li><strong>Para quê:</strong> avisar sobre novidades do livro, das ferramentas e de outros trabalhos do autor.</li>
<li><strong>Base legal:</strong> o seu consentimento (LGPD, art. 7º, I).</li>
<li><strong>Por quanto tempo:</strong> até você pedir para sair.</li>
</ul>

<h2>Como sair ou apagar</h2>
<p>Todo e-mail enviado tem um link de descadastro. Se preferir, escreva para <a href="mailto:contato@pcgdigital.com.br">contato@pcgdigital.com.br</a> pedindo para apagar os seus dados. Você também pode pedir acesso a eles, correção e informações sobre o tratamento, como prevê o art. 18 da LGPD.</p>

<h2>Compra do livro</h2>
<p>A compra acontece fora deste site, no Clube de Autores ou na Amazon, que têm as suas próprias políticas. Não recebemos nem guardamos dados de pagamento.</p>

<h2>Mudanças</h2>
<p>Se algo mudar nesta página, a data no topo será atualizada.</p>
</main></body></html>
"""

def write_privacidade():
    d = OUT / "privacidade"; d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(PRIVACIDADE_HTML, encoding="utf8")

PAGES = [
    dict(path="/", title="Gestão Pastoral — Livros e ferramentas para a paróquia | Pe. Pedro Gardini",
         desc="Livros do Pe. Pedro de Celso Gardini para servir, organizar e acolher: Gestão Pastoral, Jesus, a Torá e a Identidade Judaica e O Essencial é Invisível aos Olhos. Ferramentas práticas para a paróquia.",
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
    if page["path"] == "/":
        g.append({"@context": "https://schema.org", "@type": "Book", "name": "Jesus, a Torá e a Identidade Judaica",
                  "alternateName": "Jesus, a Torá e a Identidade Judaica: Um convite para ler a Bíblia de outro jeito",
                  "author": {"@id": SITE + "/#autor"}, "inLanguage": "pt-BR", "bookFormat": "https://schema.org/EBook",
                  "image": SITE + "/livros/capa-jesus-tora.jpg", "url": "https://www.amazon.com.br/dp/B0HNTQC769",
                  "offers": {"@type": "Offer", "price": "17.73", "priceCurrency": "BRL",
                             "availability": "https://schema.org/InStock", "url": "https://www.amazon.com.br/dp/B0HNTQC769"}})
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
    h = re.sub(r'(<script type="module")', r'<script src="/tools-access.js"></script>\1', h, count=1)
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

# Fim da pré-venda: preço atual do livro impresso (R$ 52,68, Clube de Autores) e textos sem "pré-venda".
# Os textos estão no bundle compilado; cada troca precisa achar exatamente o número de ocorrências esperado.
TROCAS_PRECO = [
    ("Garanta na pré-venda por R$ 42,68.", "Livro impresso por R$ 52,68.", 1),
    ("Garanta na pré-venda por R$ 42,68", "Livro impresso por R$ 52,68", 1),
    ("Garantir na pré-venda por R$ 42,68", "Comprar por R$ 52,68", 1),
    ("Livro impresso na pré-venda: R$ 42,68", "Livro impresso: R$ 52,68", 1),
    (" Livro impresso: pré-venda por R$ 42,68", " Livro impresso: R$ 52,68", 1),
    ("Impresso · R$ 42,68", "Impresso · R$ 52,68", 1),
    ("Kindle · Amazon", "Kindle · R$ 31,99", 1),
    ("Comprar Kindle na Amazon", "Comprar Kindle por R$ 31,99", 2),
    ("Prefere Kindle? Compre na Amazon", "Prefere Kindle? R$ 31,99 na Amazon", 1),
    ("Garantir por R$ 42,68", "Comprar por R$ 52,68", 1),
    ("Livro impresso · condição de pré-venda", "Livro impresso", 1),
    ("Livro impresso · pré-venda", "Livro impresso", 1),
    ("Uma condição especial válida durante os 28 dias da pré-venda.", "Venda pelo Clube de Autores.", 1),
    ("Pré-venda aberta", "Já disponível", 2),
    (" via gestao-pastoral.com.br", " via livrosquetransformam.pcgdigital.com.br", 1),
    ('," Garantir"]', '," Comprar"]', 1),
]

def atualizar_preco():
    for js in (OUT / "assets").glob("index-*.js"):
        t = js.read_text(encoding="utf-8")
        for antigo, novo, n in TROCAS_PRECO:
            assert t.count(antigo) == n, f"{antigo!r}: esperado {n}, achei {t.count(antigo)}"
            t = t.replace(antigo, novo)
        assert "42,68" not in t and "pré-venda" not in t.lower()
        js.write_text(t, encoding="utf-8")

# Livro "Jesus, a Torá e a Identidade Judaica" (ebook Kindle). Entra como 2º card na página inicial.
# A capa fica em livros-extra/ e é copiada para public/livros/.
TORA_AMAZON = "https://www.amazon.com.br/dp/B0HNTQC769"
TORA_PRECO = "R$ 17,73"
TORA_CAPA_SRC = ROOT / "livros-extra" / "capa-jesus-tora.jpg"
TORA_CAPA = "/livros/capa-jesus-tora.jpg"
TORA_TITULO = "Jesus, a Torá e a Identidade Judaica"
TORA_SUBTITULO = "Um convite para ler a Bíblia de outro jeito"
TORA_DESCRICAO = ("Uma leitura católica, bíblica e pastoral que apresenta Jesus em seu ambiente judaico, a Torá, "
                  "Paulo e as raízes judaicas da fé cristã. Para catequistas, agentes de pastoral e grupos de estudo bíblico.")
BOTAO_CONTORNO = ("inline-flex items-center justify-center rounded-lg border border-[#173467]/30 px-4 py-2.5 text-sm "
                  "font-semibold text-[#173467] transition-colors hover:bg-white")
BOTAO = ("inline-flex items-center justify-center rounded-lg bg-[#173467] px-4 py-2.5 text-sm font-semibold "
         "text-white transition-colors hover:bg-[#22447f]")

def _js(s): return json.dumps(s, ensure_ascii=False)

def adicionar_livro_tora():
    for js in (OUT / "assets").glob("index-*.js"):
        t = js.read_text(encoding="utf-8")
        novo_livro = (',{slug:"jesus-tora",title:' + _js(TORA_TITULO) + ',subtitle:' + _js(TORA_SUBTITULO) +
                      ',description:' + _js(TORA_DESCRICAO) + ',coverUrl:' + _js(TORA_CAPA) +
                      ',status:"disponível",accent:"navy"}],zd=NO[0],Gc=NO[1];')
        trocas = [
            ('status:"em breve",accent:"terracotta"}],zd=NO[0],Gc=NO[1];',
             'status:"em breve",accent:"terracotta"}' + novo_livro),
            ('children:NO.map(e=>{const t=e.slug==="gestao-pastoral";',
             'children:[NO[0],NO[2],NO[1]].map(e=>{const t=e.slug!=="o-essencial",g=e.slug==="gestao-pastoral";'),
            ('children:"Livro impresso: R$ 52,68"}),b.jsx("div",{"data-loc":"client/src/pages/Home.tsx:36"',
             'children:g?"Livro impresso: R$ 52,68":' + _js("Ebook Kindle: " + TORA_PRECO) +
             '}),b.jsx("div",{"data-loc":"client/src/pages/Home.tsx:36"'),
            ('className:"mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap",children:t?b.jsxs(b.Fragment,',
             'className:"mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap",children:t&&!g?b.jsx("a",{href:' +
             _js(TORA_AMAZON) + ',target:"_blank",rel:"noreferrer",className:' + _js(BOTAO_CONTORNO) +
             ',children:' + _js("Comprar na Amazon · " + TORA_PRECO) + '}):t?b.jsxs(b.Fragment,'),
            ('children:"Gestão Pastoral"}),b.jsx(Ct,{"data-loc":"client/src/components/SiteHeader.tsx:15"',
             'children:"Gestão Pastoral"}),b.jsx("a",{href:"/jesus-tora",className:"transition-colors hover:text-[#173467]",children:"Jesus e a Torá"}),b.jsx(Ct,{"data-loc":"client/src/components/SiteHeader.tsx:15"'),
            ('children:t&&!g?b.jsx("a",{href:' + _js(TORA_AMAZON),
             'children:t&&!g?b.jsxs(b.Fragment,{children:[b.jsx("a",{href:"/jesus-tora",className:' + _js(BOTAO) +
             ',children:"Conhecer o livro →"}),b.jsx("a",{href:' + _js(TORA_AMAZON)),
            ('children:' + _js("Comprar na Amazon · " + TORA_PRECO) + '}):t?b.jsxs(b.Fragment,',
             'children:' + _js("Comprar na Amazon · " + TORA_PRECO) + '})]}):t?b.jsxs(b.Fragment,'),
            ("Dois livros, uma mesma missão.", "Uma coleção de livros, uma mesma missão."),
            ("Juntas, elas unem gestão, acolhida e espiritualidade do cotidiano pastoral.",
             "Juntas, elas unem gestão, acolhida, leitura da Bíblia e espiritualidade do cotidiano pastoral."),
        ]
        for antigo, novo in trocas:
            assert t.count(antigo) == 1, f"{antigo[:60]!r}: esperado 1, achei {t.count(antigo)}"
            t = t.replace(antigo, novo)
        js.write_text(t, encoding="utf-8")
    # artes das redes sociais (o Buffer busca as imagens neste endereço público)
    if (ROOT / "livros-extra" / "redes").exists():
        shutil.copytree(ROOT / "livros-extra" / "redes", OUT / "redes", dirs_exist_ok=True)
    pg = OUT / "jesus-tora"; pg.mkdir(exist_ok=True)
    shutil.copy(ROOT / "livros-extra" / "jesus-tora.html", pg / "index.html")
    d = OUT / "livros"; d.mkdir(exist_ok=True)
    im = Image.open(TORA_CAPA_SRC).convert("RGB")
    im.thumbnail((800, 1400), Image.LANCZOS)
    im.save(d / "capa-jesus-tora.jpg", quality=84, optimize=True, progressive=True)

# Menu para celular (o menu de cima só aparecia em telas largas).
# Usa <details>, que abre e fecha sem precisar de código extra; as regras de CSS vão no fim do CSS do site.
MENU_LINKS = [("Livros", "/#livros"), ("Gestão Pastoral", "/gestao-pastoral"), ("Jesus e a Torá", "/jesus-tora"),
              ("O Essencial", "/o-essencial"), ("Ferramentas", "/ferramentas"), ("Sobre o autor", "/#autor")]
MENU_CSS = """
/* menu celular */
.mm{display:block}.mm>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:6px;border:1px solid #17346733;border-radius:999px;padding:8px 14px;color:#173467;font-weight:600;font-size:14px;background:#fff}
.mm>summary::-webkit-details-marker{display:none}.mm[open]>summary{background:#173467;color:#fff}
.mm>nav{position:absolute;left:0;right:0;top:100%;background:#fffdf8;border-bottom:1px solid #0f172a1a;box-shadow:0 18px 30px #0f172a1f;padding:8px 20px 16px;display:grid}
.mm>nav a{padding:13px 4px;border-bottom:1px solid #0f172a0f;color:#334155;font-size:16px;font-weight:500}
.mm>nav a:last-child{border-bottom:0}.mm>nav a:hover{color:#173467}
@media (min-width:768px){.mm{display:none}}
@media (max-width:767px){.vl{display:none!important}}
"""

def menu_celular():
    links = ",".join('b.jsx("a",{href:' + _js(h) + ',children:' + _js(n) + '})' for n, h in MENU_LINKS)
    icone = ('b.jsx("svg",{width:18,height:18,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,'
             '"aria-hidden":"true",children:b.jsx("path",{d:"M4 6h16M4 12h16M4 18h16"})})')
    menu = ('b.jsxs("details",{className:"mm",children:[b.jsxs("summary",{"aria-label":"Abrir menu",children:[' + icone +
            ',"Menu"]}),b.jsx("nav",{"aria-label":"Menu",onClick:e=>{const d=e.currentTarget.closest("details");d&&d.removeAttribute("open")},children:[' +
            links + ']})]})')
    for js in (OUT / "assets").glob("index-*.js"):
        t = js.read_text(encoding="utf-8")
        for antigo, novo in [
            ('SiteHeader.tsx:19",href:"/#livros",className:"inline-flex', 'SiteHeader.tsx:19",href:"/#livros",className:"vl inline-flex'),
            ('"Ver livros"]})]})})}', '"Ver livros"]}),' + menu + ']})})}'),
        ]:
            assert t.count(antigo) == 1, antigo
            t = t.replace(antigo, novo)
        js.write_text(t, encoding="utf-8")
    for css in (OUT / "assets").glob("index-*.css"):
        css.write_text(css.read_text(encoding="utf-8") + MENU_CSS, encoding="utf-8")

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    optimize_images()
    atualizar_preco()
    adicionar_livro_tora()
    menu_celular()
    write_tools_access()
    write_privacidade()
    # Verificação do Google Search Console (propriedade https://livrosquetransformam.pcgdigital.com.br/); não remover.
    (OUT / "google345f10a5f59b8a6b.html").write_text("google-site-verification: google345f10a5f59b8a6b.html")
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
    sm.append(f'  <url><loc>{SITE}/jesus-tora</loc><priority>0.9</priority></url>')
    sm.append(f'  <url><loc>{SITE}/privacidade/</loc><priority>0.2</priority></url>')
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /relatorio-financeiro\n{"" if TOOLS_LIVE else "Disallow: /ferramentas" + chr(10)}\nSitemap: {SITE}/sitemap.xml\n", encoding="utf8")
    print("ok:", sum(1 for _ in OUT.rglob("*") if _.is_file()), "arquivos em", OUT)

main()
