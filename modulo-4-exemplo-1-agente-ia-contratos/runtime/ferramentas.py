"""
Ferramentas e Evidencias.

Cada ferramenta usa a LLM para gerar dados reais baseados no contexto.
Sem API key, usa fallback mock simples.
Inclui consumo de tokens (_tokens) no resultado para rastreamento.
"""

import json
import os
import random
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*a, **kw): pass

load_dotenv(Path(__file__).parent / ".env")

from llm_config import get_llm_client_and_model
from ferramentas_reais import IMPLEMENTACOES_REAIS

_TOKENS_ZERO = {"prompt": 0, "completion": 0, "total": 0}


def _resolver_repo_raiz() -> str:
    base = Path(__file__).resolve().parent
    for candidato in [base, *base.parents]:
        if (candidato / ".git").exists():
            return str(candidato)
    return str(base.parents[2])


def _chamar_llm_ferramenta(prompt_sistema: str, prompt_usuario: str, campos_saida: dict) -> tuple:
    """Chama a LLM para gerar a saida de uma ferramenta.

    Retorna (dados, uso_tokens). dados=None se falhar ou sem API key.
    """
    cliente, modelo = get_llm_client_and_model()
    if not cliente:
        return None, _TOKENS_ZERO.copy()

    try:
        resposta = cliente.chat.completions.create(
            model=modelo,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario},
            ],
        )
    except Exception:
        return None, _TOKENS_ZERO.copy()

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
        if nome:
            if nome in IMPLEMENTACOES_REAIS:
                real = IMPLEMENTACOES_REAIS[nome]

                def funcao(argumentos, _real=real):
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


def montar_argumentos_mock(habilidade: dict, historico: list) -> dict:
    """Monta argumentos para uma ferramenta usando evidencias do historico."""
    argumentos = {}
    evidencias = extrair_evidencias_do_historico(historico)
    repo_root = _resolver_repo_raiz()

    for nome_campo, tipo_campo in habilidade.get("entrada", {}).items():
        tipo_normalizado = tipo_campo.lower() if isinstance(tipo_campo, str) else "string"

        if nome_campo in ("caminho_repositorio", "caminho_repositorio_local"):
            argumentos[nome_campo] = repo_root
        elif nome_campo == "modulo_numero":
            argumentos[nome_campo] = 4
        elif nome_campo == "max_linhas":
            argumentos[nome_campo] = 80
        elif nome_campo == "remote":
            argumentos[nome_campo] = "origin"
        elif nome_campo == "branch":
            argumentos[nome_campo] = "main"
        elif nome_campo == "comparacao" and evidencias.get("comparar_repositorios"):
            argumentos[nome_campo] = evidencias["comparar_repositorios"]
        elif nome_campo == "verificacao_aula_atual" and evidencias.get("verificar_aula_atual_pronta"):
            argumentos[nome_campo] = evidencias["verificar_aula_atual_pronta"]
        elif nome_campo == "pasta_exemplo_atual":
            if evidencias.get("verificar_aula_atual_pronta"):
                argumentos[nome_campo] = evidencias["verificar_aula_atual_pronta"].get("pasta_aula_atual")
            elif evidencias.get("comparar_repositorios"):
                local = evidencias["comparar_repositorios"].get("local_exemplos") or []
                argumentos[nome_campo] = sorted(local)[-1] if local else ""
            else:
                argumentos[nome_campo] = ""
        elif nome_campo == "proximo_exemplo" and evidencias.get("identificar_proximo_exemplo"):
            argumentos[nome_campo] = evidencias["identificar_proximo_exemplo"]
        elif nome_campo == "caminho_unipds" and evidencias.get("identificar_proximo_exemplo"):
            argumentos[nome_campo] = evidencias["identificar_proximo_exemplo"].get("caminho_unipds", "")
        elif nome_campo in ("pasta_destino", "pasta_exemplo") and evidencias.get("identificar_proximo_exemplo"):
            argumentos[nome_campo] = evidencias["identificar_proximo_exemplo"].get("pasta", "")
        elif nome_campo == "resumo_diff" and evidencias.get("git_diff_resumo"):
            argumentos[nome_campo] = evidencias["git_diff_resumo"].get("resumo", "")
        elif tipo_normalizado == "object" and evidencias:
            argumentos[nome_campo] = evidencias
        else:
            argumentos[nome_campo] = _gerar_valor_fallback(tipo_campo, nome_campo)

    return argumentos
