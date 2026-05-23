# Skill: /grill-me — Interrogación del Brief

## Propósito

Clarificar todas las ambigüedades del Client Brief ANTES de escribir una sola línea de código.
Un brief vago produce código vago. Esta skill fuerza la precisión.

## Cuándo usar

Siempre que el usuario traiga una idea nueva, un brief, o una feature request.
Invocar ANTES de `/write-a-prd`.

## El Proceso

1. **Lee** el `client-brief.md` o el brief que el usuario provea
2. **Identifica** todas las ambigüedades, asunciones implícitas y decisiones no tomadas
3. **Interroga** al usuario sistemáticamente, una pregunta a la vez
4. **No avances** hasta tener respuesta clara a cada pregunta
5. **Documenta** las respuestas — serán la base del PRD

## Áreas de Interrogación

### Usuarios y Contexto
- ¿Quién es el usuario primario exactamente?
- ¿Qué sabe hacer / qué no sabe hacer?
- ¿En qué dispositivo / entorno usa esto?

### Funcionalidad Core
- ¿Qué es lo MÍNIMO que debe funcionar para que sea útil?
- ¿Qué pasa cuando X falla? (pregunta por cada componente crítico)
- ¿Hay casos borde que el usuario no mencionó?

### Criterios de Éxito
- ¿Cómo sabes que esto "funciona"?
- ¿Hay métricas? ¿Latencia? ¿Precisión?
- ¿Qué es "suficientemente bueno" para la primera entrega?

### Decisiones Técnicas
- ¿Hay restricciones de tecnología?
- ¿Qué debe ser local vs. en la nube?
- ¿Hay dependencias externas que podrían fallar?

### Scope
- ¿Qué está explícitamente FUERA del alcance?
- ¿Qué se deja para después?

## Reglas

- Una pregunta a la vez, esperar respuesta antes de continuar
- No hacer asunciones silenciosas
- Si la respuesta genera nuevas dudas, pregunta de nuevo
- Al finalizar, hacer un resumen de todo lo acordado para que el usuario confirme

## Ejemplo de Invocación

```
Usuario: /grill-me, el brief está en client-brief.md

Agente: [Lee el brief]
        Primera pregunta: "El brief menciona un 'loop en tiempo real'.
        ¿Cuál es la latencia máxima aceptable entre que el usuario
        termina de hablar y el agente empieza a responder?"
```
