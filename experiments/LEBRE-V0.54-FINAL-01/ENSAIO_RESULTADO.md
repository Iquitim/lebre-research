# Ensaio da avaliação final da v0.54 (séries já gastas, antes de qualquer acesso à reserva)

**Data:** 11/10/2026. Código: `ensaio_v054.py`, que usa `final_run.processar` e `final_analise.main` sem alteração;
protótipo no commit `cfe72ce`; v0.53 = `lebre==0.2.0`. Séries: 3 bacias e 3 medidores da reserva da v0.53, 2 eólicas e 2
solares da reserva da v0.53 (2024-2025) e a taxa nominal de 1 ano do Tesouro (usada no Lab), lida de cópias baixadas à
parte. Previsões e saídas ficam fora do repositório (pasta temporária).

**Funcionamento:** 11 de 11 séries rodaram (v0.54, v0.53, referência, versões curtas e SARIMAX), sem erro e sem previsão
não finita; a análise rodou de ponta a ponta. Leitores dos níveis conferem com o formato (testados também em WTI e nas
curvas nominal de 2015 e real de 2005).

| Família | v0.54 ÷ v0.53 (todas) | custo v0.54 ÷ v0.53 (mediana) | observação |
|---|---|---|---|
| camels (3) | 0,981 | 1,006 | a M1 dormiu em 1 de 3 bacias (custo 0,962, erro 0,945); nas outras, idêntica à v0.53 e custo ~1,01 |
| bdg2 (3) | 0,943 | 1,000 | a M1 dormiu em 2 de 3 medidores, tarde; erro 0,920 e 0,911 nesses dois |
| eolica (2) | 0,998 | 0,825 | a M1 dormiu 2 e 3 vezes |
| solar (2) | 1,000 | 0,859 | |
| niveis (1) | 1,000 | 0,848 | |

Razão mediana de custo nas 11 séries: 0,935 (IC 95% 0,857 a 1,006). Critérios A: nenhuma falha. Memória estimada:
85.268 B. Nenhuma remoção aceita.

**O que isto indica para a reserva (sem mudar critérios):** nas bacias e nos prédios, que são 60 das 93 séries da
reserva, a M1 costuma manter peso, dorme pouco ou tarde e o custo fica perto do da v0.53. A mediana das razões por série
deve cair dentro desse grupo, e o critério B (limite superior < 1) pode não ser atendido mesmo com a economia na eólica,
na solar e nos níveis. Nas séries em que a M1 dormiu, o erro também caiu.
