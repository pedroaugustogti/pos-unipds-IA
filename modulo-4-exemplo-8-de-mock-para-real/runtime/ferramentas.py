"""
Ferramentas e Evidencias.

Resolve skills declarados em skills.md para implementacoes via adapters ou mocks.
O campo tipo_implementacao define como resolver:
  - mock    → LLM/deterministico (padrao)
  - rest    → rest_adapter.py chama API HTTP
  - database → db_adapter.py executa query parametrizada
  - mcp     → mcp_adapter.py conecta a MCP server

Skills sem tipo_implementacao usam mock (backward compatible).
Trace-analyzer e backlog-decomposer mantem implementacoes deterministicas do Ex. 7.
"""

import json
import os
import random
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*a, **kw): pass

load_dotenv(Path(__file__).parent / ".env")

from ferramentas_analise_reais import FERRAMENTAS_OBRIGATORIAS, IMPLEMENTACOES_ANALISE
from ferramentas_backlog_reais import IMPLEMENTACOES_BACKLOG
from ferramentas_monitor_reais import ferramenta_relatorio_incidente

_TOKENS_ZERO = {"prompt": 0, "completion": 0, "total": 0}

IMPLEMENTACOES_DETERMINISTICAS = {
    **IMPLEMENTACOES_ANALISE,
    **IMPLEMENTACOES_BACKLOG,
    "relatorio_incidente": ferramenta_relatorio_incidente,
}


def ferramenta_e_deterministica(nome: str) -> bool:
    return nome in IMPLEMENTACOES_DETERMINISTICAS


def agente_tem_somente_ferramentas_deterministicas(contratos: dict) -> bool:
    habilidades = contratos.get("habilidades", {}).get("habilidades", [])
    nomes = [habilidade.get("nome") for habilidade in habilidades if habilidade.get("nome")]
    return bool(nomes) and all(ferramenta_e_deterministica(nome) for nome in nomes)


def _carregar_trace_para_mock() -> dict:
    caminho = Path(__file__).parent / "trace.json"
    if not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def _chamar_llm_ferramenta(prompt_sistema: str, prompt_usuario: str, campos_saida: dict) -> tuple:
    chave_api = os.environ.get("OPENAI_API_KEY")
    if not chave_api:
        return None, _TOKENS_ZERO.copy()

    from openai import OpenAI

    cliente = OpenAI(api_key=chave_api)
    resposta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario},
        ],
    )

    uso_tokens = _TOKENS_ZERO.copy()
    if resposta.usage:
        uso_tokens = {
            "prompt": resposta.usage.prompt_tokens or 0,
            "completion": resposta.usage.completion_tokens or 0,
            "total": resposta.usage.total_tokens or 0,
        }

    try:
        return json.loads(resposta.choices[0].message.content), uso_tokens
    except (json.JSONDecodeError, IndexError):
        return None, uso_tokens


def construir_ferramenta(habilidade: dict):
    nome = habilidade.get("nome", "")
    descricao = habilidade.get("descricao", "")
    campos_saida = habilidade.get("saida", {})
    texto_saida = "\n".join(f"  - {campo}: {tipo}" for campo, tipo in campos_saida.items())

    prompt_sistema = f"""Voce e uma ferramenta chamada '{nome}'.
Funcao: {descricao}

Voce DEVE retornar APENAS JSON valido com exatamente estes campos:
{texto_saida}

Regras:
- Gere dados realistas e coerentes com os argumentos recebidos
- Responda em portugues"""

    def funcao(argumentos):
        prompt_usuario = f"Argumentos recebidos:\n{json.dumps(argumentos, indent=2, ensure_ascii=False)}"
        dados_llm, uso_tokens = _chamar_llm_ferramenta(prompt_sistema, prompt_usuario, campos_saida)
        if dados_llm:
            dados_llm["_entrada"] = argumentos
            return {"sucesso": True, "dados": dados_llm, "_tokens": uso_tokens}
        dados = {c: _gerar_valor_fallback(t, c) for c, t in campos_saida.items()}
        dados["_entrada"] = argumentos
        return {"sucesso": True, "dados": dados, "_tokens": _TOKENS_ZERO.copy()}

    return funcao


def _gerar_valor_fallback(tipo_campo: str, nome_campo: str):
    tipo_normalizado = tipo_campo.lower() if isinstance(tipo_campo, str) else "string"
    if tipo_normalizado == "float":
        return round(random.uniform(0.01, 100.0), 2)
    if tipo_normalizado == "int":
        return random.randint(1, 500)
    if tipo_normalizado == "bool":
        return random.choice([True, False])
    if tipo_normalizado == "list":
        return [{"item": f"{nome_campo}_1"}]
    if tipo_normalizado == "object":
        return {"campo": nome_campo}
    return f"{nome_campo}_valor"


def _resolver_adapter(habilidade: dict):
    tipo = habilidade.get("tipo_implementacao", "mock")

    if tipo == "rest":
        try:
            from adapters.rest_adapter import criar_funcao_rest
            return criar_funcao_rest(habilidade)
        except ImportError:
            print(f"  [adapters] rest_adapter nao encontrado, usando mock para {habilidade.get('nome')}")
            return construir_ferramenta(habilidade)

    if tipo == "database":
        try:
            from adapters.db_adapter import criar_funcao_database
            return criar_funcao_database(habilidade)
        except ImportError:
            print(f"  [adapters] db_adapter nao encontrado, usando mock para {habilidade.get('nome')}")
            return construir_ferramenta(habilidade)

    if tipo == "mcp":
        try:
            from adapters.mcp_adapter import criar_funcao_mcp
            return criar_funcao_mcp(habilidade)
        except ImportError:
            print(f"  [adapters] mcp_adapter nao encontrado, usando mock para {habilidade.get('nome')}")
            return construir_ferramenta(habilidade)

    return construir_ferramenta(habilidade)


def _wrap_deterministica(impl):
    def funcao(argumentos):
        try:
            return impl(argumentos or {})
        except Exception as erro:
            return {"sucesso": False, "erro": str(erro), "_tokens": _TOKENS_ZERO.copy()}
    return funcao


def construir_ferramentas_dos_contratos(contratos: dict) -> dict:
    habilidades = contratos.get("habilidades", {}).get("habilidades", [])
    ferramentas = {}
    for habilidade in habilidades:
        nome = habilidade.get("nome")
        if not nome:
            continue

        tipo = habilidade.get("tipo_implementacao", "mock")

        if tipo != "mock":
            ferramentas[nome] = _resolver_adapter(habilidade)
            print(f"  [ferramentas] {nome} → {tipo}")
        elif nome in IMPLEMENTACOES_DETERMINISTICAS:
            ferramentas[nome] = _wrap_deterministica(IMPLEMENTACOES_DETERMINISTICAS[nome])
        else:
            ferramentas[nome] = construir_ferramenta(habilidade)
    return ferramentas


def extrair_evidencias_do_historico(historico: list) -> dict:
    evidencias = {}
    for registro in historico:
        plano = registro.get("plano", {})
        resultado = registro.get("resultado_acao")
        nome_ferramenta = plano.get("nome_ferramenta")
        if resultado and resultado.get("sucesso") and nome_ferramenta:
            evidencias[nome_ferramenta] = resultado.get("dados", {})
    return evidencias


def _extrair_servico_da_entrada(historico: list, entrada: str = "") -> str:
    texto = entrada
    for registro in historico:
        texto += "\n" + registro.get("percepcao", "")
    match = re.search(r"servico de (\w+)", texto, re.I)
    return match.group(1) if match else "pagamentos"


def montar_argumentos_mock(habilidade: dict, historico: list, entrada: str = "") -> dict:
    evidencias = extrair_evidencias_do_historico(historico)
    trace = _carregar_trace_para_mock()
    nome = habilidade.get("nome", "")
    servico = _extrair_servico_da_entrada(historico, entrada)
    analise = evidencias.get("analisar_objetivo", {})
    epicos_dados = evidencias.get("gerar_epicos", {})
    stories_dados = evidencias.get("detalhar_stories", {})
    riscos_dados = evidencias.get("avaliar_riscos", {})
    perguntas_dados = evidencias.get("gerar_perguntas", {})

    if nome == "analisar_objetivo":
        return {"objetivo": entrada or "objetivo de produto", "contexto_adicional": ""}
    if nome == "gerar_epicos":
        return {
            "dominios": analise.get("dominios", []),
            "capacidades": analise.get("capacidades", []),
            "restricoes": analise.get("restricoes", []),
        }
    if nome == "detalhar_stories":
        return {
            "epicos": epicos_dados.get("epicos", []),
            "personas": analise.get("personas", []),
        }
    if nome == "avaliar_riscos":
        return {
            "epicos": epicos_dados.get("epicos", []),
            "stories": stories_dados.get("stories", []),
            "restricoes": analise.get("restricoes", []),
        }
    if nome == "gerar_perguntas":
        return {
            "epicos": epicos_dados.get("epicos", []),
            "riscos": riscos_dados.get("riscos", []),
            "restricoes": analise.get("restricoes", []),
        }
    if nome == "montar_backlog":
        return {
            "epicos": epicos_dados.get("epicos", []),
            "stories": stories_dados.get("stories", []),
            "criterios_aceite": stories_dados.get("criterios_aceite", []),
            "riscos": riscos_dados.get("riscos", []),
            "perguntas": perguntas_dados.get("perguntas", []),
        }
    if nome == "relatorio_incidente":
        metricas = evidencias.get("consultar_metricas", {})
        logs = evidencias.get("buscar_logs", {})
        deploys = evidencias.get("historico_deploys", {})
        return {
            "nome_servico": servico,
            "severidade": "alta",
            "evidencia": {
                "metricas": metricas,
                "logs": {"contagem_total": logs.get("contagem_total")},
                "deploys": deploys.get("contagem_total"),
            },
            "recomendacao": {"acao_1": "Verificar configuracao de chaves API"},
        }

    argumentos = {}
    for nome_campo, tipo_campo in habilidade.get("entrada", {}).items():
        tipo_normalizado = tipo_campo.lower() if isinstance(tipo_campo, str) else "string"
        if nome_campo == "nome_servico":
            argumentos[nome_campo] = servico
        elif nome_campo == "janela_tempo_minutos":
            argumentos[nome_campo] = 60
        elif nome_campo == "janela_tempo_horas":
            argumentos[nome_campo] = 24
        elif nome_campo == "nivel_minimo":
            argumentos[nome_campo] = "WARN"
        elif nome_campo == "health_metrics":
            argumentos[nome_campo] = trace.get("health_metrics", {})
        elif nome_campo == "etapas":
            argumentos[nome_campo] = trace.get("etapas", [])
        elif nome_campo == "performance_data":
            argumentos[nome_campo] = trace.get("performance_data", {})
        elif nome_campo == "ferramentas_esperadas":
            argumentos[nome_campo] = FERRAMENTAS_OBRIGATORIAS if nome == "analisar_conformidade" else []
        elif nome_campo == "saude" and evidencias.get("analisar_saude"):
            argumentos[nome_campo] = evidencias["analisar_saude"]
        elif nome_campo == "performance" and evidencias.get("analisar_performance"):
            argumentos[nome_campo] = evidencias["analisar_performance"]
        elif nome_campo == "conformidade" and evidencias.get("analisar_conformidade"):
            argumentos[nome_campo] = evidencias["analisar_conformidade"]
        elif nome_campo == "anomalias" and evidencias.get("detectar_anomalias"):
            argumentos[nome_campo] = evidencias["detectar_anomalias"].get("anomalias", [])
        else:
            argumentos[nome_campo] = _gerar_valor_fallback(tipo_campo, nome_campo)
    return argumentos
