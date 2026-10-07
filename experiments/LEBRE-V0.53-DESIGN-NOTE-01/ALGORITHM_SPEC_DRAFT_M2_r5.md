# LEBRE v0.53 — M2, rascunho 5: AdaHedge com compartilhamento (Fixed Share) sobre a perda recortada

**Data:** 08/10/2026 · **Status:** proposta, antes de qualquer código desta revisão. **Base:** PRA-08 (com o adendo da
seção 4) e o rascunho 4, que falhou só em B01 (série Arinos) porque os pesos dependem de todo o histórico.

## 1. Mudança em relação ao rascunho 4

Perda (recortada, mesma escala), saída, auditoria e estrutura como no rascunho 4. Muda a atualização dos pesos, que passa
a ser a da equação (13) de Cesa-Bianchi et al. (2012), com d = 2:

- v_{t+1} ∝ p_t^{η_t/η_{t−1}} × exp(−η_t ℓ_t);  p_{t+1} = α_t/2 + (1 − α_t) v_{t+1};  p_1 = (½, ½).
- **Taxa de troca:** α_t = 2/(t + 1), que equivale ao α_t = 1/t do Corolário 6 de Adamskiy et al. (2016) na outra
  parametrização (com α_1 = 1, p_2 volta a ser uniforme, como lá).
- **Taxa de aprendizado:** a regra do AdaHedge aplicada ao próprio previsor compartilhado: η_t = ln 2 / Δ_{t−1}, com
  Δ_t = Σ δ_s, δ_s = max(0, h_s − m_s), h_s = p_s · ℓ_s e m_s = −(1/η_s) ln Σ_j p_{j,s} exp(−η_s ℓ_{j,s}) (com η = ∞,
  m_s = min_j ℓ_{j,s}); η_0 = η_1. Convenções: com η_{t−1} = η_t = ∞, a razão de expoentes é 1 e a atualização fica no
  previsor de menor perda da rodada; com η_{t−1} = ∞ e η_t finito, a razão é 0.
- **Efeito pretendido:** o compartilhamento limita a memória a cerca de ln(2/α_t)/η_t unidades de perda recortada, de
  modo que um déficit antigo (como o da fase de aprendizado em Arinos ou a partida de B02) não domina para sempre; o η do
  AdaHedge mantém essa memória maior quando os dados são fáceis.

Nenhuma constante nova.

## 2. Garantia e limites

- Teorema 4 de Cesa-Bianchi et al. (2012): η_t e α_t são não crescentes, então a cota vale para as taxas efetivamente
  usadas, contra qualquer sequência de comparação, inclusive "o melhor previsor em cada intervalo". **A combinação com a
  regra do AdaHedge é nossa**; não há cota nova provada, e a cota do Teorema 4 fica fraca quando η_t é grande.
- Como no rascunho 4, a garantia é sobre a perda recortada, não sobre a perda quadrática da média ponderada.
- **Custo:** recontado na implementação, 54 FP por passo (pesos, recorte e saída) mais ~18 da auditoria: ~72.
- **Observado no teste do protótipo, antes da medição:** numa série sintética em que a LEBRE é claramente melhor, o peso
  dela fica em ~0,94 no passo 400 (η efetivo ~0,3 e piso α_t/2 no outro previsor), contra ~1,00 no rascunho 4. Risco
  declarado para o critério 2.

## 3. Medição

Mesmo plano dos rascunhos 2 a 4 (23 famílias, critérios 1, 2 com C05, 4, 5, 6, 7), uma configuração, sem parâmetros
livres, plano próprio commitado antes de rodar.
