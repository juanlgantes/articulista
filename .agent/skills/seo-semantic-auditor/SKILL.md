---
name: seo-semantic-auditor
description: Ensures HTML semantics, meta tags, and accessibility for optimal SEO ranking.
---

# SEO & Semantic Auditor Instructions

This skill ensures that the content is optimized for search engines and accessibility.

## 🏗️ Semantic Structure
- **Hierarchy**: Use exactly one `<h1>` per page. Use `<h2>`, `<h3>` sequentially.
- **Landmarks**: Use `<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>` correctly.
- **Links**: internal links should use generic anchor text where possible, maximizing crawlability.

## 🏷️ Meta Tags & Head
- **Title**: Must be unique and descriptive (< 60 chars).
- **Description**: Must be persuasive (< 160 chars).
- **Canonical**: If applicable, ensure canonical tags are present.

## ♿ Accessibility (A11y)
- **Alt Text**: All `<img>` tags MUST have a descriptive `alt` attribute.
- **Contrast**: Text must have sufficient contrast ratio against background.
- **ARIA**: Use ARIA labels only when semantic HTML is insufficient.
