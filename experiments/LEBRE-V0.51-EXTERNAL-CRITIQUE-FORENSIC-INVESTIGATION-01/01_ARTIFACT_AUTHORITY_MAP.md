# 01 — Mapa de autoridade dos artefatos

| Nível | Artefato | Disponível | Observação |
|---|---|---|---|
| 1 — resultados brutos | `INTERNAL_V051_RESULTS.csv`, `HELDOUT_V051_*.csv`, `V051_DECISION.json` (v0.51) e `RUN_*.csv` / `AUDIT_*.csv` (este estudo) | sim | gerados pelo código abaixo |
| 1 — resultados brutos da réplica | `results/lebre051/run_hypotheses.txt` | **ARTIFACT_MISSING** | só existem os números transcritos no relatório PDF |
| 2 — código executável | `lebre_v051.py`, `lebre_s051.py` (hashes congelados conferem) e `experiments/bench01/streams.py` (escalonador) | sim | autoridade para o comportamento |
| 2 — código da réplica | `edubraqd/lebre-prototipo/src/lebre051/` | **ARTIFACT_MISSING** | repositório privado |
| 3 — configuração congelada | `FREEZE_V051_SHA256.txt`, `FREEZE_S051_SHA256.txt`, `CODE_DATA_SHA256_AT_PREREG.txt` | sim | todos conferem |
| 4 — pré-registro | `PREREG_V051.md` + `PREREG_V051_SHA256.txt` | sim (local) | não publicado com o documento |
| 5 — especificação | `LEBRE_ARCHITECTURE_v0.51_SPEC_{PTBR,EN}.pdf` | sim | omite parâmetros (ver 03) |
| 6 — relatório da réplica | `LEBRE-achados-e-validacoes(-2).pdf` | sim | fonte das hipóteses H4–H9 |
| 7 — narrativa | relatórios `V051_REPORT.md` e `POSTHOC_FEEDBACK_REPORT.md` | sim | subordinados aos níveis 1–4 |

**Divergências entre níveis documentadas neste estudo:**
- A especificação diz que as entradas são padronizadas "por médias e variâncias acumuladas até o instante anterior". O código (nível 2) usa uma **média exponencial com α = 10⁻⁴**, iniciada em média 0 e variância 1. Prevalece o código.
- A especificação não diz o que fazer quando o conjunto ativo está cheio. O código **substitui** a vítima de maior CUSUM se R ≥ h/2. Prevalece o código; a lacuna fica registrada.
- A especificação não limita o número de estados latentes. O código admite **um só** e deixa de testar os demais polos enquanto ele está ativo. Esse fato decide o B3.
