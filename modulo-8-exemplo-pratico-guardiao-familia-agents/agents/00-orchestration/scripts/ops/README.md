# ops/

Scripts de manutenção do repositório (migração de paths, reorganização).

| Script | Uso |
|--------|-----|
| `build_repo_knowledge.py` | Gera `REPO_KNOWLEDGE.md` + `KNOWLEDGE.md` em cada agente |
| `reorganize_lib.py` | Migração pacote `lib/` |
| `fix_lib_imports.py` | Corrige imports após reorganização |

Rodar apenas quando estrutura de pastas mudar; não fazem parte do runtime de tasks.
