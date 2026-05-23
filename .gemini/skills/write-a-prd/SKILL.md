# Skill: /write-a-prd — Product Requirements Document

## Propósito

Convertir el brief clarificado (output de `/grill-me`) en un PRD estructurado
guardado en `issues/prd.md`. Este documento es la fuente de verdad para todo
el desarrollo del semestre.

## Cuándo usar

Después de `/grill-me`. Nunca antes — el PRD sin interrogación previa es basura.

## El Proceso

1. **Pide** una descripción larga y detallada del problema y soluciones posibles
2. **Explora** el repo para entender la estructura existente
3. **Entrevista** al usuario sobre cada aspecto del plan (puede tomar múltiples rondas)
4. **Dibuja** los módulos principales que hay que construir o modificar
5. **Genera** el PRD usando la plantilla de abajo y lo guarda en `issues/prd.md`

## Plantilla del PRD

```markdown
# PRD: [Nombre del Proyecto]

## 1. Problema
[Descripción clara del problema que resuelve]

## 2. Usuarios
[Quién lo usa y en qué contexto]

## 3. Solución Propuesta
[Descripción de alto nivel de la solución]

## 4. Pipeline / Arquitectura
[Diagrama o descripción del flujo principal]

## 5. Módulos a Construir
[Lista de componentes con su responsabilidad]

## 6. User Stories
[Formato: Como [usuario], quiero [acción] para [beneficio]]

## 7. Criterios de Aceptación
[Qué debe ser verdad para considerar cada story "done"]

## 8. Decisiones Técnicas
[Stack, librerías elegidas y por qué]

## 9. Decisiones de Testing
[Qué se testea, cómo, con qué herramientas]

## 10. Fuera de Alcance
[Qué explícitamente NO se construye ahora]

## 11. Riesgos Técnicos
[Qué podría salir mal y cómo se mitiga]
```

## Reglas

- El PRD debe ser lo suficientemente detallado para que un agente pueda implementar sin preguntar
- Cada decisión técnica debe tener justificación
- Los criterios de aceptación deben ser verificables (no "funciona bien", sino "latencia < 2s")
- Guardar siempre en `issues/prd.md`
