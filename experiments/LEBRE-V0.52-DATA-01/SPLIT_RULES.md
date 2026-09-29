# Divisão desenvolvimento / held-out da v0.52 (fixada em 26/09/2026)

**Arquivo da divisão:** `SPLIT_V052.json`, SHA-256 `f05cb7487c645fba6fca311060d08912502c9de37b52e1d773a86e7db1ef0c46` (em `SPLIT_V052_SHA256.txt`).
**Gerado por:** `make_split_v052.py`. Usa só metadados e **cobertura** (fração de valores não faltantes); os valores das séries não foram inspecionados.
**Dados de referência:** `data/external_v052/SHA256SUMS.txt`; o hash dele está gravado no JSON.
**Sementes:** 5201 (ONS), 5202 (CAMELS-BR), 5203 (BDG2). Conferidas: nunca usadas antes no projeto.

## 1. ONS — cascatas de usinas

- **Tarefa:** alvo = vazão **afluente** horária de uma usina; entradas = vazão **defluente** da(s) usina(s) imediatamente a montante, pela topologia física das cascatas. A topologia está no script e **ainda precisa ser conferida** com o diagrama esquemático oficial do ONS antes do pré-registro.
- **Janela:** 01/01/2015 – 31/12/2025, horária (96.432 horas).
- **Agregação pré-declarada:** médias de 3 horas (≈ 32 mil passos por tarefa). Os atrasos de viagem de até ~4 dias cabem no dicionário (L = 32).
- **Elegibilidade:** cobertura ≥ 90% do alvo e de cada entrada.
- **Unidade de divisão: o rio inteiro.** Nenhuma cascata aparece nos dois conjuntos.
- **Resultado:**
  - **Desenvolvimento:** rio **Grande**, sorteado entre os rios com ≥ 3 tarefas elegíveis. São 11 tarefas, de Camargos→Itutinga até Marimbondo→Água Vermelha.
  - **Held-out:** 45 tarefas em 10 rios (Paranapanema 9, Paranaíba 8, Tocantins 6, Tietê 5, Iguaçu 4, Uruguai 3, Jacuí 3, Doce 3, São Francisco 2, Paraná 2).
  - **Excluída:** Salto Caxias → Baixo Iguaçu, com cobertura do alvo de 63%. A usina entrou em operação durante a janela.
- **Ponto de atenção:** as **4 tarefas com várias entradas** (Capivara, Itumbiara, Machadinho, Jupiá) caíram todas no held-out; o desenvolvimento só tem tarefas de uma entrada. O ajuste para o caso de várias entradas terá de vir de dados **semi-sintéticos**, construídos com entradas do rio Grande.

## 2. CAMELS-BR — bacias

- **Tarefa:** alvo = vazão diária; entradas = precipitação, evapotranspiração real e temperatura da bacia.
- **Elegibilidade (atributos publicados):** uso consuntivo < 1%, grau de regulação < 0,05 e controle de qualidade da vazão ≥ 95%. **237 bacias elegíveis.**
- **Resultado:** 10 bacias de desenvolvimento e 50 de held-out, sorteadas sem sobreposição. A lista está no JSON.

## 3. BDG2 — edifícios

- **Tarefa:** alvo = consumo horário de água gelada, água quente ou vapor; entradas = clima do local.
- **Elegibilidade:** medidores "cleaned" com cobertura ≥ 90% e ≥ 50% de valores não nulos. **766 elegíveis.**
- **Resultado:** 5 medidores de desenvolvimento e 30 de held-out, sorteados.

## 4. Tratamento de falhas (pré-declarado, igual para todos os modelos)

1. **Agregação (ONS):** a média de 3 h é calculada se houver ≥ 2 das 3 horas; senão, o bloco fica faltante.
2. **Alvo faltante:** o modelo ainda emite a previsão, mas **não atualiza** nada (nem pesos nem evidência) e o passo **não entra** na métrica.
3. **Entrada faltante:** usa-se o último valor observado (causal). O passo entra em **quarentena**: sem evidência e sem aprendizado estrutural, como o portão de contrato da LEBRE. Os comparadores recebem a mesma entrada preenchida.
4. **Valores negativos ou fisicamente impossíveis** (vazão < 0): tratados como faltantes.
5. **Nenhuma** interpolação que use valores futuros.

## 5. Regras de uso

- Os dados de **held-out** só são carregados na execução final pré-registrada. Durante o desenvolvimento, os scripts leem apenas as tarefas de desenvolvimento.
- Qualquer alteração na topologia, na janela ou nos critérios depois deste ponto exige uma nova divisão, com novas sementes e registro do motivo.

## 6. Adendo (26/09/2026): regra de validade achada no desenvolvimento, antes de qualquer acesso ao held-out

A base horária do ONS contém erros grosseiros de registro. No rio Grande, de desenvolvimento, Furnas chega a 972 mil m³/s para uma afluência típica de ~1.000. Regra acrescentada, causal e igual para todos os modelos:

- **Um valor é inválido** (tratado como faltante) se exceder **20 × o percentil 90 da própria série nos 7 dias anteriores**:
  - ONS: janela de 56 blocos de 3 h, aplicada ao alvo e a cada entrada, depois da agregação;
  - BDG2: janela de 168 h, aplicada ao alvo.
- Implementada em `experiments/LEBRE-V0.52-PROTO-01/data_v052.py` (`_spike_filter`).
- A divisão (`SPLIT_V052.json`) **não muda**: a regra afeta só o tratamento de valores, não quais tarefas pertencem a cada conjunto.

## 7. Conferência da topologia do ONS (26/09/2026; `TOPOLOGY_CHECK.csv`)

**Método:** cada par (alvo ← usina de montante) foi comparado com o cadastro oficial do ONS (dataset "Reservatórios", CC-BY: rio, coordenadas e data de entrada), **só com metadados**, sem inspecionar valores das séries do held-out.

**Resultado:**
- **50 dos 61 pares** estão no mesmo rio.
- **Os outros 11** são confluências ou afluentes que desembocam no reservatório de jusante: Tibagi → Capivara; Araguari e Corumbá → Itumbiara; Pelotas e Canoas → Machadinho; Tietê → Jupiá.
- **Inconsistência do cadastro:** Nova Ponte aparece como "Paranaíba", mas a usina fica fisicamente no Araguari, a montante de Miranda. O par está correto.
- **Distâncias** de 4 a 390 km. Os trechos mais longos (Tocantins 276–390 km; Sobradinho → Luiz Gonzaga 278 km) são compatíveis com tempos de viagem de até ~4 dias, dentro do dicionário (32 blocos de 3 h).

**Conclusão:** a topologia usada na divisão é consistente com o cadastro oficial. **A divisão não muda.**

## 8. Adendo 2 (26/09/2026): regra de salto do ONS, antes de qualquer acesso ao held-out

- **Por quê:** no rio Grande (desenvolvimento), picos isolados de 20–43 mil m³/s em Furnas (típico ~1.000) sobreviveram à regra 20×p90, porque a série varia muito.
- **Regra acrescentada** (ONS, alvo e entradas, depois da regra 20×p90; causal e igual para todos os modelos): um bloco de 3 h é inválido se exceder **ao mesmo tempo 10 × o último valor válido e 5 × a mediana dos 56 blocos anteriores**. A vazão de um reservatório grande não decuplica em 3 h. A condição da mediana impede que um valor baixo isolado trave a série.
- **Efeito no desenvolvimento:**
  - Furnas passa de 48,9 para 23,1 × mediana;
  - a fração faltante sobe ~1 ponto percentual em Furnas e em M. Moraes, e ≤ 0,5 p.p. nas demais.
- **A divisão não muda.**
- **Alternativa descartada:** uma regra no modelo (limitar o alvo a ŷ ± κσ). Ajudava no ONS, mas prejudicava séries com picos legítimos (BDG2 0,930 → 1,06 para qualquer κ; `TUNE_KAPPA.csv`). O problema era de **dados**, não de modelo.
