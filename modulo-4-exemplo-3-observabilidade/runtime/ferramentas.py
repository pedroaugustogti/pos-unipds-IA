"""
Ferramentas e Evidencias.

Cada ferramenta usa a LLM para gerar dados reais baseados no contexto.
Sem API key, usa fallback mock simples.
Inclui consumo de tokens (_tokens) no resultado para rastreamento.
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
from ferramentas_monitor_reais import IMPLEMENTACOES_MONITOR

_TOKENS_ZERO = {"prompt": 0, "completion": 0, "total": 0}

IMPLEMENTACOES_DETERMINISTICAS = {**IMPLEMENTACOES_MONITOR, **IMPLEMENTACOES_ANALISE}


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
    """Chama a LLM para gerar a saida de uma ferramenta.

    Retorna (dados, uso_tokens). dados=None se falhar ou sem API key.
    """
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
    """Cria uma funcao que usa a LLM para gerar dados reais."""
    nome = habilidade.get("nome", "")
    descricao = habilidade.get("descricao", "")
    campos_saida = habilidade.get("saida", {})
    campos_entrada = habilidade.get("entrada", {})

    texto_saida = "\n".join(f"  - {campo}: {tipo}" for campo, tipo in campos_saida.items())

    prompt_sistema = f"""Voce e uma ferramenta chamada '{nome}'.
Funcao: {descricao}

Voce DEVE retornar APENAS JSON valido com exatamente estes campos:
{texto_saida}

Regras:
- Gere dados realistas e coerentes com os argumentos recebidos
- Para campos do tipo 'list', retorne uma lista de objetos com detalhes reais
- Para campos do tipo 'object', retorne um objeto estruturado com dados reais
- Para campos do tipo 'string', retorne texto descritivo e especifico
- NUNCA use placeholders como 'mock', 'exemplo', 'teste' — gere conteudo real
- Os dados devem ser coerentes entre si e com o contexto fornecido
- Responda em portugues"""

    def funcao(argumentos):
        prompt_usuario = f"Argumentos recebidos:\n{json.dumps(argumentos, indent=2, ensure_ascii=False)}"

        dados_llm, uso_tokens = _chamar_llm_ferramenta(prompt_sistema, prompt_usuario, campos_saida)

        if dados_llm:
            dados_llm["_entrada"] = argumentos
            return {"sucesso": True, "dados": dados_llm, "_tokens": uso_tokens}

        # fallback mock simples
        dados = {}
        for nome_campo, tipo_campo in campos_saida.items():
            dados[nome_campo] = _gerar_valor_fallback(tipo_campo, nome_campo)
        dados["_entrada"] = argumentos
        return {"sucesso": True, "dados": dados, "_tokens": _TOKENS_ZERO.copy()}

    return funcao


def _gerar_valor_fallback(tipo_campo: str, nome_campo: str):
    """Fallback quando nao ha API key — gera valores minimos."""
    tipo_normalizado = tipo_campo.lower() if isinstance(tipo_campo, str) else "string"
    if tipo_normalizado == "float":
        return round(random.uniform(0.01, 100.0), 2)
    if tipo_normalizado == "int":
        return random.randint(1, 500)
    if tipo_normalizado == "bool":
        return random.choice([True, False])
    if tipo_normalizado == "list":
        return [{"item": f"{nome_campo}_1"}, {"item": f"{nome_campo}_2"}]
    if tipo_normalizado == "object":
        return {"campo": nome_campo, "valor": "sem_api_key"}
    return f"{nome_campo}_sem_api_key"


def construir_ferramentas_dos_contratos(contratos: dict) -> dict:
    """Constroi o registro de ferramentas a partir dos contratos (habilidades)."""
    habilidades = contratos.get("habilidades", {}).get("habilidades", [])
    ferramentas = {}
    for habilidade in habilidades:
        nome = habilidade.get("nome")
        if not nome:
            continue
        if nome in IMPLEMENTACOES_DETERMINISTICAS:
            _real = IMPLEMENTACOES_DETERMINISTICAS[nome]

            def funcao(argumentos, _real=_real):
                try:
                    return _real(argumentos or {})
                except Exception as erro:
                    return {"sucesso": False, "erro": str(erro), "_tokens": _TOKENS_ZERO.copy()}

            ferramentas[nome] = funcao
        else:
            ferramentas[nome] = construir_ferramenta(habilidade)
    return ferramentas


def extrair_evidencias_do_historico(historico: list) -> dict:
    """Extrai evidencias coletadas do historico de forma generica."""
    evidencias = {}
    for registro in historico:
        plano = registro.get("plano", {})
        resultado = registro.get("resultado_acao")
        nome_ferramenta = plano.get("nome_ferramenta")
        if resultado and resultado.get("sucesso") and nome_ferramenta:
            evidencias[nome_ferramenta] = resultado.get("dados", {})
    return evidencias


def _extrair_servico_da_entrada(historico: list) -> str:
    for registro in historico:
        percepcao = registro.get("percepcao", "")
        match = re.search(r"servico de (\w+)", percepcao, re.I)
        if match:
            return match.group(1)
        match = re.search(r"Alerta: (.+)", percepcao)
        if match and "servico" in match.group(1).lower():
            m2 = re.search(r"servico de (\w+)", match.group(1), re.I)
            if m2:
                return m2.group(1)
    return "pagamentos"


def montar_argumentos_mock(habilidade: dict, historico: list, entrada: str = "") -> dict:
    """Monta argumentos para uma ferramenta usando evidencias do historico."""
    argumentos = {}
    evidencias = extrair_evidencias_do_historico(historico)
    trace = _carregar_trace_para_mock()
    nome = habilidade.get("nome", "")
    servico = _extrair_servico_da_entrada(historico) or _extrair_servico_da_entrada(
        [{"percepcao": f"Alerta: {entrada}"}] if entrada else []
    )

    if nome == "relatorio_incidente":
        metricas = evidencias.get("consultar_metricas", {})
        logs = evidencias.get("buscar_logs", {})
        deploys = evidencias.get("historico_deploys", {})
        return {
            "nome_servico": servico,
            "severidade": "alta",
            "evidencia": {
                "metricas": {
                    "latencia_p99_ms": metricas.get("latencia_p99_ms"),
                    "taxa_erro": metricas.get("taxa_erro"),
                    "status": metricas.get("status"),
                },
                "logs": {
                    "contagem_total": logs.get("contagem_total"),
                    "amostra": (logs.get("eventos") or [])[:2],
                },
                "deploys": deploys.get("contagem_total"),
            },
            "recomendacao": {
                "acao_1": "Verificar configuracao de chaves API no servico",
                "acao_2": "Validar secret manager apos deploy recente de variaveis",
                "acao_3": "Monitorar taxa de erro apos correcao",
            },
        }

    for nome_campo, tipo_campo in habilidade.get("entrada", {}).items():
        tipo_normalizado = tipo_campo.lower() if isinstance(tipo_campo, str) else "string"

        if nome_campo == "nome_servico":
            argumentos[nome_campo] = servico
        elif nome_campo == "janela_tempo_minutos":
            argumentos[nome_campo] = 15
        elif nome_campo == "janela_tempo_horas":
            argumentos[nome_campo] = 1
        elif nome_campo == "nivel_minimo":
            argumentos[nome_campo] = "error"
        elif nome_campo == "severidade":
            argumentos[nome_campo] = "alta"
        elif nome_campo == "health_metrics":
            argumentos[nome_campo] = trace.get("health_metrics", {})
        elif nome_campo == "etapas":
            argumentos[nome_campo] = trace.get("etapas", [])
        elif nome_campo == "performance_data":
            argumentos[nome_campo] = trace.get("performance_data", {})
        elif nome_campo == "tempo_total_segundos":
            argumentos[nome_campo] = trace.get("tempo_total_segundos", 0)
        elif nome_campo == "tokens_consumidos":
            argumentos[nome_campo] = trace.get("tokens_consumidos", {})
        elif nome_campo == "tipo_agente":
            argumentos[nome_campo] = trace.get("tipo_agente", "task_based")
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
        elif tipo_normalizado == "object" and evidencias:
            argumentos[nome_campo] = evidencias
        else:
            argumentos[nome_campo] = _gerar_valor_fallback(tipo_campo, nome_campo)

    return argumentos
