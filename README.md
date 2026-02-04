# 🎁 Gift Finder AI

> Um assistente inteligente de compras de presentes powered by Google Gemini.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)
![Gemini AI](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-8E75B2.svg)
![Status](https://img.shields.io/badge/Status-Finalizado-success.svg)

## 📸 Preview

<div align="center">
  <img src="https://via.placeholder.com/800x400?text=<img width="1919" height="1000" alt="image" src="https://github.com/user-attachments/assets/87442abe-db07-43d1-8d9c-663989383de8" />
" alt="Preview do Projeto" width="100%">
</div>

## 📄 Sobre o Projeto

O **AI Gift CANT** é uma aplicação web desenvolvida para resolver o problema de "não saber o que dar de presente". 

Utilizando o modelo **Gemini 1.5 Flash** do Google e a ferramenta de **Google Search**, a aplicação não apenas sugere ideias criativas com base no perfil do presenteado, mas também valida se esses produtos existem no mercado brasileiro e retorna preços reais.

### ✨ Funcionalidades

-   **IA Generativa:** Análise de perfil (Gostos, Idade, Ocasião) para sugestões personalizadas.
-   **Busca em Tempo Real:** Uso da API do Google para buscar preços e links de compra reais (evitando alucinações de preços).
-   **Interface Responsiva:** Design customizado com CSS, adaptado para Desktop e Mobile (com correção para iOS).
-   **Personalização:** Tema visual elegante e personalizável.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** [Python](https://www.python.org/)
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Inteligência Artificial:** [Google GenAI SDK](https://ai.google.dev/) (Gemini 2.5 Flash)
* **Manipulação de Imagem:** Pillow (PIL)
* **Estilização:** CSS3 Customizado

## 🚀 Como Rodar o Projeto

Pode ser rodado via StreamLit!! https://presentescant.streamlit.app/

### Pré-requisitos

Certifique-se de ter o [Python](https://www.python.org/downloads/) instalado em sua máquina.

### 1. Clone o repositório
bash
git clone [[https://github.com/SEU-USUARIO/gift-finder-ai.git](https://github.com/SEU-USUARIO/gift-finder-ai.git)
cd gift-finder-ai](https://github.com/GabsCavalcant/Gift-Find-IA.git)
2. Crie um ambiente virtual (Recomendado)
Bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

3. Instale as dependências
Bash
pip install -r requirements.txt

4. Configuração da API Key
Você precisará de uma chave de API do Google Gemini.

Obtenha sua chave no Google AI Studio.

Crie uma pasta .streamlit na raiz do projeto.

Crie um arquivo secrets.toml dentro dela:

Ini, TOML
# .streamlit/secrets.toml
GOOGLE_API_KEY = "SUA_CHAVE_AQUI"
(Alternativamente, você pode inserir a chave diretamente na barra lateral da aplicação).

5. Execute a aplicação
Bash
streamlit run gift.py

🤝 Autor
Gabriel Cavalcante Estudante de Ciência da Computação - IFSP ```
