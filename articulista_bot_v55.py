import subprocess
import time
import os
import re
import sys
import shutil

# --- CONFIGURACIÓN ---
REPO_NAME = "juanlgantes/articulista"
MAX_CICLOS = 4
JULES_CMD = "/home/juanlgantes/.nvm/versions/node/v20.20.0/bin/jules"

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

def normalizar_lineas_lf():
    """Convierte CRLF a LF en archivos de texto del proyecto para evitar errores de patch."""
    log("🧹 Normalizando finales de línea (LF)...")
    formatos = ('.html', '.css', '.js', '.md', '.py')
    for root, dirs, files in os.walk(os.getcwd()):
        if '.git' in dirs: dirs.remove('.git')
        for file in files:
            if file.endswith(formatos):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f: content = f.read()
                    new_content = content.replace(b'\r\n', b'\n')
                    if new_content != content:
                        with open(path, 'wb') as f: f.write(new_content)
                except Exception as e:
                    log(f"⚠️ No se pudo normalizar {file}: {e}")

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
    """Polling robusto: Espera a que el estado sea 'Completed' antes de bajar nada."""
    log(f"⏳ Monitoreando sesión {session_id}...")
    start_time = time.time()
    intentos = 0
    while intentos < 120: # 60 minutos máximo de espera
        elapsed = int(time.time() - start_time)
        
        # 1. Consultar la lista de sesiones
        status_raw = ejecutar([JULES_CMD, 'remote', 'list', '--session'])
        
        # 2. Verificar si nuestra sesión ya está en 'Completed'
        # Buscamos el ID y que en esa misma línea aparezca 'Completed'
        if re.search(rf"{session_id}.*Completed", status_raw, re.IGNORECASE):
            log(f"\n✅ Jules ha finalizado (Estado: Completed).")
            log("⏳ Esperando buffer de seguridad (30s) para confirmar inactividad y sincronía...")
            time.sleep(30)
            
            log("🔄 Ejecutando PULL final para traer todos los cambios...")
            res = ejecutar([JULES_CMD, 'remote', 'pull', '--session', session_id, '--apply'])
            
            if "Patch applied successfully" in res or "Applied" in res:
                log("🎉 Paquete completo recibido y aplicado.")
                return True
            else:
                log(f"❌ ERROR: El pull falló (conflicto o estado inconsistente): {res}")
                return False 
        
        # 3. Mostrar progreso
        sys.stdout.write(f"\r⏳ Jules sigue trabajando... Tiempo transcurrido: {elapsed}s")
        sys.stdout.flush()
        
        time.sleep(30)
        intentos += 1
    
    log("\n❌ Timeout: La sesión no se completó en el tiempo previsto.")
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
    # 1. Recuperar contexto (Lógica Smart Resume)
    # Si existe ORDEN_DEL_DIA con contenido, SIEMPRE tiene prioridad (Continuidad del Proyecto).
    if os.path.exists("ORDEN_DEL_DIA.md") and os.path.getsize("ORDEN_DEL_DIA.md") > 0:
        fuente = "ORDEN_DEL_DIA.md"
        with open(fuente, "r", encoding="utf-8") as f: instruccion = f.read()
    elif ciclo_actual == 1:
        fuente = "MISION.md"
        if os.path.exists(fuente):
            with open(fuente, "r", encoding="utf-8") as f: instruccion = f.read()
        else:
            instruccion = "INICIO PROYECTO: Estructura inicial y configuración."
    else:
        return "FATAL_ERROR_NO_PLAN"

    log(f"📄 Fuente de Misión: {fuente}")

    # 2. Prompt Maestro
    prompt = (
        f"MISIÓN TÉCNICA:\n{instruccion}\n\n"
        "--- PROTOCOLO DE CALIDAD (SINGLE TAP) ---\n"
        "1. EJECUCIÓN: Implementa SOLAMENTE el siguiente paso lógico. NO intentes terminar todo el proyecto de golpe.\n"
        "   - PRINCIPIO: Calidad > Cantidad.\n"
        "   - PRINCIPIO: Cero Alucinaciones.\n"
        "2. PLANIFICACIÓN OBLIGATORIA: Al terminar, DEBES escribir/sobrescribir el archivo 'ORDEN_DEL_DIA.md'.\n"
        "   - Contenido: Instrucciones técnicas precisas para el SIGUIENTE ciclo (lo que falta por hacer).\n"
        "   - Si el proyecto terminó, escribe 'STATUS: COMPLETADO'.\n"
        "   - ⚠️ IMPORTANTE: Si no escribes este archivo con el plan futuro, el ciclo se romperá.\n\n"
        "3. CONTEXTO HISTÓRICO:\n"
        "   - Antes de empezar, LEE el archivo 'TRT_REFLECTION_LOG.md'.\n"
        "   - Contiene tus errores pasados y tu constitución de calidad. OBEDÉCELOS."
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
        
        # 0. Pre-Flight Consistency
        normalizar_lineas_lf()
        sincronizar_git(f"Pre-Flight Sync: Ciclo {ciclo}")

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