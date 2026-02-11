import subprocess
import time
import os
import re
import sys
import shutil
import select

# --- CONFIGURACIÓN ---
REPO_NAME = "juanlgantes/articulista"
MAX_CICLOS = 4
JULES_CMD = "/home/juanlgantes/.nvm/versions/node/v20.20.0/bin/jules"

def log(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] {msg}")

class CommandResult:
    def __init__(self, stdout, stderr, returncode):
        self.stdout = stdout.strip()
        self.stderr = stderr.strip()
        self.returncode = returncode
        self.success = (returncode == 0)

def ejecutar(cmd_list, fatal=False):
    """Ejecuta un comando y devuelve un CommandResult. Si fatal=True, aborta el script en error."""
    try:
        if cmd_list[0] == 'jules':
            cmd_list[0] = JULES_CMD
            
        res = subprocess.run(cmd_list, capture_output=True, text=True, cwd=os.getcwd())
        result = CommandResult(res.stdout, res.stderr, res.returncode)
        
        if fatal and not result.success:
            log(f"🛑 ERROR FATAL ejecutando {cmd_list}")
            log(f"📝 STDERR: {result.stderr}")
            sys.exit(1)
            
        return result
    except Exception as e:
        log(f"🔥 CRITICAL ERROR executing {cmd_list}: {e}")
        if fatal: sys.exit(1)
        return CommandResult("", str(e), 1)

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
    """Sube cambios y ORDEN_DEL_DIA. Bloqueante: si falla el push, el bot para."""
    status = ejecutar(['git', 'status', '--porcelain'])
    if not status.stdout:
        log("ℹ️ No hay cambios para subir.")
        return True

    log("🔄 Sincronizando GitHub...")
    ejecutar(['git', 'add', '.'], fatal=True)
    ejecutar(['git', 'commit', '-m', mensaje], fatal=False) # Commit puede fallar si no hay cambios reales
    res_push = ejecutar(['git', 'push', 'origin', 'main'], fatal=True)
    log("✅ Estado actualizado en la nube.")
    return True

def esperar_a_jules(session_id):
    """Polling robusto: Espera a que el estado sea 'Completed' antes de bajar nada."""
    log(f"⏳ Monitoreando sesión {session_id}...")
    start_time = time.time()
    intentos = 0
    while intentos < 120: # 60 minutos máximo de espera
        elapsed = int(time.time() - start_time)
        
        # 1. Consultar la lista de sesiones
        status_raw = ejecutar([JULES_CMD, 'remote', 'list', '--session']).stdout
        
        # 2. Verificar si nuestra sesión ya está en 'Completed'
        # Buscamos el ID y que en esa misma línea aparezca 'Completed'
        if re.search(rf"{session_id}.*Completed", status_raw, re.IGNORECASE):
            log(f"\n✅ Jules ha finalizado (Estado: Completed).")
            log("⏳ Esperando buffer de seguridad (30s) para confirmar inactividad y sincronía...")
            time.sleep(30)
            
            res = ejecutar([JULES_CMD, 'remote', 'pull', '--session', session_id, '--apply'])
            
            if "Patch applied successfully" in res.stdout or "Applied" in res.stdout:
                log("🎉 Paquete completo recibido y aplicado.")
                return True
            else:
                log(f"❌ ERROR: El pull falló (conflicto o estado inconsistente).")
                log(f"📝 Detalle: {res.stdout} {res.stderr}")
                return False 
        
        # 3. Mostrar progreso
        sys.stdout.write(f"\r⏳ Jules sigue trabajando... Tiempo transcurrido: {elapsed}s")
        sys.stdout.flush()
        
        time.sleep(30)
        intentos += 1
    
    log("\n❌ Timeout: La sesión no se completó en el tiempo previsto.")
    return False

# Función eliminada para simplificar: obtener_git_hash ya no es necesaria.

def esperar_confirmacion(timeout_segundos=300):
    """Espera a que el usuario presione ENTER o a que pasen X segundos (híbrido)."""
    log(f"⏳ Pausa de seguridad: Presiona ENTER para saltar al siguiente ciclo o espera {timeout_segundos//60} min para auto-lanzamiento...")
    # select.select espera a que haya datos en stdin (tecla presionada)
    # Solo funciona correctamente en sistemas tipo Unix (Linux/WSL)
    try:
        rlist, _, _ = select.select([sys.stdin], [], [], timeout_segundos)
        if rlist:
            sys.stdin.readline() # Limpiar el buffer de entrada
            log("⏩ Acción manual detectada. Continuando...")
        else:
            log("🤖 Tiempo agotado. Continuando automáticamente...")
    except:
        # Fallback por si select falla en algún entorno
        time.sleep(10)

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
        
        # 1.1 Si el plan indica que hemos terminado, paramos.
        # Usamos regex para buscar 'STATUS: COMPLETADO' al inicio de una línea,
        # evitando falsos positivos dentro de las instrucciones del protocolo.
        if re.search(r"^STATUS: COMPLETADO", instruccion, re.MULTILINE | re.IGNORECASE):
            return "SIGNAL_MISSION_COMPLETE"
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
        "1. CONSCIENCIA DEL PROYECTO:\n"
        "   - Tu objetivo no es solo cerrar tickets, sino EVOLUCIONAR el proyecto.\n"
        "   - Antes de escribir código, piensa: ¿Esto mejora la arquitectura? ¿Es mantenible?\n"
        "   - CALIDAD SUPREMA: Prefiero que hagas MENOS cosas pero PERFECTAS, a que hagas muchas mediocres.\n\n"
        "2. EJECUCIÓN: Implementa SOLAMENTE el siguiente paso lógico. NO intentes terminar todo el proyecto de golpe.\n"
        "   - PRINCIPIO: Calidad > Cantidad.\n"
        "   - PRINCIPIO: Cero Alucinaciones.\n"
        "3. PLANIFICACIÓN OBLIGATORIA: Al terminar, DEBES escribir/sobrescribir el archivo 'ORDEN_DEL_DIA.md'.\n"
        "   - Contenido: Instrucciones técnicas precisas para el SIGUIENTE ciclo (lo que falta por hacer).\n"
        "   - Si el proyecto terminó, escribe 'STATUS: COMPLETADO'.\n"
        "   - ⚠️ IMPORTANTE: Si no escribes este archivo con el plan futuro, el ciclo se romperá.\n\n"
        "4. CONTEXTO HISTÓRICO:\n"
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

    ejecutar(['git', 'pull', 'origin', 'main', '--rebase'], fatal=True)
    
    ciclo = 1
    while ciclo <= MAX_CICLOS:
        log(f"\n🎬 === CICLO {ciclo} ===")
        
        # 0. Pre-Flight Consistency
        normalizar_lineas_lf()
        sincronizar_git(f"Pre-Flight Sync: Ciclo {ciclo}")

        # 1. Generar Misión
        mision = generar_mision_unificada(ciclo)
        if mision == "SIGNAL_MISSION_COMPLETE":
            log("🏁 STATUS: COMPLETADO detectado en la Brújula. ¡Objetivo cumplido!")
            break
        if mision == "FATAL_ERROR_NO_PLAN":
            log("🛑 ERROR CRÍTICO: ORDEN_DEL_DIA.md está vacío o no existe tras el ciclo anterior.")
            log("⚠️ El Worker anterior no hizo su trabajo de planificación.")
            break
            
        # 2. Lanzar Jules
        log(f"🚀 Enviando a Jules...")
        salida = ejecutar([JULES_CMD, 'new', mision]).stdout
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
        
        log(f"✅ Ciclo {ciclo} completado con éxito.")
        esperar_confirmacion(300) # 5 minutos de pausa o ENTER
        ciclo += 1

if __name__ == "__main__":
    main()