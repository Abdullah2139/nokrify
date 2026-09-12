import uvicorn
import os

if __name__ == "__main__":
    print("==================================================")
    print("  🚀 Nokrify - Pakistan Data Jobs Radar Live")
    print("  Target: Fresh Graduate BSc Computer Systems Eng.")
    print("  Dashboard: http://localhost:8000")
    print("==================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
