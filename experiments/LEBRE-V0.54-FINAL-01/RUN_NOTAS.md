# Notas da execução final da v0.54

## 1. Falha de infraestrutura na primeira passada (11/10/2026), corrigida e documentada

**O que aconteceu.** `final_run.py` punha a pasta `LEBRE-V0.53-FINAL-01` no início do `sys.path` para importar
`final_regua.py`. No Windows, os processos filhos do `ProcessPoolExecutor` herdam o `sys.path` do pai e reimportam o
módulo principal; nos filhos, `import final_dados` passou a carregar o carregador **da v0.53**, que tem o mesmo nome.

**Efeito em cada família:**

- **camels e bdg2 (60 séries):** o carregador da v0.53 chama o mesmo leitor (`data_v052.load`, `final=True`) com a mesma
  conferência; as séries são idênticas às do carregador da v0.54. **Resultados válidos, mantidos.**
- **eolica (8) e niveis (17):** a busca pelo nome na reserva da v0.53 falhou (`StopIteration`); nada foi calculado.
- **solar:** 4 usinas falharam; as outras 4 (Alex, Belmonte, Calcário, Luzia), que também estavam na reserva da v0.53,
  foram carregadas da cópia da v0.53, com dados de **2024-2025** (17.544 passos; dados já gastos), e não de 2026.
  **Resultados inválidos**, retirados de `preds/` antes de qualquer análise. Nenhum dado solar de 2026 tinha sido lido.

Nenhuma análise foi feita sobre a primeira passada; só a contagem de concluídas e de erros foi vista.

**Correção (só infraestrutura; modelos, configuração, tarefas e critérios inalterados):** `final_run.py` e
`final_analise.py` carregam `final_regua.py` (e a análise da v0.53) por caminho explícito, sem alterar o `sys.path`.
Conferido num processo filho que o `final_dados` importado é o da v0.54, e que a análise reproduz o resultado do ensaio.
SHA-256 (12 primeiros dígitos): `final_run.py` 341d51259eeb → 4952f1d3b95b; `final_analise.py` 9ce193852fa0 → a3db5db81a9a
(`SHA256SUMS.txt` atualizado). A segunda passada roda só as séries que faltam (as 33 de eólica, solar e níveis).

## 2. Chronos-2: falha de ambiente nos níveis (11 a 13/10/2026)

A primeira execução de `final_chronos.py` concluiu 76 de 93 séries e parou na primeira série de níveis: o Python do
sistema, onde o Chronos-2 roda, não tinha o leitor de planilhas `.xls` (`xlrd`), usado por `final_dados.eia_xls`. Nenhum
código mudou. A execução foi completada com o mesmo `xlrd` 2.0.1 do ambiente do LEBRE Lab, posto só no `PYTHONPATH`
dessa execução (cópia do pacote, sem instalar nada no sistema); o script pula as séries já feitas. O Chronos-2 é só
referência reportada e não entra em nenhum critério.

## 3. SARIMAX nos níveis

O SARIMAX com entradas falhou nas 17 séries de níveis (`MissingDataError: exog contains inf or nans`): as entradas têm
lacunas em dias sem negociação, e `comp_dev.run_airline_x` não as aceita. O mesmo aconteceu com o câmbio em nível na
avaliação da v0.53. O SARIMAX é só referência reportada; nada foi refeito.
