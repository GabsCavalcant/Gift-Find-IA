import streamlit as st
import google.generativeai as genai
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gift Finder AI", page_icon="🎁")

# --- BARRA LATERAL (Para a Chave) ---
with st.sidebar:
    st.header("Configuração")
    # Aqui o usuário pode colocar a chave dele, OU você deixa a sua fixa (cuidado!)
    api_key = st.text_input("Insira sua API Key do Google:", type="password")
    st.markdown("[Pegue sua chave grátis aqui](https://aistudio.google.com/app/apikey)")

# --- LÓGICA DA IA ---
def buscar_presentes(chave, gosto, orcamento):
    genai.configure(api_key=chave)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Aja como um personal shopper.
    Sugira 3 presentes criativos para alguém que gosta de: {gosto}.
    Orçamento máximo: R$ {orcamento}.
    Responda APENAS com uma lista JSON: [{{ "nome": "...", "preco": 0.0, "motivo": "..." }}]
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpeza básica do JSON
        texto = response.text.replace("```json", "").replace("```", "")
        return json.loads(texto)
    except Exception as e:
        st.error(f"Erro na IA: {e}")
        return []

# --- A TELA DO APP ---
st.title("🎁 Gift Finder AI")
st.write("Descubra o presente ideal em segundos com Inteligência Artificial.")

# Entradas do Usuário
col1, col2 = st.columns(2)
with col1:
    gosto_usuario = st.text_input("Do que a pessoa gosta?", placeholder="Ex: Café, Star Wars, Corrida")
with col2:
    orcamento_usuario = st.number_input("Orçamento Máximo (R$)", min_value=10.0, value=100.0)

# Botão de Ação
if st.button("🔍 Encontrar Presentes"):
    if not api_key:
        st.warning("Por favor, insira uma API Key na barra lateral para funcionar!")
    elif not gosto_usuario:
        st.warning("Diga do que a pessoa gosta!")
    else:
        with st.spinner("A IA está pensando..."):
            sugestoes = buscar_presentes(api_key, gosto_usuario, orcamento_usuario)
            
            if sugestoes:
                st.success("Aqui estão algumas ideias!")
                for item in sugestoes:
                    with st.expander(f"🎁 {item['nome']} - R$ {item['preco']}"):
                        st.write(item['motivo'])