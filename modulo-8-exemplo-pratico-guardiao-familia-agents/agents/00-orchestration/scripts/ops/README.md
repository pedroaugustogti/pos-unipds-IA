# ops/

Scripts de manutenção do repositório (migração de paths, reorganização).

| Script | Uso |
|--------|-----|
| `build_repo_knowledge.py` | Gera `REPO_KNOWLEDGE.md` + `KNOWLEDGE.md` em cada agente — **rodar após mudar READMEs ou paths** |
| `patch_runtime_paths_in_docs.py` | Substitui paths legados `output/` → `output/{ticket}/` + `system/` em `.md` |
| `migrate_output_to_system.py` | Move estado global de `output/` para `system/`; deixa só tickets em `output/` |
| `reorganize_output_tickets.py` | Migra artefatos legados para layout `{ticket}/{agent}-({cycle})/` |
| `reorganize_lib.py` | Migração pacote `lib/` |
| `fix_lib_imports.py` | Corrige imports após reorganização |

Fluxo típico após mudança de layout runtime: `patch_runtime_paths_in_docs.py` → `build_repo_knowledge.py`.

Rodar apenas quando estrutura de pastas mudar; não fazem parte do runtime de tasks.
