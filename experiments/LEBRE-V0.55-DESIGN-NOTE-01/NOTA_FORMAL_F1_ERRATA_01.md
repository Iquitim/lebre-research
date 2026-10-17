# Nota formal F1 — errata 01

**Data:** 17/10/2026 · **Objeto:** `NOTA_FORMAL_F1.md` (16/10/2026), §1, hipótese (H0), e o **[FATO]** que a acompanha.

## O que a nota afirma

> Rₜ, Gₜ, Bₜ e o indicador 1{t ∈ 𝒯} são ℱₜ₋₁-mensuráveis. No código, (H0) vale: (…) Bₜ (…) calculados em `predict`,
> antes de yₜ.

## O que o código faz

No núcleo congelado da v0.54 (`_core.py`, `observe`), a escala é

  Bₜ = 2·max(σ̂ᵣ, piso),  piso = 0,1·√(y_sv) para t ≥ 200.

A variância corrente do alvo, `y_sv`, é atualizada **com o próprio yₜ** imediatamente antes do cálculo do piso:

```
dy = y - self.y_sm; self.y_sm += ry * dy; self.y_sv += ry * (dy * (y - self.y_sm) - self.y_sv)
floor = SCALE_FLOOR * math.sqrt(max(self.y_sv, 0.0)) if self.t >= 200 else 0.0
B = CLIP_K * max(self.sigr, floor)
```

σ̂ᵣ é previsível: ele é atualizado depois, a cada 8 passos. Mas, sempre que o piso domina, **Bₜ depende de yₜ**. Então
(H0) **não vale estritamente** para o código congelado, e o [FATO] da nota está errado nesse ponto. Rₜ, Gₜ e o indicador
dos passos testados continuam previsíveis.

## Consequência

- **Os Teoremas 1 e 2 continuam corretos como enunciados:** eles supõem (H0). O que muda é que o código congelado não
  satisfaz (H0) exatamente.
- **Tamanho do desvio:** a taxa de atualização é max(10⁻⁴, 1/n). Depois de n passos, o efeito de yₜ sobre o piso é de
  ordem 1/n, e o piso só entra quando domina σ̂ᵣ. Não há medição do efeito sobre a validade; ele não é declarado como
  desprezível sem prova.
- **Onde o piso domina:** em séries integradas, ele chegou a 8 vezes σ̂ᵣ na D4 do LEBRE Lab. É justamente onde Bₜ mais
  depende do nível.
- A auditoria da porta da M2 (`full.py`) calcula o seu piso com a variância de **antes** de yₜ (comentário "past only")
  e não é afetada.

## Correção

No protótipo da v0.55 (rascunho 7, chave PRED_FLOOR em `experiments/LEBRE-V0.55-PROTO-01/lebre055/anchored.py`), o piso
é calculado antes de ver yₜ, e (H0) passa a valer por construção. A v0.54 congelada não é editada: a limitação fica
registrada nesta errata, e deve constar da próxima revisão da especificação.

**Como foi achado:** ao investigar por que a evidência de uma entrada verdadeira crescia devagar em séries integradas
(diagnóstico do rascunho 7).
