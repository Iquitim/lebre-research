# Pré-registro — LEBRE v0.52 corrigida na "reserva 2"

**Data:** 27/09/2026 · **Status:** registrado **antes** de qualquer acesso às séries da reserva 2. A seleção (`select_reserve2.py`) só leu atributos de elegibilidade, a cobertura e a fração de zeros, como a divisão original, além de nomes de arquivos; nenhum valor das séries foi inspecionado.

## 1. Objetivo

Testar em dados nunca vistos a **correção das lacunas do alvo** e medir a v0.52 **dentro da sua classe de orçamento** (centenas de FP/passo), com os modelos caros como teto de referência. Princípio do projeto: a LEBRE não precisa ser a melhor; precisa **entregar bem com orçamento mínimo e sem falhas catastróficas**.

## 2. Dados — reserva 2 (`RESERVA2.json`)

- Regra fixada antes: **as próximas posições das mesmas permutações com semente** da divisão original (CAMELS-BR, semente 5202: posições 60–79; BDG2, semente 5203: posições 35–54). O script verifica que as posições anteriores reproduzem exatamente o desenvolvimento e a reserva 1.
- **20 bacias do CAMELS-BR** (vazão diária; precipitação, evapotranspiração e temperatura) + **20 medidores do BDG2** (consumo horário; temperatura do ar e de orvalho; ciclos de 24 e 168 h declarados).
- **Limitações:** sem ONS (os rios elegíveis se esgotaram); 40 séries (intervalos largos); 4 locais do BDG2 são compartilhados com o desenvolvimento (Bull, Eagle, Hog, Moose): as séries-alvo são novas, mas o clima de entrada é o mesmo.

## 3. Modelos (congelados)

- **V052_CORRIGIDA** (candidata): configuração da medição #7 + retenção nas lacunas + contrato de saída.
- **V052_CONGELADA:** a configuração avaliada na reserva 1, sem a correção.
- **Classe de orçamento** (≤ 2.000 FP/passo): V051, NLinear, DLinear, Holt-Winters, ARX denso NLMS, LASSO online (calibrados nos primeiros 15%).
- **Referências** (fora da classe): SARIMAX com entradas (ajuste por máxima verossimilhança nos primeiros 15%), ARX por mínimos quadrados com ordem online (~4·10⁴ FP), Chronos-2 com covariáveis (~10⁹–10¹⁰ FP; 1.000 pontos).

## 4. Análise (`heldout2_analysis.py`, fixada agora)

- MSE relativo ao NLinear na máscara comum (últimos 70%); média geométrica por grupo e total; IC 95% por bootstrap estratificado (2.000 reamostras, semente 8002).
- **Série catastrófica:** erro relativo > 10, ou desvio máximo da previsão em relação à mediana > 10× a amplitude observada, ou previsão não finita num passo observado.
- **Perguntas:**
  - **Q1** — catastróficas da CORRIGIDA (esperado: 0) e da CONGELADA;
  - **Q2** — CORRIGIDA / CONGELADA;
  - **Q3** — posição da CORRIGIDA na classe de orçamento;
  - **Q4** — fração do teto (CORRIGIDA / Chronos-2 com covariáveis nos 1.000 pontos; também contra SARIMAX-X e ARX por mínimos quadrados);
  - **Q5** — robustez (pior grupo, fração > 1,5, catastróficas);
  - **Q6** — custo da CORRIGIDA (média ≤ 400; máximo por passo ≤ 1.000 FP).

## 5. Expectativas registradas antes

- **Desenvolvimento** (estresse de lacunas): 0 explosões com a correção, contra 10 sem ela; ~2% menos erro mesmo sem lacunas injetadas.
- **Reserva 1, sem as séries catastróficas** (análise posterior): v0.52 0,706 contra SARIMAX-X 0,823 e NLinear 1,0; Chronos-2 com covariáveis 0,674 contra 0,712 nos 1.000 pontos.
- **Custo:** ~395 FP médio no desenvolvimento, com 4 entradas. No BDG2, com 2 entradas mais ciclos de 24/168, pode passar de 400: **é o limite declarado e será reportado como está**.

## 6. Integridade

Execução única; repetição só por falha de infraestrutura, documentada. Nenhuma alteração de modelo depois do acesso. Todos os resultados são reportados.

| Arquivo | SHA-256 |
|---|---|
| lebre_v052h.py | `edbaf21dfc19729ce08f114f707f8f1ff900fd55cc6a9011114fc1b48b4e9fd7` |
| change_engine.py | `11bb13022e408776b2c0a222852e22d00e4c443b7a9f78471a9ce7a1b4c96e9d` |
| lebre_v052.py | `212872117d795203ae4bf46382af9b95b13eb05cb6cca507fa7e4546ef530b27` |
| final7.py (configuração) | `ccce251c8b46e0ff8da7d2a7297d65f1a333d4dde5f94eaf9790f2e16a3179e3` |
| comp_dev.py | `0bc9d773364ac130acfec1e1f688d2eb14b8a2eecc0a90569de51b7a6c9af40f` |
| strong_baselines.py | `323a9803abee2149ec880f02988a51ff87861b6bcaf36ab2e05f975a3561d258` |
| chronos_dev.py | `33deb6e80521b6941e47934ad8f738fc88b42070aa441590fa03549a307122b0` |
| data_v052.py | `88a77ae64b92e414aa55af070a5b142a88ddd20652e0b5d6c8cf841c4f8970fa` |
| select_reserve2.py | `d878391a91c3df59a052e5ba956277d79abb22c8b3fdc4779c7e6e7a528384dd` |
| RESERVA2.json | `23ce1a3aebaaff9020741120bbe2fe6025d0f013f58cffb9b60b6915c7ba050e` |
| heldout2_run.py | `bc7a4be42eb26bcef33d5b7537622b2edc85dc30fa942a3b2b37c2260aeb9118` |
| heldout2_chronos.py | `11de91e450055ac8306f37d702698a8f56a715d10002d56bd90c2fa75cce8c2f` |
| heldout2_analysis.py | `e3f013a44c45fadb411ad5256263e4d220e570d0f8afab3149b7df5542dba719` |
