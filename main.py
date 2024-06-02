from fastapi import FastAPI, HTTPException, File, UploadFile
import uvicorn
import os
from fastapi.responses import HTMLResponse
import prediction
from fastapi.middleware.cors import CORSMiddleware
import io
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html", "r") as f:
            html_content = f.read()
            return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    image_path = prediction.predict_image(file_location)
    with open(image_path, "rb") as f:
        file_content = f.read()
    
    encoded_image = base64.b64encode(file_content).decode()
    return {"image": encoded_image}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)