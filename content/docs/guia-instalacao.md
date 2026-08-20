---
title: "Guia de Instalação e Ativação"
description: "Instruções completas para clonar, configurar e executar o projeto localmente com Hugo, Docker ou Dev Containers."
weight: 1
---

Este guia fornece o passo a passo completo para configurar o ambiente de desenvolvimento, instalar as dependências e executar o site localmente.

---

## Pré-requisitos

Antes de iniciar, certifique-se de ter as seguintes ferramentas instaladas em sua máquina:

| Ferramenta                  | Versão Recomendada            | Finalidade                                                |
| :-------------------------- | :---------------------------- | :-------------------------------------------------------- |
| **Git**                     | `2.x+`                        | Controle de versão e clonagem do repositório              |
| **Go (Golang)**             | `1.20+`                       | Gerenciamento de módulos Hugo (`hugo mod`)                |
| **Hugo Extended**           | `0.120+` (Extended)           | Gerador de site estático (requer suporte a CGO/SCSS)      |
| **Docker & Docker Compose** | _(Opcional)_ Versões recentes | Execução isolada em containers através do script auxiliar |

---

## 1. Clonando o Repositório

Abra o terminal e faça o clone do repositório em sua máquina:

```bash
# Clone o repositório
git clone https://github.com/joaopedro-chaves/joaopedro-chaves.github.io.git

# Acesse o diretório do projeto
cd joaopedro-chaves.github.io
```

---

## 2. Formas de Execução

Você pode executar o projeto de três maneiras diferentes, de acordo com sua preferência:

### Opção A: Execução Local Nativa (Recomendada)

Com o **Go** e o **Hugo Extended** instalados:

1. **Baixar e sincronizar os módulos do Hugo (tema Hextra):**

   ```bash
   hugo mod tidy
   ```

2. **Iniciar o servidor de desenvolvimento:**

   ```bash
   hugo server --logLevel debug --disableFastRender -p 8000
   ```

3. **Acessar o site:**
   Abra seu navegador em [http://localhost:8000](http://localhost:8000). Qualquer alteração nos arquivos Markdown ou no `hugo.yaml` atualizará a página automaticamente (_Live Reload_).

---

### Opção B: Utilizando o Script Auxiliar (`scripts/dev.sh`)

O projeto inclui um script automatizado em Bash para facilitar o gerenciamento do ambiente com Docker e criação de novos conteúdos:

1. **Conceda permissão de execução ao script (se necessário):**

   ```bash
   chmod +x scripts/dev.sh
   ```

2. **Comandos disponíveis:**
   - **Iniciar o ambiente:**
     ```bash
     ./scripts/dev.sh start
     ```
   - **Ver logs em tempo real:**
     ```bash
     ./scripts/dev.sh logs
     ```
   - **Reiniciar o ambiente:**
     ```bash
     ./scripts/dev.sh reload
     ```
   - **Parar o ambiente:**
     ```bash
     ./scripts/dev.sh stop
     ```
   - **Criar um novo post interativamente:**
     ```bash
     ./scripts/dev.sh new-post
     ```
   - **Exibir ajuda:**
     ```bash
     ./scripts/dev.sh help
     ```

---

### Opção C: VS Code Dev Containers & GitHub Codespaces

O repositório já conta com configuração pronta em `.devcontainer/`:

1. **VS Code Local:** Instale a extensão _Dev Containers_, abra a pasta do projeto e selecione a opção **"Reopen in Container"**.
2. **GitHub Codespaces:** Crie um Codespace diretamente no repositório do GitHub. O ambiente será provisionado com Go, Hugo Extended e extensões recomendadas automaticamente.

---

## 3. Estrutura de arquivos de conteúdos

```bash
content/
├── _index.md            # Página inicial (Landing Page)
├── docs/                # Seção de Documentação
│   ├── _index.md
│   ├── guia-instalacao.md
│   ├── arquitetura.md
│   ├── images/
│   │   └── img01.png # Imagens devem está na pasta /content/docs/images/ e ser referenciadas pelo caminho relativo
├── blog/                # Seção do Blog
│   ├── _index.md
│   ├── 2026
│   │   ├── 2026-09-01-titulo-do-post.md  # data e nome do post em formato slug
│   │   └── 2026-08-20-titulo-do-post.md
│   ├── images/
│   │   └── img01.png
└── projetos/            # Seção do Portfólio
    ├── _index.md
    └── projeto-1.md
    ├── images/
    │   └── img01.png
```

## 4. Criando Conteúdo

### Criando um Post no Blog

Você pode utilizar o script:

```bash
./scripts/dev.sh new-post
```

O assistente solicitará:

- **Título do post:** Ex.: `Meu Novo Artigo`
- **Descrição:** Breve resumo do conteúdo
- **Tags:** Ex.: `hugo, desenvolvimento, tutorial`

O arquivo será criado automaticamente em `content/blog/ANO/DATA-slug.md` com o frontmatter pré-configurado.

### Criando uma Nova Página de Documentação

Para criar uma nova documentação, basta adicionar um arquivo `.md` dentro de `content/docs/`:

```markdown
---
title: "Título da Sua Página"
description: "Descrição da página para SEO e buscas."
weight: 10
---

Escreva seu conteúdo em Markdown aqui...
```

### Criando uma Nova Página de Projetos

Para criar uma nova página de projetos, basta adicionar um arquivo `.md` dentro de `content/projects/`:

```markdown
---
title: "Título do Projeto"
description: "Descrição do projeto para SEO e buscas."
weight: 10
---

Escreva o conteúdo do seu projeto aqui em Markdown.
```

---

## 5. Atualização do Tema Hextra

Para atualizar o módulo do tema Hextra para a versão mais recente:

```bash
hugo mod get -u
hugo mod tidy
```

---

## 6. Resolução de Problemas (Troubleshooting)

### Erro: `hugo: command not found` ou versão sem suporte a SASS/SCSS

- **Causa:** O Hugo não está instalado ou você instalou a versão padrão em vez da versão **Extended**.
- **Solução:** Instale o pacote `hugo-extended` (via Homebrew no macOS: `brew install hugo`, ou baixando o binário `hugo_extended_*` do [GitHub Releases do Hugo](https://github.com/gohugoio/hugo/releases)).

### Erro com módulos Go (`go: not found` ou `hugo mod error`)

- **Causa:** O Hugo utiliza o Go para gerenciar temas via Hugo Modules.
- **Solução:** Instale o Go (`golang`) e certifique-se de que `go version` execute normalmente no terminal.

### Alterações não refletidas no navegador

- Execute com as flags `--disableFastRender` e `--ignoreCache`:
  ```bash
  hugo server --disableFastRender --ignoreCache
  ```

---

## 7. Publicando o Site

### GitHub Pages

Para publicar o site no GitHub Pages, basta fazer o push das alterações para a branch principal (`main`). O fluxo automatizado do GitHub Actions em `.github/workflows/pages.yaml` se encarregará do build e publicação.

- Documentação do GitHub Pages: [https://docs.github.com/en/pages/](https://docs.github.com/en/pages/)

---

## 8. Customização do Tema Hextra

O tema **Hextra** é altamente customizável através do arquivo de configuração `hugo.yaml`, de estilos CSS personalizados e de componentes visuais integrados (Shortcodes).

### 8.1. Configurações Globais (`hugo.yaml`)

Você pode personalizar o comportamento e o visual do tema editando as seguintes seções do `hugo.yaml`:

#### 🏷️ Título, Logo e Identidade

```yaml
title: "Meu Nome | DevHub"
baseURL: "https://joaopedro-chaves.github.io"

params:
  navbar:
    displayTitle: true # Exibir o título na barra de navegação
    displayLogo: true # Ativar exibição de logotipo
    logo:
      path: images/logo.svg # Caminho da imagem (dentro de static/ ou assets/)
      link: / # Destino do clique no logo
      width: 32
      height: 32
```

#### Modo Claro e Escuro (Dark/Light Mode)

```yaml
params:
  theme:
    default: "system" # Opções: "system" (padrão do SO), "light" ou "dark"
    displayToggle: true # Exibir o botão de alternar tema no menu
```

#### Menu de Navegação Superior (`menu.main`)

Adicione ou edite links, seções e ícones sociais na barra superior:

```yaml
menu:
  main:
    - name: Docs
      pageRef: /docs
      weight: 1
    - name: Blog
      pageRef: /blog
      weight: 2
    - name: Projetos
      pageRef: /projects
      weight: 3
    - name: Sobre
      pageRef: /about
      weight: 4
    - name: Busca
      weight: 5
      params:
        type: search # Barra de busca rápida integrada
    - name: GitHub
      weight: 6
      url: "https://github.com/seu-usuario"
      params:
        icon: github # Ícones suportados: github, x-twitter, linkedin, etc.
```

#### Rodapé e Edição no GitHub

```yaml
params:
  footer:
    displayCopyright: true
    displayPoweredBy: false # Oculta "Powered by Hextra" se desejar
    copyright: "© 2026 João Pedro Chaves. Todos os direitos reservados."

  editURL:
    enable: true
    base: "https://github.com/joaopedro-chaves/joaopedro-chaves.github.io/edit/main/content"
```

---

### 8.2. Estilos Personalizados (CSS / SCSS)

Para adicionar estilos próprios ou sobrescrever cores padrão do tema:

1. Crie o arquivo `assets/css/custom.css` no projeto.
2. Adicione suas regras CSS ou variáveis de cor:

```css
/* Exemplo: Customizar a cor de destaque principal */
:root {
  --primary-hue: 212deg; /* Matiz HSL para a cor principal */
}

/* Customizações adicionais */
.hextra-card {
  border-radius: 12px;
}
```

---

### 8.3. Componentes Visuais do Hextra (Shortcodes)

Você pode enriquecer a documentação e os artigos do blog usando os shortcodes nativos do Hextra:

#### Caixas de Destaque (Callouts)

```markdown
{{</* callout type="info" */>}}
Nota informativa para destacar um detalhe relevante.
{{</* /callout */>}}

{{</* callout type="warning" */>}}
Aviso importante sobre pré-requisitos ou versões.
{{</* /callout */>}}

{{</* callout type="error" */>}}
Mensagem de erro crítico ou incompatibilidade.
{{</* /callout */>}}
```

#### Cards de Navegação

```markdown
{{</* cards */>}}
  {{</* card link="/docs" title="Documentação" icon="book-open" subtitle="Guias técnicos e tutoriais" */>}}
  {{</* card link="/projects" title="Projetos" icon="code" subtitle="Portfólio de projetos" */>}}
{{</* /cards */>}}
```

#### Abas de Código (Tabs)

````markdown
{{</* tabs items='["Linux / macOS", "Windows (PowerShell)"]' */>}}
  {{</* tab */>}}
  ```bash
  ./scripts/dev.sh start
  ```
  {{</* /tab */>}}
  {{</* tab */>}}
  ```powershell
  hugo server -p 8000
  ```
  {{</* /tab */>}}
{{</* /tabs */>}}
````

#### Caixa de navegação com imagens (Cards com Imagem)

```markdown
{{</* cards */>}}
  {{</* card link="/docs" title="Guia de Instalação" image="/images/exemplo.png" subtitle="Breve descrição opcional" */>}}
  {{</* card link="https://github.com" title="Link Externo" image="https://placeholder.com" */>}}
{{</* /cards */>}}
```

