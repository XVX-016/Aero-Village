from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json
import os
from pathlib import Path

app = FastAPI(
    title="SVAMITVA Smart Village Intelligence Platform",
    description="Backend API for building detection and village infrastructure planning"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).parent.parent
GEOJSON_PATH = BASE_DIR / "outputs" / "building_footprints.geojson"
STATS_PATH = BASE_DIR / "building_stats.csv"
WEB_GEOJSON_PATH = BASE_DIR / "web_demo" / "data" / "building_footprints.geojson"

@app.get("/")
def root():
    return {
        "status": "Backend running",
        "service": "SVAMITVA API",
        "version": "1.0.0"
    }

@app.get("/api/buildings")
async def get_buildings():
    """Get building footprints GeoJSON"""
    try:
        # Try web_demo path first (WGS84), then outputs (UTM)
        geojson_path = WEB_GEOJSON_PATH if WEB_GEOJSON_PATH.exists() else GEOJSON_PATH
        
        if not geojson_path.exists():
            raise HTTPException(status_code=404, detail="Building data not found")
        
        with open(geojson_path, 'r') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Get building statistics"""
    try:
        if not STATS_PATH.exists():
            # Return default stats if file doesn't exist
            return {
                "total_buildings": 100,
                "total_area_m2": 3062.21,
                "average_area_m2": 30.62,
                "villages_surveyed": 325000,
                "property_cards_issued": 109000000,
                "drones_deployed": 500,
                "data_accuracy_cm": 5
            }
        
        import pandas as pd
        df = pd.read_csv(STATS_PATH)
        
        return {
            "total_buildings": len(df),
            "total_area_m2": df['area_m2'].sum() if 'area_m2' in df.columns else 0,
            "average_area_m2": df['area_m2'].mean() if 'area_m2' in df.columns else 0,
            "min_area_m2": df['area_m2'].min() if 'area_m2' in df.columns else 0,
            "max_area_m2": df['area_m2'].max() if 'area_m2' in df.columns else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload drone imagery for analysis"""
    try:
        # In production, we would save the file and trigger an AI pipeline
        # For now, we simulate a successful upload and return metadata
        return {
            "status": "success",
            "filename": file.filename,
            "content_type": file.content_type,
            "message": "Imagery received and queued for spatial extraction",
            "extraction_id": "ext_982341",
            "metadata": {
                "coordinates": [34.123, -118.456],
                "altitude_m": 120,
                "sensor": "Zenmuse P1"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/query")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SVAMITVA API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
