# backend/main.py
import os
import time
import shutil
from google import genai 

# Crear carpetas temporales
os.makedirs("uploads", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# Leer la API key desde variable de entorno
api_key = os.environ.get("GENAI_API_KEY")
if not api_key:
    raise ValueError("❌ No se encontró la API key. Define la variable GENAI_API_KEY.")

client = genai.Client(api_key=api_key)

def main():
    print("=== Generador de Video con Veo 3.1 ===\n")
    
    # 1. Pedir al usuario seleccionar archivo de imagen
    image_path = input("Ingresa la ruta de la imagen (ej: C:\\Users\\Usuario\\Desktop\\foto.jpg): ").strip()
    
    if not os.path.isfile(image_path):
        print("❌ La imagen no existe. Verifica la ruta.")
        return
    
    # 2. Pedir prompt desde consola
    prompt = input("Ingresa el prompt para el video: ").strip()
    
    if prompt == "":
        print("❌ El prompt no puede estar vacío.")
        return
    
    # 3. Copiar la imagen a carpeta temporal
    temp_image_path = os.path.join("uploads", os.path.basename(image_path))
    shutil.copy(image_path, temp_image_path)
    print(f"Imagen guardada temporalmente en: {temp_image_path}")
    
    # 4. Llamar a Veo 3.1 (API)
    print("Generando video con Veo 3.1, esto puede tardar unos segundos...")
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        image=temp_image_path
    )
    
    # 5. Esperar hasta que el video esté listo
    while not operation.done:
        print("⏳ Esperando que el video se genere...")
        time.sleep(5)
        operation = client.operations.get(operation)
    
    # 6. Descargar video
    video = operation.response.generated_videos[0]
    video_path = os.path.join("videos", f"{os.path.splitext(os.path.basename(image_path))[0]}_veo3.mp4")
    client.files.download(file=video.video)
    video.video.save(video_path)
    
    print(f"✅ Video generado y guardado en: {video_path}")

if __name__ == "__main__":
    main()
