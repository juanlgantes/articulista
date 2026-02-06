import subprocess
import time
import os
import re
import sys

# --- CONFIGURACIÓN ---
REPO_NAME = "juanlgantes/articulista"
MAX_CICLOS = 4  # Cuántas veces quieres que piense y trabaje seguido antes de parar

def log(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] {msg}")

def ejecutar(cmd_list):
    """Ejecuta comandos de terminal de forma silenciosa pero efectiva."""
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, cwd=os.getcwd())
        return res.stdout.strip()
    except Exception as e:
        log(f"CRITICAL ERROR EXECUTING COMMAND: {e}")
        return str(e)

def hay_cambios_locales():
    """Detecta si Jules ha creado algo nuevo en el disco."""
    estado = ejecutar(['git', 'status', '--porcelain'])
    return len(estado) > 0

def sincronizar_git(mensaje):
    """
    CRÍTICO: Sube los cambios a GitHub.
    Esto es OBLIGATORIO para que en la siguiente tarea Jules vea el trabajo anterior.
    """
    if not hay_cambios_locales():
        log("ℹ️ No hay cambios para subir. Saltando sync.")
        return

    log("🔄 Sincronizando GitHub para que Jules vea el nuevo estado...")
    ejecutar(['git', 'add', '.'])
    ejecutar(['git', 'commit', '-m', mensaje])
    ejecutar(['git', 'push', 'origin', 'main'])
    log("✅ Estado actualizado en la nube.")

def esperar_a_jules(session_id):
    """Espera a que Jules entregue el paquete."""
    log(f"⏳ Esperando entrega de sesión {session_id}...")
    intentos = 0
    while intentos < 80: # 40 minutos max
        time.sleep(30)
        res = ejecutar(['jules', 'remote', 'pull', '--session', session_id, '--apply'])
        
        if "Patch applied successfully" in res or "Applied" in res:
            log("🎉 Paquete recibido.")
            return True
        
        if "No such file" in res:
            sys.stdout.write(".") 
            sys.stdout.flush()
        
        intentos += 1
    return False

def obtener_git_hash():
    """Devuelve el hash del último commit (HEAD)."""
    return ejecutar(['git', 'rev-parse', 'HEAD'])

def carpeta_tiene_contenido():
    """Verifica si hay algo más que la carpeta .git y el propio script."""
    # Lista todo excluyendo .git y el archivo actual
    archivos = [f for f in os.listdir('.') 
                if f != '.git' and f != os.path.basename(__file__)]
    return len(archivos) > 0

def leer_trt_log():
    """Lee el archivo de reflexión TRT para inyectar contexto histórico."""
    log_path = "TRT_REFLECTION_LOG.md"
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""
    return ""

# ==============================================================================
#  CEREBRO DINÁMICO (Lógica de Continuidad por Cambios)
# ==============================================================================

def generar_mision_worker(ciclo_actual, hash_anterior):
    """
    Fase 1: EL TRABAJADOR. Ejecuta la misión core.
    PROHIBIDO: Decidir el siguiente paso (ORDEN_DEL_DIA).
    """
    log("👷 [WORKER] Iniciando Fase de Construcción...")
    
    # Check 1: ¿Hay algo sobre lo que trabajar?
    if not carpeta_tiene_contenido():
        log("❌ La carpeta parece estar vacía (solo .git o bot).")
        return "La carpeta está vacía. Crea un archivo SPECS.md con el plan del proyecto y una estructura inicial adecuada."

    # Check 2: Control de Progreso (Evidencia de Cambios)
    if ciclo_actual > 1:
        hash_actual = obtener_git_hash()
        log(f"🔎 [Check Progreso] Hash Anterior: {hash_anterior[:7]} | Hash Actual: {hash_actual[:7]}")
        
        if hash_actual == hash_anterior:
            log("🛑 No se detectaron nuevos commits del ciclo anterior.")
            return "STATUS: COMPLETADO"
        else:
            log("✅ Se detectaron cambios. El proyecto avanza.")

    # 1. Determinar Fuente de la Misión
    if ciclo_actual == 1:
        if os.path.exists("MISION.md"):
            try:
                with open("MISION.md", "r", encoding="utf-8") as f:
                    core_mission = f.read()
            except:
                core_mission = "Lee SPECS.md y comienza el proyecto."
        else:
             core_mission = "No existe MISION.md. Analiza el estado actual y propón el mejor siguiente paso."
        log(f"📄 Fuente: MISION.md (Ciclo {ciclo_actual})")
    else:
        if os.path.exists("ORDEN_DEL_DIA.md"):
            try:
                with open("ORDEN_DEL_DIA.md", "r", encoding="utf-8") as f:
                    core_mission = f.read()
            except:
                core_mission = "Continúa donde lo dejaste en el ciclo anterior."
        else:
            core_mission = "No existe ORDEN_DEL_DIA.md. Continúa lógicamente con la mejora del proyecto."
        log(f"📄 Fuente: ORDEN_DEL_DIA.md (Ciclo {ciclo_actual})")

    # 2. Constraints del Worker (Prohibido planificar)
    worker_constraints = (
        "\n\n[ROL: WORKER / CONSTRUCTOR]\n"
        "Tu tarea es EJECUTAR lo solicitado en la misión. Enfócate puramente en código e implementación.\n"
        "PROHIBIDO: No toques ni crees el archivo 'ORDEN_DEL_DIA.md'. De eso se encarga el Red Team después de ti.\n"
        "Solo genera el código funcional necesario."
    )

    quality_constitution = (
        "\n\n[CONSTITUCIÓN DE CALIDAD]\n"
        "1. CALIDAD > CANTIDAD.\n"
        "2. CERO ALUCINACIONES: Si no sabes algo, para.\n"
        "3. DETERMINISMO: Usa soluciones probadas."
    )
    
    trt_context = leer_trt_log()
    trt_section = f"\n\n[MEMORIA TRT]\n{trt_context}" if trt_context else ""

    return f"MISIÓN:\n{core_mission}\n{worker_constraints}\n{quality_constitution}\n{trt_section}"

def generar_mision_red_team():
    """
    Fase 2: EL JUEZ (RED TEAM). Revisa y Planifica.
    OBLIGATORIO: Criticar y escribir ORDEN_DEL_DIA.md.
    """
    log("⚖️ [RED TEAM] Iniciando Fase de Auditoría y Planificación...")
    
    return (
        "ACTÚA COMO UN AUDITOR DE CÓDIGO Y ARQUITECTO (RED TEAM).\n"
        "Acabas de recibir código nuevo del 'Worker'. Tu trabajo es:\n"
        "1. CRITICAR: Busca errores de seguridad, bugs, o mala calidad en los últimos cambios. CORRÍGELOS si existen.\n"
        "2. PLANIFICAR: Escribe/Actualiza el archivo 'ORDEN_DEL_DIA.md'.\n"
        "   - Contenido de ORDEN_DEL_DIA.md: Lista detallada de qué se debe hacer EXACTAMENTE en la siguiente sesión.\n"
        "   - Sé técnico y específico.\n"
        "\n[MEMORIA TRT IMPLACABLE]\n" + leer_trt_log()
    )

def ejecutar_fase(nombre, mision):
    """Ejecuta una fase (Worker o Red Team) en Jules."""
    log(f"🚀 Lanzando {nombre}...")
    salida = ejecutar(['jules', 'new', mision])
    match = re.search(r"ID:\s+(\d+)", salida)
    
    if match:
        session_id = match.group(1)
        log(f"⏳ Esperando a {nombre} (ID: {session_id})...")
        exito = esperar_a_jules(session_id)
        return exito
    else:
        log(f"❌ Error lanzando {nombre}: {salida}")
        return False

# ==============================================================================
#  BUCLE PRINCIPAL (DOUBLE TAP)
# ==============================================================================

def main():
    log(f"🤖 CEO V53 - ARQUITECTURA DOUBLE TAP (WORKER + RED TEAM) - {REPO_NAME}")
    
    # 1. Asegurar estado inicial limpio
    ejecutar(['git', 'pull', 'origin', 'main', '--rebase'])
    
    ciclo_actual = 1
    # Hash inicial antes de empezar a trabajar
    hash_al_inicio_del_ciclo = obtener_git_hash() 
    
    while ciclo_actual <= MAX_CICLOS:
        log(f"\n🎬 === CICLO {ciclo_actual} ===")
        
        # Guardamos hash base para comparación futura
        current_hash_for_next_check = obtener_git_hash()
        
        # --- FASE 1: WORKER ---
        mision_worker = generar_mision_worker(ciclo_actual, hash_al_inicio_del_ciclo)
        
        if mision_worker == "STATUS: COMPLETADO":
            log("🏆 El Proyecto parece terminado.")
            break
            
        exito_worker = ejecutar_fase("WORKER", mision_worker)
        
        if not exito_worker:
            log("⚠️ El Worker falló. Saltando Red Team y reintentando ciclo...")
            continue
            
        # Sincronizamos tras el Worker para que el Red Team vea los cambios
        sincronizar_git(f"Jules V53 [Worker]: Ciclo {ciclo_actual}")
        
        # --- FASE 2: RED TEAM ---
        mision_red_team = generar_mision_red_team()
        exito_red_team = ejecutar_fase("RED TEAM", mision_red_team)
        
        if exito_red_team:
            sincronizar_git(f"Jules V53 [Red Team]: Ciclo {ciclo_actual} - Audit & Plan")
            
            # Actualizamos hash para el siguiente ciclo
            hash_al_inicio_del_ciclo = current_hash_for_next_check
            time.sleep(10)
        else:
            log("⚠️ El Red Team falló. Revisar logs.")

        ciclo_actual += 1

    log("\n🏁 PROCESO FINALIZADO.")

if __name__ == "__main__":
    main()