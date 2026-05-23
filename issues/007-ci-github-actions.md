# [AFK] Infraestructura: CI con GitHub Actions

**Labels:** `infra`, `priority:medium`

## Descripción

Configurar GitHub Actions para correr los tests automáticamente en cada push.

## Criterios de Aceptación

- [ ] `.github/workflows/ci.yml` corre `pytest` en cada push a `main` y PRs
- [ ] El workflow usa Python 3.11
- [ ] Los tests pasan en CI (los mocks reemplazan dependencias de hardware)
- [ ] El workflow reporta cobertura de código

## Notas

- Los tests NO deben requerir micrófono, modelo Whisper descargado, ni API keys
- Usar `pytest-mock` y `unittest.mock` para todas las dependencias externas
- Audio de prueba generado programáticamente con numpy

## Archivos a Crear

- `.github/workflows/ci.yml`
- `.env.example` (con todas las variables de entorno documentadas)
