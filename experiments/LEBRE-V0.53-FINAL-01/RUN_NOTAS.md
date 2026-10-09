# Notas da execução final (09/10/2026)

1. **Falha de infraestrutura, 1 de 104 séries (carga do Sudeste).** `final_run.py` terminou com 103 séries ok e um erro
   em `('carga', 'SUDESTE')`: `KeyError: 'SUDESTE'` ao selecionar o subsistema. No arquivo de 2026 do ONS, o subsistema
   `SE` passou a se chamar "SUDESTE/CENTRO-OESTE" (em 2025 era "SUDESTE"); conferidos só os nomes das categorias, nenhum
   valor de carga. **Correção só de leitura** (`final_dados.carga`): o subsistema passa a ser escolhido pelo código
   (`id_subsistema`: SE, S, NE, N), que não mudou. `teste_final_dados.teste_carga` continua reproduzindo a carga de 2025
   do LEBRE Lab valor a valor; para Sul, Nordeste e Norte as linhas selecionadas são as mesmas (as três já rodadas não são
   refeitas). Só a série do Sudeste roda de novo, como prevê a seção 4 do pré-registro. Nenhum modelo, critério ou outra
   série foi alterado, e nenhum resultado foi olhado antes desta correção.
