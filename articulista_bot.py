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

def leer_archivo_local(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r') as f: return f.read()
    return ""

def limpiar_git_lock():
    lock = os.path.join(".git", "index.lock")
    if os.path.exists(lock): os.remove(lock)

def sincronizar_repo_local():
    """El Script se encarga de Git, no Jules."""
    limpiar_git_lock()
    # 1. Traer cambios remotos
    subprocess.run(['git', 'pull', 'origin', RAMA_ACTIVA], check=False)
    # 2. Guardar cambios locales (los que trajo Jules)
    subprocess.run(['git', 'add', '.'], check=False)
    # Solo hacemos commit si hay cambios
    estado = ejecutar_seguro(['git', 'status', '--porcelain'])
    if estado.strip():
        subprocess.run(['git', 'commit', '-m', "CEO: Guardando trabajo de Jules"], check=False)
        subprocess.run(['git', 'push', 'origin', RAMA_ACTIVA], check=False)
        log("💾 Sincronización Git realizada (Push local).")

def esperar_y_descargar(session_id, rol):
    log(f"⏳ Esperando a {rol} (Sesión {session_id})...")
    intentos = 0
    racha_silencio = 0 
    ultimo_mensaje = ""
    
    while intentos < 300: 
        time.sleep(30)
        # ESTA ES LA CLAVE: 'pull' descarga los archivos de Jules a TU carpeta
        res = ejecutar_seguro(['jules', 'remote', 'pull', '--session', session_id])
        res_limpia = res.strip()
        
        hay_datos_nuevos = (res_limpia != ultimo_mensaje) and ("diff --git" in res or "Downloaded" in res)
        ultimo_mensaje = res_limpia

        if hay_datos_nuevos:
            racha_silencio = 0 
            log(f"   ⚡ ACTIVIDAD REAL. Descargando cambios de {rol} al disco local...")
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
    
    # 1. Sincronizamos antes de empezar
    sincronizar_repo_local()
    
    # 2. Leemos estado LOCAL (Lo que tienes en tu disco)
    mision = leer_archivo_local(ARCHIVO_MISION)
    orden_actual = leer_archivo_local(ARCHIVO_ORDEN)
    
    # 3. Inyectamos estado al prompt
    instrucciones = f"""
    ERES EL ARQUITECTO. NO USES GIT.
    
    ESTADO ACTUAL DEL PROYECTO (Leído del disco):
    --------------------------------------------------
    {orden_actual[:2000]}
    --------------------------------------------------
    
    TU TAREA:
    1. Si ves "STATUS: COMPLETADO", borra todo y escribe la SIGUIENTE tarea técnica en '{ARCHIVO_ORDEN}'.
    2. Si el archivo está vacío, escribe la PRIMERA tarea.
    3. Si ya hay una tarea pendiente (sin completar), NO HAGAS NADA.
    
    SOLO EDITA EL ARCHIVO. NO HAGAS GIT PUSH.
    """
    instrucciones_linea = instrucciones.replace('\n', ' ').replace('  ', '')
    
    salida = ejecutar_seguro(['jules', 'remote', 'new', '--repo', MI_REPO, '--session', instrucciones_linea])
    match = re.search(r"ID:\s*(\d+)", salida)
    if not match: return
    
    # 4. Esperamos y DESCARGAMOS lo que haga
    if esperar_y_descargar(match.group(1), "ARQUITECTO"):
        # 5. Guardamos nosotros
        sincronizar_repo_local()

def turno_ingeniero():
    log("\n" + "="*40)
    log("🔨 TURNO: INGENIERO")
    log("="*40)
    
    sincronizar_repo_local()
    orden_actual = leer_archivo_local(ARCHIVO_ORDEN)
    
    if "STATUS: COMPLETADO" in orden_actual:
        log("⚠️ El Arquitecto no ha puesto tarea nueva. Saltando turno...")
        return
    if not orden_actual.strip():
        log("⚠️ No hay órdenes. Saltando turno...")
        return

    instrucciones = f"""
    ERES EL INGENIERO. NO USES GIT.
    
    TU ORDEN (Leída del disco):
    --------------------------------------------------
    {orden_actual[:2000]}
    --------------------------------------------------
    
    TU TAREA:
    1. Genera/Edita los archivos de código (HTML/CSS/JS) solicitados.
    2. AL FINALIZAR, añade "\nSTATUS: COMPLETADO" al final de '{ARCHIVO_ORDEN}'.
    
    SOLO EDITA ARCHIVOS. NO HAGAS GIT PUSH.
    """
    instrucciones_linea = instrucciones.replace('\n', ' ').replace('  ', '')
    
    salida = ejecutar_seguro(['jules', 'remote', 'new', '--repo', MI_REPO, '--session', instrucciones_linea])
    match = re.search(r"ID:\s*(\d+)", salida)
    if not match: return
    
    if esperar_y_descargar(match.group(1), "INGENIERO"):
        sincronizar_repo_local()

def main():
    log(f"🚀 CEO V32 (THE SECRETARY - LOCAL SYNC): {MI_REPO}")
    
    while True:
        turno_arquitecto()
        log("⏳ Relevo (10s)...")
        time.sleep(10)
        
        turno_ingeniero()
        log("💤 Ciclo completo (10s)...")
        time.sleep(10)

if __name__ == "__main__":
    main()