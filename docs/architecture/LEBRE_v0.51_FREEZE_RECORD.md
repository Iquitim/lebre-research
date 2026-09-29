# LEBRE v0.51 — Registro formal de congelamento

**Arquitetura:** LEBRE (Lifecycle-governed Evidence-Based Resource Evolution)
**Versão:** 0.51
**Status:** `FROZEN_RESEARCH_BASELINE_WITH_SCOPE_LIMITS`
**Etapa:** `LEBRE-V0.51-FREEZE-01`
**Data:** 25 de setembro de 2026
**Relação com a v0.1:** a v0.1 continua sendo a **referência canônica** do projeto (`FROZEN_WITH_SCOPE_LIMITS`). Este congelamento cria uma **linha de base de pesquisa** e não altera nem substitui a v0.1.

---

## 1. O que está congelado

| Item | Conteúdo |
|---|---|
| Código do modelo | `lebre_v051.py` (combinador, memória M, intervalo) e `lebre_s051.py` (especialista estrutural S). Só dependem de numpy. Os hashes são idênticos aos do congelamento pré-registro (`FREEZE_V051_SHA256.txt`, `FREEZE_S051_SHA256.txt`). |
| Harness de avaliação | `eval_v051.py`, `analyze_v051.py`, `chronos_v051.py`, `posthoc_feedback.py` e o padronizador causal `experiments/bench01/streams.py` (`CausalStandardScaler`, fator 10⁻⁴). |
| Dados | Carregador e arquivos de `data/external_v051/`. Os hashes conferem com os do pré-registro. |
| Pré-registro e decisão | `PREREG_V051.md` (hash conferido), `V051_DECISION.json`. |
| Resultados | Suíte interna, held-out principal (Q1–Q10), segundo conjunto (N1–N10, já visto), BENCH-04, análises pós-hoc. |
| Diagnóstico estrutural sintético | Execuções do código congelado em processos com estrutura conhecida, usadas no §11.2 da especificação. |
| Especificação | PDFs PT-BR/EN, HTMLs e fontes do build (`build_v051_spec.py`, `v051_text.py`, `v051_diagrams.py`), além de `ARQUITETURA_V051.md`. |

A lista completa, com SHA-256, está em `LEBRE_v0.51_SHA256SUMS.txt` (52 arquivos, todos verificados no momento do congelamento).

## 2. Constantes congeladas

| Grupo | Constantes |
|---|---|
| Memória M | μ = 0,05; perfil sazonal a = 0,1 (Θ = 0,9); média exponencial 0,01; 5 features (2 sem período); **sem ε** (pula só se ‖φ‖² = 0) |
| Estrutural S | μ = 0,1; ε = 10⁻⁶; L = 32; polos {0; 0,5; 0,8; 0,95}; **no máximo 1 latente ativo**; M_max = 4; α = 0,05 (p_dict = dL + 4 + d); ρ = 1 (τ = ρ/(σ̂²·m_φ)); T_max = 200 amostras; amostra a cada 2 passos; decisões a cada 10 passos; triagem 2/passo com peso 0,2; 4 vagas de teste de atraso; substituição se R ≥ h/2; ARL = 6000; T_idle = 500; recorte ±8; excitação 10%; dormência se w_S < 0,01 |
| Combinador | η = 1/2; λ = 0,99; exp/raiz/inversa a cada 8 passos |
| Intervalo | α = 0,1; γ = 0,1; atualização a cada 8 passos com o indicador do passo corrente × 8 |
| Ambiente | padronização causal das entradas com fator 10⁻⁴ (fora da contagem de FP); período s declarado |

## 3. Evidência que acompanha o congelamento

**Pré-registrada (vinculante):**
- Promovida: todos os critérios vinculantes foram atendidos.
- Held-out principal: 0,84× o NLinear online calibrado e 1,37× o Chronos-2.
- 121 FP/passo em média (pico 196) no held-out; 147 de média máxima (pico 249) na suíte interna com d = 5.
- Cobertura interna de 0,902; fidelidade da explicação ~10⁻¹⁴; variação máxima de 1,076× conforme o ponto de partida; 0 divergências.

**Pós-hoc (diagnóstica, não vinculante):**
- O desempenho em dados reais vem principalmente da memória M: 15/20 séries sem nenhuma promoção estrutural, e 16/20 com w_S médio < 0,01.
- Um modelo airline ajustado por MLE série a série é ~5% mais preciso.
- Descoberta estrutural sintética: confiável para um atraso; parcial para vários atrasos (sensível a τ); falha com latente acionado por entrada. A falha vem do limite de um latente e da escolha do primeiro polo, não da saturação do orçamento.
- Controle de promoções falsas: 0 em 17 686 episódios nulos.

## 4. Limitações conhecidas congeladas junto (não são defeitos a corrigir nesta versão)

1. **Latente único:** o primeiro polo a cruzar o limiar ocupa a vaga. Um latente acionado por entrada com outro polo fica inalcançável.
2. **Vazão da busca:** a primeira promoção leva tipicamente 1,5–3 mil passos, embora o teste em si leve ~200–300.
3. **Vários atrasos:** recuperação parcial, sensível ao prior τ. Com caudas pesadas, há remoções frequentes de átomos verdadeiros.
4. **Intervalo:** a atualização a cada 8 passos com um único indicador gera dependência de fase quando 8 divide s. A cobertura por série fica em 0,85–0,97.
5. **Contrato numérico de M:** sem ε, diverge em "trecho constante seguido de salto". O caso não foi observado nas séries reais avaliadas.
6. **Memória de estado:** ≈ 196d + 12s + 190 bytes (float32). O "~1,3 KB" é uma mediana, não um limite.
7. **Custo:** a padronização (~12 FP por entrada) fica fora da contagem. O orçamento de 150 FP vale até ~6 entradas.
8. **Evidência real da parte estrutural:** inexistente em séries reais guiadas por entradas.

## 5. Proveniência e ressalvas

- **Código e dados:** todos os hashes registrados no pré-registro conferem (9/9 arquivos de código e dados).
- **`ARQUITETURA_V051.md` diverge do hash registrado no pré-registro** (`dacc17bc…`). A diferença vem de correções exclusivamente documentais feitas entre 23 e 25/09/2026: parâmetros operacionais, contrato numérico, cadência do intervalo, memória, alcance estrutural e limites. Essas correções alinham o texto ao código congelado. A versão byte a byte do pré-registro **não pôde ser reconstruída**, e por isso não foi preservada. O documento não fazia parte dos critérios de decisão.
- **Especificação PDF:** as mesmas correções documentais foram aplicadas. O build exige Python ≥ 3.12.
- **Pré-registro:** é um registro interno do projeto; não foi publicado externamente.

## 6. Governança

- `NOVELTY_CLAIM_READY = NO`. Este congelamento estabelece uma linha de base reproduzível e não afirma novidade.
- `M3_STATUS = UNOPENED`. A v0.51 permanece com no máximo um estado latente.
- A v0.1 canônica e o código em `src/` e `tests/` **não foram modificados**.
- **Regra de mudança:** qualquer alteração em arquivo listado em `LEBRE_v0.51_SHA256SUMS.txt` invalida este congelamento. Melhorias vão para a v0.52, comparadas contra esta linha de base, com pré-registro e **uma mudança isolada por experimento**.

## 7. Verificação

```
sha256sum -c docs/architecture/LEBRE_v0.51_SHA256SUMS.txt
```
Deve ser executado a partir da raiz do repositório. Todas as 52 linhas devem retornar `OK`.

## 8. Errata

- **`LEBRE_v0.51_ERRATA_01.md`** (25/09/2026, SHA-256 `e8308677e033861c5e8e3cbb8ae2f21452bfc26637f576d9b1e969538a671930`): correções só de texto, sem alterar código, parâmetros ou resultados.
  - E1: alcance da garantia de promoção (vale sob H₀ = "S já correto sem o candidato").
  - E2: triagem e validade.
  - E3: memória M é *inspirada* no airline/Holt-Winters, não equivalente.
  - E4: a reversão à média não é suavização exponencial simples.
  - E5: controle de erro só por episódio.
  - E6: posicionamento frente ao prior art.

  Os arquivos congelados não foram editados; a errata prevalece sobre os trechos indicados.

## 9. Revisão documental 1

- **PDFs:** `pdf/LEBRE_ARCHITECTURE_v0.51_SPEC_r1_{PTBR,EN}.pdf`, com a Errata 01 incorporada no texto e um "Histórico de revisões" no §14.
- **Markdown:** `ARQUITETURA_V051_r1.md`. Além da errata, corrige a frase "alarmes do CUSUM com taxa de erro controlada", que contradizia a especificação.
- **Fontes do build:** `v051r1_text.py` e `build_v051r1_spec.py` (cópias; as fontes congeladas não foram alteradas).
- **Hashes:** `LEBRE_v0.51_r1_SHA256SUMS.txt` (11 arquivos).
- **Congelamento original:** os 52 arquivos continuam íntegros. A arquitetura, o código, os parâmetros e os resultados não mudam.
- **Leitura recomendada:** use a revisão 1. A revisão original fica preservada como registro do que foi avaliado.
