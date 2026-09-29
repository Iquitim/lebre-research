# Adendo ao pré-registro — v0.4.2 (confirmação interna + BENCH-03b held-out)

**Escrito e com hash registrado antes de qualquer execução abaixo.** Objeto: `lebre_v042.py`
(SHA-256 `5c9ac0f7…94986506`), sem calibração.

## Histórico que motiva a v0.4.2 (resultados já obtidos)

- **v0.4** (pré-registrada): G1–G6 ✅; BENCH-03 `COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE` (5/5); salvaguardas I11 (+86) e atraso de detecção (2,0×) ❌.
- **v0.4.1** (adendo): G1–G6 ✅; BENCH-03 5/5, 1ª de 25; salvaguardas vinculantes I14 (+101), I4 (+0,019) e detecção (1,39×) ❌ → não promovida.
- **Diagnóstico** em DEV (sementes 2176..2235, já usadas e agora declaradas DEV): as potências P_j do C2 eram estimadas com memória de ~4 amostras
  (ganhos ruidosos, maior desajuste na I4) e os átomos maduros reduziam a taxa de evidência (atraso de detecção).
- **v0.4.2:** potência analítica pelo P6 (P = 1 para entradas e atrasos; (1−p)/(1+p) para latente e acionamento); evidência a cada 2 passos
  para todos os átomos (o C4/MATURE sai); ganhos a cada 100 passos; intervalos a cada 8 passos.
  No DEV-60 todas as salvaguardas passam (detecção 1,21×; I4 +0,008; I11–I14 ≤ +25).

## Parte 1″ — confirmação interna

Sementes **2236..2265** (livres). Braços: V02_A0, V032, V042 e CTRL_ARX. As hipóteses G1–G6 e as salvaguardas vinculantes são as do `PREREG_ADDENDUM_V041.md`:
- latência I11–I14 ≤ +50;
- ΔNMSE por tarefa ≤ +0,010;
- reativação da I7 ≤ +25;
- atraso de detecção ≤ 1,25× o da v0.3.2.

## Parte 2″ — BENCH-03b (held-out: séries, níveis, experimentos e sementes nunca usados)

- **A (Monash, X = [y_{t−1}], limitado a 50 000 pontos):** a **segunda** série de australian_electricity_demand (s = 48),
  solar_10_minutes (s = 144), pedestrian_counts (s = 24) e kdd_cup_2018 (s = 24).
- **B (River, T = 16 000, sementes 7311..7320):** FriedmanDrift LEA/GRA/GSG (mesmas posições do BENCH-03), Planes2D e Mv.
- **C:** F16, treino FullMSine_Level5 → teste FullMSine_Level6_Validation; ParWH, treino Est-phase-0-amp-3 → teste Val-amp-3.
- **D (sementes 7411..7420):** FIR esparso de comprimento 32, K ∈ {3, 5}, entrada branca ou AR(1) com 0,8, **SNR de 15 dB**, troca em T/2.
- **Modelos, harness e calibração:** idênticos ao BENCH-03, com LEBRE_V042 e LEBRE_V032. Sementes estocásticas nos dados reais: 7511..7513.
- **Critérios:** K-a a K-e do `PREREG_BENCH03.md`, com a v0.4.2 como objeto (K-d contra a v0.3.2).
- A v0.4.2 também é reportada no BENCH-03, **rotulada como semi-held-out** (esses dados já foram vistos).

## Regra de promoção

A LEBRE é promovida a **v0.4 (versão de pesquisa), implementada por `lebre_v042.py`**, se a Parte 1″ passar em G1–G6 **e** em todas as salvaguardas
vinculantes, **e** o BENCH-03b der `COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE` ou `PARTIALLY_COMPETITIVE`. Caso contrário, a v0.3.2 permanece vigente.
