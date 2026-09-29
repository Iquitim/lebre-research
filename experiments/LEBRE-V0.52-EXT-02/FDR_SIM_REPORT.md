# EXT-02, item 1 — Simulação do controle de mudanças falsas: resultado

**Execução:** única, 700 execuções, com plano e script com hash registrados antes (`HASHES_BEFORE_RUN.txt`). Modelo congelado, configuração canônica.
**Arquivos:**
- `FDR_SIM_RUNS.csv`;
- `FDR_SIM_SUMMARY.csv`;
- `FDR_SIM_RUNS_FINAL.csv`: estrutura final por execução, análise descritiva acrescentada depois da execução.

## Resultado

| Cenário | ρ das entradas | Execuções com ≥ 1 mudança falsa (IC 95%) | FDR estimado (limite sup.) | Falsas ainda presentes no fim | Verdade encontrada |
|---|---|---|---|---|---|
| N1 nulo global | 0,5 / 0,95 | 0/50 e 0/50 | 0 | 0 | — |
| N2 nulo exógeno, alvo AR | 0,5 / 0,95 | 0/50 e 0/50 | 0 | 0 | — |
| N3 nulo heterocedástico | 0,5 / 0,95 | 0/50 e 0/50 | 0 | 0 | — |
| N4 nulo com quebra de variância | 0,5 / 0,95 | 0/50 e 0/50 | 0 | 0 | — |
| P1 parcial | 0,5 / 0,95 | 0/50 e 0/50 | 0 | 0 | 100% / 92% |
| P2 parcial com isca (corr. ~0,7) | 0,5 | **7/50** [0,06; 0,27] | **0,090** (0,163) | 4 | 94% |
| | 0,95 | 0/50 | 0 | 0 | 96% |
| P3 parcial, ruído AR e cauda pesada | 0,5 | **10/50** [0,10; 0,34] | **0,077** (0,120) | 3 | 100% |
| | 0,95 | 0/50 | 0 | 0 | **2%** |

- **Nulos globais:** 0 de 400 execuções com qualquer mudança falsa (IC 95% [0; 0,009]).
- **Pelo critério declarado,** aplicado por cenário (100 execuções), **os 7 cenários passam**: P2 FDR 0,045 (sup. 0,088) e P3 0,038 (sup. 0,063).
- **Por célula,** porém, **duas ficam acima de 0,05:** P2 e P3 com ρ = 0,5. Isso é reportado, não escondido.

## Leitura

1. **O mecanismo das mudanças falsas é o de substitutas correlacionadas.** Em todas as 17 execuções, a falsa foi uma entrada correlacionada com a verdadeira (a isca de P2; em P3, entradas ligadas a x0 pelo fator comum) aceita **antes** da verdadeira. Enquanto a verdadeira não está no modelo, a substituta **melhora de fato a previsão** da referência. A nula do teste (nenhuma melhora preditiva) é falsa nesse momento, e o e-process está correto ao rejeitá-la. O erro é estrutural, não preditivo: o teste certifica **relevância preditiva em relação à referência vigente**, não estrutura causal.
2. **Autocorreção parcial.** Depois de aceitar a entrada verdadeira, o teste periódico de remoção retirou a substituta em 10 das 17 execuções. Em 7 de 700 execuções (1%), uma substituta ficou no modelo final.
3. **Limite de informação.** Com entradas suaves e ruído dependente (P3, ρ = 0,95), a verdadeira foi encontrada em 2% das execuções, consistente com o limite de informação já documentado.
4. **Implicação para o texto:**
   - a afirmação correta é "controle empírico de **falsas melhoras preditivas** e, no fim, estrutura raramente espúria nos cenários testados";
   - não é "controle de falsas estruturas": com substitutas correlacionadas, aceitações estruturalmente falsas ocorreram em até 20% das execuções de uma célula.

## Limitações

- Cenários sintéticos lineares, com 4 entradas e 30 mil passos.
- 50 sementes por célula, o que dá intervalos largos.
- A contagem de "falsa" é estrutural, definida pela verdade do gerador.
