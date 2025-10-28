from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}

@app.post("/generate-video/")
async def generate_video(prompt: str = Form(...), image: UploadFile = File(...)):
    temp_path = f"temp_{image.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    print(f"Prompt recibido: {prompt}")
    print(f"Imagen guardada en: {temp_path}")
    return {"status": "ok", "message": "Imagen recibida correctamente"}
