"""One-command local launcher; --check verifies installation without a browser."""
import argparse
import importlib
import json
from pathlib import Path
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

ROOT=Path(__file__).resolve().parent

def preflight():
    modules=["fastapi","uvicorn","numpy","PIL","cv2","reportlab","multipart"]
    missing=[]
    for name in modules:
        try: importlib.import_module(name)
        except ImportError: missing.append(name)
    if missing:
        raise RuntimeError("Faltan dependencias: "+", ".join(missing)+". Ejecute Instalar_OculoEdge.bat.")
    for path in ["static/index.html","static/app.css","static/app.js","static/eye.svg"]:
        if not (ROOT/path).is_file(): raise RuntimeError("Falta un recurso local: "+path)
    from core.model_engine import DiagnosticEngine
    from data.dataset_loader import get_available_samples
    engine=DiagnosticEngine()
    samples=get_available_samples(str(ROOT/"data/samples"))
    from PIL import Image
    import numpy as np
    if engine.mode=="heuristic":
        for s in samples:
            with Image.open(s["path"]) as img: result=engine.predict(np.array(img.convert("RGB")))
            if result["prediction_id"]!=s["expected_grade"]:
                raise RuntimeError("La prueba de demostración falló en "+s["filename"])
    print("Instalación verificada. Motor: "+engine.mode+". Recursos locales disponibles.")
    return engine.describe()

def main():
    parser=argparse.ArgumentParser(description="OculoEdge offline en localhost")
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--no-browser",action="store_true")
    parser.add_argument("--port",type=int,default=8050)
    args=parser.parse_args()
    if not 1024<=args.port<=65535: parser.error("Puerto requerido: 1024 a 65535")
    try:
        preflight()
        if args.check: return
        url=f"http://127.0.0.1:{args.port}"
        with socket.socket() as probe:
            occupied=probe.connect_ex(("127.0.0.1",args.port))==0
        if occupied:
            try:
                with urllib.request.urlopen(url+"/api/health",timeout=2) as response: existing=json.load(response)
            except Exception:
                raise RuntimeError(f"El puerto {args.port} está ocupado. Use --port 8051.")
            if existing.get("system")!="OculoEdge": raise RuntimeError("El puerto pertenece a otra aplicación.")
            print("OculoEdge ya está ejecutándose en "+url)
            if not args.no_browser: webbrowser.open(url)
            return
        print("OculoEdge: "+url+" · Ctrl+C para detener. Sin servicios externos.")
        if not args.no_browser:
            def open_ready():
                for _ in range(60):
                    try:
                        with urllib.request.urlopen(url+"/api/health",timeout=.5) as res:
                            if res.status==200: webbrowser.open(url); return
                    except Exception: time.sleep(.25)
            threading.Thread(target=open_ready,daemon=True).start()
        import uvicorn
        uvicorn.run("app.server:app",host="127.0.0.1",port=args.port,log_level="info",workers=1)
    except (RuntimeError, ValueError) as exc:
        print("No se pudo iniciar OculoEdge: "+str(exc),file=sys.stderr); sys.exit(1)

if __name__=="__main__": main()
