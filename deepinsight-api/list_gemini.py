import google.generativeai as genai
from config import get_settings

def list_gemini_models():
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    try:
        print("Available Gemini models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_gemini_models()
