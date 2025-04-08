import json
import requests
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")

def extrair_conteudo_site(url): 

    with sync_playwright() as p:
        print("[DEBUG] Iniciando Playwright")
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

        try:
            print("[DEBUG] Acessando URL...")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")

            print("[DEBUG] Esperando seletor...")
            page.wait_for_selector('article, h1, p', timeout=15000)

            print("[DEBUG] Tirando screenshot...")
            page.screenshot(path="erro_debug.png", full_page=True)

            print("[DEBUG] Extraindo título...")
            titulo = page.locator('h1').first.text_content() or ""

            print("[DEBUG] Extraindo subtítulos...")
            subtitulos = page.locator('h2, h3').all_text_contents()

            print("[DEBUG] Extraindo parágrafos...")
            paragrafos = page.locator('p').all_text_contents()
            texto = "\n\n".join(paragrafos)

            print("[DEBUG] Finalizando extração")
            return {
                'link': url,
                'titulo': titulo.strip(),
                'subtitulos': [s.strip() for s in subtitulos if s.strip()],
                'texto': texto.strip()
            }

        except Exception as e:
            print(f"[ERRO AO EXECUTAR] {e}")
            page.screenshot(path="erro_debug.png", full_page=True)
            raise Exception("Falha ao extrair conteúdo. Verifique o console e o screenshot.")

        finally:
            browser.close()

def consultar_pagespeed_api(url):
    try:
        api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "key": PAGESPEED_API_KEY,
            "strategy": "desktop",
            "category": ["performance", "accessibility", "best-practices", "seo"]
        }

        response = requests.get(api_url, params=params, timeout=60)
        data = response.json()

        if "lighthouseResult" not in data:
            print(f"[AVISO] Nenhum dado encontrado para {url}")
            return {}

        lighthouse = data["lighthouseResult"]
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        def safe_get(d, key):
            return d.get(key, {}).get("displayValue", "N/A")

        def safe_score(cat):
            score = categories.get(cat, {}).get("score")
            return round(score * 100) if score is not None else "N/A"

        return {
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

    except Exception as e:
        print(f"[ERRO] Falha ao consultar PageSpeed para {url}: {e}")
        return {}

if __name__ == "__main__":

    input_path = Path("input_url.txt")

    if not input_path.exists():
        print("❌ Nenhuma URL encontrada no arquivo input_url.txt.")
        exit(1)

    with open(input_path, "r") as f:
        url = f.read().strip()

    try:
        resultado = extrair_conteudo_site(url)

        print("[DEBUG] Avaliando SEO com GPT-4o...")

        prompt_seo = f"""
Avalie o seguinte conteúdo de blog com base nas boas práticas de SEO. 
Considere os critérios: uso de palavras-chave no título, headings, meta description, links internos/externos, tamanho e legibilidade do texto. 
Retorne um dicionário JSON com:

- "nota_seo": um número float entre 0 e 10 (não use porcentagem)
- "explicacao": um parágrafo com os pontos fortes e fracos
- "sugestoes": uma lista com 3 sugestões práticas e aplicáveis de melhorias SEO

Conteúdo:
Título: {resultado["titulo"]}
Subtítulos: {resultado["subtitulos"]}
Texto: {resultado["texto"][:3000]}...
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt_seo}],
                temperature=0.4
            )

            raw_response = response.choices[0].message.content
            print("[DEBUG] Conteúdo retornado pelo GPT-4o:")
            print(raw_response)

            # Remove blocos de markdown (```json ... ```)
            cleaned_response = re.sub(r"```json|```", "", raw_response).strip()

            # Tenta carregar como JSON
            seo_analysis = json.loads(cleaned_response)

            resultado["nota_seo"] = seo_analysis.get("nota_seo")
            resultado["explicacao"] = seo_analysis.get("explicacao")
            resultado["sugestoes"] = seo_analysis.get("sugestoes")

            print("[DEBUG] Análise de SEO concluída")

        except Exception as e:
            print(f"[ERRO] Falha ao analisar SEO: {e}")
            resultado["nota_seo"] = None
            resultado["explicacao"] = "Erro durante a análise de SEO."
            resultado["sugestoes"] = []

        print("[DEBUG] Consultando métricas do PageSpeed...")
        resultado["page_speed"] = consultar_pagespeed_api(url)

        output_dir = Path("output_files")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"resultado_{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"Resultado salvo em: {output_path}")
        # Salva nome do último arquivo gerado para o app ler
        with open("last_result.txt", "w") as f:
            f.write(str(output_path))

    except Exception as e:
        print(f"Erro ao executar a análise: {e}")
        exit(1)

