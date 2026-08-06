from crewai.tools import tool

MANAGER_PASSWORD = "GESTOR-APROVA"

DESTRUCTIVE_KEYWORDS = (
    "destruir",
    "destrua",
    "destruo",
    "destroy",
    "apagar",
    "apague",
    "apaga",
    "delete",
    "excluir",
    "exclua",
    "drop",
)

MUTATION_KEYWORDS = (
    "terraform",
    "apply",
    "aplicar",
    "aplique",
    "provision",
    "deploy",
    "criar",
    "crie",
    "banco de dados",
    "database",
)

STATUS_KEYWORDS = (
    "maquina",
    "máquina",
    "maquinas",
    "máquinas",
    "status",
    "online",
    "em pé",
    "em pe",
    "quantas",
    "quantos",
    "health",
    "disponivel",
    "disponível",
    "ativas",
    "ativos",
)


def is_destructive_command(text: str) -> bool:
    """Detects destructive intent including conjugations like 'destrua'."""
    lowered = text.lower()
    return any(word in lowered for word in DESTRUCTIVE_KEYWORDS)


def is_infra_mutation_command(text: str) -> bool:
    """Detects infra changes that must go through execute_terraform governance."""
    lowered = text.lower()
    return is_destructive_command(text) or any(word in lowered for word in MUTATION_KEYWORDS)


def is_status_query(text: str) -> bool:
    """Detects read-only status questions (no tool call / no password)."""
    lowered = text.lower()
    return any(word in lowered for word in STATUS_KEYWORDS)


def run_status_check(_prompt: str) -> str:
    """Returns simulated cluster status without involving the LLM."""
    return (
        "📊 **Status do ambiente** (simulado)\n"
        "- Máquinas online: **12**\n"
        "- Máquinas offline: **0**\n"
        "- Cluster: `prod-infra-ops` ✅ saudável"
    )


def extract_manager_password(text: str) -> str:
    """Extracts manager approval token from the user message."""
    upper = text.upper()
    compact = upper.replace("-", "").replace(" ", "")
    if MANAGER_PASSWORD.replace("-", "") in compact or MANAGER_PASSWORD in upper:
        return MANAGER_PASSWORD
    return "None"


def run_chatops_action(prompt: str) -> str:
    """Runs execute_terraform with parsed password (deterministic governance)."""
    return execute_terraform.run(
        command=prompt,
        manager_password=extract_manager_password(prompt),
    )


@tool("execute_terraform")
def execute_terraform(command: str, manager_password: str = "None") -> str:
    """
    Tool to apply infrastructure changes via Terraform.
    If the command involves sensitive operations ('destroy', 'apagar', 'destruir', 'destrua'),
    the manager_password MUST be provided as 'GESTOR-APROVA'.
    """
    if is_destructive_command(command):
        if manager_password != MANAGER_PASSWORD:
            return (
                "🛑 BLOCKED: Ação crítica detectada! "
                "Forneça a senha do gestor: GESTOR-APROVA"
            )
        return "✅ APPROVED: Human-in-the-loop validado. Terraform executado com sucesso."

    return f"✅ SUCCESS: O comando '{command}' foi executado (baixo impacto)."
