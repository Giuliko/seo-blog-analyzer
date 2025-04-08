from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import os
import json
import pandas as pd
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from datetime import datetime
import requests

load_dotenv()

# === CONFIG ===
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')

# === AGENTES ===
search_tool = SerperDevTool()

google_agent = Agent(
    role="Pesquisador de Artigos XP",
    goal="Buscar no Google os links dos artigos recentes do blog da XP investimentos",
    backstory="Você é um especialista em encontrar conteúdos de blog usando comandos de busca avançada no Google.",
    tools=[search_tool],
    verbose=True
)

# === TASK DE BUSCA NO GOOGLE ===
search_task = Task(
    description="Use uma busca no Google para encontrar os 10 links mais recentes de artigos do blog da XP Investimentos (https://conteudos.xpi.com.br)",
    expected_output="Uma lista com pelo menos 10 links válidos de artigos.",
    agent=google_agent
)

crew_busca = Crew(
    agents=[google_agent],
    tasks=[search_task],
    process=Process.sequential
)

print("Buscando links...")
resultado_busca = crew_busca.kickoff()  # CrewOutput object
resultado_busca_str = str(resultado_busca)

# === TRANSFORMAR O TEXTO DE LINKS EM LISTA ===
import re
lista_links = re.findall(r"https://conteudos\.xpi\.com\.br[\w\-/]+", resultado_busca_str)

print("Links encontrados:")
print(lista_links)

# === SCRAPER COM PLAYWRIGHT ===
def extrair_conteudo_xp_blog(url): 
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            timezone_id="America/Sao_Paulo",
            locale="pt-BR",
        )

        page = context.new_page()
        page.goto(url, timeout=60000)

        # Screenshot para debug
        page.screenshot(path="pagina_xp_stealth.png", full_page=True)

        try:
            page.wait_for_selector('article', timeout=15000)
        except:
            print(f"'article' ainda não encontrado em {url}")

        titulo = page.locator('h1').first.text_content() or ""
        subtitulos = page.locator('h2, h3').all_text_contents()
        paragrafos = page.locator('p').all_text_contents()
        texto = "\n\n".join(paragrafos)

        browser.close()

        return {
            'link': url,
            'titulo': titulo.strip(),
            'subtitulos': [s.strip() for s in subtitulos],
            'texto': texto.strip()
        }
    
def consultar_pagespeed_api(url):
    api_key = os.getenv("GOOGLE_PAGESPEED_API_KEY")
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    params = {
        "url": url,
        "key": api_key,
        "strategy": "desktop",
        "category": ["performance", "accessibility", "best-practices", "seo"]
    }

    try:
        response = requests.get(api_url, params=params, timeout=60)
        data = response.json()

        if "lighthouseResult" not in data:
            print(f"[AVISO] Nenhum dado encontrado para {url}")
            return {}

        lighthouse = data["lighthouseResult"]
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        # Fallback de valor
        def safe_get(d, key):
            return d.get(key, {}).get("displayValue", "N/A")

        def safe_score(cat):
            score = categories.get(cat, {}).get("score")
            return round(score * 100) if score is not None else "N/A"

        resultado = {
            "core_web_vitals": {
                "LCP": safe_get(audits, "largest-contentful-paint"),
                "INP": safe_get(audits, "interaction-to-next-paint"),
                "CLS": safe_get(audits, "cumulative-layout-shift"),
                "FCP": safe_get(audits, "first-contentful-paint"),
                "TTFB": safe_get(audits, "server-response-time"),
            },
            "performance": {
                "FCP": safe_get(audits, "first-contentful-paint"),
                "TotalBlockingTime": safe_get(audits, "total-blocking-time"),
                "SpeedIndex": safe_get(audits, "speed-index"),
                "LCP": safe_get(audits, "largest-contentful-paint"),
                "CLS": safe_get(audits, "cumulative-layout-shift"),
            },
            "accessibility": safe_score("accessibility"),
            "best_practices": safe_score("best-practices"),
            "seo": safe_score("seo")
        }

        return resultado

    except Exception as e:
        print(f"[ERRO] Falha ao consultar PageSpeed para {url}: {e}")
        return {}

# === EXTRAIR CONTEÚDOS ===
print("Extraindo conteúdos com Playwright...")
artigos = []
for link in lista_links:
    try:
        artigo = extrair_conteudo_xp_blog(link)
        artigos.append(artigo)
    except Exception as e:
        print(f"Erro ao processar {link}: {e}")

# === RODAR AVALIAÇÃO SEO E MELHORIAS ===
print("Avaliando SEO e gerando melhorias...")

seo_agent = Agent(
    role="Analista de SEO",
    goal="Avaliar o conteúdo de artigos do blog com base em critérios de SEO e atribuir uma nota",
    backstory="Você é um especialista em SEO que identifica pontos fortes e fracos em conteúdos de blog.",
    verbose=True
)

improvement_agent = Agent(
    role="Especialista em Melhorias de SEO",
    goal="Sugerir três melhorias práticas de SEO para o conteúdo do artigo analisado",
    backstory="Você é um consultor experiente em SEO focado em sugerir mudanças diretas que aumentem o ranqueamento dos conteúdos.",
    verbose=True
)

resultados = []

for artigo in artigos:
    conteudo_str = {
        "titulo": artigo["titulo"],
        "subtitulos": artigo["subtitulos"],
        "texto": artigo["texto"]
    }

    # Criar nova Crew por artigo
    seo_task = Task(
        description=(
            "Avalie o conteúdo a seguir com base nas boas práticas de SEO, considerando: "
            "palavra-chave no título, uso de headings, meta description, tamanho do texto, links internos/externos, legibilidade..."
            "Conteúdo: {conteudo_str}"
        ),
        expected_output="""
            Um dicionário com as chaves:
            - "nota_seo": um número entre 0 e 10 (float)
            - "explicacao": um texto explicando os critérios bons e ruins do conteúdo.

            Exemplo:
            {
            "nota_seo": 6.5,
            "explicacao": "O conteúdo tem bom uso de heading tags, mas falta uma meta description e links internos."
            }
        """,
        agent=seo_agent
    )

    # Criar nova Crew por artigo para nota de SEO - ADICIONADA
    crew_seo = Crew(
        agents=[seo_agent], 
        tasks=[seo_task], 
        process=Process.sequential
        )

    resultado_seo = crew_seo.kickoff()

    improvement_task = Task(
        description=(
            "Com base nas avaliações de SEO realizadas, gere 3 sugestões práticas para melhorar o artigo."
        ),
        expected_output="Lista de 3 sugestões claras e aplicáveis.",
        agent=improvement_agent
    )

    crew_improvement = Crew(
        agents=[improvement_agent], 
        tasks=[improvement_task], 
        process=Process.sequential
        )

    sugestoes = crew_improvement.kickoff()

    # Extração de métricas técnicas com PageSpeed
    print(f"Analisando PageSpeed para: {artigo['link']}")
    metricas_pagespeed = consultar_pagespeed_api(artigo["link"])

    try:
        seo_dict = json.loads(resultado_seo.raw) if hasattr(resultado_seo, "raw") else json.loads(str(resultado_seo))
    except:
        seo_dict = {"nota_seo": None, "explicacao": str(resultado_seo)}

    # Extrair sugestões
    sugestoes_texto = sugestoes.raw if hasattr(sugestoes, "raw") else str(sugestoes)

    resultados.append({
        "titulo_blog": artigo["titulo"],
        "link": artigo["link"],
        "nota_seo": seo_dict.get("nota_seo"),
        "explicacao": seo_dict.get("explicacao"),
        "sugestoes": sugestoes_texto,
        "page_speed": metricas_pagespeed
    })

# Garante que a pasta 'output_files' exista
os.makedirs("output_files", exist_ok=True)

# Gera timestamp no formato YYYYMMDD_HHMMSS
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Define o nome do arquivo com timestamp
file_name = f"avaliacoes_seo_completas_{timestamp}.json"
file_path = os.path.join("output_files", file_name)

df = pd.DataFrame(resultados)
df.to_json(file_path, orient="records", indent=2, force_ascii=False)

print(f"Processo finalizado. Resultados salvos em {file_path}")
