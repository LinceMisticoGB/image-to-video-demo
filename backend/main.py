# main.py
import os
import base64
import requests
from runwayml import RunwayML, TaskFailedError

# ===============================
# CONFIGURACIÓN
# ===============================
RUNWAY_API_KEY = "key_48447e5c483200b1dc08a8fdf4941b72ea4cfa1b76d50c4531026eac8534731f8932458afe67d2db41da46393c1016edc0eea417f3dedfdade358744243f6006"
IMGBB_API_KEY = "9b6a38f74e50702889c4afd2704f325f"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Inicializa Runway
try:
    client = RunwayML(api_key=RUNWAY_API_KEY)
except Exception as e:
    print(f"❌ Error al inicializar Runway: {e}")
    exit()

# ===============================
# FUNCIONES AUXILIARES
# ===============================
def subir_a_imgbb(ruta_imagen: str) -> str:
    """Sube la imagen a ImgBB y devuelve la URL pública"""
    with open(ruta_imagen, "rb") as f:
        encoded = base64.b64encode(f.read())
    
    response = requests.post(
        IMGBB_UPLOAD_URL,
        data={"key": IMGBB_API_KEY, "image": encoded}
    )
    if response.status_code != 200:
        raise Exception(f"Error subiendo la imagen a ImgBB: {response.text}")
    data = response.json()
    return data['data']['url']

def generar_video(prompt: str, url_imagen: str) -> str:
    """Genera un video usando Runway Image-to-Video"""
    try:
        task = client.image_to_video.create(
            model='gen4_turbo',
            prompt_image=url_imagen,
            prompt_text=prompt,
            ratio='1280:720',
            duration=4.0
        )
        task = task.wait_for_task_output()
        return task.output.video.url
    except TaskFailedError as e:
        raise Exception(f"La generación de video falló: {e.task_details}")
    except Exception as e:
        raise Exception(f"Error de Runway: {e}")

# ===============================
# FUNCIÓN PRINCIPAL PARA FASTAPI
# ===============================
def process_image_to_video(file_path: str, prompt: str) -> str:
    """
    Recibe la ruta de la imagen y el prompt.
    Devuelve la URL del video generado.
    """
    url_imagen = subir_a_imgbb(file_path)
    video_url = generar_video(prompt, url_imagen)
    return video_url
