# Relatório de gaps de performance — boot emulador + build mobile (Guardião)

Data: 2026-08-27  
Contexto: dual AVD (`Pixel_6_API34_Stable` @5554 + `Pixel_6_API34_Child` @5556) para Appium golden (Expo parent/child).

## Medições desta sessão

| Cenário | Wall clock (ambos online) | Notas |
|--------|---------------------------|--------|
| Cold boot anterior (`-no-snapshot-load`, GPU off no AVD, 4 cores / flags manuais) | ~60s | Baseline pré-otimização |
| Cold boot lean (`-gpu host -no-audio -no-boot-anim`, 2048MB/2 cores, config lean) | **~37s** | Parent ~30s; child já pronto ao fim do wait |
| “Quick boot” com `-no-snapshot-save` | **~37s** | Sem ganho: snapshot não era gravado no exit |

Footprint local (aprox.):

| Path | Tamanho |
|------|---------|
| `C:\gf\r\p\android` | ~756 MB |
| `C:\gf\r\c\android` | ~594 MB |
| `C:\gf\r\p\node_modules` | ~665 MB |
| `C:\gf\r\c\node_modules` | ~744 MB |

## O que já foi aplicado

Arquivo: `guardiao-familia-api/test/appium/start-emulators.ps1`

- Dual lean: **2048 MB / 2 cores** por AVD (antes: 4096/4 ×2 → pressão forte no host)
- Flags: `-gpu host`, `-no-audio`, `-no-boot-anim`, `-accel on`, rede full
- `-ApplyLeanAvdConfig`: GPU host, teclado, GPS; desliga áudio/câmera/sdcard/sensores/GSM
- Runtime pós-boot: animações 0, stay-on, wifi, geo fix SP
- Snapshot: **grava no exit por padrão** (quick boot real); `-NoSnapshotSave` / `-ColdBoot` opcionais
- `lib/local_e2e.py`: `docker info` não derruba mais o stack em `TimeoutExpired`

Backup dos `config.ini`: `*.avd/config.ini.lean.bak`

## Gaps restantes (priorizados)

### Boot / runtime emulador

1. **Snapshot ainda não “quente”** — após lean + cold, fazer 1 exit limpo (`adb -s … emu kill`) **sem** `-NoSnapshotSave` e medir de novo. Meta: **&lt;15s** wall dual.
2. **Resolução Pixel 6 1080×2400@420** — pesada para RN/UiAutomator. Gap: criar skin `720×1280@320` (ou Pixel 4a) só para E2E → menos pixels = dump UI/Appium mais rápido.
3. **`disk.dataPartition.path = &lt;temp&gt;`** nos AVDs — dados voláteis; força reinstall/pm clear com mais frequência. Gap: data partition persistente para manter APKs entre boots.
4. **Dual emulador sempre** — para tickets só-parent ou só-child, usar `-Single` (já existe) e evitar 2× RAM.
5. **Geo/sensors** — GPS on é necessário; acelerômetro/giroscópio podem ficar off se nenhum teste de motion depender (ganho pequeno).

### Build / install (maior custo fora do boot)

1. **`expo prebuild` + `gradlew installDebug --no-daemon`** em `install_mobile_dev_clients.ps1`  
   - Gap: `--no-daemon` mata o Gradle daemon a cada run → builds frios. Preferir daemon ligado em máquina de dev; `--no-daemon` só em CI limpa.  
   - Gap: `Clean`/`gradlew clean` destrói cache incremental — não usar no loop diário.
2. **android/ ~600–750 MB por app** — rebuild full é lento. Gap: nunca apagar `android/` sem necessidade; `prebuild` só se faltar `gradlew`.
3. **Junctions `C:\gf\r\{p,c,a}`** — já ajudam path Windows; manter `GF_GRADLE_HOME=C:\gf\.gradle` compartilhado entre parent/child.
4. **Metro dual (8082/9090)** — cold Metro + bundle Expo é o outro grande custo pós-boot. Gap: deixar Metro sempre up; não matar node entre goldens; usar cache Metro (`--clear` só quando JS quebrar).
5. **Dev client reinstall** — `pm clear` no golden limpa permissões (ok para teste), mas reinstall APK só quando native mudar.
6. **Docker Desktop cold start** — último golden falhou em `docker info` timeout. Gap: manter Docker/Postgres/Redis/API up; script de golden com `--with-docker` só quando health falhar.

### Appium / fluxo

1. Timeouts longos em overlays Expo / Chrome FRP / permission dialogs dominam o wall do golden mais que o boot do AVD.
2. UiAutomator2 crash (instrumentation) — restart Appium :4723 entre runs; não reutilizar sessão podre.

## Playbook recomendado (mínimo custo)

```powershell
# 1) Uma vez após mudar config lean
.\test\appium\start-emulators.ps1 -WaitBoot -ApplyLeanAvdConfig -ColdBoot
# exit limpo para gravar snapshot
adb -s emulator-5554 emu kill; adb -s emulator-5556 emu kill

# 2) Dia a dia
.\test\appium\start-emulators.ps1 -WaitBoot   # quick boot
# Metro já up; API já up
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle
```

## Metas

| Etapa | Hoje (aprox.) | Meta |
|-------|---------------|------|
| Dual boot (wall) | ~37s | ≤15s (snapshot quente) |
| Metro ready (já quente) | ~0–5s | ≤5s |
| `installDebug` incremental | minutos | &lt;60s com daemon+cache |
| Golden Appium E2E | vários min | reduzir waits/overlays, não o AVD |

## Arquivos de log desta otimização

- `agents/00-runtime/output/emulator_boot_lean_cold.log`
- `agents/00-runtime/output/emulator_boot_lean_quick.log`
