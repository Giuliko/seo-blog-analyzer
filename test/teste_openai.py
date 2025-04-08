import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """
Avalie o seguinte conteúdo de blog com base nas boas práticas de SEO.
Considere os critérios: uso de palavras-chave no título, headings, meta description, links internos/externos, tamanho e legibilidade do texto.
Retorne um dicionário JSON com:

- "nota_seo": um número float entre 0 e 10 (não use porcentagem)
- "explicacao": um parágrafo com os pontos fortes e fracos

Conteúdo:
Título: Como economizar dinheiro em 2024
Subtítulos: ['Dicas práticas', 'Erros comuns', 'Ferramentas úteis']
Texto: Economizar dinheiro pode parecer difícil, mas com disciplina e planejamento é totalmente possível. Neste artigo, vamos explorar estratégias práticas que ajudam a melhorar sua saúde financeira mesmo em tempos desafiadores...
"""

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    content = response.choices[0].message.content
    print("[DEBUG] Conteúdo da OpenAI:")
    print(content)

    # Tenta converter para JSON
    result = json.loads(content)
    print("\n✅ JSON válido:")
    print(result)

except Exception as e:
    print(f"\n❌ Erro: {e}")
