# ESPECIFICACIONES DEL PROYECTO: ARTICULISTA

## 1. Visión General
**Nombre:** ARTICULISTA
**Descripción:** Plataforma web minimalista y ultra-rápida enfocada en nichos de afiliación.
**Objetivo Principal:** Monetización a través de enlaces de referidos (ej. Amazon), priorizando SEO y velocidad de carga.

## 2. Stack Tecnológico
- **Lenguajes:** HTML5 Semántico, CSS3 Moderno, Vanilla JavaScript.
- **Frameworks:** NINGUNO (Prohibido React, Vue, Bootstrap, etc. para maximizar velocidad).
- **Entorno:** Servidor estático (Python http.server o similar).

## 3. Requisitos de Rendimiento
- **Google Lighthouse:** Score > 95 en todas las métricas (Performance, Accessibility, Best Practices, SEO).
- **Diseño:** Mobile-First, Responsive.

## 4. Estructura del Sitio
- **Home:** Layout tipo Grid mostrando artículos destacados.
- **Post Template:** Plantilla de artículo optimizada para lectura con Call to Actions (CTAs) claros.
- **Componentes Comunes:**
    - Sidebar/Footer para enlaces legales y de afiliado.
    - Navegación simplificada.

## 5. Guía de Estilo (Design System)
- **Tipografía:**
    - UI/Encabezados: Sans Serif (System Stack / Helvetica).
    - Cuerpo de texto: Serif (Georgia) para mejor legibilidad.
- **Paleta de Colores:**
    - Primario: #2c3e50 (Azul/Gris - Confianza).
    - Secundario: #ecf0f1 (Gris Claro - Fondo/Estructura).
    - Acento/CTA: #e67e22 (Naranja - Conversión) o #27ae60 (Verde - Éxito).
- **Layout:** Uso de CSS Flexbox y Grid. Elementos ocultos deben usar `visibility: hidden` si se requiere mantener estructura en grids.

## 6. Convenciones
- **Idioma:** Español (Código, Comentarios, Documentación).
- **Archivos:**
    - Estilos: `css/style.css` (Variables CSS en :root).
    - Scripts: `js/`
    - Imágenes: `img/`

## 7. Agradecimientos
Gracias a todo el equipo de desarrollo y colaboradores por su dedicación en este proyecto.
