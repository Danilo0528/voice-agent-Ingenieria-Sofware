#!/usr/bin/env bash
# setup_github.sh — Inicializa el repo Git y lo prepara para GitHub
# Ejecutar UNA VEZ después de clonar o crear el proyecto

set -euo pipefail

echo "🚀 Inicializando repositorio Git para voice-agent..."

# Inicializar git
git init
git branch -M main

# Primer commit
git add .
git commit -m "chore: initial project structure

- README con metodología AFK Agent (Gemini CLI)
- Client Brief en docs/
- Estructura de directorios src/, tests/, issues/
- pyproject.toml con dependencias
- Issues del backlog (001-007)
- Skills de Gemini CLI (.gemini/skills/tdd/)
- Script del agente (ralph/prompt.md + once.sh)
- Pipeline base con tests (tracer bullet parcial)
- CI con GitHub Actions
- .env.example

Usando Gemini CLI como herramienta principal de desarrollo.
Metodología: AFK Agent Workflow por Matt Pocock (AI Hero)"

echo ""
echo "✅ Repo inicializado con commit inicial."
echo ""
echo "Siguiente paso: crear el repo en GitHub y hacer push:"
echo ""
echo "  gh repo create voice-agent --public --push"
echo ""
echo "O si prefieres manual:"
echo "  git remote add origin https://github.com/TU_USUARIO/voice-agent.git"
echo "  git push -u origin main"
echo ""
echo "Luego crea las issues en GitHub con:"
echo "  bash scripts/create_github_issues.sh"
