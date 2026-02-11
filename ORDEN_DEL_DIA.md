## Resumen de Cambios
- [x] Optimizado `<title>` y `<meta description>` en `index.html`.
- [x] Generado `sitemap.xml` incluyendo todas las páginas.
- [x] Creado `robots.txt` para gestión de crawlers.

--- PROTOCOLO DE CALIDAD (SINGLE TAP) ---
1. EJECUCIÓN: Implementa SOLAMENTE el siguiente paso lógico. NO intentes terminar todo el proyecto de golpe.
   - PRINCIPIO: Calidad > Cantidad.
   - PRINCIPIO: Cero Alucinaciones.
2. PLANIFICACIÓN OBLIGATORIA: Al terminar, DEBES escribir/sobrescribir el archivo 'ORDEN_DEL_DIA.md'.
   - Contenido: Instrucciones técnicas precisas para el SIGUIENTE ciclo (lo que falta por hacer).
   - Si el proyecto terminó, escribe 'STATUS: COMPLETADO'.
   - ⚠️ IMPORTANTE: Si no escribes este archivo con el plan futuro, el ciclo se romperá.

3. CONTEXTO HISTÓRICO:
   - Antes de empezar, LEE el archivo 'TRT_REFLECTION_LOG.md'.
   - Contiene tus errores pasados y tu constitución de calidad. OBEDÉCELOS.

## Instrucciones para el Siguiente Ciclo
ID: 007
Título: Performance Audit & Minification
Prioridad: Media
Descripción: Para mantener el score de Lighthouse > 95, debemos asegurar que el CSS y JS estén optimizados.
Tareas Técnicas:
1. Auditar tamaño de imágenes (placeholders).
2. Minificar `style.css` (manual o script simple).
3. Verificar carga diferida (lazy loading) en todas las imágenes.
4. Ejecutar validación final de HTML W3C.
