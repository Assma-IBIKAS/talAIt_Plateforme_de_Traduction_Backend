import os
import requests
from dotenv import load_dotenv


load_dotenv()

# URLs des deux modèles
MODEL_URLS = {
    "fr-en": "https://router.huggingface.co/hf-inference/models/Helsinki-NLP/opus-mt-fr-en",
    "en-fr": "https://router.huggingface.co/hf-inference/models/Helsinki-NLP/opus-mt-en-fr"
}

HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("❌ HF_TOKEN n'est pas défini dans les variables d'environnement.")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
}

def translate(text: str, direction: str):
    """
    direction: 'fr-en' ou 'en-fr'
    """
    if direction not in MODEL_URLS:
        raise ValueError("Direction invalide ! Utilise 'fr-en' ou 'en-fr'.")

    API_URL = MODEL_URLS[direction]

    payload = {"inputs": text}

    response = requests.post(API_URL, headers=headers, json=payload)

    # Vérification d'erreurs
    if response.status_code != 200:
        return {
            "error": f"Erreur Hugging Face ({response.status_code})",
            "details": response.text
        }

    return response.json()


# === EXEMPLES D'UTILISATION ===

# output_fr_en = translate("Bonjour, je suis développeuse.", "fr-en")
# output_en_fr = translate("Hello, how are you?", "en-fr")

# print("FR → EN :", output_fr_en)
# print("EN → FR :", output_en_fr)
