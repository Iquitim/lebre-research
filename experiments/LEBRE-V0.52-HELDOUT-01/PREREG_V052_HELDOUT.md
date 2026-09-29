# Pré-registro — avaliação da LEBRE v0.52 em dados reservados

**Data:** 27/09/2026 · **Status:** registrado **antes** de qualquer acesso aos dados reservados. Nenhuma série desta avaliação foi carregada, vista ou usada em desenvolvimento.

## 1. Objetivo

Medir **onde a v0.52 fica**, sem mudar premissas nem modelo, em séries reais nunca vistas por nenhum modelo, contra ablações e comparadores fortes. Esta avaliação é **descritiva**: não há decisão de promoção aqui. Ela serve de base para a revisão de literatura e para o congelamento da versão.

## 2. Dados (reserva da divisão SPLIT_V052, criada em 26/09/2026 antes da modelagem)

- **ONS:** 45 usinas em 10 rios **diferentes** do rio de desenvolvimento (Doce, Iguaçu, Jacuí, Paraná, Paranaíba, Paranapanema, São Francisco, Tietê, Tocantins, Uruguai). Alvo: vazão afluente; entradas: defluência das usinas imediatamente a montante; médias de 3 h; ciclo diário declarado (8).
- **CAMELS-BR:** 50 bacias. Alvo: vazão diária; entradas: precipitação (MSWEP), evapotranspiração (GLEAM) e temperatura (ERA5-Land).
- **BDG2:** 30 medidores de aquecimento/resfriamento. Alvo: consumo horário; entradas: temperatura do ar e de orvalho do local; ciclos diário (24) e semanal (168) declarados.
- As regras de validade (picos, saltos) são as fixadas antes de qualquer acesso (SPLIT_RULES §6 e §8). Checksum da divisão: SPLIT_V052.json SHA-256 `f05cb7487c645fba6fca311060d08912502c9de37b52e1d773a86e7db1ef0c46`.

## 3. Modelos (todos congelados; nenhum ajuste nos dados reservados)

**LEBRE v0.52 — configuração da medição #7, sem mudança** ("COMPLETA"): hipóteses por entrada, com refinamento hierárquico, evidência unilateral, piso de escala, pico persistente, passo da base 0,05, escalonamento de aquecimentos, triagem espalhada, estatística do pico em meia janela e ciclo semanal na memória dos prédios.

**Ablações** (mesmo código, uma peça por vez): SEM_DIVISOES; TUDO_LIGADO (todas as unidades ativas, sem testes); TUDO_LIGADO_RLS (idem, aprendiz de mínimos quadrados); ATÔMICA (v0.52 por atraso); V051 (versão congelada anterior); SÓ_MEMÓRIA (especialista de memória com o ciclo semanal nos prédios).

**Comparadores com os protocolos do desenvolvimento:**
- online, calibrados nos primeiros 15% (até 5.000 passos): NLinear, DLinear, Holt-Winters, AMRules, ARX denso NLMS, LASSO online;
- ARX_RLS_PLS: seis ARX por mínimos quadrados recursivos, escolha online por mínimos quadrados preditivos, sem calibração;
- SARIMAX-X e airline (SARIMA), por máxima verossimilhança nos primeiros 15%;
- modelos de fundação sem treino, em 1.000 pontos: Chronos-2 com covariáveis (entradas passadas + valor atual como covariável futura), Chronos-2 univariado, Chronos-Bolt small.

## 4. Métricas e análises (fixadas em `heldout_analysis.py`)

- **Principal:** MSE relativo ao NLinear por série, na máscara comum (últimos 70%, alvo observado, todos os modelos finitos; um modelo com < 95% de previsões finitas numa série conta como **falha** ali). Média geométrica por grupo e no total (peso igual por série); secundária: média dos três grupos.
- **Incerteza:** IC de 95% por bootstrap estratificado por grupo (2.000 reamostras, semente 8001), para cada modelo e para as razões pareadas COMPLETA / outro.
- **Protocolo dos 1.000 pontos** para a comparação com os modelos de fundação.
- **Robustez:** pior grupo; fração de séries com erro relativo > 1,5.
- **Custo:** FP médio por passo; p99,9 e máximo por passo da COMPLETA.
- **Estrutura:** unidades aceitas, momento da primeira aceitação, grupos reportados, cobertura do intervalo.

## 5. Perguntas (lidas a partir dos IC; "melhor" = IC da razão pareada inteiramente abaixo de 1)

- **Q1.** A COMPLETA é melhor que TUDO_LIGADO (o mecanismo de testes contribui para a precisão fora da amostra)?
- **Q2.** Onde a COMPLETA fica em relação ao ARX_RLS_PLS (o comparador forte do desenvolvimento), no total e por grupo?
- **Q3.** Onde ela fica em relação ao Chronos-2 com covariáveis (1.000 pontos)?
- **Q4.** Ela mantém a robustez do desenvolvimento (pior grupo e fração de falhas grandes menores que as dos comparadores lineares)?
- **Q5.** As divisões hierárquicas fazem diferença (COMPLETA contra SEM_DIVISOES)?
- **Q6.** O custo (média ≤ 400; pico ≤ 1.000 FP) se mantém em séries novas, inclusive com mais entradas (d até 5 no ONS)?

## 6. Expectativas a partir do desenvolvimento (para a leitura honesta depois)

Desenvolvimento (29 séries, **reusadas em 7 rodadas de ajuste**; viés otimista esperado): COMPLETA 0,709; TUDO_LIGADO 0,731; ARX_RLS_PLS 0,654 (BDG2 2,73); SEM_DIVISOES 0,699; SARIMAX-X 0,992; nos 1.000 pontos, COMPLETA 0,669 contra Chronos-2 com covariáveis 0,701. **Espera-se degradação fora da amostra.**

## 7. Integridade

- **Execução única.** Só uma falha de infraestrutura (não de modelo) permite repetir a execução, e isso é documentado; as séries já salvas não são refeitas.
- Nenhum parâmetro, regra ou modelo é alterado depois do acesso.
- Os resultados são reportados integralmente, inclusive os desfavoráveis.

**Arquivos (SHA-256):**

| Arquivo | SHA-256 |
|---|---|
| lebre_v052h.py | `e7765c4c48fcf20216ea76cf5a40bc4a9d7249a8eb900037e9d7c1280ed94aff` |
| change_engine.py | `11bb13022e408776b2c0a222852e22d00e4c443b7a9f78471a9ce7a1b4c96e9d` |
| lebre_v052.py | `212872117d795203ae4bf46382af9b95b13eb05cb6cca507fa7e4546ef530b27` |
| final7.py (configuração) | `ccce251c8b46e0ff8da7d2a7297d65f1a333d4dde5f94eaf9790f2e16a3179e3` |
| final4.py | `5452788b17314c03f03755216c4328c2ddaba70a1e9fdf54b342087fbb5fd026` |
| comp_dev.py | `0bc9d773364ac130acfec1e1f688d2eb14b8a2eecc0a90569de51b7a6c9af40f` |
| strong_baselines.py | `323a9803abee2149ec880f02988a51ff87861b6bcaf36ab2e05f975a3561d258` |
| chronos_dev.py | `33deb6e80521b6941e47934ad8f738fc88b42070aa441590fa03549a307122b0` |
| data_v052.py | `88a77ae64b92e414aa55af070a5b142a88ddd20652e0b5d6c8cf841c4f8970fa` |
| abl_analysis.py (memória isolada) | `ffe71d53a6c9c3c24094ce0fcd4a5ee3821e9bade90650567026d2a124833695` |
| lebre_v051.py | `f4dcf460dedfcb583844c54b2cb27d2afe52b44e85f86762305e08ddf226cda3` |
| heldout_run.py | `36e4c8c640d58105d744b1fed77944312d5f9db7c05cc4b471a5382dcf3a4338` |
| heldout_chronos.py | `68dbb04ba7b8877503a7ae73fe40e167cfc52de590ae94c7abe63568d60bbce5` |
| heldout_analysis.py | `15c33355a1f709ff23d946b99b570d135410585c17c6d3c87aab8115a8248333` |

**Nota:** o hash de lebre_v052h.py difere do registrado na medição #7 (`e6bb3a89…`) só porque as opções das ablações (all_on, rls_live) foram acrescentadas depois dela. Desligadas, o código reproduz a medição #7 **bit a bit** (verificado em 27/09/2026 com um sintético completo).
