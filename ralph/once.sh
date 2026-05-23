#!/usr/bin/env bash
# ralph/once.sh — Ejecuta el agente Gemini CLI en una issue del backlog
# Adaptado de la metodología AFK de Matt Pocock (AI Hero)
# Original usa Claude Code; este script usa Gemini CLI (gratuito)

set -euo pipefail

# ─── Colores ────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🤖 Ralph — AFK Agent Runner (Gemini CLI Edition)${NC}"
echo "=================================================="

# ─── Verificar que Gemini CLI esté instalado ───────────────────────────────
if ! command -v gemini &> /dev/null; then
    echo -e "${RED}❌ Gemini CLI no está instalado.${NC}"
    echo "Instala con: npm install -g @google/gemini-cli"
    exit 1
fi

# ─── Leer issues abiertas ──────────────────────────────────────────────────
ISSUES_DIR="issues"
ISSUES=""

if [ -d "$ISSUES_DIR" ]; then
    for f in "$ISSUES_DIR"/*.md; do
        [ -f "$f" ] || continue
        ISSUES+="### $(basename "$f")\n"
        ISSUES+="$(cat "$f")\n\n"
    done
fi

if [ -z "$ISSUES" ]; then
    echo -e "${YELLOW}⚠️  No hay issues en issues/. Crea al menos una antes de correr el agente.${NC}"
    exit 0
fi

# ─── Leer últimos 5 commits ────────────────────────────────────────────────
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null || echo "No hay commits aún")

# ─── Construir prompt completo ─────────────────────────────────────────────
PROMPT_FILE="ralph/prompt.md"
if [ ! -f "$PROMPT_FILE" ]; then
    echo -e "${RED}❌ No se encontró ralph/prompt.md${NC}"
    exit 1
fi

AGENT_PROMPT=$(cat "$PROMPT_FILE")

FULL_PROMPT="$AGENT_PROMPT

---

## Issues Abiertas (tu backlog)

$ISSUES

---

## Últimos 5 Commits (contexto de lo hecho)

$RECENT_COMMITS

---

## Instrucción

Elige la issue de mayor prioridad (según el orden definido arriba) que NO tenga [HITL].
Trabaja en ella completamente siguiendo el flujo TDD.
Cuando termines, haz commit y mueve la issue a issues/done/.
Solo trabaja en UNA issue.
"

# ─── Ejecutar Gemini CLI ────────────────────────────────────────────────────
echo -e "${GREEN}📋 Issues encontradas:${NC}"
ls issues/*.md 2>/dev/null | xargs -I{} basename {} || echo "  (ninguna)"
echo ""
echo -e "${GREEN}📝 Últimos commits:${NC}"
echo "$RECENT_COMMITS"
echo ""
echo -e "${YELLOW}🚀 Iniciando agente Gemini CLI...${NC}"
echo "Modo: Human-in-the-Loop (tú apruebas cada acción)"
echo ""

# Pasar el prompt al agente
echo "$FULL_PROMPT" | gemini --yolo

echo ""
echo -e "${GREEN}✅ Agente terminó su ciclo.${NC}"
echo ""
echo "Revisa qué hizo:"
echo "  git log --oneline -3"
echo "  git diff HEAD~1"
