# Fonte das bacias novas para a avaliação final da v0.56 — decisão (antes de qualquer download)

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DATA-01` · **Situação:** fonte decidida; **nenhum arquivo baixado**. As
regras de elegibilidade e de sorteio serão escritas e commitadas antes do download, como nas reservas anteriores.

## 1. Por que é preciso

Das 237 bacias elegíveis do CAMELS-BR, as posições 0–219 da permutação (semente 5202) já foram usadas no
desenvolvimento, nas validações e nas avaliações finais. Restam 17 (posições 220–236), insuficientes para uma família de
avaliação final (30 nas anteriores). Elas continuam lacradas.

## 2. Decisão: CAMELS-CL (Chile), versão de 2018 depositada no PANGAEA

- **Referência:** Alvarez-Garreton, C., et al. (2018). The CAMELS-CL dataset: catchment attributes and meteorology for
  large sample studies – Chile dataset. *Hydrology and Earth System Sciences* 22, 5817–5846.
  https://doi.org/10.5194/hess-22-5817-2018
- **Dados:** https://doi.pangaea.de/10.1594/PANGAEA.894885 — **licença CC-BY-4.0** (conferida na página do depósito em
  25/10/2026). 516 bacias, séries diárias.
- **Por que esta fonte:**
  - mesma família de conjuntos (CAMELS) do CAMELS-BR, com formato parecido, e precipitação do **mesmo produto** (MSWEP);
  - clima e hidrologia de outro país: o teste mede generalização, não familiaridade com as bacias brasileiras;
  - nenhuma sobreposição possível com as bacias já usadas (o Caravan, alternativa considerada, inclui as do CAMELS-BR);
  - licença explícita e arquivos com endereço fixo e tamanho declarado.
- **Por que não as versões de 2020 e 2022 do site do CR2:** a página não declara licença e o download passa por um
  formulário de registro. A versão do PANGAEA tem licença explícita e é registrada como suplemento do artigo de referência.

## 3. Correspondência com as entradas do CAMELS-BR

| CAMELS-BR (usado até a v0.55) | CAMELS-CL (arquivo do depósito) | Observação |
|---|---|---|
| vazão (mm/dia) | `3_CAMELScl_streamflow_mm` | igual |
| precipitação MSWEP | `6_CAMELScl_precip_mswep` | mesmo produto |
| evapotranspiração **real** (GLEAM) | `12_CAMELScl_pet_hargreaves` (evapotranspiração **potencial**) | **diferença declarada**: não há evapotranspiração real no depósito |
| temperatura média (ERA5-Land) | `10_CAMELScl_tmean_cr2met` | produto diferente (CR2MET) |

Também serão necessários os atributos (`1_CAMELScl_attributes`), só para a elegibilidade e o sorteio por metadados.

## 4. O que fica para as regras (antes do download)

- **Elegibilidade:** a regra brasileira usa uso consuntivo, grau de regularização e controle de qualidade da vazão. O
  equivalente no CAMELS-CL (grau de intervenção, grandes barragens, cobertura e período do registro) será fixado depois
  de ler a descrição dos atributos no artigo, sem abrir nenhuma série.
- **Sorteio:** semente nova, conferida como não usada; 30 bacias; cobertura mínima declarada.
- **Período:** o do depósito de 2018; a janela será declarada pela cobertura, não pelos valores.
- **Atribuição:** "Source: CAMELS-CL (Alvarez-Garreton et al., 2018), CC-BY-4.0", em NOTICE e nos documentos.
- **Família pequena extra:** as 17 bacias brasileiras inéditas podem entrar como checagem secundária; isso será decidido
  nas regras.
