import subprocess
import time
import os
import re

# --- CONFIGURACIÓN ---
MI_REPO = "juanlgantes/articulista"
RAMA_ACTIVA = "main"
ARCHIVO_ORDEN = "ORDEN_DEL_DIA.md"
ARCHIVO_MISION = "MISION.md"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def ejecutar_seguro(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True)
        return res.stdout.strip() + "\n" + res.stderr.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def debug_sistema_archivos():
    """FORENSE: Nos muestra qué demonios hay en el disco."""
    print("\n🔎 --- DEBUG: RASTREO DE ARCHIVOS ---")
    subprocess.run(['ls', '-R'], check=False)
    print("--------------------------------------\n")

def leer_archivo_local(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r') as f: return f.read()
    return ""

def limpiar_git_lock():
    lock = os.path.join(".git", "index.lock")
    if os.path.exists(lock): os.remove(lock)

def sincronizar_repo_local():
    limpiar_git_lock()
    subprocess.run(['git', 'pull', 'origin', RAMA_ACTIVA], check=False)
    subprocess.run(['git', 'add', '.'], check=False)
    estado = ejecutar_seguro(['git', 'status', '--porcelain'])
    if estado.strip():
        subprocess.run(['git', 'commit', '-m', "CEO: Guardando trabajo de Jules"], check=False)
        subprocess.run(['git', 'push', 'origin', RAMA_ACTIVA], check=False)
        log("💾 Sincronización Git realizada (Push local).")
    else:
        log("💾 Git dice: 'Nada nuevo que guardar'.")

def esperar_y_descargar(session_id, rol):
    log(f"⏳ Esperando a {rol} (Sesión {session_id})...")
    intentos = 0
    racha_silencio = 0 
    ultimo_mensaje = ""
    
    while intentos < 300: 
        time.sleep(30)
        res = ejecutar_seguro(['jules', 'remote', 'pull', '--session', session_id])
        res_limpia = res.strip()
        
        hay_datos_nuevos = (res_limpia != ultimo_mensaje) and ("diff --git" in res or "Downloaded" in res)
        ultimo_mensaje = res_limpia

        if hay_datos_nuevos:
            racha_silencio = 0 
            log(f"   ⚡ ACTIVIDAD REAL. Descargando cambios...")
            # MOMENTO FORENSE: Ver qué ha llegado
            debug_sistema_archivos()
        else:
            racha_silencio += 1
            minutos = racha_silencio * 0.5
            barra = "█" * int(minutos * 2)
            print(f"   [{intentos}] 🧘 Calma: {minutos} min / 3.0 min {barra}")
            
            if minutos >= 3.0: 
                log(f"\n✅ Turno finalizado (Timeout).")
                return True
            if "Ready for review" in res and racha_silencio >= 2:
                log(f"\n✅ Turno finalizado (Confirmado).")
                return True
        intentos += 1
    return False

def turno_arquitecto():
    log("\n" + "="*40)
    log("🏛️ TURNO: ARQUITECTO")
    log("="*40)
    
    sincronizar_repo_local()
    mision = leer_archivo_local(ARCHIVO_MISION)
    orden_actual = leer_archivo_local(ARCHIVO_ORDEN)
    
    instrucciones = f"""
    ERES EL ARQUITECTO.
    
    ESTADO ACTUAL (Leído del disco):
    --------------------------------------------------
    {orden_actual[:2000]}
    --------------------------------------------------
    
    TU TAREA:
    1. Si ves "STATUS: COMPLETADO" (o vacío), escribe la SIGUIENTE tarea técnica.
    2. Si hay tarea pendiente, no hagas nada.
    
    IMPORTANTE:
    - NO CREES CARPETAS para el archivo de órdenes.
    - Escribe el archivo '{ARCHIVO_ORDEN}' en la RAÍZ del directorio actual.
    - Usa: `echo "CONTENIDO" > {ARCHIVO_ORDEN}` si es necesario para asegurar la ruta.
    """
    instrucciones_linea = instrucciones.replace('\n', ' ').replace('  ', '')
    
    salida = ejecutar_seguro(['jules', 'remote', 'new', '--repo', MI_REPO, '--session', instrucciones_linea])
    match = re.search(r"ID:\s*(\d+)", salida)
    if not match: return
    
    if esperar_y_descargar(match.group(1), "ARQUITECTO"):
        sincronizar_repo_local()

def turno_ingeniero():
    log("\n" + "="*40)
    log("🔨 TURNO: INGENIERO")
    log("="*40)
    
    sincronizar_repo_local()
    orden_actual = leer_archivo_local(ARCHIVO_ORDEN)
    
    # DEBUG: ¿Qué ve el ingeniero?
    print(f"👀 CONTENIDO QUE VE EL INGENIERO:\n---\n{orden_actual[:200]}\n---")

    if "STATUS: COMPLETADO" in orden_actual:
        log("⚠️ El Arquitecto no ha puesto tarea nueva. Saltando turno...")
        return
    if not orden_actual.strip():
        log("⚠️ No hay órdenes (Archivo vacío o no existe). Saltando turno...")
        return

    instrucciones = f"""
    ERES EL INGENIERO.
    
    TU ORDEN:
    --------------------------------------------------
    {orden_actual[:2000]}
    --------------------------------------------------
    
    TU TAREA:
    1. Genera los archivos solicitados (HTML/CSS) EN LA RAÍZ (o carpetas css/js según corresponda).
    2. AL FINALIZAR, añade "\nSTATUS: COMPLETADO" a '{ARCHIVO_ORDEN}'.
    """
    instrucciones_linea = instrucciones.replace('\n', ' ').replace('  ', '')
    
    salida = ejecutar_seguro(['jules', 'remote', 'new', '--repo', MI_REPO, '--session', instrucciones_linea])
    match = re.search(r"ID:\s*(\d+)", salida)
    if not match: return
    
    if esperar_y_descargar(match.group(1), "INGENIERO"):
        sincronizar_repo_local()

def main():
    log(f"🚀 CEO V33 (THE FORENSIC): {MI_REPO}")
    debug_sistema_archivos() # Ver estado inicial
    
    while True:
        turno_arquitecto()
        log("⏳ Relevo (10s)...")
        time.sleep(10)
        
        turno_ingeniero()
        log("💤 Ciclo completo (10s)...")
        time.sleep(10)

if __name__ == "__main__":
    main()