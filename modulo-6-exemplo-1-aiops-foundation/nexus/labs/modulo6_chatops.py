import os
import sys

import streamlit as st

# Ensure project root is in the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crewai import Crew, Task

from core.agents import get_chatops_agent
from core.crew_config import kickoff_with_retry, nexus_crew_kwargs
from tools.chatops_tools import (
    is_destructive_command,
    is_infra_mutation_command,
    is_status_query,
    run_chatops_action,
    run_status_check,
)

# --- INTERFACE VISUAL (STREAMLIT) ---
st.set_page_config(page_title="Nexus Slack Simulator", page_icon="💬", layout="wide")

st.markdown(
    """
<style>
    .reportview-container { background: #0e1117; }
    .chat-header { color: #5865F2; font-weight: bold; font-size: 24px; margin-bottom: 20px; }
    .stButton>button { background-color: #5865F2; color: white; border-radius: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("💬 Nexus Slack Simulator")
st.markdown("Canais: `#infra-ops` | Logado como: `@pedro.oliveira`")
st.caption(
    "Ações destrutivas exigem **GESTOR-APROVA** na mensagem. "
    "Ex.: `destrua o banco de dados — senha GESTOR-APROVA`"
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def _chat_response(prompt: str) -> str:
    """Route sensitive infra actions and status checks without LLM tool calls."""
    if is_destructive_command(prompt) or is_infra_mutation_command(prompt):
        return run_chatops_action(prompt)

    if is_status_query(prompt):
        return run_status_check(prompt)

    agent = get_chatops_agent(tools=[], max_iter=1)
    task = Task(
        description=(
            f"O usuário @pedro.oliveira disse: '{prompt}'. "
            "Responda de forma curta e amigável em português, com emojis. "
            "Não execute infraestrutura; apenas converse."
        ),
        expected_output="Resposta curta do bot.",
        agent=agent,
    )
    try:
        return str(
            kickoff_with_retry(
                Crew(agents=[agent], tasks=[task], **nexus_crew_kwargs()),
                label="chatops",
            )
        )
    except Exception as error:
        if "tool_use_failed" in str(error).lower():
            return (
                "🤖 Não consegui processar essa ação automaticamente. "
                "Para status de máquinas, pergunte: *quantas máquinas estão em pé?*"
            )
        raise


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: @nexus-bot destrua o banco de dados..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Nexus-Bot processando..."):
            try:
                response = _chat_response(prompt)
            except Exception as error:
                response = f"❌ Erro na IA: {error}"

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
