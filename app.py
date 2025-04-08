import streamlit as st
import subprocess
import glob
import json
from pathlib import Path

st.set_page_config(page_title="🔍 Analisador de Blog", layout="centered")
st.title("🔍 Analisador de Artigos de Blog")
st.write("Insira a URL e aguarde a análise completa (conteúdo + SEO).")

url = st.text_input("URL do artigo")

if st.button("Analisar artigo"):
    if not url.startswith("http"):
        st.warning("Insira uma URL válida começando com http ou https.")
    else:
        # 1. Salva a URL
        with open("input_url.txt", "w") as f:
            f.write(url)
        st.info("📡 Iniciando análise com navegador visível...")

        # 2. Executa o main.py automaticamente
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)

        if result.returncode == 0:
            st.success("✅ Análise concluída com sucesso!")

            # 3. Pega o resultado mais recente
            arquivos = sorted(glob.glob("output_files/resultado_*.json"), reverse=True)
            if arquivos:
                with open(arquivos[0], "r", encoding="utf-8") as f:
                    resultado = json.load(f)

                st.subheader("📄 Resultado da Análise")
                st.markdown(f"**Título:** {resultado['titulo']}")
                st.markdown("**Subtítulos:**")
                for subtitulo in resultado["subtitulos"]:
                    st.markdown(f"- {subtitulo}")
                st.markdown("**Trecho:**")
                st.text(resultado["texto"][:1000] + "..." if len(resultado["texto"]) > 1000 else resultado["texto"])

                # 4. Botão para baixar o JSON
                with open(arquivos[0], "rb") as f:
                    st.download_button("📥 Baixar resultado JSON", f, file_name=Path(arquivos[0]).name)
            else:
                st.warning("Não foi possível encontrar o resultado.")
        else:
            st.error("❌ Ocorreu um erro ao executar o main.py:")
            st.code(result.stderr)
