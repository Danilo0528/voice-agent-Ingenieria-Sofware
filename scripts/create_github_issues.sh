#!/usr/bin/env bash
# scripts/create_github_issues.sh
# Crea las issues en GitHub usando GitHub CLI (gh)
# Requiere: gh auth login

set -euo pipefail

if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI no instalado. Instala con: https://cli.github.com"
    exit 1
fi

echo "📋 Creando issues en GitHub..."

gh issue create \
  --title "Tracer Bullet: Pipeline de Voz End-to-End Mínimo" \
  --body-file issues/001-tracer-bullet-pipeline.md \
  --label "tracer-bullet,priority:high"

gh issue create \
  --title "Captura de Audio con Voice Activity Detection (VAD)" \
  --body-file issues/002-audio-capture-vad.md \
  --label "feature,audio"

gh issue create \
  --title "Speech-to-Text con Whisper (Local)" \
  --body-file issues/003-stt-whisper.md \
  --label "feature,stt"

gh issue create \
  --title "Cliente LLM con Historial de Conversación" \
  --body-file issues/004-llm-client.md \
  --label "feature,llm"

gh issue create \
  --title "Text-to-Speech con pyttsx3" \
  --body-file issues/005-tts-synthesizer.md \
  --label "feature,tts"

gh issue create \
  --title "Panel de Monitoreo Web con FastAPI + WebSockets" \
  --body-file issues/006-web-panel.md \
  --label "feature,frontend,backend"

gh issue create \
  --title "Infraestructura: CI con GitHub Actions" \
  --body-file issues/007-ci-github-actions.md \
  --label "infra"

echo "✅ Issues creadas. Verifica en: $(gh repo view --json url -q .url)/issues"
