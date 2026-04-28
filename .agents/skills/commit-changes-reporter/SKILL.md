---
name: commit-changes-reporter
description: >
  Genera documentación de cambios por commit leyendo el historial de Git.
  Usá esta skill SIEMPRE que el usuario pida “resumir commits”, “release notes”,
  “qué cambió entre X e Y”, “lista de archivos modificados por commit”, o
  necesite un documento por commit con resumen + archivos tocados. La salida se
  guarda en la carpeta commit-changes/ en la raíz del repo.
---

# Commit Changes Reporter

Esta skill genera un **documento Markdown por commit** con:

- Resumen (basado en el mensaje del commit)
- Metadata (SHA, autor, fecha)
- Archivos modificados (con `name-status`)
- Diffstat (líneas agregadas/eliminadas por archivo)

Los archivos se escriben en `commit-changes/` en la raíz del repositorio.

## Antes de correr

1) Asegurate de estar en un repo git.
2) Si el usuario NO especifica rango de commits, PREGUNTÁ y frená.

Rangos típicos:

- Últimos N commits: `--last 10`
- Entre tags/SHAs: `--range v1.2.0..v1.3.0` o `--range <sha1>..<sha2>`
- Desde un commit (inclusive) hasta HEAD: `--range <sha>..HEAD`

## Comando recomendado

Ejecutá el script:

```bash
python .agents/skills/commit-changes-reporter/scripts/generate_commit_changes.py
```

Por defecto (sin parámetros) genera docs **para lo que entró en el último `git pull`**.

Opcionales:

- `--out-dir commit-changes` (default)
- `--last 20` (si no querés range)
- `--range v1.2.0..HEAD` (si querés controlar el rango)
- `--since-last-pull` (fuerza modo “último pull”, aunque hayas pasado otros args)

## Qué produce

- `commit-changes/<YYYY-MM-DD>-<shortsha>-<slug>.md` por commit (en orden cronológico)
- `commit-changes/INDEX.md` con links a los documentos generados

## Reglas

- NO inventes cambios: el resumen sale del mensaje del commit y del diffstat.
- Si un commit tiene mensaje pobre (ej: “update”), marcá el resumen como “Mensaje no descriptivo” y listo.
- NO incluyas parches completos (mantenerlo “pequeño”).
