import subprocess
import time
import os
import re
import sys

# --- CONFIGURACIÓN ---
REPO_NAME = "juanlgantes/articulista"
ARCHIVO_ORDEN = "ORDEN_DEL_DIA.md"
MAX_ITERACIONES = 1  # Solo 1 vuelta para probar la creación de la web

def log(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] {msg}")

def ejecutar(cmd_list, check=False):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True, cwd=os.getcwd())
        return res.stdout.strip() + "\n" + res.stderr.strip()
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"

def sincronizar_git(mensaje):
    """Ciclo: Pull Rebase -> Add -> Commit -> Push"""
    log("🔄 Sincronizando con GitHub...")
    ejecutar(['git', 'pull', 'origin', 'main', '--rebase'])
    ejecutar(['git', 'add', '.'])
    stat = ejecutar(['git', 'commit', '-m', mensaje])
    
    if "nothing to commit" in stat:
        log("   ℹ️ Nada nuevo que subir.")
    else:
        # Intentamos push, si falla forzamos
        res_push = ejecutar(['git', 'push', 'origin', 'main'])
        if "rejected" in res_push:
            log("⚠️ Push rechazado. Intentando fusión forzada...")
            ejecutar(['git', 'pull', 'origin', 'main', '--allow-unrelated-histories'])
            ejecutar(['git', 'push', 'origin', 'main'])
        else:
            log("   ✅ Git Push completado.")

def esperar_y_aplicar(session_id):
    log(f"⏳ Jules está construyendo la web (Sesión {session_id})...")
    intentos = 0
    max_intentos = 60 # 30 minutos (el código web puede tardar más que un texto)
    
    while intentos < max_intentos:
        time.sleep(30)
        res = ejecutar(['jules', 'remote', 'pull', '--session', session_id, '--apply'])
        
        if "Patch applied successfully" in res or "Applied" in res:
            log(f"🎉 ¡ÉXITO! Estructura web recibida.")
            return True
        
        if "No such file" in res:
            sys.stdout.write(".") 
            sys.stdout.flush()
        else:
            print(f"[{intentos}] Jules Status: {res[:50]}...")
        intentos += 1
        
    log("❌ TIEMPO AGOTADO.")
    return False

def leer_orden():
    if os.path.exists(ARCHIVO_ORDEN):
        with open(ARCHIVO_ORDEN, 'r') as f:
            return f.read().strip()
    return "Revisar estado del proyecto"

def main():
    log(f"🚀 CEO V46 (ARTICULISTA BUILDER) - {REPO_NAME}")
    
    # 0. Sincronización preventiva (para subir el SPECS.md si no se ha subido)
    sincronizar_git("Sync inicial antes de empezar")

    iteracion = 1
    mision = leer_orden()
    
    log(f"📋 Misión detectada: {mision}")
    log("---------------------------------------------------")

    # 1. Lanzar a Jules
    salida_new = ejecutar(['jules', 'new', mision])
    
    # 2. Capturar ID
    match = re.search(r"ID:\s+(\d+)", salida_new)
    
    if match:
        session_id = match.group(1)
        log(f"🏗️  Jules ha empezado a programar. ID: {session_id}")
        
        # 3. Esperar resultado
        if esperar_y_aplicar(session_id):
            # 4. Sincronizar resultado
            sincronizar_git(f"Jules: Estructura Web v1.0 ({session_id})")
            log(f"✅ Misión cumplida. Revisa los archivos .html y .css creados.")
        else:
            log("⚠️ La tarea falló.")
    else:
        log(f"❌ Error al lanzar tarea. Salida:\n{salida_new}")

if __name__ == "__main__":
    main()
