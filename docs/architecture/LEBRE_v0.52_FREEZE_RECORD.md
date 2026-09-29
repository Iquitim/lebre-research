# LEBRE v0.52 — Registro formal de congelamento

**Arquitetura:** LEBRE (Lifecycle-governed Evidence-Based Resource Evolution)
**Versão:** 0.52 (com a correção das lacunas do alvo)
**Status:** `FROZEN_RESEARCH_VERSION_NOT_PROMOTED_WITH_SCOPE_LIMITS`
**Etapa:** `LEBRE-V0.52-FREEZE-01`
**Data:** 27 de setembro de 2026
**Relação com as versões anteriores:** a v0.1 continua sendo a **referência canônica** do projeto e a v0.51 continua sendo a **linha de base de pesquisa congelada**. As duas não foram alteradas: os 52 arquivos congelados da v0.51 conferem com seus hashes. Este congelamento **registra** a v0.52 como versão de pesquisa **avaliada em dados nunca vistos**, e **não é uma promoção**: as avaliações em dados reservados foram descritivas e não tinham critério vinculante de promoção.

---

## 1. Princípio que orienta a versão

A LEBRE **não precisa ser o melhor previsor**. Ela precisa **entregar bem com orçamento mínimo** (centenas de operações de ponto flutuante por passo) **e sem falhas catastróficas**. Modelos caros são **tetos de referência**, não alvos a vencer.

## 2. O que está congelado

| Item | Conteúdo |
|---|---|
| **Código do modelo** | Previsor hierárquico por entrada, motor de mudanças (e-process unilateral, níveis tipo e-LOND) e especialista de memória (com o segundo ciclo declarado). Só dependem de numpy. |
| **Configuração canônica** | A configuração "V052_CORRIGIDA" (§3), idêntica à avaliada na reserva 2. O código congelado reproduz **bit a bit** as previsões salvas (conferido em 3 séries, inclusive uma que explodia sem a correção). |
| **Cópias históricas** | Versões exatas de cada medição de desenvolvimento e a versão avaliada na reserva 1 (sem a correção). |
| **Infraestrutura de avaliação** | Carregadores de dados com a trava de acesso à reserva, comparadores (NLinear, DLinear, Holt-Winters, AMRules, ARX denso, LASSO online, ARX por mínimos quadrados com ordem online, SARIMA/SARIMAX), protocolo Chronos, scripts de estresse, nulos, custo e oráculo. |
| **Dados** | Regras e divisão da v0.52 (sementes 5201–5203, checksums dos arquivos), seleção da reserva 2 (próximas posições das mesmas permutações). |
| **Pré-registros e resultados** | Reserva 1 (125 séries) e reserva 2 (40 séries): pré-registros, scripts, previsões por série, tabelas, relatórios e logs. **Todos os 27 hashes declarados nos pré-registros conferem**, e os hashes dos dois pré-registros conferem com os anotados no diário no momento do registro. |
| **Documentação** | Diário de desenvolvimento, notas de desenho, especificação do algoritmo (rascunho 1 com adendos até o §13) e auditorias de literatura PRA-03 e PRA-04. |

Lista completa com SHA-256: `LEBRE_v0.52_SHA256SUMS.txt` (**650 arquivos**, todos verificados no momento do congelamento).

## 3. Constantes congeladas (configuração canônica)

| Grupo | Constantes |
|---|---|
| **Unidades de mudança** | uma por entrada (inclui o próprio passado do alvo, padronizado causalmente) + estado latente do resíduo (polos 0,8 e 0,95). Bloco de resposta: médias em faixas de oitava [1], [2–3], [4–7], [8–15], [16–31] + atraso de pico escolhido pelo desafiante. Divisões hierárquicas de faixa. M_max = 4 unidades ativas |
| **Desafiantes** | mínimos quadrados recursivos no episódio sobre [bloco, pico, valor atual], P₀ = 10·I; aquecimento de 250 amostras sem evidência; estatística do pico pré-branqueada em meia janela alternada, escolha em 200 amostras, persistente entre episódios |
| **Evidência** | perda recortada min{e²/B², 1} com B = 2·max(σ̂, 0,1·s_lenta); e-process sub-exponencial unilateral, c = 1 + max(ε, 0), centragem γ = min(média passada, 0), mistura uniforme em 8 valores de λ (0,9·2⁻ᵏ/c); ε de acréscimo, troca e divisão = 0,002; ε de remoção = −0,002 |
| **Multiplicidade** | α = 0,05; γ = 1/(2P) para as primeiras P = 2 × (número de unidades) hipóteses, depois 0,5·γ_k com γ_k ∝ 1/(k log² k); nível α·γ·(R + 1) |
| **Episódios** | 2 vagas; aquecimentos escalonados (um por vez); varredura: encerra se a evidência do episódio for ≤ 0 após 100 amostras; limite de 5.000 amostras; espera de 2.000 passos; remoção periódica a cada 2.000 passos; decisões a cada 10 passos |
| **Triagem** | por entrada ainda não ativa, correlações pré-branqueadas AR(1) das médias de faixa com o resíduo, peso 0,02, cada parte na sua própria fase a cada 4 passos; abertura acima de 15,09 (χ²₅, 99%); divisões acima de 6,63 (χ²₁, 99%) |
| **Especialista estrutural (base)** | NLMS com μ = **0,05** (desajuste pequeno: condição de uso, §5); contrato de entrada ±8 σ com quarentena de 32 passos |
| **Memória** | features da v0.51 + ε relativo e piso de escala lenta; segundo ciclo declarado (168 h) nas séries horárias de prédios; **retenção do último valor observado durante lacunas do alvo** |
| **Combinação e saída** | média dinâmica de modelos (λ = 0,99, η = 1/2, a cada 8 passos); **contrato de saída**: envelope dos alvos observados (taxa 10⁻³), margem 0,5× a largura; previsão não finita → último valor observado |
| **Intervalo** | quantil adaptativo, α = 0,1, γ = 0,1, a cada 8 passos |
| **Grupos reportados** | entradas com correlação causal ≥ 0,95 são reportadas junto da entrada aceita (não afetam decisões) |

## 4. Evidência que acompanha o congelamento

**Pré-registrada, reserva 2** (40 séries nunca vistas: 20 CAMELS-BR, 20 BDG2):
- 1º lugar na classe de orçamento: erro relativo ao NLinear **0,767** [IC 95%: 0,657; 0,858], contra 0,957 do DLinear (~4× mais caro) e 1,000 do NLinear;
- **zero** séries catastróficas e **nenhuma** série acima de 1,5; pior grupo 0,836;
- empate com o SARIMAX com entradas (0,999 [0,965; 1,038]); erro 16% acima do Chronos-2 com covariáveis (1.000 pontos: 0,769 contra 0,662), a um custo ~10⁷ vezes menor;
- custo médio **407** FP/passo e máximo **1.015** por passo: **~2% acima dos limites declarados** (400 e 1.000).

**Pré-registrada, reserva 1** (125 séries; versão **sem** a correção): 6 explosões por instabilidade da memória durante lacunas do alvo; resultado total dominado por elas (5,20). Esse modo de falha motivou a correção.

**Desenvolvimento (não vinculante):**
- controle de mudanças falsas: 0/40 e 0/30 execuções com alvo sem estrutura; simulação do e-process com erro tipo I ≤ 0,025 (α = 0,05);
- teste de estresse de lacunas: 10 → 0 explosões com a correção;
- ablações em dados reservados: o mecanismo de testes **não melhorou a precisão** em relação a "todas as entradas ligadas, sem testes" (0,99); as divisões hierárquicas não fizeram diferença (0,996). O valor do mecanismo está na estrutura certificada e explicada, não na precisão.

## 5. Condição de uso e limitações congeladas junto

1. **Condição de uso:** para que "melhora preditiva certificada" signifique "estrutura", a referência precisa ter **desajuste pequeno**. Com NLMS de passo 0,1, 20% dos alvos sem estrutura aceitaram uma mudança.
2. **Limite de informação:** entradas muito suaves (autocorrelação ~0,99) com atraso médio/longo não são descobertas no comprimento das séries; nem um oráculo online descobre. A previsão continua boa nesses casos.
3. **Custo:** ~2% acima do contrato (média e pico) nos prédios e bacias; a contagem de FP é analítica e **não foi medida em microcontrolador**.
4. **Entradas quase idênticas:** indistinguíveis por melhora preditiva; o modelo reporta o grupo.
5. **Cobertura empírica:** hidrologia (ONS, CAMELS-BR) e prédios (BDG2) com poucas entradas; a reserva 2 não tem ONS; 40 séries dão intervalos largos; 4 locais do BDG2 compartilham o clima com o desenvolvimento.
6. **Comparadores ausentes:** modelos ultraleves (SparseTSF, FITS, TinyCast) e o TTM com exógenas não foram avaliados no protocolo online.
7. **Originalidade (PRA-04):** o mecanismo central (e-process de melhora preditiva para mudanças estruturais com controle no fluxo) **já existe** em árvores online (Amoukou, Mishra & Veloso, 2026). A contribuição da v0.52 é de **integração/extensão** (séries com entradas, unidades por entrada, hierarquia, remoção e troca, FDR, orçamento), mais o achado metodológico da condição de uso e a evidência empírica sob orçamento.

## 6. O que fica fora deste congelamento

- As opções experimentais implementadas e **desligadas** na configuração canônica (controle pareado, triagem bruta, desafiante persistente, ablações "tudo ligado", aprendiz vivo por mínimos quadrados, cortes de custo) fazem parte do código congelado apenas como **ablações**.
- Qualquer nova avaliação exige **dados nunca vistos**. As reservas 1 e 2 estão consumidas. Continuam disponíveis as posições 80+ da permutação do CAMELS-BR e 55+ da do BDG2; os rios elegíveis do ONS se esgotaram.
