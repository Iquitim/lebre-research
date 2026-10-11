# LEBRE v0.54 — M3 (interpretação em séries não estacionárias): diagnóstico e adiamento

**Data:** 11/10/2026 · **Status:** a M3 **não entra na v0.54**. Este documento registra o mecanismo encontrado, a
exploração feita e o caminho proposto para a v0.55. Nenhuma medição registrada usou a M3.

## O problema

Em séries de níveis (câmbio, petróleo, juros), a LEBRE aceita e mantém entradas externas espúrias: na linha de base E23,
4 de 4 séries de C03 terminam com uma entrada externa na estrutura. A M2 já corrige a precisão (a previsão final segue a
persistência), mas a estrutura reportada continua dizendo que uma entrada sem relação causal é relevante.

## O mecanismo

A previsão do núcleo combina duas partes:

- a **memória** m, que parte do último valor (persistência mais ajustes);
- a **estrutura** s, um modelo linear do nível do alvo sobre as entradas padronizadas e o passado do próprio alvo.

Os testes de adição comparam s com s mais a candidata. Num passeio aleatório, s é um preditor fraco do nível: o passado
do alvo entra padronizado por uma média que se move devagar, e sobra um componente que volta à média. Qualquer entrada
que também passeia ajuda s a acompanhar o nível, e o e-process registra essa melhora, que é real para s. A aceitação é
válida para a hipótese testada ("melhora a previsão estrutural"), mas não para a interpretação ("a entrada explica o
alvo além do seu próprio passado").

## Exploração (sementes 20261323 a 20261333, fora de qualquer medição registrada)

- **Passeios aleatórios independentes** (alvo e 5 entradas, 4.000 passos, referência de persistência): entradas externas
  aceitas em 5 de 11 séries. As previsões finais são iguais com e sem essas entradas, porque a M2 segue a persistência.
- **Com a M4 (remoção por queda da contribuição):** nenhuma entrada espúria removida. A contribuição delas não cai,
  então o teste de remoção não abre. A M4 sozinha não resolve a M3, como confirmou a medição M4_E1 (C03: 4 de 4 com
  entrada externa, com e sem M4).

## Caminho proposto para a v0.55

Ancorar a estrutura na memória: a estrutura passaria a modelar o que a memória não prevê (s' = m + estrutura), e os
testes de adição passariam a perguntar se a candidata melhora a previsão **além do próprio passado do alvo**. Num
passeio aleatório, o resíduo da memória é quase ruído branco, e uma entrada que só passeia não o prevê. É uma mudança no
núcleo, com efeito em todas as famílias, que exige o processo completo: rascunho, medição no banco e validação em dados
novos. A alternativa da nota de desenho ("diferenciar o alvo como hipótese do mecanismo") é um caso particular desse
caminho.

## Consequência para a v0.54

O critério da M3 na nota de desenho (C03: entrada externa na estrutura final em no máximo 1 de 4 séries) **não é
atingido** na v0.54, e isso será declarado na avaliação final.
