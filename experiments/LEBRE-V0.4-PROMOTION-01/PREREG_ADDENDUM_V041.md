# Adendo ao pré-registro — v0.4.1

**Escrito e com hash registrado antes da execução das avaliações abaixo e antes de ver qualquer resultado do BENCH-03.**

## Motivação (resultado pré-registrado da v0.4, Parte 1)

A v0.4 passou em G1–G6, mas **falhou a salvaguarda da I11** (latência +86 passos > +50) e **dobrou o atraso de detecção** (487 contra 241).
Diagnóstico em DEV (sementes 3301..3310, `dev_detect.py`):

1. O estado MATURE com cadência 16 reduzia a taxa de evidência a 1/16 (a mesma violação do P2 vista no ARB10).
2. As estatísticas de escala do C2 (P_j) e σ̂² decaíam durante o silêncio, gerando ganhos explosivos na reativação (violação do P4).

**v0.4.1** (`lebre_v041.py`, SHA-256 `29631707…0f4d84`) corrige os dois pontos:

- evidência em duas escalas: átomos jovens a cada 2 passos (como na v0.3.2) e átomos maduros a cada 4;
- σ̂² e P_j congelados sem excitação;
- ganhos recalculados a cada 50 passos;
- intervalos atualizados a cada 4 passos, com a taxa em tempo de fluxo preservada.

Um CUSUM em blocos, na taxa exata, foi testado e descartado (perde retenção na I14). O reinício de ganhos foi testado e descartado (sem efeito).

## Parte 1′ — confirmação interna da v0.4.1

Sementes **2206..2235** (livres). Braços: V02_A0, V032, V041 e CTRL_ARX. As hipóteses G1–G6 são as mesmas, com V041 no lugar de V04.
As salvaguardas passam a ser **vinculantes para a promoção**:

- latência de chaveamento I11–I14: V041 − V032 ≤ +50 passos em cada tarefa;
- ΔNMSE por tarefa ≤ +0,010;
- reativação da I7: V041 − V032 ≤ +25 passos;
- atraso médio de detecção: V041 ≤ 1,25 × V032.

## Parte 2′ — BENCH-03 para a v0.4.1

Mesmas tarefas, sementes, baselines, harness e critérios K-a a K-e do `PREREG_BENCH03.md`, com a **v0.4.1** como objeto. A v0.4.1 roda
separadamente nas mesmas tarefas e sementes e é comparada aos resultados dos baselines do BENCH-03 (os baselines não mudam). A v0.4
congelada também é reportada, como registro.

## Regra de promoção (substitui a do pré-registro original)

A LEBRE é promovida a **v0.4 (versão de pesquisa), implementada por `lebre_v041.py`**, se a Parte 1′ passar em G1–G6 **e** em todas as
salvaguardas vinculantes, **e** a Parte 2′ der `COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE` ou `PARTIALLY_COMPETITIVE`.
Caso contrário, a v0.3.2 permanece vigente.
