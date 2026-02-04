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
def buscar_presentes(chave, gosto, orcamento, quem_e =None, cor=None, idade=None, ocasiao = None):
    # Conectando com a API usando a chave que o usuário passou
    client = genai.Client(api_key=chave)
    
    # Configurando a ferramenta de busca nativa (Grounding)
    # Isso é o que faz ele buscar preços reais e não alucinar valores
    ferramenta = types.Tool(
        google_search=types.GoogleSearch()
    )
    #Adicao de detalhes extras opcionais
    detalhes_extras = ""
    if quem_e and quem_e != "Não especificar":
        detalhes_extras += f"O presente é para {quem_e} \n"
    
    if cor:
        detalhes_extras += f"A cor favorida da Pessoa é: {cor} \n"
    
    try:
        if idade > 0:
            detalhes_extras += f"A idade da pessoa é: {idade}\n"
    except ValueError as e:
        print(f"Error, Numero invalido : {e}")     
                
    if ocasiao and ocasiao != "Não especificar":
        detalhes_extras += f"A ocasião para o Presente é : {ocasiao}"
    
    # Prompt tunado para retornar JSON. 
    # Se mudar isso aqui, pode quebrar o json.loads lá embaixo.
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
st.title("🎁 Gift Finder Cant AI")
st.write("Projeto de estudo: Buscador de presentes com IA e preços reais.")

# Ucolunas pra ficar lado a lado (mais bonito)
coluna1,coluna2  = st.columns(2)
 
with coluna1:
    gosto_usuario = st.text_input("Do que a pessoa gosta? (Obrigatorio)", placeholder="Ex: Gamer, Churrasco, Harry Potter")
with coluna2:
    orcamento_usuario = st.number_input("Orçamento (R$) (Obrigatorio)", min_value=10.0, value=200.0)
    
    
#Campos opcionais

with st.expander("Campos opcionais de Filtro - Aperte para abrir"):
     #juntos para decomactar as colunas
        c_opcao1, c_opcao2 = st.columns(2)
        with c_opcao1:
            quem_e_input = st.text_input("Insira Pra Quem Seria O Presente. ", placeholder= "Exemplo: Mãe, Amigo")
            cor_input = st.text_input ("Insira A cor favorita dessa Pessoa", placeholder="Exemplo: Verde,Rosa")
   
        with c_opcao2:
            idade_input = st.number_input("Insira A Idade ", placeholder= "Exemplo: 24", min_value=0, step=1, value=0, format="%d")
            ocasiao_input = st.text_input("Insira A Ocasião Que Deseja Entregar O Presnete ", placeholder= "Exemplo: Aniversario")

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
            sugestoes = buscar_presentes(api_key, gosto_usuario, orcamento_usuario, quem_e=quem_e_input, cor= cor_input, idade=idade_input,ocasiao=ocasiao_input)
            
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