# LEBRE v0.53 — M2, rascunho 2: agregação para a saída, evidência para a auditoria

**Data:** 08/10/2026 · **Status:** proposta, antes de qualquer código desta revisão. **Base:** PRA-07 (literatura para o
problema de C05) e a medição do rascunho 1 (`M2_DEV_R1_RESULTADO.md` no LEBRE Lab). **Condição do responsável pelo
projeto:** nenhuma versão é promovida sem resolver C05.

## 1. Por que mudar a concepção

O rascunho 1 decide a saída com um teste (e-process com nível e-LOND). Testes exigem evidência acumulada, e numa série
curta essa espera custa caro (C05). É o "catch-up phenomenon" (van Erven, Grünwald e de Rooij, 2012). A literatura de
previsão com especialistas troca a garantia de erro tipo I da troca por uma garantia de **arrependimento**: a perda
acumulada da saída fica perto da do melhor entre R e L, para qualquer sequência de dados.

## 2. Mudança

- **Saída:** média ponderada de R (referência trivial) e L (LEBRE), com pesos de um algoritmo de especialistas que
  dispensa conhecer a escala das perdas. Candidatos (seção 4): **AdaHedge** e **FlipFlop** (de Rooij et al., 2014),
  sobre a perda quadrática de cada previsor.
- **Prioridade inicial:** pesos iguais (sem favorecer R nem L).
- **Auditoria:** o e-process do rascunho 1, com orçamento próprio, continua rodando para registrar **eventos** "L
  melhor que R" e "R melhor que L", com evidência; ele **não** decide a saída.
- **Estrutura:** inalterada; o caminho estrutural continua idêntico ao da v0.52.
- **Referência:** a mesma regra do rascunho 1 (zero só se declarado; sazonal se há ciclo; senão persistência).

## 3. Garantias e limites

- **Perda quadrática é convexa:** a perda da média ponderada é no máximo a média ponderada das perdas, então o
  arrependimento do AdaHedge sobre as perdas dos especialistas vale para a saída (desigualdade de Jensen). A garantia é
  determinística (vale para qualquer sequência), mas de **pior caso**, da ordem da raiz da perda acumulada do melhor; o
  comportamento esperado em dados com um previsor consistentemente melhor é bem mais favorável (FlipFlop: arrependimento
  constante quando seguir o líder funciona). **A medição no Lab é que decide**, não a garantia.
- **O que se perde:** a saída deixa de ter a semântica "troca só com evidência". Afirmações do tipo "a LEBRE é melhor que
  a referência nesta série" passam a vir só dos eventos de auditoria.
- **Custo:** 2 especialistas; ~10 FP por passo para os pesos, mais a auditoria (~18 FP). A medir.

## 4. Medição (plano próprio no LEBRE Lab, antes de rodar)

- **Candidatos:** AdaHedge; FlipFlop. Nenhum parâmetro livre além dos do próprio algoritmo (FlipFlop tem dois
  parâmetros de troca com valores recomendados pelos autores; usar os recomendados, sem ajuste).
- **Famílias:** as 22 da medição anterior **e uma família nova de séries curtas** (dados de desenvolvimento cortados nos
  primeiros 360 passos de cada série de B01-B07 e C01-C04, mais C05 inteira), para que a solução não seja feita sob
  medida para C05.
- **Critérios (fixados no plano):** os critérios 1, 2, 4, 5 e 6 do rascunho 1; **C05 com M2 ÷ v0.52 de limite superior
  <= 1,02, obrigatório**; e, na família curta, M2 ÷ melhor entre v0.52 e referência com limite superior <= 1,05. O
  critério 3 (alternância) não se aplica a pesos contínuos.
- **Se nenhum candidato atender:** voltar à literatura (Fixed Share para tracking; Squint), sem ajustar parâmetros.

## 5. Resultado no banco de desenvolvimento (08/10/2026)

Medição no LEBRE Lab (`M2_DEV_R2_PLANO.md` com o adendo 1, `M2_DEV_R2_RESULTADO.md`; protótipo `82e7b16`). Reprodução da
v0.52 e do rascunho 1 exatas.

- **C05 resolvida nas duas configurações:** M2 ÷ v0.52 = 1,000 (IC 95% 1,000–1,000), contra 2,07 no rascunho 1; o peso
  da LEBRE passa de 0,9 entre os passos 2 e 33 (antes, promoção entre 200 e 260).
- **AdaHedge atende aos critérios 1, 2, 4, 5 e 6** nas 22 famílias; em B07 a combinação supera os dois previsores (0,92
  contra a referência, 0,98 contra a v0.52, intervalos excluindo 1).
- **As duas falham o critério 7 (séries curtas):** limite superior 1,115 (AdaHedge) e 1,129 (FlipFlop), contra 1,05. A
  falha vem só de B02 (carga elétrica): nos primeiros passos a LEBRE ainda não aprendeu o nível e acumula um déficit de
  perda que os pesos, por tratarem todo o passado igualmente, demoram centenas de passos para recuperar (ou não
  recuperam em 360). FlipFlop também falha o critério 1 em C04 (1,012).
- **Custo:** acréscimo de ~66 FP por passo (agregação 48, auditoria ~18), dentro do limite revisado de 75 declarado no
  plano antes de rodar; o limite antigo de 25 não seria atendido. A aceitação do limite revisado é do responsável pelo
  projeto.
- **Pela regra do plano, nenhuma configuração é escolhida.** O próximo passo é a literatura de acompanhamento do melhor
  especialista que muda (Fixed Share; arrependimento adaptativo a intervalos), sem ajustar parâmetros.
