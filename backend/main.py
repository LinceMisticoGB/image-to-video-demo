# main.py
import os
import time
import shutil
import base64
import requests
from PIL import Image
from runwayml import RunwayML, TaskFailedError # Importar el SDK de Runway
 # Para la relación de aspecto
from runwayml import RunwayML, TaskFailedError # Importa el cliente y la excepción
  # Importa la clase de esquema (¡Esta es la línea clave!)
# ===============================================
# ⚠️ 1. CONFIGURACIÓN CRÍTICA
# ===============================================

# 🚨 REEMPLAZA ESTA CLAVE CON TU CLAVE REAL DE RUNWAY API.
# NOTA: Debes obtenerla en el panel de desarrollador de Runway.
RUNWAY_API_KEY = "key_48447e5c483200b1dc08a8fdf4941b72ea4cfa1b76d50c4531026eac8534731f8932458afe67d2db41da46393c1016edc0eea417f3dedfdade358744243f6006" 

# Configura tu API Key para imgbb
IMGBB_API_KEY = "9b6a38f74e50702889c4afd2704f325f"
IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Inicializa el cliente de Runway
try:
    client = RunwayML(api_key=RUNWAY_API_KEY)
except Exception as e:
    print(f"❌ Error al inicializar el cliente de Runway. Asegúrate de que RUNWAY_API_KEY esté configurada. Error: {e}")
    exit()

# Carpetas locales
os.makedirs("uploads", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# ===============================================
# 2. FUNCIONES AUXILIARES
# ===============================================

def subir_a_imgbb(ruta_imagen: str) -> str:
    """Sube la imagen a imgbb y devuelve la URL pública."""
    # (Tu código de ImgBB funciona para obtener la URL pública requerida por Runway)
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
        raise Exception(f"Error subiendo la imagen a ImgBB: {response.text}")
    data = response.json()
    return data['data']['url']


def generar_video(prompt: str, url_imagen: str):
    """Genera el video usando el SDK de Runway Image-to-Video (Gen-4 Turbo)."""
    
    print("Iniciando tarea de generación de video con Runway...")
    
    try:
        task = client.image_to_video.create(
            model='gen4_turbo', 
            prompt_image=url_imagen,
            prompt_text=prompt,
            #Usamos la dimensión exacta para 16:9
            ratio='1280:720', 
            duration=4.0, 
        )
        
        print(f"Tarea iniciada. Esperando a que el video termine de generarse...")
        
        # ⚠️ Función clave del SDK: Espera a que la tarea termine y obtiene el resultado.
        # Esto puede tardar varios minutos.
        task = task.wait_for_task_output() 
        
        # El resultado final está en task.output
        output_url = task.output.video.url
        
        return output_url

    except TaskFailedError as e:
        raise Exception(f"La generación de video falló. Detalles: {e.task_details}")
    except Exception as e:
        # Atrapa otros errores (API Key inválida, límites, etc.)
        raise Exception(f"Ocurrió un error general de Runway: {e}")

# ===============================================
# 3. FUNCIÓN PRINCIPAL
# ===============================================

def main():
    print("=== Generador de Video con Runway ML ===\n")
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
    print(f"\nImagen guardada temporalmente en: {temp_path}")

    # Subir la imagen a la nube
    print("Subiendo imagen a la nube...")
    try:
        url_imagen = subir_a_imgbb(temp_path)
        print(f"Imagen subida correctamente: {url_imagen}")
    except Exception as e:
        print(f"❌ Error al subir la imagen: {e}")
        return

    # Generar el video
    try:
        video_url = generar_video(prompt, url_imagen)
        
        print("\n✅ Video generado correctamente!")
        print(f"🔗 URL del Video de Runway: {video_url}")
        
        # Opcional: Descargar el video para guardarlo localmente
        video_name = os.path.basename(video_url).split('?')[0] # Limpiar la URL
        video_save_path = os.path.join("videos", video_name)
        
        print(f"Descargando video a: {video_save_path}...")
        video_data = requests.get(video_url).content
        with open(video_save_path, 'wb') as f:
            f.write(video_data)
        print("¡Descarga completada!")
        
    except Exception as e:
        print(f"\n❌ Ocurrió un error durante la generación del video: {e}")

if __name__ == "__main__":
    main()