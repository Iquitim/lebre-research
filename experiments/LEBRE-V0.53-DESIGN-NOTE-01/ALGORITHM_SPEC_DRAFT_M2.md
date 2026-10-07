# LEBRE v0.53 — Rascunho da especificação, parte 1: M2 (porta da referência trivial)

**Data:** 07/10/2026 · **Status:** rascunho 0, sem código. Os parâmetros marcados ⟨a fixar⟩ são fixados no
desenvolvimento, só com o LEBRE Lab e os dados de desenvolvimento da v0.52, antes do pré-registro. A reserva da v0.53
(`LEBRE-V0.53-DATA-01`) não é usada aqui.
**Base:** nota de desenho 01 (seção M2), protótipos D04 e D05 do LEBRE Lab, análise de incerteza do Lab, PRA-06 e a
revisão de 07/10/2026. As referências ao código da v0.52 são à biblioteca congelada `lebre==0.1.0`
(`_core.py`, `_engine.py`), que reproduz a v0.52-r1.

## 0. O que M2 resolve e o que não resolve

- **Resolve (hipótese):** a perda da LEBRE contra a previsão trivial em séries sem nada a aprender (F8) e a parte de
  precisão de F9. No Lab: 5% a 7% acima de prever zero ou do passeio aleatório, com intervalo de 95% acima de 1.
- **Não resolve:** F6 (precisão do modelo base, é a M1), a interpretação das entradas aceitas em séries não
  estacionárias (M3), remoções (M4) e custo (M5).
- **O que a evidência do Lab já mostra:** uma porta heurística (média exponencial) recuperou a maior parte da perda e não
  piorou mais de 0,7% onde a LEBRE vence (19 famílias). Esta especificação troca a heurística pelo mecanismo de
  evidência que a v0.52 já usa nas mudanças estruturais.

## 1. Mecanismo de evidência da v0.52 que M2 reaproveita (como está no código)

| Elemento | v0.52 | Onde |
|---|---|---|
| Perda recortada | ℓ(e) = min(e² / B², 1), com B = 2 · max(σ, piso); σ = raiz da média exponencial (λ = 0,99) do erro quadrático do modelo vigente, atualizada a cada 8 passos, só com o passado; piso = 0,1 · desvio do alvo depois de 200 passos | `_core.py`, `observe` |
| Incremento | d_t = ℓ(vigente) − ℓ(desafiante) − ε; limitado em [−1 − ε, 1] | idem |
| Hipótese nula (fraca) | nos passos testados, o desafiante não melhora a perda recortada do vigente em mais de ε, em média | `_engine.py`, `Hypothesis` |
| E-process | mistura unilateral sub-exponencial sobre 8 valores de λ, com c = 1 + max(ε, 0) e centragem previsível γ_i = min(média passada, 0) | idem |
| Nível de aceitação | tipo e-LOND, fixado na criação da hipótese: α · g(n) · (descobertas + 1), limitado a 0,5; α = 0,05 | `ChangeEngine.hypothesis` |
| Cadência | revisão a cada 10 passos; episódio encerrado se, depois de 100 amostras, a soma não for positiva, ou após 5.000 | `ChangeEngine.review` |

A perda é limitada, o que atende à condição dos teoremas principais de Choe e Ramdas (2024) para comparar previsores
(PRA-06).

## 2. Definição de M2

### 2.1 Referência trivial R

Declarada pelo usuário ou deduzida, sempre calculada só com o passado:

| Opção | Previsão de R no passo t | Quando usar |
|---|---|---|
| `zero` | 0 | O alvo é uma variação (retornos, mudanças de taxa) |
| `persistencia` | último alvo observado | Padrão quando não há ciclo declarado |
| `sazonal` | alvo de um ciclo atrás (o primeiro ciclo declarado); se faltar, o último observado | Padrão quando há ciclo declarado |

`zero` nunca é deduzida: exige declaração, porque aplicada a um nível seria uma referência absurda.

### 2.2 Estado e saída

- **Modo** ∈ {REF, LEBRE}; começa em **REF**.
- A LEBRE (memória, estrutura, experimentos) roda sempre, como na v0.52, inclusive no modo REF; só a **saída** muda.
- Saída no passo t: R_t no modo REF; a previsão da v0.52 (depois do contrato de saída) no modo LEBRE.

### 2.3 Hipóteses da porta

Duas hipóteses persistentes, com chaves próprias no mesmo motor de evidência da v0.52:

| Hipótese | Ativa no modo | Vigente | Desafiante | Ao ser aceita |
|---|---|---|---|---|
| **promover** | REF | R | LEBRE | modo ← LEBRE |
| **rebaixar** | LEBRE | LEBRE | R | modo ← REF |

- **Incremento:** d_t = ℓ(y_t − vigente_t) − ℓ(y_t − desafiante_t) − ε_porta, com a perda recortada da seção 1 e B
  calculado a partir do erro **do vigente** (o modelo em uso), como na v0.52.
- **Margem:** ε_porta ⟨a fixar⟩, a mesma para promover e rebaixar. Valor inicial a testar: 0,002 (o das adições da
  v0.52). A margem nas duas direções evita alternância rápida.
- **Níveis:** as hipóteses da porta entram na **mesma** sequência e-LOND das mudanças estruturais. Cada troca de modo
  conta como uma descoberta, e o controle de mudanças falsas cobre as duas coisas juntas.
- **Vaga:** a porta tem vaga própria e não ocupa as 2 vagas de experimentos; não tem parâmetros a aprender.
- **Episódios:** mesma regra da v0.52 (revisão a cada 10 passos; episódio encerrado sem avanço depois de 100 amostras,
  ou após 5.000), com uma diferença: ao encerrar um episódio sem aceitação, a hipótese da porta é **aposentada** e
  recriada (com novo nível), para que um longo período desfavorável não impeça uma troca futura ⟨a confirmar no
  desenvolvimento; alternativa: manter a hipótese persistente, como as estruturais⟩. Ver seção 6.
- **Ao aceitar:** a hipótese é consumida (como na v0.52) e a hipótese da direção oposta é criada.

### 2.4 Dados faltantes, quarentena e intervalo

- **Alvo faltante ou quarentena:** a porta não observa nada nesse passo (como os experimentos da v0.52).
- **Intervalo de previsão:** o controlador de cobertura da v0.52 passa a usar o erro da **saída** (R ou LEBRE). Ao trocar
  de modo, o intervalo continua do valor corrente; a adaptação da v0.52 o ajusta.
- **Eventos:** cada troca de modo vira um evento auditável (passo, direção, log-evidência, amostras), no mesmo formato
  dos eventos estruturais.

## 3. Pseudocódigo (por passo)

```
predict(x_t):
    L_t ← previsão da v0.52 (inalterada)
    R_t ← referência trivial (zero | último observado | um ciclo atrás)
    saída ← R_t se modo = REF senão L_t
    guardar (L_t, R_t)

observe(y_t):
    v0.52.observe(y_t)                                   # aprendizado e evidência estrutural inalterados
    se y_t observado e fora de quarentena:
        vig, des ← (R_t, L_t) se modo = REF senão (L_t, R_t)
        B ← 2 · max(σ_vigente, piso)                     # σ_vigente: só passado
        d ← min((y_t − vig)²/B², 1) − min((y_t − des)²/B², 1) − ε_porta
        hipótese_ativa.observe(d)
        atualizar σ_vigente e o controlador de cobertura com o erro da saída
    a cada 10 passos:
        se log_e(hipótese_ativa) ≥ log(1/nível): trocar modo; consumir; registrar evento; criar hipótese oposta
        senão se episódio sem avanço (>= 100 amostras e soma <= 0) ou >= 5000: aposentar e recriar (seção 2.3)
```

## 4. Validade e limites

- **Por hipótese:** sob a nula fraca, cada e-process da porta é um supermartingale não negativo, porque d é limitado e
  previsível (R_t e L_t são calculados antes de y_t); a aceitação ao nível e-LOND controla a taxa de trocas falsas junto
  com as mudanças estruturais, nas mesmas condições da v0.52.
- **O que "troca falsa" significa:** trocar para a LEBRE quando, nos passos testados, ela não melhorava a perda recortada
  de R em mais de ε em média (ou o inverso). É a mesma semântica das mudanças estruturais.
- **Limite 1:** a garantia é sobre a perda **recortada**; ganhos em erros grandes (acima de B) não contam como evidência.
- **Limite 2:** as hipóteses recriadas consomem orçamento e-LOND; em séries muito longas com muitas recriações, os níveis
  ficam mais exigentes e as trocas mais lentas.
- **Limite 3:** no início da série a saída é R. Onde a LEBRE é muito melhor (carga, solar), há uma perda inicial até a
  primeira promoção. O D04 sugere que ela é pequena, mas a porta por evidência é mais lenta que a heurística.

## 5. Custo (estimativa, a medir)

| Parte | FP por passo |
|---|---|
| Referência R | 1 a 2 |
| Perdas e incremento da porta | ~12 |
| Revisão da porta (8 termos da mistura, a cada 10 passos) | ~2,4 |
| **Total** | **~16** (acréscimo de ~4% sobre a média de 415 da v0.52) |

Sem custo de memória relevante (duas hipóteses, σ e a última previsão de R; para `sazonal`, a memória da v0.52 já guarda o
valor de um ciclo atrás ⟨a confirmar⟩).

## 6. Escolhas a fixar no desenvolvimento (no Lab; nunca na reserva)

| Escolha | Opções | Como decidir |
|---|---|---|
| ε_porta | 0; 0,002; 0,005 | Ablação no Lab; escolher a menor margem sem alternância excessiva (seção 7) |
| Hipóteses da porta | recriadas ao fim do episódio sem avanço; ou persistentes | Ablação no Lab: tempo até trocar depois de uma mudança de regime (A05) e perda inicial (B01, B02) |
| Escala B | erro do vigente; ou o maior entre os dois erros | Fixar no erro do vigente, como a v0.52; só mudar se a ablação mostrar falha |

Regra para não ajustar demais no banco de desenvolvimento: no máximo essas três escolhas, cada uma com as opções acima,
decididas por critérios escritos antes de rodar; todas as combinações testadas entram no registro do Lab.

## 7. Critérios no banco de desenvolvimento (escritos antes de implementar)

Medidos no LEBRE Lab com a regra de incerteza (`analises/INCERTEZA_PLANO.md`):

1. **C01, C03, C04:** limite superior do intervalo de 95% da razão M2 ÷ referência <= 1,01.
2. **Famílias em que a v0.52 vence a referência** (as 19 do D04/D05): limite superior da razão M2 ÷ v0.52 <= 1,02.
3. **Alternância:** no máximo 1 troca de modo por 2.000 passos em média, em cada família.
4. **Mudanças falsas:** nos cenários nulos (A02, C01, C04), nenhum aumento de entradas externas aceitas em relação à v0.52
   (a porta compartilha o orçamento e-LOND e não pode piorar o controle).
5. **Custo:** acréscimo médio <= 25 FP por passo.

Se 1 falhar com 2 atendido, a porta por evidência é mais conservadora que a heurística do D04; registrar e considerar
ε_porta menor antes de qualquer outra mudança.

## 8. Questões em aberto

- Na série inteira, quantas trocas são esperadas sob a nula? Medir no Lab (cenários nulos) antes de afirmar algo.
- A porta deveria ver também a referência `sazonal` quando o ciclo declarado está errado? Fica para M6.
- Interação com M1 (especialista de precisão): M1 muda a previsão L, e a porta compara L com R; a ordem de
  implementação proposta é M2 primeiro, M1 depois, medindo de novo os critérios de M2.
