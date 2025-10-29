import requests
import base64
import time
import json
import os
from typing import Optional, Dict, Any

# ⚠️ IMPORTANTE: Mueve las API keys a variables de entorno
IMGBB_API_KEY = "9b6a38f74e50702889c4afd2704f325f"
RUNWAY_API_URL = "https://api.dev.runwayml.com/v1/generations"
RUNWAY_API_KEY = "key_48447e5c483200b1dc08a8fdf4941b72ea4cfa1b76d50c4531026eac8534731f8932458afe67d2db41da46393c1016edc0eea417f3dedfdade358744243f6006"

def process_image_to_video(image_bytes: bytes, prompt: str, duration: int = 4, motion: str = "medium") -> Optional[str]:
    """
    Procesa una imagen para generar un video usando RunwayML API
    
    Args:
        image_bytes: Bytes de la imagen de entrada
        prompt: Texto descriptivo para la generación del video
        duration: Duración del video en segundos (3-10)
        motion: Nivel de movimiento ('low', 'medium', 'high')
    
    Returns:
        URL del video generado o None si hay error
    """
    
    # Validaciones iniciales
    if not RUNWAY_API_KEY or RUNWAY_API_KEY == "your_runway_api_key_here":
        raise ValueError("RUNWAY_API_KEY no está configurada correctamente en las variables de entorno")
    
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Los bytes de la imagen están vacíos")
    
    if not prompt or len(prompt.strip()) == 0:
        raise ValueError("El prompt no puede estar vacío")
    
    if duration < 3 or duration > 10:
        raise ValueError("La duración debe estar entre 3 y 10 segundos")
    
    # Validar tamaño de la imagen (máximo 5MB para RunwayML)
    if len(image_bytes) > 5 * 1024 * 1024:
        raise ValueError("La imagen es demasiado grande. Máximo 5MB permitido.")
    
    # Codificar imagen a base64
    try:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        print(f"✅ Imagen codificada: {len(image_b64)} caracteres base64")
    except Exception as e:
        raise ValueError(f"Error codificando la imagen: {str(e)}")
    
    # Configurar headers para RunwayML
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Construir payload para RunwayML Gen-3 Alpha
    payload = {
        "model": "gen-3-alpha",  # Modelo correcto
        "prompt": prompt.strip(),
        "image": f"data:image/jpeg;base64,{image_b64}",
        "duration": duration,
        "motion": motion,
        "seed": int(time.time() % 10000)  # Seed aleatorio
    }
    
    try:
        print(f"🔄 Enviando solicitud a RunwayML...")
        print(f"📝 Prompt: {prompt}")
        print(f"🖼️ Tamaño imagen: {len(image_bytes)} bytes")
        print(f"⏱️ Duración: {duration}s")
        print(f"🎬 Motion: {motion}")
        
        # Endpoint correcto para generaciones
        url = f"{RUNWAY_API_URL}/generations"
        print(f"🌐 URL: {url}")
        
        # Hacer la petición
        response = requests.post(
            url, 
            headers=headers, 
            json=payload,
            timeout=120  # 120 segundos timeout para generación de video
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        # Verificar si la petición fue exitosa
        response.raise_for_status()
        
        # Procesar respuesta
        data = response.json()
        print(f"✅ Respuesta de RunwayML recibida")
        print(f"📊 Respuesta completa: {json.dumps(data, indent=2)}")
        
        # La estructura de respuesta puede variar, intentemos diferentes formatos
        video_url = None
        
        if "data" in data and len(data["data"]) > 0:
            # Formato 1: data[0].url
            video_url = data["data"][0].get("url")
        elif "output" in data and len(data["output"]) > 0:
            # Formato 2: output[0].url
            video_url = data["output"][0].get("url")
        elif "url" in data:
            # Formato 3: url directo
            video_url = data["url"]
        elif "generation" in data and "url" in data["generation"]:
            # Formato 4: generation.url
            video_url = data["generation"]["url"]
        
        if not video_url:
            print(f"❌ No se pudo encontrar la URL del video en la respuesta")
            print(f"📊 Estructura de respuesta: {json.dumps(data, indent=2)}")
            raise ValueError("No se pudo extraer la URL del video de la respuesta")
        
        # Validar URL
        if not video_url.startswith(('http://', 'https://')):
            print(f"⚠️ URL de video puede ser inválida: {video_url}")
        
        print(f"🎥 Video generado exitosamente: {video_url}")
        return video_url
        
    except requests.exceptions.Timeout:
        raise Exception("Timeout: La generación del video tardó demasiado (más de 120 segundos)")
    except requests.exceptions.ConnectionError:
        raise Exception("Error de conexión: No se pudo conectar a RunwayML API")
    except requests.exceptions.HTTPError as e:
        error_msg = f"Error HTTP {response.status_code}"
        try:
            error_detail = response.json()
            print(f"🔍 Error detail: {json.dumps(error_detail, indent=2)}")
            if "error" in error_detail:
                error_msg += f": {error_detail['error']}"
            elif "message" in error_detail:
                error_msg += f": {error_detail['message']}"
            elif "detail" in error_detail:
                error_msg += f": {error_detail['detail']}"
        except:
            error_text = response.text[:500] + "..." if len(response.text) > 500 else response.text
            error_msg += f": {error_text}"
        raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error en la petición a RunwayML: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Estructura de respuesta inesperada: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parseando respuesta JSON: {str(e)}")

def check_runway_status() -> bool:
    """Verifica si la API de RunwayML está disponible"""
    try:
        headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
        }
        response = requests.get(
            f"{RUNWAY_API_URL}/models",
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error verificando estado: {e}")
        return False

def get_runway_models() -> Optional[Dict[str, Any]]:
    """Obtiene información sobre los modelos disponibles en RunwayML"""
    try:
        headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
        }
        response = requests.get(
            f"{RUNWAY_API_URL}/models",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error obteniendo modelos: {e}")
        return None

# Función alternativa si la API principal no funciona
def process_image_to_video_fallback(image_bytes: bytes, prompt: str) -> str:
    """
    Función fallback que simula la generación de video
    para desarrollo y testing
    """
    print("🔄 Usando modo fallback (simulación)")
    
    # Simular procesamiento
    time.sleep(3)
    
    # Devolver URL de video de ejemplo o mensaje
    return "https://example.com/simulated-video.mp4"

if __name__ == "__main__":
    # Prueba de conexión
    print("🧪 Probando conexión con RunwayML...")
    
    if check_runway_status():
        print("✅ RunwayML API está disponible")
        
        # Obtener modelos disponibles
        models = get_runway_models()
        if models:
            print("📋 Modelos disponibles:")
            if isinstance(models, dict) and 'data' in models:
                for model in models['data']:
                    print(f"  - {model.get('id', 'Unknown')}")
    else:
        print("❌ RunwayML API no está disponible")
        print("💡 Usando modo fallback para desarrollo")
    
    # Ejemplo de uso
    try:
        # Crear una imagen simple de prueba
        from PIL import Image, ImageDraw
        test_image_path = "test_image.jpg"
        
        # Crear imagen de prueba si no existe
        if not os.path.exists(test_image_path):
            print("🖼️ Creando imagen de prueba...")
            img = Image.new('RGB', (512, 512), color='blue')
            draw = ImageDraw.Draw(img)
            draw.rectangle([100, 100, 400, 400], fill='red')
            img.save(test_image_path, 'JPEG')
            print("✅ Imagen de prueba creada")
        
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        # Generar video
        video_url = process_image_to_video(
            image_bytes=image_data,
            prompt="Una persona caminando en un parque con efectos especiales",
            duration=4,
            motion="medium"
        )
        
        print(f"🎉 Prueba exitosa! Video URL: {video_url}")
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        print("💡 Intentando con modo fallback...")
        
        try:
            video_url = process_image_to_video_fallback(image_data, "Test prompt")
            print(f"🎉 Prueba fallback exitosa! Video URL: {video_url}")
        except Exception as fallback_error:
            print(f"❌ Error incluso en fallback: {fallback_error}")