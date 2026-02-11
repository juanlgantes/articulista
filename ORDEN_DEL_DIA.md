ID: 008
Título: Inicialización de Infraestructura de Calidad (Agent-QA)
Prioridad: Alta (Bloqueante para nuevos features)
Contexto: Transición al modelo "Agentic Engineering Pipeline". El estado actual carece de pruebas automatizadas persistentes y estándares de linting.

Descripción:
Para cumplir con la nueva arquitectura de agentes (The AI Squad), debemos establecer la base tecnológica para el Agent-QA y el Agent-Auditor. No se pueden desarrollar nuevas funcionalidades hasta que el pipeline de calidad esté operativo.

Tareas Técnicas:
1. **Documentación del Pipeline:**
   - Crear `docs/AGENTIC_PIPELINE.md` con la especificación completa del flujo de trabajo (Roles, Etapas, DoD).
2. **Infraestructura de Pruebas (Agent-QA):**
   - Configurar un framework de pruebas E2E persistente (Playwright) en la carpeta `tests/` (no `verification/`).
   - Crear un script de ejecución `npm test` o `python3 -m pytest` (según stack) que ejecute la suite.
3. **Estándares de Código (Agent-Auditor):**
   - Implementar configuración básica de Linting para HTML, CSS y JS (e.g., `.editorconfig`, ESLint, o scripts de validación).
4. **Primer Test Suite:**
   - Migrar las verificaciones actuales (Home, Privacy Policy) a tests formales que validen el "Happy Path".

---
NOTAS DEL AGENTE ANTERIOR:
- El proyecto cumple con los requisitos de performance (Lighthouse > 95).
- Se ha realizado una auditoría de imágenes y SEO.
- El código fuente CSS está en `css/style.original.css`.
