
import google.generativeai as genai
import os

MINHA_CHAVE = "AIzaSyDjcnFpe3iEJ8wn8lZeDjUigR_BYuC7J14" 
genai.configure(api_key=MINHA_CHAVE)

print("Listando modelos disponíveis para você...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Erro: {e}")