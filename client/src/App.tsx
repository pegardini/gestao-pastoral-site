import { Link, Route, Switch } from "wouter";
import { ArrowRight, BookOpen, Mail, UserRound, Wrench } from "lucide-react";
import { useState } from "react";
import { Chapter1 } from "./pages/Chapter1";
import { Ferramentas } from "./pages/Ferramentas";
import { GestaoPastoral } from "./pages/GestaoPastoral";
import { Home } from "./pages/Home";
import { OEssencial } from "./pages/OEssencial";
import { RelatorioFinanceiro } from "./pages/RelatorioFinanceiro";

export const CLUB_URL = "https://clubedeautores.com.br/cart";
export const AMAZON_URL = "https://www.amazon.com.br/s?k=Gest%C3%A3o+Pastoral+Pedro+de+Celso+Gardini";
export const ASSETS = {
  gestao: "/manus-storage/capa-gestao-pastoral_4021fa04.jpg",
  essencial: "/manus-storage/capa_essencial_rosa_serena_subtitulo_reforcado_9fd5d091.png",
  autor: "/manus-storage/retrato_pe_pedro_limpo_535a3d64.png",
};

export function Header() {
  const [open, setOpen] = useState(false);
  return <header className="print-hidden" style={{ position: "sticky", top: 0, zIndex: 10, background: "rgba(255,253,248,.94)", backdropFilter: "blur(14px)", borderBottom: "1px solid #e2e8f0" }}>
    <div className="container" style={{ minHeight: 68, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 20 }}>
      <Link href="/" className="font-serif" style={{ color: "#173467", fontWeight: 700, fontSize: "1.1rem" }}>▣ Pe. Pedro de Celso Gardini</Link>
      <button aria-label="Abrir menu" onClick={() => setOpen(!open)} style={{ display: "none", border: 0, background: "transparent", color: "#173467", fontSize: 24 }}>☰</button>
      <nav style={{ display: "flex", alignItems: "center", gap: 22, fontSize: 14, color: "#475569" }}>
        <Link href="/#livros">Livros</Link><Link href="/gestao-pastoral">Gestão Pastoral</Link><Link href="/o-essencial">O Essencial</Link><Link href="/ferramentas">Ferramentas</Link><Link href="/#autor">Sobre o autor</Link>
        <Link href="/#livros" style={{ background: "#173467", color: "white", padding: "10px 16px", borderRadius: 999, fontWeight: 600 }}>Ver livros</Link>
      </nav>
    </div>
    {open && <nav className="container" style={{ paddingBottom: 16, display: "grid", gap: 10 }}><Link href="/#livros">Livros</Link><Link href="/gestao-pastoral">Gestão Pastoral</Link><Link href="/o-essencial">O Essencial</Link><Link href="/ferramentas">Ferramentas</Link></nav>}
  </header>;
}

export function Footer() { return <footer style={{ background: "#fffaf4", borderTop: "1px solid #f1e5d8", padding: "38px 0", color: "#64748b" }}><div className="container" style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: 24 }}><div><p className="font-serif" style={{ color: "#173467", fontWeight: 700, margin: 0 }}>Pe. Pedro de Celso Gardini</p><p style={{ marginBottom: 0 }}>Livros para servir, organizar e acolher.</p></div><div style={{ display: "flex", gap: 15 }}><a href="mailto:contato.livrogestao@gmail.com" aria-label="E-mail"><Mail size={18}/></a><a href="https://instagram.com/pegardini" aria-label="Instagram">Instagram</a><a href="https://youtube.com/@pedrogardini" aria-label="YouTube">YouTube</a><a href="https://linkedin.com/in/pedro-de-celso-gardini-ba8baa22" aria-label="LinkedIn">LinkedIn</a></div></div></footer>; }

export function BookCallout() { return <aside className="print-hidden" style={{ border: "1px solid #f1d7a3", background: "#fff8e8", borderRadius: 14, padding: 12, display: "flex", gap: 12, alignItems: "center" }}><img src={ASSETS.gestao} alt="Capa do livro Gestão Pastoral" style={{ width: 36, height: 56, objectFit: "cover", borderRadius: 5 }} /><div style={{ flex: 1 }}><small style={{ color: "#92400e", fontWeight: 700, textTransform: "uppercase" }}>Livro impresso · pré-venda</small><div className="font-serif" style={{ color: "#173467", fontWeight: 700 }}>Gestão Pastoral</div><small>Garanta na pré-venda por R$ 42,68.</small></div><a href={CLUB_URL} target="_blank" rel="noreferrer" style={{ background: "#173467", color: "white", padding: "8px 12px", borderRadius: 8, fontWeight: 600 }}>Garantir</a></aside>; }

export default function App() { return <Switch><Route path="/"><Home /></Route><Route path="/gestao-pastoral"><GestaoPastoral /></Route><Route path="/o-essencial"><OEssencial /></Route><Route path="/o-essencial/primeiro-capitulo"><Chapter1 /></Route><Route path="/leia-o-primeiro-capitulo"><Chapter1 /></Route><Route path="/ferramentas"><Ferramentas /></Route><Route path="/relatorio-financeiro"><RelatorioFinanceiro /></Route><Route><div className="container" style={{ padding: "100px 0" }}><h1>404</h1><Link href="/">Voltar ao início</Link></div></Route></Switch>; }

export { ArrowRight, BookOpen, UserRound, Wrench };
