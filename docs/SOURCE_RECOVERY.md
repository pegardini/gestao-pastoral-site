# Nota de recuperação do código-fonte

A recuperação foi feita a partir do deployment público informado pelo proprietário do site. O HTML publicado apontou para um bundle Vite de produção e para uma folha CSS; o bundle não continha `sourceMappingURL`, e a rota convencional do source map retornou apenas o shell HTML. Em consequência, não foi possível obter por HTTP os arquivos TypeScript originais do projeto WebDev.

O bundle, entretanto, preservou metadados `data-loc` com os caminhos dos arquivos de origem. Esses metadados identificaram as páginas `Home.tsx`, `GestaoPastoral.tsx`, `OEssencial.tsx`, `OEssencialAperitivo.tsx`, `Chapter1.tsx`, `Ferramentas.tsx`, `RelatorioFinanceiro.tsx` e componentes como `SiteHeader.tsx`, `SiteFooter.tsx`, `BookPurchaseCallout.tsx` e `ToolsAccessGate.tsx`.

O diretório `recovered-deployment/` é a cópia byte a byte dos artefatos públicos necessários à execução da versão publicada, incluindo os nomes originais dos bundles e as três imagens públicas. O diretório `client/` é a camada React editável recuperada, organizada com base nos textos, rotas, estilos, imagens e interações observáveis no bundle. A separação evita apresentar um artefato compilado como se fosse o fonte original e oferece ao próximo profissional tanto a versão publicada quanto uma base de manutenção legível.
