# server.py
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil, os
import main  # tu main.py

app = FastAPI()
os.makedirs("uploads", exist_ok=True)
os.makedirs("videos", exist_ok=True)

@app.get("/")
def root():
    return {"message": "Backend activo y funcionando 🚀"}

@app.post("/api/generate-video")
async def api_generate_video(prompt: str = Form(...), file: UploadFile = None):
    if file is None:
        raise HTTPException(status_code=400, detail="Se requiere un archivo de imagen.")

    # Guardar imagen temporalmente
    temp_path = os.path.join("uploads", file.filename)
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Procesar imagen + prompt usando main.py
        video_url = main.process_image_to_video(temp_path, prompt)

        return JSONResponse(content={"video_url": video_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
