import os
import threading
import time
import subprocess
import shutil
import webbrowser
import io
import rawpy
import imageio
import urllib.parse  # Crucial for decoding paths
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# --- Setup ---
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)

found_files_pool = []
processed_paths = set()
total_saved_mb = 0.0

RAW_EXTS = {'.cr3', '.cr2', '.nef', '.arw', '.dng', '.orf', '.raf'}
TARGET_FOLDERS = [Path.home() / "Downloads", Path.home() / "Desktop", Path.home() / "Documents", Path.home() / "Library/Caches"]

def background_scanner():
    while True:
        current_batch = []
        for root_folder in TARGET_FOLDERS:
            if not root_folder.exists(): continue
            try:
                for path in root_folder.rglob("*"):
                    if path.is_file() and not path.name.startswith('.') and ".app" not in str(path) and str(path) not in processed_paths:
                        try:
                            size_mb = round(path.stat().st_size / (1024 * 1024), 2)
                            if size_mb > 0.5:
                                current_batch.append({"path": str(path.absolute()), "size": size_mb})
                                processed_paths.add(str(path))
                        except: continue
                    if len(current_batch) >= 10:
                        analyze_batch(current_batch)
                        current_batch = []
                        time.sleep(2)
            except Exception: pass
        time.sleep(30)

def analyze_batch(batch):
    data_summary = "\n".join([f"PATH: {f['path']} | SIZE: {f['size']}MB" for f in batch])
    prompt = "Identify obsolete macOS items. Format: PATH >> REASON >> FOLDER_MODE_TRUE_OR_FALSE"
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=f"{prompt}\n\n{data_summary}")
        for line in response.text.strip().split('\n'):
            if " >> " in line:
                parts = line.split(" >> ")
                path_str = parts[0].strip()
                size_val = next((f['size'] for f in batch if f['path'] == path_str), 0.1)
                found_files_pool.append({
                    "path": path_str, "name": Path(path_str).name,
                    "folder": Path(path_str).parent.name, "size": size_val,
                    "reason": parts[1].strip(), "is_folder": "TRUE" in parts[2].upper()
                })
        print(f"✅ Batch analyzed. Pool: {len(found_files_pool)}")
    except Exception: pass

@app.route('/')
def index(): return render_template('dashboard.html')

@app.route('/poll')
def poll(): return jsonify({"files": found_files_pool, "saved": round(total_saved_mb, 2)})

@app.route('/preview')
def preview_file():
    raw_path = request.args.get('path')
    if not raw_path: return "No path", 400
    
    # Decodes %20 into spaces, %C3%A1 into á, etc.
    file_path = urllib.parse.unquote(raw_path)
    
    if not os.path.exists(file_path):
        print(f"❌ 404: {file_path}")
        return "File not found", 404

    ext = Path(file_path).suffix.lower()
    try:
        if ext in RAW_EXTS:
            with rawpy.imread(file_path) as raw:
                rgb = raw.postprocess(use_camera_wb=True, half_size=True, no_auto_bright=True, bright=1.0)
                buf = io.BytesIO()
                imageio.imsave(buf, rgb, format='JPEG', quality=75)
                buf.seek(0)
                return send_file(buf, mimetype='image/jpeg')
        return send_file(file_path)
    except Exception as e: return str(e), 500

@app.route('/delete', methods=['POST'])
def delete_item():
    global total_saved_mb, found_files_pool
    data = request.json
    path = data.get('path')
    size = data.get('size', 0)
    try:
        if os.path.isdir(path): shutil.rmtree(path)
        else: os.remove(path)
        total_saved_mb += float(size)
        found_files_pool = [f for f in found_files_pool if f['path'] != path]
        return jsonify({"success": True})
    except Exception as e:
        print(f"Delete Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reveal', methods=['POST'])
def reveal_item():
    subprocess.run(['open', '-R', request.json.get('path')])
    return jsonify({"success": True})

if __name__ == "__main__":
    threading.Thread(target=background_scanner, daemon=True).start()
    webbrowser.open("http://127.0.0.1:8080")
    app.run(port=8080, debug=False)