import subprocess
import time
import os
import re
import sys

# --- CONFIGURACIÓN ---
REPO_NAME = "juanlgantes/articulista"
ARCHIVO_ORDEN = "ORDEN_DEL_DIA.md"
ARCHIVO_SPECS = "SPECS.md"

def log(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] {msg}")

def ejecutar(cmd_list):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, cwd=os.getcwd())
        return res.stdout.strip() + "\n" + res.stderr.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def leer_archivo(ruta):
    if os.path.exists(ruta):
        with open(ruta, 'r') as f: return f.read().strip()
    return ""

def escribir_archivo(ruta, contenido):
    with open(ruta, 'w') as f: f.write(contenido)

def sincronizar_git(mensaje):
    """El ciclo sagrado de seguridad."""
    log("🔄 GIT: Sincronizando...")
    ejecutar(['git', 'pull', 'origin', 'main', '--rebase'])
    ejecutar(['git', 'add', '.'])
    stat = ejecutar(['git', 'commit', '-m', mensaje])
    if "nothing to commit" not in stat:
        ejecutar(['git', 'push', 'origin', 'main'])
        log("   ✅ Guardado en la nube.")
    else:
        log("   ℹ️ Sin cambios locales.")

def esperar_a_jules(session_id):
    """La espera activa (Ralph Wiggum Loop)."""
    log(f"⏳ Esperando resultados de Sesión {session_id}...")
    intentos = 0
    # Damos más tiempo porque crear webs es complejo
    while intentos < 60: 
        time.sleep(30)
        res = ejecutar(['jules', 'remote', 'pull', '--session', session_id, '--apply'])
        
        if "Patch applied successfully" in res or "Applied" in res:
            log(f"🎉 ¡CÓDIGO RECIBIDO! Jules ha entregado.")
            return True
        
        if "No such file" in res:
            sys.stdout.write(".") 
            sys.stdout.flush()
        else:
            # Si Jules da feedback de error, lo mostramos
            if "error" in res.lower():
                log(f"⚠️ Jules Error: {res}")
        intentos += 1
    
    log("❌ TIEMPO AGOTADO.")
    return False

def turno_arquitecto():
    """
    CEREBRO: Analiza qué falta y decide la siguiente tarea.
    No alucina tareas, mira los archivos reales.
    """
    log("🧠 TURNO: ARQUITECTO (Analizando proyecto...)")
    
    # 1. Comprobación de existencia de archivos clave
    tiene_specs = os.path.exists(ARCHIVO_SPECS)
    tiene_index = os.path.exists("index.html")
    tiene_css = os.path.exists("css/style.css")
    
    orden_actual = leer_archivo(ARCHIVO_ORDEN)
    
    # LÓGICA DE DECISIÓN
    nueva_orden = ""
    
    if not tiene_specs:
        log("   ⚠️ Faltan las especificaciones.")
        return False # No podemos trabajar sin specs
        
    if not tiene_index:
        log("   ⚠️ Falta index.html. Prioridad: Estructura.")
        nueva_orden = "Genera el archivo index.html semántico y responsive siguiendo SPECS.md. Usa Grid Layout para el Home."
        
    elif not tiene_css:
        log("   ⚠️ Falta CSS. Prioridad: Estilo.")
        nueva_orden = "Genera css/style.css siguiendo la Guía de Estilo de SPECS.md. Define variables CSS en :root."
        
    elif "STATUS: COMPLETADO" in orden_actual:
        log("   ✅ Todo parece en orden. Esperando nuevas directrices humanas.")
        return False
    else:
        # Si hay una orden manual pendiente, la respetamos
        log(f"   📋 Orden vigente detectada: {orden_actual[:40]}...")
        return True

    # Si el arquitecto decidió una nueva orden, la escribimos
    if nueva_orden and nueva_orden not in orden_actual:
        log(f"   📝 ARQUITECTO ESCRIBE ORDEN: {nueva_orden}")
        escribir_archivo(ARCHIVO_ORDEN, nueva_orden)
        return True
    
    return True

def turno_ingeniero():
    """
    BRAZO: Ejecuta la orden que haya en el archivo.
    """
    log("🔨 TURNO: INGENIERO (Ejecutando...)")
    
    mision = leer_archivo(ARCHIVO_ORDEN)
    if not mision or "STATUS: COMPLETADO" in mision:
        log("   💤 Nada que construir.")
        return

    # Lanzar a Jules
    salida = ejecutar(['jules', 'new', mision])
    match = re.search(r"ID:\s+(\d+)", salida)
    
    if match:
        session_id = match.group(1)
        log(f"   🚀 Jules trabajando. ID: {session_id}")
        
        exito = esperar_a_jules(session_id)
        if exito:
            # Firmamos la orden como completada
            escribir_archivo(ARCHIVO_ORDEN, f"{mision}\n\nSTATUS: COMPLETADO")
            sincronizar_git(f"Jules: {mision[:30]}...")
    else:
        log(f"   ❌ Error lanzando Jules: {salida}")

def main():
    log(f"🤖 CEO V47 (ARQUITECTURA COMPLETA) - {REPO_NAME}")
    
    if not os.path.exists(".git"):
        log("❌ ERROR: Ejecuta en la raíz del repo.")
        return

    # Ciclo de vida: Arquitecto -> Ingeniero -> Dormir
    # Hacemos 2 pases para asegurar (Estructura -> Estilos)
    for i in range(2):
        hay_trabajo = turno_arquitecto()
        if hay_trabajo:
            turno_ingeniero()
        else:
            break
        time.sleep(5)

    log("\n🏁 Ciclo finalizado. Revisa los resultados.")

if __name__ == "__main__":
    main()
