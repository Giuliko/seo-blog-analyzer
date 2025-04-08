# 🔍 SEO Blog Analyzer

Este projeto permite que qualquer usuário analise um artigo de blog **com apenas uma URL**, avaliando:

- ✅ **Conteúdo extraído automaticamente**
- 📈 **Nota de SEO de 0 a 10 com explicação**
- 🛠️ **3 sugestões práticas para melhorar o SEO**
- 🚀 **Métricas técnicas do PageSpeed (Core Web Vitals, Performance, SEO, Acessibilidade e mais)**

---

## 📸 Interface

![Preview](output_files/erro_debug.png) <!-- Opcional: use uma imagem real do app -->

---

## 🚀 Como usar

1. **Clone o repositório:**

git clone https://github.com/Giuliko/seo-blog-analyzer.git
cd seo-blog-analyzer

2. **Crie um ambiente virtual (opcional):**

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

3. **Instale as dependências:**

pip install -r requirements.txt

4. **Configure o arquivo .env:**

OPENAI_API_KEY=sua-chave-da-openai
GOOGLE_PAGESPEED_API_KEY=sua-chave-do-pagespeed

5. **Execute a aplicação Streamlit:**

streamlit run app.py

🧠 Tecnologias utilizadas:

. OpenAI GPT-4o — para análise de SEO e sugestões
. Playwright — para scraping avançado, mesmo em páginas protegidas
. PageSpeed API — métricas técnicas de performance
. Streamlit — interface amigável para o usuário

📁 Estrutura de saída
- Após a análise, o app gera um arquivo JSON em output_files/ com a seguinte estrutura:

{
  "titulo": "Título do artigo",
  "subtitulos": ["Sub 1", "Sub 2"],
  "texto": "Trecho do conteúdo extraído...",
  "nota_seo": 7.8,
  "explicacao": "Texto explicando os critérios de avaliação",
  "sugestoes": ["Sugestão 1", "Sugestão 2", "Sugestão 3"],
  "page_speed": {
    "core_web_vitals": {...},
    "performance": {...},
    "accessibility": 91,
    "best_practices": 100,
    "seo": 92
  }
}

📬 Contribuições
Sinta-se à vontade para abrir issues, contribuir com melhorias ou sugestões!
Este projeto foi desenvolvido por @Giuliko com ❤️ e muito scraping.

🛡️ Licença
Este projeto está licenciado sob a MIT License.
