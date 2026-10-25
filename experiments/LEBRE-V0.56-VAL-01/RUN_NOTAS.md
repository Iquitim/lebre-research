# Notas de execução — validação da v0.56

## 1. Errata do texto do pré-registro (registrada durante a execução, antes de qualquer leitura de resultado)

O §2 de `PREREG_V056_VAL.md` diz que o IC usa "o bootstrap pareado de blocos móveis da avaliação final da v0.55 (`reps`,
média das réplicas em log)". As duas referências não coincidem:
- a avaliação final da v0.55 usou `par_bootstrap` (`LEBRE-V0.55-FINAL-01/final_analise.py`, a regra do E20), que mantém
  os passos sem alvo como lacunas dentro dos blocos;
- `reps` (`LEBRE-V0.55-COMP-01/comp_analise.py`, a função da comparação externa e dos diagnósticos da v0.56) aplica os
  blocos às perdas já mascaradas.

São o mesmo método, um bootstrap pareado de blocos móveis com 2.000 réplicas e a média das réplicas em log, e diferem só
no tratamento dos passos sem alvo. **O script commitado antes da execução (`val_analise.py`, commit `6c32263`) usa
`reps`, a função nomeada no pré-registro, e é ele que vale.** A avaliação final usa "a mesma estatística da validação"
(`PREREG_V056_FINAL.md`, §2), portanto também `reps`. Nenhuma mudança de código.
