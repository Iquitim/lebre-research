# 08 — Roteiro proposto

**Regras que valem para todas as etapas** (as mesmas das versões anteriores):
- a v0.54 congelada (`f9906c4`, `lebre==0.3.0`) é a linha de base e não é editada;
- cada variante vive numa pasta de experimento, por subclasse;
- cada medição tem plano e critérios commitados **antes** de rodar, e nada é ajustado depois;
- desenvolvimento e confirmação usam sementes e dados diferentes;
- uma mudança só entra no núcleo por avaliação final pré-registrada em dados nunca vistos, com regra de promoção
  vinculante.

**Sementes reservadas para este programa** (conferidas como não usadas em 16/10/2026): 2026101500 a 2026102999. Elas
serão divididas por etapa no primeiro plano, e cada faixa será registrada em `docs/research/SEEDS.md` antes do uso.
**Dados reais nunca usados:** CAMELS-BR posições 170+, BDG2 posições 145+, 40 usinas eólicas elegíveis de 2024–2025.
Rios do ONS e usinas solares de 2024–2025 estão esgotados.

## Etapas

As etapas são independentes, salvo onde indicado.

### Etapa 0 — Formal, sem medição (F1)

- **0.1.** Escrever por extenso as provas do `02`, §2 e §3: centragem previsível sob a nula fraca, passos pulados,
  mistura, e-LOND assíncrono com nula dependente da trajetória, e os dois motores dando 2α.
- **0.2.** Conferência por um leitor independente.
- **0.3.** Frase do limite conjunto 2α na próxima revisão da especificação.
- **Critério de conclusão:** prova conferida; nenhuma lacuna aberta. **Promove ao núcleo:** nada (só texto).

### Etapa 1 — Diagnósticos baratos, instrumentando a v0.54 sem mudá-la

- **1.1 (F3).** Decompor o atraso de readição em triagem, vaga, aquecimento e evidência, nos cenários T5 da auditoria.
- **1.2 (F2).** Ablações D (sem M1), E (só memória) e F (só estrutura) no banco de desenvolvimento (cenários sintéticos
  do LEBRE Lab e as séries de desenvolvimento já usadas). Responde H2.1 e dá o primeiro efeito isolado da M1.
- **Critério de conclusão:** relatórios com IC. **Decisão que sai daqui:**
  - se a evidência dominar o atraso de readição, rebaixar H3.1 e priorizar a variante A′ da F3;
  - se D mostrar a M1 neutra em alguma família, abrir H2.4 na Etapa 2.

### Etapa 2 — Protótipo da cascata (F2, H2.5): a M3 da v0.55

- Rascunho da especificação da variante B; teste de identidade (com a cascata desligada, igual à v0.54); teste de não
  vazamento (embaralhar o futuro não pode mudar nenhuma previsão passada).
- Medição de desenvolvimento pré-registrada:
  - C03, passeios aleatórios independentes (n ≥ 50), cointegração, cenários P1 a P3 do EXT-02, alvo AR forte e sazonal
    (risco R1);
  - critérios do `03`, §4;
  - ablação C (sem M1) só se a Etapa 1 justificar.
- **Promove ao núcleo:** só depois de validação em dados novos e da avaliação final da v0.55.

### Etapa 3 — Memória de regimes (F3, H3.1–H3.3)

- **3.1.** A′ (duração mínima ligada ao histórico da unidade) primeiro, por ser a simplificação.
- **3.2.** B, C e D só se A′ não atingir o critério.
- Critérios do `04`, §5; inclui nulos, iscas e o efeito de riqueza acumulada (§4 do `04`).
- **Independente da Etapa 2**, mas as duas mexem no núcleo. Se ambas avançarem, a avaliação final da v0.55 mede a
  combinação, e cada uma também separadamente.

### Etapa 4 — Mapa em alta dimensão (F4)

- Harness de "tudo ligado" e baselines D e E na pasta do experimento.
- Fase exploratória e, depois, a confirmatória (`05`, §4).
- Inclui F1-c (calibração da nula estrutural em d alto).
- **Linha independente:** não promove nada ao núcleo por si. Se encontrar uma degradação do FDR com d (H4.2 rejeitada),
  essa descoberta passa a ser um defeito a tratar.

### Etapa 5 — Linhas teóricas independentes (adiadas)

- **H1.3:** referência lenta separada só para os testes.
- **H3.4:** regra de riqueza com estado (e-closure online, hipóteses persistentes com FDR), com prova própria.

Nenhuma delas entra no núcleo sem prova e medição.

## Ordem recomendada

Etapa 0 e Etapa 1 em paralelo, porque são baratas e não mexem no código. Depois, Etapa 2 (o defeito mais bem
diagnosticado) e Etapa 3. A Etapa 4 roda quando houver capacidade, porque não bloqueia a v0.55.

## Resposta à pergunta final

**Justificam a próxima evolução da LEBRE (v0.55):**
- **F2, como cascata ancorada na memória**, restrita à H2.5. É a correção do defeito M3, com mecanismo deduzido.
- **F3, como correção do limite da M4.** Começa pela simplificação A′; o warm start só entra se A′ não bastar.

As duas atacam defeitos já medidos e declarados.

**Ficam como linhas de pesquisa independentes:**
- **F4**, como mapa de desempenho;
- **H1.3** e **H3.4**, como teoria.

**Não têm evidência para alterar a arquitetura atual:**
- **F1 como correção da validade.** O e-process é válido sob NLMS adaptativo, por dedução. O que falha é a
  interpretação estrutural, já documentada e tratada pela F2.
- **A remoção da M1 (H2.4)**, até as ablações da Etapa 1.
