import os
import json
import uuid
import time
import threading
import pandas as pd # Excel Generation ke liye
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime

# Core Modules
from core.browser import BrowserManager
from core.search import GoogleMapsSearch
from core.extractor import DataExtractor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Root directory is two levels up from backend/python/
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

class SearchRequest(BaseModel):
    keyword: str
    location: str
    country: str = "India"
    limit: Optional[int] = 1000

def run_scraper_logic(req, results_container):
    browser_manager = None
    try:
        session_id = str(uuid.uuid4())[:8]
        browser_manager = BrowserManager()
        page = browser_manager.launch()
        
        search_engine = GoogleMapsSearch(page)
        query = f"{req.keyword} in {req.location}"
        search_engine.search_direct_url(query)
        
        print(f"[THREAD] Searching: {query}")
        total_found = search_engine.scroll_until_end(max_scrolls=50, stop_after_no_change=5)
        
        cards = search_engine.get_cards()
        extractor = DataExtractor(page, country=req.country)
        businesses = extractor.extract_all_with_details(cards)
        
        browser_manager.close()

        # Save to History (Session file)
        session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
        session_data = {
            "session_id": session_id,
            "keyword": req.keyword,
            "location": req.location,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_leads": len(businesses),
            "status": "completed",
            "data": businesses
        }
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        results_container["success"] = True
        results_container["session_id"] = session_id
        results_container["data"] = businesses
        results_container["total_found"] = total_found
        
    except Exception as e:
        print(f"[THREAD ERROR] {str(e)}")
        if browser_manager: 
            try: browser_manager.close()
            except: pass
        results_container["success"] = False
        results_container["error"] = str(e)

@app.post("/api/search")
def perform_search(req: SearchRequest):
    results_container = {}
    thread = threading.Thread(target=run_scraper_logic, args=(req, results_container))
    thread.start()
    thread.join()
    return results_container

@app.get("/api/history")
def get_history():
    history = []
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(SESSIONS_DIR, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                history.append({
                    "session_id": data.get("session_id"),
                    "keyword": data.get("keyword"),
                    "location": data.get("location"),
                    "date": data.get("date"),
                    "total_leads": data.get("total_leads"),
                    "status": data.get("status")
                })
    return {"success": True, "data": sorted(history, key=lambda x: x['date'], reverse=True)}

@app.post("/api/export")
def export_leads(data: List[dict]):
    try:
        if not data:
            return {"success": False, "error": "No data to export"}
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Clean up columns for Excel
        cols = ["name", "rating", "review_count", "category", "phone", "website", "address"]
        df = df[cols] if all(c in df.columns for c in cols) else df
        
        # Excel file path
        export_path = os.path.join(DATA_DIR, "leads_export.xlsx")
        df.to_excel(export_path, index=False)
        
        return FileResponse(export_path, filename="leads_export.xlsx")
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Mount frontend static files
# This must be at the end to avoid overriding API routes
app.mount("/", StaticFiles(directory=ROOT_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Change host to 0.0.0.0 to allow access from other devices/tunnels
    uvicorn.run(app, host="0.0.0.0", port=8000)
