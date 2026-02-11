#!/bin/bash

# --- COLORCITOS ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Iniciando Preparación para Lanzamiento del Bot...${NC}"

# 1. Asegurar lo que tenemos localmente (TRT_LOG, etc)
echo -e "${GREEN}📦 Guardando cambios locales pendientes...${NC}"
git add .
git commit -m "Pre-Execution Sync: $(date +'%Y-%m-%d %H:%M:%S')" || echo "ℹ️ Nada nuevo que guardar."

# 2. Limpieza de Desastres (Crucial para evitar patch failed)
echo -e "${GREEN}🧹 Limpiando inconsistencias de archivos (checkout)...${NC}"
git checkout .

# --- CONFIG ---
JULES_CMD="/home/juanlgantes/.nvm/versions/node/v20.20.0/bin/jules"

# 3. Sincronía total con GitHub
echo -e "${GREEN}🔄 Alineando con el servidor remoto (origin main)...${NC}"
git pull origin main --rebase

# 4. Sincronía con la nube de Jules (Pull de la última sesión)
echo -e "${GREEN}🔍 Buscando última sesión de Jules...${NC}"
# Obtenemos el ID de la sesión más reciente que esté en 'Completed'
LATEST_SESSION=$($JULES_CMD remote list --session | grep -i "Completed" | head -n 1 | awk '{print $1}')

if [ ! -z "$LATEST_SESSION" ]; then
    echo -e "${YELLOW}📥 Intentando aplicar cambios de la sesión: $LATEST_SESSION...${NC}"
    # Normalizamos antes del pull por si acaso
    find . -maxdepth 2 -name "*.html" -o -name "*.md" -o -name "*.py" | xargs -I {} sed -i 's/\r$//' {}
    
    PULL_RES=$($JULES_CMD remote pull --session $LATEST_SESSION --apply 2>&1)
    if [[ $PULL_RES == *"successfully"* ]] || [[ $PULL_RES == *"Applied"* ]]; then
        echo -e "${GREEN}🎉 Sesión $LATEST_SESSION aplicada con éxito.${NC}"
    else
        echo -e "${RED}⚠️ No se pudo aplicar el parche automáticamente (ID: $LATEST_SESSION).${NC}"
        echo -e "${YELLOW}Detalle:${NC} $PULL_RES"
    fi
else
    echo -e "${YELLOW}ℹ️ No se encontraron sesiones completadas recientemente.${NC}"
fi

# 5. Diagnóstico de Estado (Smart Resume)
echo -e "${YELLOW}🔍 Verificando estado del proyecto...${NC}"
if [ -s "ORDEN_DEL_DIA.md" ]; then
    echo -e "   ➡️  ${GREEN}Estado: CONTINUIDAD.${NC} (Se ha detectado un plan previo en ORDEN_DEL_DIA.md)."
    echo -e "      El bot retomará las tareas pendientes guardadas."
else
    echo -e "   ➡️  ${GREEN}Estado: INICIO.${NC} (ORDEN_DEL_DIA.md está vacío o no existe)."
    echo -e "      El bot usará MISION.md para arrancar desde cero."
fi

echo -e "\n${GREEN}✨ PREPARACIÓN COMPLETADA.${NC}"
echo -e "Si el estado anterior es lo que esperas, dispara el proceso:"
echo -e "${YELLOW}python3 articulista_bot_v55.py${NC}\n"
