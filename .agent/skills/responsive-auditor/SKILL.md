---
name: responsive-auditor
description: Validates mobile responsiveness, touch targets, and layout integrity across devices.
---

# Responsive Auditor Instructions

This skill acts as the Quality Assurance (QA) gate for the mobile and desktop experience.

## 📱 Viewport & Layout
- **Mandatory Meta Tag**: ensure `<meta name="viewport" content="width=device-width, initial-scale=1.0">` is present.
- **No Horizontal Scroll**: The layout must fit perfectly within the screen width (`100vw`) on mobile (375px).
- **Flex/Grid**: Use CSS Flexbox and Grid for layouts. Avoid fixed widths in pixels (use `%`, `vw`, or `rem`).

## 👆 Interaction Protocol
- **Touch Targets**: Buttons (especially `.btn` and nav links) MUST be at least **44x44 CSS pixels**.
- **Hover States**: Ensure `:hover` styles are present for desktop users but don't break mobile experience.

## 🖼️ Media
- **Images**: All `<img>` tags must have `max-width: 100%;` and `height: auto;` (or `object-fit`) to prevent overflow.
