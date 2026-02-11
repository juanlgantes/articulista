import subprocess
import time
import os
import re
import sys
import shutil

# --- CONFIGURACIÓN ---
REPO_NAME = "juanlgantes/articulista"
MAX_CICLOS = 4
JULES_CMD = "jules"  # Si falla, cambiar por ruta absoluta ej: "/home/user/.nvm/.../bin/jules"

def log(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] {msg}")

def ejecutar(cmd_list):
    try:
        # Reemplazar 'jules' por el comando configurado si es el primer argumento
        if cmd_list[0] == 'jules':
            cmd_list[0] = JULES_CMD
            
        res = subprocess.run(cmd_list, capture_output=True, text=True, cwd=os.getcwd())
        return res.stdout.strip()
    except Exception as e:
        log(f"🔥 CRITICAL ERROR executing {cmd_list}: {e}")
        return ""

def sincronizar_git(mensaje):
    """Sube cambios y ORDEN_DEL_DIA."""
    if not ejecutar(['git', 'status', '--porcelain']):
        log("ℹ️ No hay cambios para subir.")
        return

    log("🔄 Sincronizando GitHub...")
    ejecutar(['git', 'add', '.'])
    ejecutar(['git', 'commit', '-m', mensaje])
    ejecutar(['git', 'push', 'origin', 'main'])
    log("✅ Estado actualizado en la nube.")

def esperar_a_jules(session_id):
    """Polling inteligente con timeout."""
    log(f"⏳ Esperando entrega de sesión {session_id}...")
    intentos = 0
    # 60 intentos * 30 seg = 30 minutos máximo de espera
    while intentos < 60:
        time.sleep(30)
        res = ejecutar([JULES_CMD, 'remote', 'pull', '--session', session_id, '--apply'])
        
        if "Patch applied successfully" in res or "Applied" in res:
            log("🎉 Paquete recibido y aplicado.")
            return True
        
        if "No such file" in res or "not ready" in res.lower():
            sys.stdout.write(".") 
            sys.stdout.flush()
        
        intentos += 1
    
    log("\n❌ Timeout: Jules tardó demasiado.")
    return False

def obtener_git_hash():
    return ejecutar(['git', 'rev-parse', 'HEAD'])

def leer_trt_log():
    if os.path.exists("TRT_REFLECTION_LOG.md"):
        try:
            with open("TRT_REFLECTION_LOG.md", "r", encoding="utf-8") as f: return f.read()
        except: pass
    return ""

def generar_mision_unificada(ciclo_actual):
    """
    SINGLE TAP: Una única misión que incluye EJECUCIÓN + PLANIFICACIÓN.
    """
    # 1. Recuperar contexto
    if ciclo_actual == 1:
        fuente = "MISION.md"
        if os.path.exists(fuente):
            with open(fuente, "r", encoding="utf-8") as f: instruccion = f.read()
        else:
            instruccion = "INICIO PROYECTO: Estructura inicial y configuración."
    else:
        fuente = "ORDEN_DEL_DIA.md"
        if os.path.exists(fuente) and os.path.getsize(fuente) > 0:
            with open(fuente, "r", encoding="utf-8") as f: instruccion = f.read()
        else:
            return "FATAL_ERROR_NO_PLAN"

    log(f"📄 Fuente de Misión: {fuente}")

    # 2. Prompt Maestro
    prompt = (
        f"MISIÓN ACTUAL:\n{instruccion}\n\n"
        "--- INSTRUCCIONES OBLIGATORIAS (Protocolo Single-Tap) ---\n"
        "1. EJECUTA: Escribe todo el código necesario para cumplir la misión.\n"
        "2. PLANIFICA: Al terminar, DEBES escribir/sobrescribir el archivo 'ORDEN_DEL_DIA.md'.\n"
        "   - Contenido: Instrucciones técnicas precisas para el SIGUIENTE ciclo.\n"
        "   - Si el proyecto terminó, escribe 'STATUS: COMPLETADO'.\n"
        "   - ⚠️ SI NO ESCRIBES ESTE ARCHIVO, EL PROYECTO MORIRÁ.\n\n"
        f"[Contexto Histórico / Errores Previos]\n{leer_trt_log()}"
    )
    return prompt

def main():
    log(f"🤖 CEO V55 - ARQUITECTURA SINGLE TAP - {REPO_NAME}")
    
    # Check inicial de PATH
    if not shutil.which(JULES_CMD) and not os.path.exists(JULES_CMD):
        log(f"❌ ERROR: No encuentro '{JULES_CMD}'. Edita la variable JULES_CMD en el script con la ruta absoluta (ej: `which jules`).")
        return

    ejecutar(['git', 'pull', 'origin', 'main', '--rebase'])
    
    ciclo = 1
    while ciclo <= MAX_CICLOS:
        log(f"\n🎬 === CICLO {ciclo} ===")
        
        # 1. Generar Misión
        mision = generar_mision_unificada(ciclo)
        if mision == "FATAL_ERROR_NO_PLAN":
            log("🛑 ERROR CRÍTICO: ORDEN_DEL_DIA.md está vacío o no existe tras el ciclo anterior.")
            log("⚠️ El Worker anterior no hizo su trabajo de planificación.")
            break
            
        # 2. Lanzar Jules
        log(f"🚀 Enviando a Jules...")
        salida = ejecutar([JULES_CMD, 'new', mision])
        match = re.search(r"ID:\s+(\d+)", salida)
        
        if not match:
            log(f"❌ Error lanzando misión: {salida}")
            break
            
        # 3. Esperar Resultados
        session_id = match.group(1)
        if not esperar_a_jules(session_id):
            break
            
        # 4. Validar ORDEN_DEL_DIA (Safety Check)
        if not os.path.exists("ORDEN_DEL_DIA.md") or os.path.getsize("ORDEN_DEL_DIA.md") == 0:
            log("⚠️ PELIGRO: Jules no escribió ORDEN_DEL_DIA.md. Abortando para evitar ciclo ciego.")
            break
            
        # 5. Sincronizar (Solo si todo fue bien)
        sincronizar_git(f"Jules V55: Ciclo {ciclo} + Planificación")
        
        input(f"\n⏸️ Ciclo {ciclo} terminado. Presiona ENTER para continuar al {ciclo + 1}...")
        ciclo += 1

if __name__ == "__main__":
    main()