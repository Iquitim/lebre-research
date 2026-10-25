# Correção 01 das regras dos dados da v0.56 (antes de qualquer previsão)

**Data:** 25/10/2026.

**Falha registrada:** a regra da §3 de `SPLIT_RULES.md` exige precipitação MSWEP válida em ≥ 99% dos dias de 1990 a 2015.
O arquivo do depósito (`6_CAMELScl_precip_mswep`) **termina em 31/12/2014**: a lista de referências do artigo dava
1979–2015 para o produto, mas a série depositada vai de 1979-01-01 a 2014-12-31. Com isso, nenhuma bacia pode passar
(cobertura máxima possível de 96%), e a primeira execução do sorteio deu 0 elegíveis. Ela não foi commitada.

Estrutura conferida, sem inspecionar valores: vazão de 1913-02-15 a 2018-03-09; temperatura média (CR2MET) e
evapotranspiração potencial (Hargreaves) de 1979-01-01 a 2016-12-31; MSWEP de 1979-01-01 a 2014-12-31; 516 bacias em
todos os arquivos.

**Correção:** a janela passa a **01/01/1990 a 31/12/2014**, o período em que as três entradas existem. Nenhum limiar
muda: vazão válida em ≥ 85% dos dias da janela e as três entradas em ≥ 99%. A janela das séries usadas na validação e na
avaliação final é a mesma. Nada mais muda.
