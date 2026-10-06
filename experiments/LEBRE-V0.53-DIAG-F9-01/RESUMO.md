# Diagnóstico F9 (níveis de preço) — resumo para a v0.53

**Data:** 06/10/2026 · exploratório, feito no LEBRE Lab (banco de desenvolvimento; `diagnosticos/F9_*` no projeto
`lebre-lab`), com a biblioteca congelada `lebre==0.1.0` e só dados de desenvolvimento.

- As 4 entradas espúrias aceitas nos níveis de preço mudaram o MSE em menos de 1% (razão normal ÷ sem entradas entre
  0,995 e 1,009).
- A LEBRE sem nenhuma entrada externa fica tão atrás do passeio aleatório quanto a normal (razões de 1,03 a 1,19).
- **Conclusão:** em precisão, F9 é o mesmo problema de F8 (adaptação da memória e do modelo base ao ruído). As
  aceitações espúrias afetam a interpretação, não a precisão.
- **Efeito na nota de desenho 01:** M2 cobre F8 e a parte de precisão de F9; M3 cai de prioridade e fica restrito à
  interpretação das entradas aceitas.
- **Falha do próprio diagnóstico:** a regra de decisão não previa margem de empate; as classes por aceitação não são
  informativas e não foram usadas na conclusão.
