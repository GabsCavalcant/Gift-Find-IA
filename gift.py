from PIL import Image, ImageOps
import streamlit as st
from google import genai
from google.genai import types 
import json
import urllib.parse 
import base64

# --- 1. CONFIGURAÇÃO VISUAL ---

try:
    # Substitua "minha_foto.jpg" pelo nome exato do seu arquivo
    icon_img = Image.open("2.jpg") 
except FileNotFoundError:
    icon_img = "🎁"
st.set_page_config(page_title="Gift Finder AI", page_icon=icon_img, layout="wide")


def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Imagem '{image_file}' Arquivo não encontrado!!.")

# Função para carregar o CSS externo
def local_css(file_name):
    try:
        
        with open(file_name, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ Arquivo {file_name} não encontrado. O estilo não foi carregado.")

# Carrega o estilo (Cores vivas, bordas neon, etc)
local_css("style.css")
set_background("1.jpg")

# --- 2. SIDEBAR (SEGURANÇA) ---
with st.sidebar:
    st.header("Configuração")
    
    api_key = None
    
    # TENTATIVA DE LER SEGREDOS (COM PROTEÇÃO DE ERRO)
    try:
        # O Streamlit tenta ler o arquivo. Se não existir, ele dá erro.
        # O 'try' captura esse erro para o app não fechar.
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            st.success("Chave carregada dos segredos! 🔒")
    except Exception:
        # Se o arquivo secrets.toml não existir, não faz nada e segue pro manual
        pass

    # Se a chave não veio dos segredos, pede na tela
    if not api_key:
        api_key = st.text_input("Insira sua API Key do Google:", type="password")
        st.markdown("[Link pra pegar a chave](https://aistudio.google.com/app/apikey)")

# --- 3. O "CÉREBRO" DO APP (Sua Lógica Original) ---
def buscar_presentes(chave, gosto, orcamento, quem_e=None, cor=None, idade=None, ocasiao=None):
    client = genai.Client(api_key=chave)
    
    ferramenta = types.Tool(
        google_search=types.GoogleSearch()
    )
    
    # Adicao de detalhes extras opcionais
    detalhes_extras = ""
    if quem_e and quem_e != "Não especificar":
        detalhes_extras += f"O presente é para {quem_e} \n"
    
    if cor:
        detalhes_extras += f"A cor favorita da Pessoa é: {cor} \n"
    
    try:
        if idade and idade > 0:
            detalhes_extras += f"A idade da pessoa é: {idade}\n"
    except ValueError as e:
        print(f"Error, Numero invalido : {e}")                 
    
    if ocasiao and ocasiao != "Não especificar":
        detalhes_extras += f"A ocasião para o Presente é : {ocasiao}"
    
    prompt = f"""
    Aja como um personal shopper.
    Use a BUSCA DO GOOGLE para encontrar 5 opções de presentes REAIS vendidos no Brasil.
    Perfil: {gosto}.
    Orçamento Máximo: R$ {orcamento}.
    e esses são os detalhes extras: {detalhes_extras}
    
    DIRETRIZES:
    1. Se tiver idade, verifique a adequação do produto.
    2. Se tiver cor, priorize produtos nessa tonalidade.
    3. o mesmo segue para ocasião
    3. Retorne APENAS JSON puro.
    
    Regra: Retorne APENAS um JSON puro (sem markdown) neste formato:
    [
        {{ "nome": "Nome Produto", "preco": 0.0, "motivo": "Explicação curta" }}
    ]
    """
    
    try:
        # Ajustado para gemini-2.0-flash (o mais atual funcional)
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[ferramenta],
                temperature=0.9 
            )
        )
        
        texto = response.text.replace("```json", "").replace("```", "").strip()
        
        inicio = texto.find('[')
        fim = texto.rfind(']') + 1
        if inicio != -1:
            texto = texto[inicio:fim]

        return json.loads(texto)

    except Exception as e:
        st.error(f"Deu ruim na conexão: {e}")
        return []

# --- 4. INTERFACE DO USUÁRIO (FRONTEND NOVO) ---
st.title("IA GIFT CANT")
st.markdown("---")

# DEFINIÇÃO DO LAYOUT EM DUAS COLUNAS GRANDES
# Esquerda (col_form) = Inputs | Direita (col_results) = Resultados
col_form, col_results = st.columns([1, 1.5], gap="large")

# === COLUNA DA ESQUERDA: FORMULÁRIO ===
with col_form:
    st.write("Projeto de estudo: Buscador de presentes com IA e preços reais.")
    
    # Bloco Obrigatório (Dentro de um container visual)
    with st.container(border=True):
        gosto_usuario = st.text_input("Do que a pessoa gosta? (Obrigatório)", placeholder="Ex: Gamer, Churrasco, Harry Potter")
        orcamento_usuario = st.number_input("Orçamento (R$) (Obrigatório)", min_value=10.0, value=200.0)
    
    # Campos opcionais (Expander original mantido)
    with st.expander("Campos opcionais de Filtro - Aperte para abrir"):
        c_opcao1, c_opcao2 = st.columns(2)
        with c_opcao1:
            quem_e_input = st.text_input("Insira Pra Quem Seria O Presente.", placeholder="Exemplo: Mãe, Amigo")
            cor_input = st.text_input("Insira A cor favorita dessa Pessoa", placeholder="Exemplo: Verde, Rosa")
    
        with c_opcao2:
            idade_input = st.number_input("Insira A Idade", min_value=0, step=1, value=0, format="%d")
            ocasiao_input = st.text_input("Insira A Ocasião Que Deseja Entregar O Presente", placeholder="Exemplo: Aniversário")

    st.write("") # Espaçamento
    # O botão fica na esquerda, mas ativa a lógica
    botao_clicado = st.button("🔍 Pesquisar Presentes", use_container_width=True)

# === COLUNA DA DIREITA: RESULTADOS ===
with col_results:
    if botao_clicado:
        # Validações
        if not api_key:
            st.warning("Eita, esqueceu a chave API na barra lateral!")
        elif not gosto_usuario:
            st.warning("Preciso saber do que a pessoa gosta...")
        else:
            # Spinner visual na direita
            with st.spinner(f"Perguntando pro Google sobre '{gosto_usuario}'..."):
                sugestoes = buscar_presentes(
                    api_key, 
                    gosto_usuario, 
                    orcamento_usuario, 
                    quem_e=quem_e_input, 
                    cor=cor_input, 
                    idade=idade_input,
                    ocasiao=ocasiao_input
                )
                
                if sugestoes:
                    st.success("Achei essas opções:")
                    for item in sugestoes:
                        # Mantendo seu estilo de Expander para os resultados, mas na coluna certa
                        with st.expander(f"🎁 {item['nome']} - R$ {item['preco']}"):
                            st.write(f"💡 {item['motivo']}")
                            
                            # Link HTML estilizado
                            query = urllib.parse.quote(item['nome'])
                            link = f"https://www.google.com/search?q={query}&tbm=shop"
                            
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
                                    margin-top: 10px;
                                ">
                                    🛒 Ver no Google Shopping
                                </a>
                                ''', 
                                unsafe_allow_html=True
                            )
    else:
        # Mensagem inicial na coluna da direita (vazia)
        st.info("👈 Preencha os dados na esquerda para ver os resultados aqui!")