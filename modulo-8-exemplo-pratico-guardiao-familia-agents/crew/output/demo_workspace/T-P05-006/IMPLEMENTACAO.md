# Implementacao — `T-P05-006`

**Titulo:** Configurar FCM data messages SOS
**Agente:** frontend-mobile
**Repo alvo (mapa):** guardiao-familia-parent
**Gerado em:** 2026-08-24T17:45:41.147382+00:00
**Fonte board:** GitHub Project #2 (guardiaofamilia)

## Raciocinio do developer

SOS no Android/parent depende de **FCM data messages** (nao so notification message)
para o app processar payload mesmo em background. Esta entrega documenta o contrato
data message + handlers, com evidencia commitavel alinhada ao Project #2.

## O que foi implementado (didatico)

1. Distincao notification vs data message.
2. Payload minimo SOS (type, childId, lat/lng, ts).
3. Handlers foreground / background / killed.
4. Riscos (payload incompleto, token FCM invalido) e criterios QA-FCM.

## Matriz FCM data message SOS

| Item | Valor / decisao |
|------|-----------------|
| Canal | FCM data message |
| App | Parent Guardião Família |
| Payload | type=sos, childId, lat, lng, ts |
| Prioridade | high (SOS) |
| Segredo | server key / SA fora do git |

## Checklist

- [ ] Servidor envia data-only (ou data+notification) conforme contrato
- [ ] Parent registra handler data message
- [ ] Foreground nao descarta payload
- [ ] Background/killed acorda fluxo SOS
- [ ] Telemetria de latencia alinhada ao KR O1 (<30s)

## Riscos

| Risco | Mitigacao |
|-------|-----------|
| So notification message | Forcar data payload |
| Campos ausentes | Validar schema no client |
| Token FCM expirado | Re-registro device |

## Validacao QA

QA-FCM-01..06 (ver historico da task no dashboard)

## Pipeline

claim → implement → open_pr → review → QA → Done (Project #2)
