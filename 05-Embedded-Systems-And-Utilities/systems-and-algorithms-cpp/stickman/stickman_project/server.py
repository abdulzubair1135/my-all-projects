from fastapi import FastAPI, BackgroundTasks
import subprocess
import uvicorn

app = FastAPI()

def trigger_job():
    subprocess.run(["python", "stickman_pipeline.py"])

@app.get("/")
def home():
    return {"status": "Studio Active", "endpoints": ["/generate-and-upload"]}

@app.post("/trigger")
def start_pipeline(background_tasks: BackgroundTasks):
    background_tasks.add_task(trigger_job)
    return {"message": "Pipeline triggered successfully in background!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)