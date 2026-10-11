"""Package the tested Windows Python + installed core dependencies; no network needed."""
import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path
import shutil
import sys
import zipfile
from packaging.requirements import Requirement

ROOT=Path(__file__).resolve().parents[1]
ROOT_PACKAGES=["fastapi","uvicorn","numpy","pillow","opencv-python-headless","reportlab",
               "matplotlib","python-multipart","httpx","pypdf"]

def distributions():
    found={}; pending=list(ROOT_PACKAGES)
    while pending:
        name=pending.pop(); distribution=metadata.distribution(name); canonical=distribution.metadata["Name"].lower()
        if canonical in found: continue
        found[canonical]=distribution
        for text in distribution.requires or []:
            req=Requirement(text)
            if req.marker is None or req.marker.evaluate({"extra":""}): pending.append(req.name)
    return found

def seal_package(out, manifest):
    """Seal only packaged files, excluding caches and local keys created during QA."""
    for name in manifest["files"]:
        file=(out/name).resolve()
        if not file.is_relative_to(out): raise ValueError("Ruta de manifiesto fuera del paquete.")
        manifest["files"][name]=hashlib.sha256(file.read_bytes()).hexdigest()
    (out/"PACKAGE_MANIFEST.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    archive=out.with_suffix(".zip")
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as zipped:
        for name in sorted(manifest["files"]): zipped.write(out/name,f"{out.name}/{name}")
        zipped.write(out/"PACKAGE_MANIFEST.json",f"{out.name}/PACKAGE_MANIFEST.json")
    print(archive)
    print("SHA256 "+hashlib.sha256(archive.read_bytes()).hexdigest())
    return archive

def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",default=str(ROOT/"dist/OculoEdge_2_0_Concurso"))
    p.add_argument("--seal",action="store_true",help="Actualizar hashes/ZIP de los archivos ya empaquetados tras las pruebas")
    args=p.parse_args()
    out=Path(args.output).resolve()
    if not out.is_relative_to(ROOT/"dist") or out==ROOT/"dist": raise ValueError("El paquete debe quedar dentro de dist/.")
    if args.seal:
        seal_package(out,json.loads((out/"PACKAGE_MANIFEST.json").read_text(encoding="utf-8")))
        return
    if out.exists(): raise ValueError("La carpeta de salida ya existe; elija una carpeta nueva para preservar el paquete anterior.")
    runtime=out/"runtime"; runtime.mkdir(parents=True)
    base=Path(sys.base_prefix)
    for name in ["python.exe","pythonw.exe"]:
        if not (base/name).is_file(): raise ValueError("Se requiere Python Windows instalado.")
        shutil.copy2(base/name,runtime/name)
    for pattern in ["*.dll","LICENSE*.txt"]:
        for file in base.glob(pattern): shutil.copy2(file,runtime/file.name)
    shutil.copytree(base/"DLLs",runtime/"DLLs",ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(base/"Lib",runtime/"Lib",ignore=shutil.ignore_patterns("site-packages","__pycache__","test","tests","idlelib","tkinter","ensurepip"))
    # Isolate imports from the installed Python/registry and resolve paths after relocation.
    (runtime/f"python{sys.version_info.major}{sys.version_info.minor}._pth").write_text(
        ".\nDLLs\nLib\nLib/site-packages\n..\nimport site\n",encoding="utf-8")
    packages=distributions(); site=runtime/"Lib/site-packages"; site.mkdir()
    for distribution in packages.values():
        dist_root=Path(distribution.locate_file("")).resolve()
        for entry in distribution.files or []:
            source=Path(distribution.locate_file(entry)).resolve()
            if not source.is_relative_to(dist_root) or not source.is_file() or "__pycache__" in source.parts: continue
            target=site/source.relative_to(dist_root); target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
    for folder in ["app","core","data","reports","static","benchmarks","protocolo","tests"]:
        shutil.copytree(ROOT/folder,out/folder,ignore=shutil.ignore_patterns("__pycache__","private"))
    for name in ["run.py","Iniciar_OculoEdge.bat","README.md","GUIA_CONCURSO.md","VERIFICACION.md","LICENSE","requirements.txt","requirements-lock.txt","requirements-ml.txt"]:
        shutil.copy2(ROOT/name,out/name)
    licenses=out/"THIRD_PARTY_LICENSES.txt"
    licenses.write_text("Python and dependencies are redistributed for local use. Their license files are included in runtime/ and package dist-info directories.\n"+
                        "\n".join(f"{name}=={d.version}" for name,d in sorted(packages.items())),encoding="utf-8")
    manifest={"python":sys.version,"platform":sys.platform,"packages":{n:d.version for n,d in packages.items()},
              "mode":"heuristic","neural_runtime_included":False,"files":{}}
    for file in sorted(out.rglob("*")):
        if file.is_file(): manifest["files"][file.relative_to(out).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
    seal_package(out,manifest)

if __name__=="__main__": main()
