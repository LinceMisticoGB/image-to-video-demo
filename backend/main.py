import requests
import base64
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
# ===============================
# CONFIG: reemplaza con tus keys
# ===============================
IMGBB_API_KEY = "9b6a38f74e50702889c4afd2704f325f"
RUNWAY_API_URL = "https://api.runwayml.com/v1/video-generation"
RUNWAY_API_KEY = "key_48447e5c483200b1dc08a8fdf4941b72ea4cfa1b76d50c4531026eac8534731f8932458afe67d2db41da46393c1016edc0eea417f3dedfdade358744243f6006"
app = FastAPI()

# Permitir CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate-video")
async def generate_video(
    prompt: str = Form(...),
    image: UploadFile = File(...)
):
    print("✅ Prompt recibido:", prompt)
    print("✅ Archivo recibido:", image.filename)
    return {"msg": "Archivo recibido correctamente"}
# ===============================
# Función principal
# ===============================
def process_image_to_video(image_bytes: bytes, prompt: str) -> str:
    """
    1. Sube la imagen a ImgBB
    2. Llama a RunwayML para generar el video
    3. Retorna URL del video generado
    """

    # -------------------------------
    # 1️⃣ Subir imagen a ImgBB
    # -------------------------------
    print("Subiendo imagen a ImgBB...")
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    imgbb_payload = {
        "key": IMGBB_API_KEY,
        "image": encoded_image,
    }
    r = requests.post("https://api.imgbb.com/1/upload", data=imgbb_payload)
    if r.status_code != 200:
        raise Exception(f"Error subiendo a ImgBB: {r.text}")

    imgbb_response = r.json()
    image_url = imgbb_response['data']['url']
    print(f"Imagen subida: {image_url}")

    # -------------------------------
    # 2️⃣ Llamar a RunwayML para generar video
    # -------------------------------
    print("Generando video en RunwayML...")
    runway_payload = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": 8  # segundos
    }

    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json"
    }

    runway_response = requests.post(RUNWAY_API_URL, json=runway_payload, headers=headers)
    if runway_response.status_code != 200:
        raise Exception(f"Error generando video: {runway_response.text}")

    runway_data = runway_response.json()
    video_url = runway_data.get("video_url")
    if not video_url:
        raise Exception("Runway no devolvió video_url")

    print(f"Video generado: {video_url}")
    return video_url
