# PRA-11 — Trabalhos anteriores para as mudanças da v0.54: relatório

**Data:** 10/10/2026 · **Protocolo:** `PRA_11_PROTOCOLO.md` (fixado antes das buscas, commit `eb2ba79`) · **Registro:**
`PRA_11_LOG.md` (17 consultas e 5 conferências de resumo original).

## Conclusão em uma frase

Nenhum trabalho encontrado antecipa qualquer das seis afirmações; cada uma tem ferramentas de base conhecidas e três têm
trabalhos parciais próximos. A v0.54 não pode reivindicar nenhum componente como novo; a contribuição possível continua
sendo de **integração**, e as afirmações de diferença abaixo valem só para o que foi buscado.

## Por afirmação

| Afirmação | Mais próximo | Nível | O que falta nele, para a v0.54 |
|---|---|---|---|
| **B1 (M5a)** atualizar menos o componente de peso baixo numa combinação, preservando a reativação | M-LCB (Latypov et al. 2025): orçamento de M aprendizes por rodada entre K especialistas | Parcial | É gestão de bandidos/RL por limites de confiança, não uma combinação de previsores por pesos; não usa o peso para decidir quem aprende |
| **B2 (M5b)** custo proporcional ao uso: candidatos inativos triados com menos frequência; aprendizado pausado por regra só do passado | Filtragem seletiva de dados (Gollamudi et al. 1998; Diniz 2008), aprendizado disparado por evento (Solowjow e Trimpe 2020); ADOWIP (Wang 2026) | Base; ADOWIP parcial | ADOWIP decide **quando atualizar parâmetros** sob orçamento, mas sem evidência sempre válida e sem estrutura; nenhuma reduz a triagem de candidatos inativos |
| **B3 (M4)** remoção online de estrutura com garantia sempre válida | AdaFSML-RLS (Souza e Araújo 2012) e seleção online com esquecimento (Anagnostopoulos et al., não conferido); testes fechados online com e-valores (Fischer e Ramdas) | Parcial / base | Os métodos online de seleção não dão garantia sempre válida de remoção; os de e-valores não tratam remoção de variáveis num previsor |
| **B4 (M3)** relações espúrias em séries integradas, no fluxo | Monitoramento sequencial de cointegração (Trapani e Whitehouse 2020); regressão espúria clássica; decisão de diferenciação em lote | Base | Nada trata aceitação espúria num previsor online nem diferenciar o alvo como hipótese testada no fluxo |
| **B5 (M6)** período sazonal como hipótese com evidência sempre válida | Teoria para sequencializar testes (Koning e van Meer; Holmes e Walker); identificação de período em lote | Base | Nenhuma escolha online do período com evidência sempre válida |
| **B6 (integração)** as mudanças governadas por evidência sempre válida sob custo declarado | ADOWIP (orçamento e adaptação seletiva); seleção de modelos por e-valores (Backhaus et al. 2024) | Parcial / base | Nenhum trabalho combina as duas coisas |

## Implicações para a especificação

1. **M5a:** citar a combinação convexa de filtros (Arenas-García et al. 2006) e M-LCB como os vizinhos mais próximos; a
   regra de frequência reduzida precisa de argumento próprio sobre a reativação (nenhuma fonte o oferece).
2. **M5b:** a pausa por regra previsível continua apoiada na observação elementar da PRA-06 (apostar zero preserva o
   e-process); ADOWIP é a referência mais próxima para "adaptar só quando compensa" e deve ser citado.
3. **M4:** a forma de remoção (limiar de contribuição, troca pela referência trivial ou teste de persistência) deve dizer
   que garantia oferece; os testes fechados online com e-valores são a base mais próxima para controle de erro.
4. **M3:** citar a literatura de regressão espúria e o monitoramento de cointegração como base; a parte nova seria só a
   integração no regime de evidência da LEBRE.
5. **M6:** citar a sequencialização de testes como base; tratar memórias sazonais candidatas como hipóteses do mecanismo
   existente.

## Limitações

Um mecanismo de busca geral, consultas em inglês, leitura pelo resumo (o texto completo de AdaFSML-RLS e o de
Anagnostopoulos et al. não foram lidos), literatura de 2026 possivelmente não indexada, sem dupla triagem. Não é uma
revisão sistemática no sentido formal. Antes de qualquer afirmação de diferença num artigo, ampliar a busca e ler os
trabalhos parciais no texto completo.
