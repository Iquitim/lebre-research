# Revisão de literatura — adequação dos mecanismos da LEBRE v0.3 / v0.3.1

**Rótulos:** `ESTABELECIDO` (resultado da fonte, sob as hipóteses dela) · `ANALOGIA` (estrutura compartilhada, sem transferir garantias) ·
`HIPÓTESE_LEBRE` (afirmação sobre a LEBRE, testada só onde indicado).
**Verificação:** as referências abaixo foram localizadas por busca nesta sessão. O enunciado central de Howard et al. (2020, Lema 3(d)) e o de
de la Peña (1999) foram conferidos **no texto do PDF**. As demais estão resumidas no nível da contribuição central conhecida.

## 1. Estado latente: forma de inovações do filtro de Kalman

- **Fontes.** Ljung, *System Identification: Theory for the User*, 2ª ed., Prentice Hall, 1999 (modelos de espaço de estados, forma de
  inovações); Anderson & Moore, *Optimal Filtering*, 1979.
- `ESTABELECIDO`: o preditor de um passo de um sistema linear gaussiano em espaço de estados é o filtro de Kalman estacionário. Em forma de
  inovações ele equivale a um preditor ARMAX, ou seja, uma combinação linear de entradas passadas e de inovações passadas filtradas pelo polo `a(1−K)`.
- **Adequação.** O átomo latente da v0.3 (`s = p·s + (1−p)·u`, mais o acionamento `q` da entrada) é exatamente essa estrutura para estado de
  1ª ordem, com o polo escolhido num banco finito. **Verificado (T5):** o MSE fica a 1,18× (mediana) do ótimo de Kalman exato na I6.
  O excesso vem do banco discreto de polos, do desajuste do NLMS e da adaptação.
- **Limite.** Só dinâmica de 1ª ordem. Estados de ordem ≥ 2 (ressonador H1) não são representados, o que explica a perda para o ARX em H1.
- **Arte relacionada.** Bases ortonormais (Laguerre/Kautz): Wahlberg, *IEEE TAC* 36:551–562 (1991); Heuberger, Van den Hof & Bosgra,
  *IEEE TAC* 40:451–465 (1995). Li, Lu, Mo & Chen (arXiv 2512.21096) tratam a escolha de polos que minimiza o viés no pior caso (pontos de Tsuji).
  `ANALOGIA`: o banco {0; 0,5; 0,8; 0,95} é uma escolha ad hoc de polos. A literatura de bases ortonormais oferece um critério
  fundamentado, ainda não adotado.

## 2. Promoção (PROVISIONAL→ACTIVE): teste por martingale de mistura

- **Fontes.** Ville (1939), desigualdade para supermartingales não negativos; Robbins (1970), mistura normal; Howard, Ramdas, McAuliffe &
  Sekhon, *Time-uniform, nonparametric, nonasymptotic confidence sequences*, *Ann. Statist.* 49(2):1055–1080 (2021); Howard et al.,
  *Time-uniform Chernoff bounds via nonnegative supermartingales*, *Probability Surveys* (2020).
- `ESTABELECIDO`: se `exp(λS − λ²V/2)` é supermartingale para todo λ, então a mistura gaussiana sobre λ também é, e pela desigualdade de Ville
  P(sup M ≥ 1/α) ≤ α. É um teste válido sob parada opcional (*anytime-valid*).
- **v0.3 (iter4):** usava `V = σ̂²Σφ²` com σ̂ *plug-in* no momento da decisão, o que só é válido sob ruído gaussiano com σ conhecido e constante.
  **Falha verificada (T3):** 0,21–0,26 promoções falsas por fluxo sob ruído t₃ ou heterocedástico, contra um limite de 0,052.
  E promoções espúrias durante o silêncio (T6).
- **v0.3.1:** usa `V = Σ(eφ)²` (auto-normalizado). `ESTABELECIDO` (de la Peña, *Ann. Probab.* 27(1), 1999, Lema 6.1; Howard et al. 2020, Lema 3(d),
  **conferido no PDF**): com incrementos condicionalmente simétricos, `S_t` é sub-gaussiano com processo de variância `Σ ΔS²`, **sem exigir
  nenhum momento**. **Verificado:** 0 promoções falsas em 400 fluxos nulos (gaussiano, t₃, heterocedástico) e 0 eventos no silêncio.
- **Limite honesto.** A simetria condicional de `e_t φ_t` sob H0 vale quando φ é independente de e e o ruído é simétrico. No laço adaptativo
  (NLMS atualizando, σ̂ mudando) a validade é aproximada. A mistura precisa ser previsível: τ é fixado na abertura do episódio.
- **Multiplicidade.** Usamos Bonferroni sobre o dicionário (`log(p/α)`). Isso tem relação com o RIC de Foster & George, *Ann. Statist.* 22(4) (1994),
  penalidade `2 log p`, e com o *alpha-investing* de Zhou, Foster, Stine & Ungar (KDD 2005; *JMLR* 7, 2006). O alpha-investing é a
  **arte anterior mais próxima** da seleção estrutural em fluxo, com controle do tipo mFDR. `HIPÓTESE_LEBRE`: substituir Bonferroni por
  alpha-investing ou por e-values com controle de FWER/FDR (e-BH de Wang & Ramdas, *JRSS-B*, 2022; FWER com e-values, arXiv 2501.09015, autores não verificados nesta sessão) daria mais poder com o mesmo controle.
  **Limite:** a garantia vale por episódio de teste. Por fluxo, o número esperado de falsas promoções é ≤ (nº de episódios)·α/p.

## 3. Remoção (ACTIVE→EVICTED): CUSUM

- **Fontes.** Page (1954); Lorden, *Ann. Math. Statist.* 42:1897–1908 (1971); Moustakides, *Ann. Statist.* 14:1379–1387 (1986);
  Shin, Ramdas & Rinaldo, *E-detectors*, *NEJSDS* 2(2):229–260 (2023).
- `ESTABELECIDO`: o CUSUM sobre a razão de log-verossimilhança é minimax-ótimo no critério de Lorden, entre procedimentos com ARL até alarme falso ≥ γ
  (Moustakides). Com limiar h, o ARL é ≥ e^h.
- **Adequação.** O incremento `c(2e+c)/(2σ²)` é exatamente a razão de log-verossimilhança gaussiana entre os preditivos "com" e "sem" o átomo.
  **Verificado (T4):** 4 remoções falsas em 1,14 milhão de passos, ARL empírico ≈ 285 mil ≫ e^h = 6000 (conservador).
- **Limites.** (i) Tanto a hipótese "pré-mudança" quanto a "pós-mudança" são compostas (o coeficiente se adapta), então a otimalidade de
  Lorden–Moustakides **não se transfere** (`ANALOGIA`). Os e-detectores de Shin, Ramdas & Rinaldo são o arcabouço fundamentado
  para esse caso não paramétrico e composto. (ii) O aluguel de parcimônia soma um desvio deliberado: com ele, o ARL passa a ser um *design*,
  não uma garantia.

## 4. Aprendizado de parâmetros: NLMS

- **Fontes.** Slock, *IEEE TSP* 41:2811–2825 (1993); Haykin, *Adaptive Filter Theory*.
- `ESTABELECIDO`: o NLMS é estável em média quadrática para 0 < μ < 2, e o desajuste é ≈ μ/(2−μ) sob regressores aproximadamente brancos.
- **Adequação.** μ = 0,1 dá ≈ 5% de excesso de MSE. Com regressores correlacionados (átomos latentes com y-AR, entradas coloridas em dados reais),
  a convergência do NLMS fica lenta. O RLS resolveria, mas custa O(m²), e o orçamento foi o motivo da escolha.

## 5. Excitação persistente (retenção em quiescência)

- **Fontes.** Ioannou & Sun, *Robust Adaptive Control* (1996); Narendra & Annaswamy, *Stable Adaptive Systems* (1989).
- `ESTABELECIDO`: sem excitação persistente os parâmetros não são identificáveis e podem derivar. Zonas mortas e atualização condicionada à
  excitação são remédios clássicos.
- **Adequação.** A v0.3 congela a *evidência estrutural* (não os pesos) sem excitação. **Verificado (T6):** latente retido em 30/30 silêncios,
  com 0 eventos durante o silêncio na v0.3.1. `HIPÓTESE_LEBRE`: o limiar de 10% da potência de longo prazo é uma escolha de projeto, não derivada.

## 6. Seleção de modelos online com esquecimento

- **Fonte.** Raftery, Kárný & Ettler, *Technometrics* 52(1):52–66 (2010), Dynamic Model Averaging.
- `ANALOGIA`: o DMA faz média ponderada de modelos com esquecimento em tempo de fluxo. A v0.3 faz *seleção* dura por testes. O DMA é o
  comparador bayesiano natural, e a v0.3 não foi comparada a ele (**lacuna**).

## 7. Filtragem adaptativa esparsa

- **Fonte.** Chen, Gu & Hero, *Sparse LMS for system identification*, ICASSP 2009 (ZA-LMS / RZA-LMS).
- `ESTABELECIDO`: uma penalidade ℓ1 no LMS acelera a identificação de sistemas esparsos.
- **Relação.** O RZA-LMS é um baseline do BENCH-01 e a v0.3 o supera. A diferença de natureza é que o RZA mantém todos os taps (custo O(p));
  a v0.3 mantém apenas os átomos promovidos (custo O(m)), às custas de uma busca amostrada.

## 8. Veredito de adequação

| Mecanismo | Fundamentação | Validade empírica verificada | Lacuna principal |
|---|---|---|---|
| Latente em forma de inovações | sólida (Kalman) | 1,18× o ótimo | só 1ª ordem; polos ad hoc |
| Promoção por martingale (v0.3.1) | sólida (Ville + de la Peña) | 0 falsos positivos em 400 nulos | validade aproximada no laço adaptativo; Bonferroni conservador |
| Remoção por CUSUM | sólida em forma simples; composta na prática | ARL ≫ garantia | otimalidade não transferível; o aluguel é um *design* |
| NLMS | sólida | — | lento com regressores correlacionados |
| Portão de excitação | princípio clássico; limiar ad hoc | 30/30 retenções | limiar de 10% não derivado |
| Aluguel de parcimônia | MDL por analogia | — | T_idle é escolha de projeto |

**Conclusão:** a v0.3.1 é adequada à literatura naquilo que afirma. Cada decisão estrutural passou a ter uma justificativa estatística citável,
e as duas falhas de validade encontradas na v0.3 (plug-in de σ e dependência de escala) foram corrigidas com resultados estabelecidos.
Ela **não** é adequada para afirmar otimalidade, nem garantias exatas no laço fechado adaptativo. As comparações que faltam são com DMA,
com alpha-investing e com ARX + seleção por RIC.
