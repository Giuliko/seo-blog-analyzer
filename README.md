# 🧠 XP Blog Scraper + SEO Evaluator

Este projeto automatiza a busca, extração e análise de artigos do blog da **XP Investimentos**, avaliando seu conteúdo com base em critérios de **SEO** e gerando sugestões de melhorias.

---

## 📌 O que este projeto faz?

1. **Busca no Google** os artigos mais recentes do blog da XP.
2. **Extrai o conteúdo completo** dos artigos com Playwright.
3. **Avalia a qualidade SEO** de cada artigo usando agentes inteligentes.
4. **Sugere 3 melhorias práticas** para cada post.
5. **Exporta os resultados** em um arquivo `.json` com timestamp.

---

## 🚀 Como executar

### 1. Clone o repositório

git clone https://github.com/seu-usuario/xp_blog_scraper.git
cd xp_blog_scraper

### 2. Crie o ambiente virtual e instale dependências
Usando uv:

uv venv .venv
.venv\Scripts\Activate.ps1   # No Windows
uv pip install -r requirements.txt

Ou com pip tradicional:

python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.\.venv\Scripts\activate       # Windows
pip install -r requirements.txt

### 3. Crie um arquivo .env com suas chaves:

OPENAI_API_KEY=sk-...
SERPER_API_KEY=...

### 4. Rode o projeto

python xp_blog_scraper.py

🛠️ Tecnologias usadas
Crew AI – Para orquestrar agentes autônomos

Playwright – Para scraping moderno

OpenAI API – Para avaliação e sugestões via LLM

Serper.dev – Para realizar buscas no Google

pandas, dotenv, json, re – Utilitários de dados e ambiente

### 📂 Outputs
Os resultados são salvos automaticamente na pasta:

output_files/
  └── avaliacoes_seo_completas_YYYYMMDD_HHMMSS.json

Cada entrada contém:

✅ Título do artigo

🔗 Link

🧠 Nota SEO

📝 Explicação da avaliação

💡 Sugestões de melhoria

### 🧪 Exemplo de retorno

{
  "titulo_blog": "Como investir em renda fixa com a XP",
  "link": "https://conteudos.xpi.com.br/renda-fixa/artigo-exemplo",
  "nota_seo": 7.8,
  "explicacao": "O artigo está bem estruturado, mas falta meta description e links internos.",
  "sugestoes": [
    "Adicione uma meta description clara com a palavra-chave.",
    "Inclua links internos para outros artigos relacionados.",
    "Use mais headings para segmentar o conteúdo."
  ]
}

### 🤖 Sobre os Agentes
Este projeto utiliza múltiplos agentes coordenados por uma Crew para:

Buscar artigos

Avaliar SEO

Sugerir melhorias

Cada agente possui um objetivo claro e funciona de forma sequencial e especializada.

### 📌 Requisitos mínimos
Python 3.10+

Conta na OpenAI

Conta na Serper.dev

Chromium instalado (Playwright cuidará disso no primeiro uso)

### 📬 Contribuições
Pull requests são bem-vindos! Para mudanças maiores, por favor abra uma issue antes.

🧠 Autor
Criado por Emanoel Almeida — conectando scraping, LLMs e SEO.

