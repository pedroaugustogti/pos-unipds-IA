"""
Planejador - Perceber e Planejar.

Monta o contexto (percepcao) e decide o proximo passo via LLM ou mock.
Suporta modos: task_based, interactive, goal_oriented, autonomous.
Suporta arquiteturas cognitivas: ReAct, Plan-Execute, Reflection.
"""

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*a, **kw): pass

from ferramentas import (
    agente_tem_somente_ferramentas_deterministicas,
    extrair_evidencias_do_historico,
    ferramenta_e_deterministica,
    montar_argumentos_mock,
)
from llm_config import get_llm_client_and_model

load_dotenv(Path(__file__).parent / ".env")

_TOKENS_ZERO = {"prompt": 0, "completion": 0, "total": 0}


def perceber(estado: dict) -> str:
    """Monta o contexto atual para o planejador."""
    partes = [f"Alerta: {estado['entrada']}"]

    tipo_agente = estado.get("tipo_agente", "task_based")
    partes.append(f"Modo: {tipo_agente}")

    if estado.get("evento"):
        partes.append(f"Evento trigger: {estado['evento']}")

    for registro in estado["historico"]:
        etapa = registro["etapa"]
        plano = registro.get("plano", {})
        ferramenta_usada = plano.get("nome_ferramenta", "nenhuma")
        if registro.get("resultado_acao"):
            partes.append(f"Etapa {etapa} [{ferramenta_usada}]: {json.dumps(registro['resultado_acao'], ensure_ascii=False)}")

    ferramentas_usadas = list(estado["chamadas_por_ferramenta"].keys())
    if ferramentas_usadas:
        partes.append(f"Ferramentas ja utilizadas: {', '.join(ferramentas_usadas)}")

    partes.append(f"Etapas realizadas: {estado['etapa']}/{estado['max_etapas']}")
    partes.append(f"Chamadas de ferramenta: {estado['chamadas_ferramenta']}/{estado['max_chamadas_ferramenta']}")

    if estado.get("etapas_sem_progresso", 0) > 0:
        partes.append(f"ATENCAO: {estado['etapas_sem_progresso']} etapas sem progresso detectadas")

    return "\n".join(partes)
def construir_prompt_sistema(contratos: dict) -> str:
    """Constroi o system prompt a partir dos contratos - sem conhecer o dominio."""
    agente = contratos.get("agente", {})
    nome_agente = agente.get("nome", "agente")
    descricao_agente = agente.get("descricao", "")
    tipo_agente = agente.get("tipo", "task_based")

    objetivo = contratos.get("ciclo", {}).get("objetivo", "desconhecido")
    etapas = contratos.get("ciclo", {}).get("etapas", [])

    # ferramentas - descricao vem do contrato de habilidades do agente
    habilidades = contratos.get("habilidades", {}).get("habilidades", [])
    bloco_ferramentas = ""
    for habilidade in habilidades:
        nome = habilidade.get("nome", "")
        descricao = habilidade.get("descricao", "")
        entradas = habilidade.get("entrada", {})
        saidas = habilidade.get("saida", {})
        texto_entradas = ", ".join(f"{nome_campo}: {tipo_campo}" for nome_campo, tipo_campo in entradas.items()) if entradas else "nenhuma"
        texto_saidas = ", ".join(f"{nome_campo}: {tipo_campo}" for nome_campo, tipo_campo in saidas.items()) if saidas else "nenhuma"
        bloco_ferramentas += f"- {nome}: {descricao}\n  entrada: {{{texto_entradas}}}\n  saida: {{{texto_saidas}}}\n"

    if not bloco_ferramentas:
        bloco_ferramentas = "- nenhuma ferramenta disponivel\n"

    # contrato do planejador
    planejador = contratos.get("planejador", {})
    regras_planejador = planejador.get("regras", [])
    texto_regras = "\n".join(f"- {regra}" for regra in regras_planejador) if regras_planejador else ""

    # formato de saida — lido do contrato (permite que arquiteturas mudem o formato)
    formato_saida = planejador.get("formato_saida", {})
    if isinstance(formato_saida, dict) and formato_saida:
        campos_formato = []
        for campo, descricao in formato_saida.items():
            campos_formato.append(f'  "{campo}": "{descricao}"')
        bloco_formato = "{\n" + ",\n".join(campos_formato) + "\n}"
    else:
        bloco_formato = """{
  "proxima_acao": "CHAMAR_FERRAMENTA" ou "FINALIZAR" ou "PERGUNTAR_USUARIO",
  "nome_ferramenta": "nome da ferramenta (obrigatorio se CHAMAR_FERRAMENTA)",
  "argumentos_ferramenta": {},
  "criterio_sucesso": "o que define sucesso para esta etapa",
  "pergunta": "pergunta para o usuario (obrigatorio se PERGUNTAR_USUARIO)"
}"""

    # politicas do agente
    politicas = contratos.get("regras", {}).get("politicas", [])
    texto_politicas = "\n".join(f"- {politica}" for politica in politicas) if politicas else ""

    # instrucoes por tipo de agente
    instrucoes_tipo = ""
    if tipo_agente == "interactive":
        instrucoes_tipo = """
MODO INTERACTIVE:
- Antes de agir, valide ambiguidades com o usuario usando PERGUNTAR_USUARIO
- Se faltar informacao critica, pergunte antes de chamar ferramentas
- Inclua o campo "pergunta" com a pergunta para o usuario
"""
    elif tipo_agente == "goal_oriented":
        instrucoes_tipo = """
MODO GOAL-ORIENTED:
- Decomponha o objetivo em sub-objetivos executaveis
- Para cada sub-objetivo, planeje quais ferramentas usar
- Reavalie o plano apos cada etapa com base nos resultados
"""
    elif tipo_agente == "autonomous":
        instrucoes_tipo = """
MODO AUTONOMOUS:
- Responda ao evento trigger fornecido na percepcao
- Opere dentro dos limites rigidos definidos
- NUNCA execute acoes destrutivas sem confirmacao humana
- Priorize seguranca sobre velocidade
"""

    return f"""Voce e o planejador de um agente autonomo.

Agente: {nome_agente} - {descricao_agente}
Tipo: {tipo_agente}
Objetivo: {objetivo}

Etapas do ciclo: {' -> '.join(etapas) if etapas else 'perceber -> planejar -> agir -> avaliar'}

Ferramentas disponiveis:
{bloco_ferramentas}
Formato de resposta (APENAS JSON valido):
{bloco_formato}

CRITICO: o campo "proxima_acao" DEVE ser exatamente um destes 3 valores:
- "CHAMAR_FERRAMENTA" — para executar uma ferramenta
- "FINALIZAR" — para encerrar o ciclo
- "PERGUNTAR_USUARIO" — para pedir informacao ao usuario
NUNCA use o nome da ferramenta como proxima_acao. Use "CHAMAR_FERRAMENTA" e coloque o nome em "nome_ferramenta".

Regras gerais:
- Use cada ferramenta no maximo uma vez, a menos que precise de parametros diferentes
- As chaves de argumentos_ferramenta devem corresponder exatamente aos campos de entrada da ferramenta
- Para campos do tipo object, use dados reais coletados nas etapas anteriores
{instrucoes_tipo}
IMPORTANTE — Regras do planejador (voce DEVE seguir TODAS):
{texto_regras}

IMPORTANTE — Politicas do agente (voce DEVE seguir TODAS):
{texto_politicas}

ATENCAO: voce NAO pode usar FINALIZAR enquanto alguma regra ou politica acima nao for satisfeita.
Se uma regra exige chamar uma ferramenta antes de finalizar, voce DEVE chama-la primeiro.
"""


def _modo_planejador() -> str:
    return os.environ.get("RUNTIME_PLANEJADOR", "auto").strip().lower()


def _ferramentas_do_historico(historico: list) -> set:
    usadas = set()
    for registro in historico or []:
        plano = registro.get("plano", {})
        if plano.get("proxima_acao") == "CHAMAR_FERRAMENTA":
            nome = plano.get("nome_ferramenta")
            if nome:
                usadas.add(nome)
    return usadas


def _ordem_ferramentas(contratos: dict) -> list:
    habilidades = contratos.get("habilidades", {}).get("habilidades", [])
    nomes_habilidades = [habilidade["nome"] for habilidade in habilidades if habilidade.get("nome")]
    obrigatorias = contratos.get("regras", {}).get("ferramentas_obrigatorias", [])

    if obrigatorias and set(nomes_habilidades).issubset(set(obrigatorias)):
        ordem = []
        for nome in obrigatorias:
            if nome in nomes_habilidades and nome not in ordem:
                ordem.append(nome)
        return ordem

    return nomes_habilidades


def _agente_precisa_planejador_llm(contratos: dict) -> bool:
    """LLM no planejador so e necessaria quando skills mock nao tem implementacao deterministica."""
    for habilidade in contratos.get("habilidades", {}).get("habilidades", []):
        if habilidade.get("tipo_implementacao", "mock") != "mock":
            continue
        nome = habilidade.get("nome")
        if nome and not ferramenta_e_deterministica(nome):
            return True
    return False


def _deve_usar_planejador_mock(contratos: dict) -> bool:
    modo = _modo_planejador()
    if modo == "mock":
        return True
    if modo == "llm":
        return False
    return not _agente_precisa_planejador_llm(contratos)


def _formato_arquitetura(contratos: dict) -> dict:
    return contratos.get("planejador", {}).get("formato_saida", {}) or {}


def _injetar_campos_arquitetura(plano: dict, contratos: dict, usadas: set) -> dict:
    formato = _formato_arquitetura(contratos)

    if "raciocinio" in formato and "raciocinio" not in plano:
        plano["raciocinio"] = "Raciocinio nao informado pelo planejador."

    if "nivel_confianca" in formato and "nivel_confianca" not in plano:
        n = len(usadas)
        if n == 0:
            plano["nivel_confianca"] = "baixa"
        elif n < 3:
            plano["nivel_confianca"] = "media"
        else:
            plano["nivel_confianca"] = "alta"

    return plano


def chamar_llm(percepcao: str, contratos: dict, historico: list = None, entrada: str = "") -> tuple:
    """Chama a LLM para decidir o proximo passo."""
    historico = historico or []

    if _deve_usar_planejador_mock(contratos):
        plano = planejador_mock(percepcao, contratos, historico, entrada)
        plano["_modo"] = "mock"
        return plano, _TOKENS_ZERO.copy()

    cliente, modelo = get_llm_client_and_model()
    if not cliente:
        plano = planejador_mock(percepcao, contratos, historico, entrada)
        plano["_modo"] = "mock"
        return plano, _TOKENS_ZERO.copy()

    try:
        resposta = cliente.chat.completions.create(
            model=modelo,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": construir_prompt_sistema(contratos)},
                {"role": "user", "content": percepcao},
            ],
        )
    except Exception as erro:
        print(f"  [planejador] LLM indisponivel ({erro}), usando mock")
        plano = planejador_mock(percepcao, contratos, historico, entrada)
        plano["_modo"] = "mock"
        return plano, _TOKENS_ZERO.copy()

    uso_tokens = _TOKENS_ZERO.copy()
    if resposta.usage:
        uso_tokens = {
            "prompt": resposta.usage.prompt_tokens or 0,
            "completion": resposta.usage.completion_tokens or 0,
            "total": resposta.usage.total_tokens or 0,
        }

    try:
        plano = json.loads(resposta.choices[0].message.content)
        plano["_modo"] = "llm"
        return _injetar_campos_arquitetura(plano, contratos, _ferramentas_do_historico(historico)), uso_tokens
    except (json.JSONDecodeError, IndexError):
        print("  [planejador] resposta JSON invalida, usando mock")
        plano = planejador_mock(percepcao, contratos, historico, entrada)
        plano["_modo"] = "mock"
        return plano, uso_tokens


def planejador_mock(percepcao: str, contratos: dict, historico: list = None, entrada: str = "") -> dict:
    """Planejador deterministico — percorre ferramentas na ordem dos contratos."""
    habilidades = contratos.get("habilidades", {}).get("habilidades", [])
    historico = historico or []
    usadas = _ferramentas_do_historico(historico)
    ordem = _ordem_ferramentas(contratos)
    formato = _formato_arquitetura(contratos)
    inclui_raciocinio = "raciocinio" in formato

    tipo_agente = "task_based"
    for linha in percepcao.split("\n"):
        if linha.startswith("Modo: "):
            tipo_agente = linha.replace("Modo: ", "").strip()
            break
    if tipo_agente == "task_based":
        tipo_agente = contratos.get("agente", {}).get("tipo", "task_based")

    modo_execucao = contratos.get("planejador", {}).get("modo_execucao")
    if modo_execucao == "plan_execute" and not historico:
        passos = []
        for i, nome in enumerate(ordem, 1):
            habilidade = next((hab for hab in habilidades if hab["nome"] == nome), {})
            argumentos = montar_argumentos_mock(habilidade, historico, entrada)
            passos.append({
                "passo": i,
                "objetivo": f"executar {nome}",
                "ferramenta": nome,
                "argumentos_ferramenta": argumentos,
                "criterio_sucesso": f"{nome} executado com dados coletados",
            })
        primeiro_passo = passos[0] if passos else {}
        return {
            "plano_completo": passos,
            "proxima_acao": "CHAMAR_FERRAMENTA",
            "nome_ferramenta": primeiro_passo.get("ferramenta"),
            "argumentos_ferramenta": primeiro_passo.get("argumentos_ferramenta", {}),
            "criterio_sucesso": primeiro_passo.get("criterio_sucesso", ""),
        }

    if tipo_agente == "interactive" and not historico:
        plano = {
            "proxima_acao": "PERGUNTAR_USUARIO",
            "nome_ferramenta": None,
            "argumentos_ferramenta": None,
            "criterio_sucesso": "obter informacoes iniciais do usuario",
            "pergunta": "Qual servico esta com problema e desde quando voce observou o alerta?",
        }
        if inclui_raciocinio:
            plano["raciocinio"] = (
                "A entrada e ambigua. Faltam dados criticos como nome do servico e janela de tempo. "
                "Preciso perguntar antes de agir."
            )
        return _injetar_campos_arquitetura(plano, contratos, usadas)

    for nome in ordem:
        if nome not in usadas:
            habilidade = next((hab for hab in habilidades if hab["nome"] == nome), {})
            argumentos = montar_argumentos_mock(habilidade, historico, entrada)
            plano = {
                "proxima_acao": "CHAMAR_FERRAMENTA",
                "nome_ferramenta": nome,
                "argumentos_ferramenta": argumentos,
                "criterio_sucesso": f"{nome} executado com sucesso",
            }
            if inclui_raciocinio:
                ja_coletei = ", ".join(sorted(usadas)) if usadas else "nada ainda"
                plano["raciocinio"] = (
                    f"Ja coletei: {ja_coletei}. Proximo passo logico: chamar {nome} para obter mais evidencias."
                )
            return _injetar_campos_arquitetura(plano, contratos, usadas)

    evidencias = extrair_evidencias_do_historico(historico)
    metricas = evidencias.get("consultar_metricas", {})
    veredito = evidencias.get("gerar_veredito", {})
    backlog = evidencias.get("montar_backlog", {})

    if backlog.get("resumo"):
        criterio_final = backlog["resumo"]
    elif veredito.get("veredito"):
        criterio_final = veredito["veredito"]
    elif metricas.get("taxa_erro"):
        criterio_final = (
            f"Incidente registrado. Diagnostico: taxa de erro {metricas['taxa_erro']}% "
            f"({metricas.get('status', 'indeterminado')})"
        )
    else:
        resumo_partes = []
        for nome_ferramenta, dados in evidencias.items():
            campos = ", ".join(
                f"{chave}={valor}" for chave, valor in dados.items() if not str(chave).startswith("_")
            )
            resumo_partes.append(f"[{nome_ferramenta}] {campos}")
        criterio_final = " | ".join(resumo_partes) if resumo_partes else "analise concluida"

    plano = {
        "proxima_acao": "FINALIZAR",
        "nome_ferramenta": None,
        "argumentos_ferramenta": None,
        "criterio_sucesso": criterio_final,
    }
    if inclui_raciocinio:
        plano["raciocinio"] = (
            f"Todas as ferramentas foram chamadas. Evidencias: {', '.join(evidencias.keys())}. "
            "Posso finalizar com diagnostico."
        )
    return _injetar_campos_arquitetura(plano, contratos, usadas)
