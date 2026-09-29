# LEBRE v0.52 — Especificação do algoritmo integrado (rascunho 0)

**Data:** 25/09/2026 · **Status:** rascunho, sem código. Parâmetros entre ⟨⟩ serão fixados no desenvolvimento, antes do pré-registro.
**Base:** Nota 01 (formulação), Nota 02 (orçamento de computação e literatura), Errata 01 da v0.51.

## 0. Ideia em uma frase

Um previsor online de custo fixo em que **toda mudança de estrutura é um experimento**: um desafiante roda em sombra, é comparado com o modelo vigente por um e-process de melhora preditiva e só é aceito dentro de um controle de mudanças falsas válido para o fluxo inteiro. A escolha de quais experimentos rodar segue uma **varredura com orçamento**, inspirada na regra ótima de detecção com amostragem controlada.

## 1. Componentes

| Componente | Função | Custo aprox. (FP/passo) | De onde vem |
|---|---|---|---|
| **M: memória** | Nível e ciclo do próprio alvo (features da v0.51) + ε no NLMS | ~45 | v0.51 + correção E-numérica |
| **Estrutura vigente A** (≤ ⟨4⟩ átomos) | Atrasos, estado latente, acionamento; pesos por NLMS | ~6 por átomo | v0.51 |
| **Previsão vigente f** | Previsão final do sistema, sobre a qual as mudanças são julgadas | — | ver §5 (decisão aberta) |
| **Vagas de experimento** (m = ⟨4⟩) | Cada vaga roda um desafiante g = f + Δ e acumula evidência | ~10 por vaga | Nota 01 |
| **Triagem** | Escore barato de candidatos fora das vagas (2 sondas por passo) | ~6 | v0.51 |
| **Escalonador de varredura** | Decide qual candidato ocupa uma vaga que se libera | O(1) amortizado | Xu, Mei & Moustakides (2021) |
| **Controle de multiplicidade** | Níveis de aceitação assíncronos tipo e-LOND | O(1) | Xu & Ramdas (2024) |
| **Intervalo** | Quantil adaptativo com os 8 indicadores acumulados | ~2 | v0.51 + correção de cadência |

**Orçamento-alvo:** ≤ 150 FP/passo em média e pico ≤ 500 com d ≤ 6, igual à v0.51.

## 2. Tipos de mudança e desafiantes

| Tipo | Desafiante \(g_t = f_t + \Delta_t\) | Margem \(\varepsilon\) |
|---|---|---|
| Acrescentar c | \(\Delta = \theta_{c,t}\,\varphi_{c,t}\); θ aprendido por NLMS no resíduo de f | \(\varepsilon_{\text{add}} = ⟨\,\cdot\,⟩ > 0\) (preço da complexidade) |
| Remover a | \(\Delta = -\text{contribuição vigente de } a\) | \(\varepsilon_{\text{rem}} = ⟨\,\cdot\,⟩ \le 0\) (basta não piorar) |
| Trocar a → c | soma dos dois | \(\varepsilon_{\text{swap}} = ⟨\,\cdot\,⟩\) |

O desafiante é sempre comparado com a previsão **vigente**, mesmo quando ela muda durante o experimento (Nota 01, C2). Cada desafiante custa O(1): só soma ou subtrai um termo.

## 3. Evidência de cada experimento

- **Perda limitada:** \(\ell_t(u) = \min\{(y_t-u)^2/B_t^2, 1\}\), com \(B_t = ⟨k⟩\,\hat\sigma_{t-1}\) previsível.
- **Diferencial:** \(d_t = \ell_t(f_t) - \ell_t(g_t) - \varepsilon\).
- **E-process:** mistura sub-exponencial de Choe & Ramdas (Teorema 3) sobre \(d_t\), atualizada só nos passos em que os portões estão abertos (silêncio, quarentena, dormência), uma subsequência previsível (Choe & Ramdas, §F.1).
- **Encerramento:** quando cruza o nível de aceitação (§4), quando o log-e-process cai abaixo de um piso ⟨·⟩ (a "regra de varredura": o candidato não está ganhando, libera a vaga) ou por limite de duração ⟨·⟩.

## 4. Aceitação e controle de mudanças falsas

- Experimento k aceito quando \(E_k \ge 1/\alpha_k\), com \(\alpha_k = \alpha\,\gamma_k\,(|R^{\text{dec}}_{<k}| + 1)\), \(\sum_k\gamma_k \le 1\).
- \(R^{\text{dec}}_{<k}\) conta só as mudanças **já decididas** antes do encerramento de k (versão assíncrona conservadora). A forma exata vem de Zrnic, Ramdas & Jordan (2021), a confirmar.
- **Garantia pretendida:** a taxa de mudanças falsas fica ≤ α em todo t, para qualquer política de escalonamento previsível (G1 da Nota 01).
- **Sequência \(\gamma_k\):** precisa ser definida para um fluxo sem fim (por exemplo \(\gamma_k \propto 1/(k\log^2 k)\)). Consequência: o nível fica mais exigente com o tempo. Isso tem de ser avaliado quanto à latência em fluxos longos. **Risco conhecido.**

## 5. Decisão aberta: em que previsão as mudanças são julgadas?

- **Opção I, estrutura sobre a memória:** \(f = M + \sum_{a\in A}\theta_a\varphi_a\), sem combinador. É mais simples, e toda mudança é julgada na previsão final. Risco: a cascata M → S foi pior na v0.51 (0,304 contra 0,220 no interno), por realimentação.
- **Opção II, como na v0.51:** S e M separados, combinados por média dinâmica. As mudanças alteram S, mas são **julgadas na previsão combinada** f. Risco: quando w_S ≈ 0, nenhuma mudança em S melhora f, e a estrutura nunca cresce. Talvez isso seja até o comportamento correto.
- **Decisão:** comparar I e II no desenvolvimento (Silverbox, Cascaded Tanks, uma cascata do ONS, algumas bacias do CAMELS-BR) e fixar a escolha **antes** do pré-registro.

## 6. Escalonador (quem entra numa vaga livre)

1. Candidatos de **remoção** dos átomos ativos têm prioridade periódica (a cada ⟨·⟩ passos, cada átomo ativo recebe um experimento de remoção).
2. Depois, o candidato de **acréscimo ou troca** com maior escore de triagem que não foi testado recentemente.
3. **Troca de latente:** se há latente ativo, os outros polos entram como experimentos de troca. Isso deve resolver a trava do polo errado (B3).
4. A regra de piso no log-e-process implementa a varredura de Xu, Mei & Moustakides: persiste enquanto a evidência sobe, libera a vaga quando ela zera.

## 7. O que é medido na avaliação (a pré-registrar)

- **Segurança:** taxa empírica de mudanças falsas, em nulos e em processos com estrutura conhecida (semi-sintéticos), contra α.
- **Eficácia:** fração do tempo com estrutura correta, latência da primeira descoberta e latência de reversão depois de uma mudança de regime.
- **Previsão:** NMSE contra v0.51, só M e comparadores (alpha-investing, AMRules/FIMT-DD, RLS esparso).
- **Custo:** FP por passo (média e pico), memória, e depois ciclos e energia em microcontrolador.
- **Latência versus limites teóricos:** a latência medida contra a forma p/(m·g²) + log(1/α)/g².

## 8. Riscos principais

1. **Poder e latência:** testes de diferença de perda têm menos poder que o teste de correlação da v0.51. Somando o \(\gamma_k\) decrescente, a latência pode piorar.
2. **Opção II pode nunca crescer** em séries dominadas pela memória. Isso é aceitável se for o comportamento correto, mas precisa ser distinguido de falta de poder.
3. **Recorte da perda:** a escolha de \(B_t\) afeta o poder.
4. **Custo:** o e-process de mistura pede log/exp. Pode ser recalculado a cada k passos, mantendo a validade, se feito com cuidado (a confirmar).
