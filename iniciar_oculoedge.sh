#!/usr/bin/env bash
# ==============================================================================
# OculoEdge — Lanzador Oficial de Demostración Local (1-Clic)
# FEMECI Puebla 2026 • Universidad Tecnológica de Tehuacán
# ==============================================================================

# Obtener directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================"
echo "  OCULOEDGE • SISTEMA DE TRIAJE OFTALMOLÓGICO (EDGE AI)  "
echo "  Universidad Tecnológica de Tehuacán - FEMECI Puebla   "
echo "========================================================"
echo ""
echo "[1/4] Verificando entorno virtual de Python..."

if [ ! -d "venv" ]; then
    echo "ERROR: El entorno virtual 'venv' no fue encontrado en $SCRIPT_DIR."
    echo "Ejecute la instalación previa con requirements.txt."
    exit 1
fi

echo "[2/4] Liberando puerto 8050 de procesos anteriores..."
fuser -k 8050/tcp 2>/dev/null || true

echo "[3/4] Iniciando servidor clínico en puerto 8050..."
echo "      Modo: Inferencia Local en CPU (100% Offline)"
echo "      URL:  http://localhost:8050"
echo ""
echo "[4/4] Abriendo interfaz en el navegador web..."

# Abrir en segundo plano el navegador tras 1.5 segundos
(
    sleep 1.5
    if which xdg-open > /dev/null 2>&1; then
        xdg-open "http://localhost:8050" > /dev/null 2>&1
    elif which google-chrome > /dev/null 2>&1; then
        google-chrome "http://localhost:8050" > /dev/null 2>&1
    elif which firefox > /dev/null 2>&1; then
        firefox "http://localhost:8050" > /dev/null 2>&1
    fi
) &

# Ejecutar el servidor FastAPI
./venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 8050
