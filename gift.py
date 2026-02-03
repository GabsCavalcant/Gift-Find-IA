import streamlit as st
from google import genai
from google.genai import types 
import json
import urllib.parse 

# --- MINHAS ANOTAÇÕES ---
# Esse app usa a library nova 'google-genai' (2026) porque a antiga foi depreciada.
# O objetivo é usar o Gemini 2.0 Flash com a tool de Google Search ativada.

# 1. Configuração Visual
st.set_page_config(page_title="Gift Finder AI", page_icon="🎁")

# 2. Sidebar (Segurança)
with st.sidebar:
    st.header("Configuração")
    # Lembrete: Nunca deixar a API Key fixa no código (hardcoded) pra não vazar no Git!
    api_key = st.text_input("Insira sua API Key do Google:", type="password")
    st.markdown("[Link pra pegar a chave](https://aistudio.google.com/app/apikey)")

# 3. O "Cérebro" do App
def buscar_presentes(chave, gosto, orcamento):
    # Conectando com a API usando a chave que o usuário passou
    client = genai.Client(api_key=chave)
    
    # Configurando a ferramenta de busca nativa (Grounding)
    # Isso é o que faz ele buscar preços reais e não alucinar valores
    ferramenta = types.Tool(
        google_search=types.GoogleSearch()
    )

    # Prompt tunado para retornar JSON. 
    # Se mudar isso aqui, pode quebrar o json.loads lá embaixo.
    prompt = f"""
    Aja como um personal shopper.
    Use a BUSCA DO GOOGLE para encontrar 4 opções de presentes REAIS vendidos no Brasil.
    Perfil: {gosto}.
    Orçamento Máximo: R$ {orcamento}.
    
    Regra: Retorne APENAS um JSON puro (sem markdown) neste formato:
    [
        {{ "nome": "Nome Produto", "preco": 0.0, "motivo": "Explicação curta" }}
    ]
    """
    
    try:
        # Chamando o Gemini 2.50 Flash (mais rápido e barato que o Pro)
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[ferramenta],
                temperature=0.9 # Deixei alto pra ele ser criativo nas ideias
            )
        )
        
        # Limpeza da resposta (Gambiarra necessária)
        # Às vezes a IA manda ```json no começo, preciso remover pra não dar erro
        texto = response.text.replace("```json", "").replace("```", "").strip()
        
        # Garante que pegamos só o array [] caso venha texto extra
        inicio = texto.find('[')
        fim = texto.rfind(']') + 1
        if inicio != -1:
            texto = texto[inicio:fim]

        return json.loads(texto)

    except Exception as e:
        # Se der erro (ex: chave inválida), mostro na tela pra facilitar o debug
        st.error(f"Deu ruim na conexão: {e}")
        return []

# 4. Interface do Usuário (Frontend)
st.title("🎁 Gift Finder AI")
st.write("Projeto de estudo: Buscador de presentes com IA e preços reais.")

# Usei colunas pra ficar lado a lado (mais bonito)
col1, col2 = st.columns(2)
with col1:
    gosto_usuario = st.text_input("Do que a pessoa gosta?", placeholder="Ex: Gamer, Churrasco, Harry Potter")
with col2:
    orcamento_usuario = st.number_input("Orçamento (R$)", min_value=10.0, value=200.0)

# Botão de ação
if st.button("🔍 Pesquisar Presentes"):
    # Validações básicas antes de gastar cota da API
    if not api_key:
        st.warning("Eita, esqueceu a chave API na barra lateral!")
    elif not gosto_usuario:
        st.warning("Preciso saber do que a pessoa gosta...")
    else:
        # Spinner pra dar feedback visual enquanto carrega
        with st.spinner(f"Perguntando pro Google sobre '{gosto_usuario}'..."):
            sugestoes = buscar_presentes(api_key, gosto_usuario, orcamento_usuario)
            
            if sugestoes:
                st.success("Achei essas opções:")
                for item in sugestoes:
                    # Expander pra não poluir a tela com muito texto
                     # ... dentro do loop for item in sugestoes: ...

                         with st.expander(f"🎁 {item['nome']} - R$ {item['preco']}"):
                             st.write(f"💡 {item['motivo']}")
        
        # 1. Montamos o link limpo (apenas texto)
                             query = urllib.parse.quote(item['nome'])
                             link = f"https://www.google.com/search?q={query}&tbm=shop"
        
        # 2. Usamos st.markdown para criar um botão HTML "na força bruta"
        # Isso evita que o Streamlit se confunda com rotas locais
                             st.markdown(
                               f'''
                                 <a href="{link}" target="_blank" style="
                                  display: inline-block;
                                  padding: 10px 20px;
                                  background-color: #4CAF50;
                                    color: white;
                                     text-decoration: none;
                                        border-radius: 5px;
                                  font-weight: bold;
                                       ">
                                        🛒 Ver no Google Shopping
                                      </a>
                                                ''', 
                                     unsafe_allow_html=True
                                        )