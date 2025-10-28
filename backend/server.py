from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import main  # Importamos nuestra lógica principal

app = FastAPI(title="IA Imagen a Video Demo")

# ===============================
# CORS: permitir requests desde React (vite)
# ===============================
origins = [
    "http://localhost:5173",  # tu frontend dev
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Ruta principal: generar video
# ===============================
@app.post("/api/generate-video")
async def generate_video(prompt: str = Form(...), file: UploadFile = File(...)):
    """
    Recibe prompt y archivo desde React
    - prompt: texto descriptivo
    - file: imagen a procesar
    Retorna: JSON con URL del video generado
    """
    try:
        # Convertir UploadFile a bytes
        image_bytes = await file.read()

        # Llamar a main.py para procesar
        video_url = main.process_image_to_video(image_bytes, prompt)

        return JSONResponse({"video_url": video_url})
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)

# ===============================
# Health check
# ===============================
@app.get("/api/health")
def health():
    return {"status": "ok"}
