# Catálogo de épicos — Board v2

24 épicos em 3 trilhas.

## Trilha PRODUTO (13 épicos)

| ID | Nome | OKR | Repo | Tasks | SP | PERT (d) |
|----|------|-----|------|-------|-----|----------|
| E-P01 | Auth, sessão e pareamento | O3 | api | 13 | 36 | 13.4 |
| E-P02 | Localização e rotas Mapbox | O1 | api | 26 | 64 | 31.3 |
| E-P03 | Geofences e alertas | O1 | api | 8 | 40 | 17.4 |
| E-P04 | SOS e emergência | O1 | api | 12 | 54 | 28.5 |
| E-P05 | Push notifications nativas | O1 | parent | 11 | 32 | 16.7 |
| E-P06 | Tempo de tela e pedido extra | O3 | api | 13 | 37 | 19.1 |
| E-P07 | Gamificação e engajamento child | O3 | child | 6 | 12 | 6.3 |
| E-P08 | Família, mensagens e acesso | O3 | api | 11 | 29 | 14.6 |
| E-P09 | App parent — mapa, relatórios, IA | O3 | parent | 31 | 74 | 35.7 |
| E-P10 | App child — UX e estabilidade | O3 | child | 22 | 44 | 21.4 |
| E-P11 | LGPD e compliance produto | O2 | api | 12 | 54 | 23.5 |
| E-P12 | Backoffice operacional release | O2 | backoffice | 10 | 20 | 10.4 |
| E-P13 | Site institucional e campanha | O3 | site | 8 | 16 | 4.7 |

## Trilha INFRAESTRUTURA (6 épicos)

| ID | Nome | OKR | Repo | Tasks | SP | PERT (d) |
|----|------|-----|------|-------|-----|----------|
| E-I01 | AWS ECS Fargate foundation | O2 | api | 12 | 56 | 46.5 |
| E-I02 | CI/CD multi-repo | O2 | api | 12 | 36 | 19.0 |
| E-I03 | Observabilidade e alertas | O2 | api | 10 | 27 | 17.2 |
| E-I04 | PostgreSQL, Redis e migrations | O2 | api | 7 | 33 | 25.6 |
| E-I05 | Segurança, secrets e WAF | O2 | api | 6 | 28 | 17.4 |
| E-I06 | Ambientes staging e produção | O2 | api | 6 | 28 | 16.6 |

## Trilha STORES (5 épicos)

| ID | Nome | OKR | Repo | Tasks | SP | PERT (d) |
|----|------|-----|------|-------|-----|----------|
| E-S01 | Apple App Store parent | O2 | parent | 8 | 22 | 11.2 |
| E-S02 | Apple App Store child | O2 | child | 6 | 17 | 8.8 |
| E-S03 | Google Play parent | O2 | parent | 7 | 19 | 12.2 |
| E-S04 | Google Play child | O2 | child | 7 | 19 | 12.2 |
| E-S05 | Coordenação release e beta | O2 | api | 8 | 34 | 14.8 |

## Dependências críticas entre épicos

```
E-I01 + E-I04 → E-I06 → E-P* (API prod)
E-P05 → E-P03/E-P04 (push antes de E2E alertas)
E-P11 → E-S* (DPO antes de submit stores)
E-P02 → E-P03 (localização antes geofence UI)
```

## Lista completa de IDs

**Produto:** E-P01, E-P02, E-P03, E-P04, E-P05, E-P06, E-P07, E-P08, E-P09, E-P10, E-P11, E-P12, E-P13

**Infra:** E-I01, E-I02, E-I03, E-I04, E-I05, E-I06

**Stores:** E-S01, E-S02, E-S03, E-S04, E-S05
