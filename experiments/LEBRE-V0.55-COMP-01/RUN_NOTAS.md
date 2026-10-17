# Comparação da v0.55 com modelos externos: notas da execução

- **17/10/2026, `comp_run.py`** (modelos de série completa): 84 de 84 séries, sem erro, em CPU, no ambiente de
  referência.
- **17/10/2026, `comp_fundacao.py`, primeira tentativa em CPU:** 14 de 84 séries em cerca de 37 minutos (~2,6 min por
  série). Ela foi **interrompida a pedido do responsável** para rodar na GPU. As 14 saídas parciais foram **descartadas
  sem análise**, e nenhuma estatística foi calculada com elas.
- **Execução dos modelos de fundação em GPU:** NVIDIA GeForce RTX 5070, driver 610.88. Ambiente virtual separado, que
  replica o de referência pacote a pacote (`pip freeze` do sistema, instalado sem resolução de dependências), com uma
  única troca: torch 2.11.0+cu128 no lugar de 2.11.0+cpu. O Python do sistema não foi alterado.
  - O TTM usa `ttm_gpu.py`, cópia de `LEBRE-V0.52-EXT-01/ttm_run.py` que difere do original só nas linhas que movem
    modelos e tensores para a GPU e trazem as saídas de volta.
  - O treino e a inferência em GPU não são idênticos bit a bit aos da CPU. Por isso **todas as 84 séries rodam no mesmo
    dispositivo**.
  - Um teste sintético, de API e velocidade, mostrou o TTM ajustado com valor diferente do mesmo teste em CPU, como
    esperado para treino não determinístico entre dispositivos. Os números desse teste não são usados.
