from fastapi import FastAPI, HTTPException, File, UploadFile
import uvicorn
import os
from fastapi.responses import HTMLResponse


app = FastAPI()

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
    print(f"File uploaded: {type(file)}")
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"message": "File uploaded successfully"}
        




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)