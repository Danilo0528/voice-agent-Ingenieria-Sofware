# Skill: /prd-to-issues — PRD a Kanban de GitHub Issues

## Propósito

Convertir el `issues/prd.md` en issues individuales de GitHub bien estructuradas,
formando el backlog completo del proyecto.

## Cuándo usar

Después de `/write-a-prd`, cuando `issues/prd.md` ya existe y está aprobado.

## El Proceso

1. Lee `issues/prd.md` completo
2. Identifica cada módulo / user story como una issue independiente
3. Detecta dependencias entre issues (cuál bloquea a cuál)
4. Genera el texto de cada issue con la plantilla de abajo
5. Las issues se crean MANUALMENTE en GitHub (ver instrucciones)

## Plantilla de Issue

```markdown
## Descripción
[Qué hay que construir y por qué]

## Criterios de Aceptación
- [ ] [Criterio verificable 1]
- [ ] [Criterio verificable 2]
- [ ] Tests pasan

## Notas Técnicas
[Detalles de implementación, librerías, patrones a usar]

## Archivos a Crear/Modificar
- `src/...`
- `tests/...`

## Bloqueado por
- #[número de issue] (si aplica)
```

## Labels Recomendados

| Label | Uso |
|-------|-----|
| `tracer-bullet` | Issue de integración end-to-end (hacer primero) |
| `feature` | Nueva funcionalidad |
| `infra` | CI, configs, estructura |
| `bug` | Corrección de error |
| `blocked` | No se puede trabajar hasta resolver dependencia |

## Orden de Creación

1. Primero la **tracer bullet** (prueba end-to-end más arriesgada)
2. Luego **infra** (CI, estructura base)
3. Luego **features** en orden de dependencia
4. Al final **polish** y mejoras

## Regla Principal

Cada issue debe poder resolverse en una sola sesión de agente (`ralph/once.sh`).
Si una issue es demasiado grande, dividirla en sub-issues.
