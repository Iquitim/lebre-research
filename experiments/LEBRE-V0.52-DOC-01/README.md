# LEBRE-V0.52-DOC-01 — Material de apoio à documentação da v0.52

**Data:** 27/09/2026. **Regra:** nada congelado é editado. Os módulos da v0.52 e o porte em C da EXT-01 são só **importados** ou **compilados sem alteração**. Todas as execuções desta pasta usam **apenas dados de desenvolvimento** ou um processo sintético declarado. Nenhuma reserva foi acessada.

## Conteúdo

| Arquivo | O que é |
|---|---|
| `doc_examples.py` → `DOC_EXAMPLES.json`, `DOC_EXAMPLE_A.npz`, `DOC_EXAMPLE_B.npz` | Execuções ilustrativas da v0.52 congelada, na configuração canônica. **(A)** Série de desenvolvimento `ons:ITUTINGA`: uma entrada (defluência de Camargos) mais o próprio passado; traços de evidência, janela de previsão, custo por componente. **(B)** Processo sintético declarado (semente 5290): y = 0,8·x0(t−12) + 0,3·média(x1, t−4…t−7) + e; recupera o atraso 12 com peso 0,81. |
| `trace_breakdown.py` → `TRACE_BREAKDOWN.csv` | Agregação, por função e por classe de instrução, dos rastreios de execução do Renode feitos na EXT-01 (ONS Volta Grande e BDG2 Bull, cerca de 300 passos cada). Usa o mesmo modelo de ciclos de `EXT-01/mcu/cycles_estimate.py`. CPI 1,62 e 1,57. |
| `mcu_profile/main_profile.c`, `build_profile.sh` → `profile_*.txt` | Firmware de perfil: o mesmo `lebre052.c` e as mesmas flags e simulador da EXT-01. Acrescenta a média e o máximo por bloco de 64 passos, um histograma e os passos acima de 20 mil instruções. Rodado em 3 séries de desenvolvimento (ONS Volta Grande, CAMELS 71350001, BDG2 Bull_education_Hayley). NMSE e mudanças são iguais aos da EXT-01; a soma de instruções difere em < 0,01% por causa do laço de medição. |

## Uso

Os documentos `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_{PTBR,EN}.pdf` leem estes arquivos em tempo de construção (`docs/architecture/pdf_source/build_v052_spec.py`). Os rastreios brutos do Renode (80–130 MB) ficaram no diretório temporário da EXT-01 e não foram copiados; o CSV agregado é o que o documento usa.
