## Purpose

Permitir que palestrantes enviem propostas de palestra (Call for Papers) através de um formulário web, com validação consistente entre frontend e backend usando o contrato `SpeakerDTO`.

## ADDED Requirements

### Requirement: Speaker can submit a talk proposal

O sistema MUST aceitar uma submissão de palestra contendo `id`, `name`, `email`, `talkTitle` e `isGDE`, conforme o contrato `SpeakerDTO` exportado por `@cfp-platform/shared-types`.

#### Scenario: Successful submission with valid payload

- **WHEN** o cliente envia `POST /api/cfp` com todos os campos obrigatórios válidos
- **THEN** o sistema MUST responder com status `201 Created`
- **AND** o corpo da resposta MUST conter os dados da submissão aceita

#### Scenario: Rejected submission with invalid payload

- **WHEN** o cliente envia `POST /api/cfp` com campos ausentes, tipos incorretos ou valores inválidos
- **THEN** o sistema MUST responder com status `400 Bad Request`
- **AND** o corpo da resposta MUST descrever os erros de validação

### Requirement: Frontend form reflects SpeakerDTO contract

O formulário de submissão MUST coletar exatamente os campos definidos em `SpeakerDTO`: `id`, `name`, `email`, `talkTitle` e `isGDE`.

#### Scenario: Form displays all required fields

- **WHEN** o usuário acessa a página de submissão CFP
- **THEN** o formulário MUST exibir campos para `name`, `email`, `talkTitle` e `isGDE`
- **AND** o campo `id` MUST ser gerado ou preenchido antes do envio

#### Scenario: Submit blocked when form is invalid

- **WHEN** o formulário contém campos obrigatórios vazios ou inválidos
- **THEN** o botão de envio MUST permanecer desabilitado
- **AND** nenhuma requisição HTTP MUST ser disparada

### Requirement: Frontend is accessible

O formulário de submissão MUST seguir práticas WAI-ARIA para acessibilidade.

#### Scenario: Form fields are labeled for assistive technologies

- **WHEN** um leitor de tela navega pelo formulário
- **THEN** cada campo MUST ter um rótulo associado (`label` ou `aria-label`)
- **AND** mensagens de erro MUST ser anunciáveis via `aria-live` ou `role="alert"`

### Requirement: Unit tests cover critical behavior

O sistema MUST incluir testes unitários Jest cobrindo os comportamentos críticos de validação e estado.

#### Scenario: API rejects invalid payloads in tests

- **WHEN** um teste envia payload inválido ao endpoint de submissão
- **THEN** o teste MUST verificar resposta `400 Bad Request`

#### Scenario: Angular form initial state is tested

- **WHEN** o componente de formulário é instanciado em teste
- **THEN** o teste MUST verificar o estado inicial do Signal de formulário
- **AND** o teste MUST verificar que o botão de envio está desabilitado
