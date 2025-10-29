from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from main import process_image_to_video, process_image_to_video_fallback, check_runway_status
import traceback
import time

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate-video")
async def generate_video(prompt: str = Form(...), file: UploadFile = File(...)):
    """
    Endpoint para recibir un prompt y una imagen,
    luego genera un video usando RunwayML.
    """
    try:
        print(f"➡️ Recibiendo solicitud: prompt='{prompt}', archivo='{file.filename}'")

        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

        # Leer el archivo
        image_bytes = await file.read()
        
        # Validar que no esté vacío
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="El archivo está vacío")

        print(f"📦 Imagen recibida: {len(image_bytes)} bytes")

        # Verificar si RunwayML está disponible
        runway_available = check_runway_status()
        
        if not runway_available:
            print("⚠️ RunwayML no disponible, usando modo fallback")
            # Usar función fallback para desarrollo
            video_url = process_image_to_video_fallback(image_bytes, prompt)
        else:
            # Usar la función principal
            video_url = process_image_to_video(image_bytes, prompt)

        # Responder al frontend
        return JSONResponse(content={
            "success": True,
            "video_url": video_url,
            "message": "Video generado exitosamente",
            "runway_available": runway_available
        })

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Error en generate_video:", e)
        traceback.print_exc()
        
        # Intentar fallback en caso de error
        try:
            print("🔄 Intentando modo fallback...")
            video_url = process_image_to_video_fallback(image_bytes, prompt)
            return JSONResponse(content={
                "success": True,
                "video_url": video_url,
                "message": "Video generado en modo simulación",
                "runway_available": False
            })
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Error procesando la solicitud: {str(e)}")

@app.get("/")
def root():
    return {"message": "✅ API de generación de video activa", "status": "online"}

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado del servicio"""
    runway_status = check_runway_status()
    return {
        "status": "healthy", 
        "runway_ml_available": runway_status,
        "timestamp": time.time()
    }