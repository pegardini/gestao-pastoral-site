# Gestão Pastoral

Código-fonte e snapshot de produção do site **Gestão Pastoral — Recursos Complementares**, originalmente publicado em `https://gestaopastor-agryx2qg.manus.space/` e associado ao domínio `livrosquetransformam.pcgdigital.com.br`.

## Conteúdo do repositório

A pasta `client/` contém uma camada React/Vite editável, organizada por páginas e componentes, com a identidade visual, rotas, textos públicos, ferramentas pastorais locais e imagens públicas do site. A pasta `recovered-deployment/` preserva os artefatos exatos servidos pelo deployment consultado: HTML, bundle JavaScript, CSS, manifesto PWA e imagens públicas. Essa cópia permite comparar a versão recuperada com a camada-fonte editável e mantém o comportamento publicado mesmo quando o projeto for entregue a outro profissional.

O deployment público não expôs os arquivos TypeScript originais nem source maps. Por isso, os caminhos originais identificados no bundle (por exemplo, `client/src/pages/Home.tsx`, `client/src/pages/Ferramentas.tsx` e `client/src/components/SiteHeader.tsx`) foram usados para organizar a recuperação editável, enquanto o bundle original foi preservado integralmente no snapshot.

## Desenvolvimento local

Requer Node.js 22+ e pnpm.

| Objetivo | Comando |
|---|---|
| Instalar dependências | `pnpm install` |
| Verificar tipos | `pnpm check` |
| Gerar build React | `pnpm build` |
| Executar desenvolvimento | `pnpm dev` |
| Visualizar a versão compilada | `pnpm preview` |

O build editável é gerado em `dist/`. Para servir exatamente o snapshot publicado, use um servidor estático apontando para `recovered-deployment/`.

## Rotas

A aplicação recuperada contempla `/`, `/gestao-pastoral`, `/o-essencial`, `/o-essencial/primeiro-capitulo`, `/leia-o-primeiro-capitulo`, `/ferramentas` e `/relatorio-financeiro`.

## Segurança da publicação

Este repositório é privado. Não foram copiados arquivos `.env`, credenciais, tokens, chaves, conexões de banco, configurações locais do Manus ou dados pessoais de usuários. As imagens presentes são os três recursos públicos já utilizados pela página publicada: as duas capas e o retrato público do autor.
