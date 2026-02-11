# GEMINI Project Governance (Articulista Edition)

This document serves as the 'Constitution' for any AI agent working in the **Articulista** repository. It codifies the operational standards to ensure stability, SEO performance, and efficiency in our hybrid WSL/Windows environment.

## 1. Environment: WSL 2
- **Operating System Operations**: We definitively operate within **WSL 2**.
- **Path Prohibition**: **STRICTLY PROHIBITED** to use Windows paths (e.g., `/mnt/c/`) for git operations, file creation, or bulk editing. All filesystem operations must remain within the Linux user space.

## 2. File Protocol
- **Authorized Tools**: You must **ALWAYS** use `read_file` (or `view_file`) and `write_to_file` tools for all file manipulations.
- **Terminal Command Ban**: Do NOT use unstable terminal commands like `cp` or `mv` for file operations.

## 3. Local Server Standard
- **Execution**: Standardize all local server startups using:
  ```bash
  python3 -m http.server 8000
  ```
- **Navigation**: Access the application via [http://localhost:8000](http://localhost:8000).

## 4. Skills Integration
- **Responsive Auditing**: You are **MANDATED** to use the `responsive-auditor` skill for any tasks involving User Interface changes.
- **SEO Auditing**: You are **MANDATED** to use the `seo-semantic-auditor` skill when creating or updating content pages.
