# Implementacao — `T-P05-005`

**Titulo:** Configurar APNs production certificates
**Agente:** frontend-mobile
**Repo alvo (mapa):** guardiao-familia-parent
**Gerado em:** 2026-08-24T16:52:30.020870+00:00

## Raciocinio do developer

Push no Guardião Família (SOS/alertas) depende de APNs **production** no parent app.
Sandbox mascara falhas de certificado e bundle. Esta entrega documenta a matriz
de configuracao e os riscos, com evidencia commitavel para CR e QA.

## O que foi implementado (didatico)

1. Matriz APNs production (ambiente, credencial, bundle).
2. Checklist de configuracao no parent app / provedor de push.
3. Riscos e mitigacoes (sandbox vs prod, cert expirado, token invalido).
4. Criterios de validacao que o QA usara (foreground/background/smoke).

## Matriz APNs

| Item | Valor / decisao |
|------|-----------------|
| Ambiente | **production** (nao sandbox) |
| App | Parent app Guardião Família |
| Bundle id | Documentar o bundle de producao do parent (mapa da task) |
| Credencial | Auth Key `.p8` (preferencial) ou certificado `.p12` |
| Provedor | Expo Notifications / bridge FCM-APNs / APNs direto |
| Segredo | Fora do git; apenas referencia no runbook |

## Checklist de configuracao

- [ ] Criar/renovar chave ou certificado no Apple Developer (production)
- [ ] Associar Team ID + Key ID (ou cert) ao provedor de push
- [ ] Confirmar bundle id do target de producao
- [ ] Remover/ignorar credencial sandbox no profile de release
- [ ] Registrar data de expiracao / rotacao da chave

## Riscos e mitigacoes

| Risco | Sintoma | Mitigacao |
|-------|---------|-----------|
| Ambiente sandbox em release | Push falha so em TestFlight/App Store | Travar profile production |
| Certificado expirado | 403/InvalidProviderToken | Renovar `.p8`/`.p12` e rotacionar |
| Bundle mismatch | Device nao registra token | Alinhar bundle id parent |
| Token device invalido | Silent fail no destinatario | Re-opt-in notificacoes |

## Validacao sugerida (QA)

- QA-APNS-01 credencial production
- QA-APNS-02 bundle id coerente
- QA-APNS-03 push foreground
- QA-APNS-04 push background / killed
- QA-APNS-05 falha controlada (cert/ambiente)
- QA-APNS-06 smoke SOS / alerta familiar

## Pipeline da demo

claim → implement/commit → open_pr → review → QA → Done (HITL)
