# main.py
import os
import time
import shutil
import base64
import requests
from PIL import Image
import google.generativeai as genai

# Configura tu API Key de Gemini
API_KEY = "AIzaSyCGgMcF0KhPfDKllrAlM6_XlggoXDpCozM"
genai.configure(api_key=API_KEY)

# Configura tu API Key para imgbb (o cualquier hosting que uses)
IMGBB_API_KEY = "9b6a38f74e50702889c4afd2704f325f"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Carpetas locales
os.makedirs("uploads", exist_ok=True)
os.makedirs("videos", exist_ok=True)

def subir_a_imgbb(ruta_imagen: str) -> str:
    """Sube la imagen a imgbb y devuelve la URL pública."""
    with open(ruta_imagen, "rb") as f:
        encoded = base64.b64encode(f.read())
    response = requests.post(
        IMGBB_UPLOAD_URL,
        data={
            "key": IMGBB_API_KEY,
            "image": encoded
        }
    )
    if response.status_code != 200:
        raise Exception(f"Error subiendo la imagen: {response.text}")
    data = response.json()
    return data['data']['url']

def generar_video(prompt: str, url_imagen: str):
    """Genera el video usando Gemini Pro Vision."""
    model = genai.GenerativeModel("veo-3.1-generate-preview")
    response = model.generate_content([
        f"{prompt}",
        url_imagen
    ])
    response.resolve()  # Espera a que la generación termine
    return response.text  # Aquí Gemini puede darte el enlace o los datos del video

def main():
    print("=== Generador de Video con Veo 3.1 ===\n")
    image_path = input("Ingresa la ruta de la imagen: ").strip()
    if not os.path.isfile(image_path):
        print("❌ La imagen no existe. Verifica la ruta.")
        return
    prompt = input("Ingresa el prompt para el video: ").strip()
    if not prompt:
        print("❌ El prompt no puede estar vacío.")
        return

    # Copiar imagen a carpeta temporal
    temp_path = os.path.join("uploads", os.path.basename(image_path))
    shutil.copy(image_path, temp_path)
    print(f"Imagen guardada temporalmente en: {temp_path}")

    # Subir la imagen a la nube
    print("Subiendo imagen a la nube...")
    url_imagen = subir_a_imgbb(temp_path)
    print(f"Imagen subida correctamente: {url_imagen}")

    # Generar el video
    print("Generando video, esto puede tardar unos segundos...")
    try:
        resultado = generar_video(prompt, url_imagen)
        print("✅ Video generado correctamente!")
        print("Resultado:", resultado)
    except Exception as e:
        print("❌ Ocurrió un error durante la generación del video:", e)

if __name__ == "__main__":
    main()
