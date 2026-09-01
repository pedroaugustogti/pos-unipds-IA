# datasets — casos de regressão

JSON com tasks piloto e sequência esperada de eventos **role-based** (LangGraph v2).

Eventos canônicos: `orchestrator_enter_in_progress` → `{creator}_ready_for_code_review` → `{reviewer}_in_code_review` → … → `devops-cicd_done`.

Usado por `langsmith_eval.py` e checklist do guia Fase D.

Não editar sem atualizar eval runner correspondente.
