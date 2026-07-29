"""Implementações determinísticas das skills do backlog-decomposer."""

_TOKENS_ZERO = {"prompt": 0, "completion": 0, "total": 0}


def _ok(dados: dict) -> dict:
    return {"sucesso": True, "dados": dados, "_tokens": _TOKENS_ZERO.copy()}


def ferramenta_analisar_objetivo(argumentos: dict) -> dict:
    objetivo = (argumentos or {}).get("objetivo", "objetivo de produto")
    return _ok({
        "dominios": ["onboarding", "autenticacao", "compliance"],
        "personas": [
            {"nome": "novo_usuario", "descricao": "Usuario que inicia cadastro sem ajuda humana"},
            {"nome": "admin_suporte", "descricao": "Equipe que monitora excecoes e fraudes"},
        ],
        "capacidades": [
            "cadastro_self_service",
            "validacao_dados_tempo_real",
            "ativacao_conta_automatica",
        ],
        "restricoes": [
            "sem_suporte_humano_no_fluxo_principal",
            "conformidade_lgpd",
        ],
        "_objetivo": objetivo,
    })


def ferramenta_gerar_epicos(argumentos: dict) -> dict:
    dominios = argumentos.get("dominios") or ["onboarding", "autenticacao"]
    return _ok({
        "epicos": [
            {
                "nome": "Onboarding self-service",
                "descricao": "Permitir cadastro completo sem intervencao humana",
                "dominio": dominios[0] if dominios else "onboarding",
            },
            {
                "nome": "Validacao e ativacao",
                "descricao": "Garantir dados validos e conta ativa ao final do fluxo",
                "dominio": dominios[1] if len(dominios) > 1 else "autenticacao",
            },
        ],
        "dependencias": [
            {"de": "Onboarding self-service", "para": "Validacao e ativacao", "tipo": "sequencial"},
        ],
    })


def ferramenta_detalhar_stories(argumentos: dict) -> dict:
    epicos = argumentos.get("epicos") or []
    stories = []
    criterios = []
    for epico in epicos:
        nome = epico.get("nome", "Epico")
        stories.append({
            "epico": nome,
            "titulo": f"Como novo_usuario, quero concluir {nome.lower()}, para usar o produto sem suporte",
            "estimativa": "M",
        })
        criterios.append({
            "story": stories[-1]["titulo"],
            "criterios": [
                "fluxo concluido em menos de 5 minutos",
                "mensagens de erro claras em portugues",
                "dados obrigatorios validados antes do submit",
            ],
        })
    if not stories:
        stories = [{
            "epico": "Onboarding",
            "titulo": "Como novo_usuario, quero me cadastrar, para acessar o sistema",
            "estimativa": "M",
        }]
        criterios = [{"story": stories[0]["titulo"], "criterios": ["cadastro concluido com sucesso"]}]
    return _ok({"stories": stories, "criterios_aceite": criterios})


def ferramenta_avaliar_riscos(argumentos: dict) -> dict:
    return _ok({
        "riscos": [
            {
                "descricao": "Integracao com provedor KYC pode atrasar go-live",
                "impacto": "alto",
                "probabilidade": "media",
            },
            {
                "descricao": "Volume de cadastros pode exigir fila assincrona",
                "impacto": "medio",
                "probabilidade": "media",
            },
        ],
        "mitigacoes": [
            "Definir fallback manual para casos de falha no KYC",
            "Load test com pico de 500 cadastros/hora antes do release",
        ],
    })


def ferramenta_gerar_perguntas(argumentos: dict) -> dict:
    return _ok({
        "perguntas": [
            {"stakeholder": "produto", "pergunta": "Qual volume esperado de cadastros por dia?"},
            {"stakeholder": "compliance", "pergunta": "Existe requisito regulatorio para retencao de dados?"},
            {"stakeholder": "engenharia", "pergunta": "Qual SLA maximo aceitavel para ativacao da conta?"},
        ],
        "prioridade_perguntas": ["volume de cadastros", "requisitos regulatorios", "SLA ativacao"],
    })


def ferramenta_montar_backlog(argumentos: dict) -> dict:
    epicos = argumentos.get("epicos") or []
    stories = argumentos.get("stories") or []
    criterios = argumentos.get("criterios_aceite") or []
    riscos = argumentos.get("riscos") or []
    perguntas = argumentos.get("perguntas") or []

    backlog = {
        "epicos": epicos,
        "stories": stories,
        "criterios_aceite": criterios,
        "riscos": riscos,
        "perguntas": perguntas,
    }
    resumo = (
        f"Backlog com {len(epicos)} epicos, {len(stories)} stories, "
        f"{len(riscos)} riscos e {len(perguntas)} perguntas"
    )
    return _ok({"backlog": backlog, "resumo": resumo})


IMPLEMENTACOES_BACKLOG = {
    "analisar_objetivo": ferramenta_analisar_objetivo,
    "gerar_epicos": ferramenta_gerar_epicos,
    "detalhar_stories": ferramenta_detalhar_stories,
    "avaliar_riscos": ferramenta_avaliar_riscos,
    "gerar_perguntas": ferramenta_gerar_perguntas,
    "montar_backlog": ferramenta_montar_backlog,
}
