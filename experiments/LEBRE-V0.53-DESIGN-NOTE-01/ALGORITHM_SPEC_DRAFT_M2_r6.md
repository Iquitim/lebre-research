# LEBRE v0.53 — M2, rascunho 6: troca que decresce rápido (última tentativa no banco de desenvolvimento)

**Data:** 08/10/2026 · **Status:** proposta, antes de qualquer código desta revisão. **Base:** rascunhos 4 (sem
compartilhamento: concentra, mas não sai de um déficit antigo; falha só em B01/Arinos) e 5 (compartilhamento α_t = 1/t:
sai do déficit, mas não concentra; falha em C05, C03 e C04).

**Declaração de método:** é a sexta configuração medida no banco de desenvolvimento e a **segunda escolha de taxa de
troca feita depois de ver resultados**. Por isso: (1) é a última tentativa da M2 neste banco; se falhar, a M2 não é
resolvida na v0.53 e, pela condição do responsável pelo projeto, a v0.53 não é promovida com ela; (2) além do banco de
desenvolvimento, o candidato tem de passar numa **base de validação nova** (`VALIDACAO_PLANO.md` no LEBRE Lab), montada e
congelada antes da medição; (3) só então vai à reserva final, uma vez; (4) o relatório final declara as seis tentativas.

## 1. Mudança em relação ao rascunho 5

Só a taxa de troca: **α_t = 2/(t + 1)²** na parametrização de Cesa-Bianchi et al. (2012), equivalente a α_s = 1/s²
(s >= 2) de Adamskiy et al. (2016), seção 4.1.3, com ε = 1. Perda recortada, regra do AdaHedge para η_t, saída, auditoria
e estrutura como no rascunho 5.

**Por que esta taxa (da literatura, não de ajuste):** Adamskiy et al. mostram que, com α_s = s^{−1−ε}, o arrependimento
adaptativo no intervalo [t₁, t₂] fica em ln(N − 1) + (1 + ε) ln t₁ + c_ε, sem depender de t₂, e no intervalo inteiro
[1, T] o acréscimo sobre o arrependimento clássico é menor que 1 (para ε = 1: ln N + ln 2). Ou seja, preserva quase toda
a concentração do caso sem troca (rascunho 4) e ainda permite trocas tardias, a um custo que cresce com o instante t₁ em
que o melhor previsor muda. É o ponto intermediário entre os rascunhos 4 e 5 que a própria literatura propõe.

## 2. Garantias e limites

As do rascunho 5 (Teorema 4 de Cesa-Bianchi et al., 2012, para as taxas efetivamente usadas; combinação com o η do
AdaHedge é nossa; garantia sobre a perda recortada). O ciclo de realimentação entre o "mixability gap" e η continua
possível, mais fraco porque o compartilhamento é menor. Custo igual ao do rascunho 5 (54 FP por passo mais a auditoria).

## 3. Medição

Banco de desenvolvimento (23 famílias, critérios 1, 2 com C05, 4, 5, 6, 7) **e** base de validação, com plano próprio
commitado antes de rodar. Escolha só se passar nos dois.
