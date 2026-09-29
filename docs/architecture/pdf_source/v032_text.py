"""Bilingual content of the LEBRE v0.3.2 research specification."""

# ============================================================================ diagram labels
DIAG = {
    "pt": dict(
        d1_title="D1: Arquitetura LEBRE v0.3.2 — plano de dados e plano de controle",
        d1_sub="Predição causal linear-dinâmica esparsa, governada por testes estatísticos em tempo de fluxo",
        d1_in="Observação x_t", d1_in2="entradas padronizadas", d1_in3="+ termo de viés",
        d1_base="Caminho-base", d1_base2="θ_bᵀ[x_t; 1] (sempre ativo)",
        d1_lag="Caminho de atrasos", d1_lag2="Σ θ_ik · x_(t−k,i), k ≤ L",
        d1_lat="Caminho latente", d1_lat2="forma de inovações (Kalman)", d1_lat3="estado s + acionamento q",
        d1_pred="predição", d1_err="erro prequencial",
        d1_ctrl="PLANO DE CONTROLE (decisões a cada 10 passos; evidência a cada passo em tempo de fluxo)",
        d1_scr="Triagem", d1_scr2="DORMANT → ranking", d1_scr3="2 sondagens/passo",
        d1_test="Testes provisórios", d1_test2="martingale de mistura", d1_test3="auto-normalizado",
        d1_sup="Supervisor", d1_sup2="promoção ≥ log(p/α)", d1_sup3="orçamento M_max",
        d1_ev="Monitor de remoção", d1_ev2="CUSUM da LLR", d1_ev3="+ aluguel MDL",
        d1_gov="Governador", d1_gov2="portão de excitação", d1_gov3="cadências",
        d1_fb="e_t", d1_set="conjunto ativo",
        d1_note="Candidatos nunca entram na predição antes de promovidos (probação em sombra).",
        d2_title="D2: Ciclo de vida estrutural e suas regras de transição",
        d2_sub="Cada transição é uma decisão estatística com taxa de erro controlada",
        d2_dor="no dicionário", d2_prov="em teste formal", d2_act="na predição", d2_evi="removido",
        d2_t1="triagem (ranking)", d2_fut="futilidade após T_max testes (não afeta o erro tipo I)",
        d2_back="volta ao dicionário (pode ser retestado com estatística nova)",
        d2_rules=["Promoção: o martingale de mistura cruza log(p/α); o coeficiente inicial é a média posterior.",
                  "Remoção: o CUSUM da razão de log-verossimilhança 'sem vs. com' cruza h = log(ARL).",
                  "Substituição (orçamento cheio): só vale se a vítima já tiver R ≥ h/2.",
                  "Acoplamento: remover o estado latente remove o seu átomo de acionamento.",
                  "Silêncio (entradas < 10% da potência de longo prazo): nenhuma evidência é acumulada."],
        d3_title="D3: Episódio de teste provisório (promoção)",
        d3_sub="Martingale de mistura auto-normalizado: válido a qualquer momento (desigualdade de Ville)",
        d3_true="átomo verdadeiro", d3_null="átomo nulo", d3_promo="promoção",
        d3_x="amostras de teste no episódio (a mistura τ é fixada na abertura do episódio)",
        d3_note="Sob H0 com ruído condicionalmente simétrico: P(∃t: M_t ≥ p/α) ≤ α/p por candidato e por episódio.",
        d4_title="D4: Remoção por CUSUM com aluguel de parcimônia",
        d4_sub="Um átomo útil acumula evidência a favor; o silêncio não gera evidência; a mudança de regime dispara a remoção",
        d4_sil="silêncio", d4_sil2="(evidência congelada)", d4_chg="mudança de regime", d4_evict="remoção",
        d4_useful="átomo útil: R ≈ 0",
        d4_note="Sem aluguel: ARL até remoção falsa ≥ e^h (Lorden). O aluguel r = h/T_idle remove átomos ociosos em ~T_idle passos.",
        d5_title="D5: Caminho latente em forma de inovações",
        d5_sub="Preditor de Kalman estacionário de um estado oculto de 1ª ordem, linear nos parâmetros",
        d5_e="erro prequencial", d5_x="entrada que aciona o estado",
        d5_u="Inovação normalizada", d5_s="Estado de inovação s", d5_q="Acionamento q", d5_q2="entrada i testada após o latente",
        d5_out="Contribuição", d5_out2="aprendida por NLMS",
        d5_eq="z_t = a·z_(t−1) + b·x_(t,i) + ν_t  ⇒  ŷ_t ⊃ θ_s·s_t + θ_q·q_t  com polo p ≈ a(1−K)",
        d5_notes=["Substitui a unidade recorrente com RTRL da v0.2 (~20 FP) por ~9 FP de filtros de 1ª ordem.",
                  "O banco de polos {0; 0,5; 0,8; 0,95} cobre τ ≈ 1, 2, 5 e 20 passos; um polo é escolhido por teste.",
                  "Verificado: MSE a 1,17× (mediana) do preditor de Kalman exato na tarefa I6."]),
    "en": dict(
        d1_title="D1: LEBRE v0.3.2 architecture — data plane and control plane",
        d1_sub="Sparse linear-dynamical causal prediction governed by stream-time statistical tests",
        d1_in="Observation x_t", d1_in2="standardised inputs", d1_in3="+ bias term",
        d1_base="Base pathway", d1_base2="θ_bᵀ[x_t; 1] (always on)",
        d1_lag="Delay pathway", d1_lag2="Σ θ_ik · x_(t−k,i), k ≤ L",
        d1_lat="Latent pathway", d1_lat2="innovations form (Kalman)", d1_lat3="state s + drive q",
        d1_pred="prediction", d1_err="prequential error",
        d1_ctrl="CONTROL PLANE (decisions every 10 steps; evidence accrues in stream time)",
        d1_scr="Screening", d1_scr2="DORMANT → ranking", d1_scr3="2 probes/step",
        d1_test="Provisional tests", d1_test2="mixture martingale", d1_test3="self-normalised",
        d1_sup="Supervisor", d1_sup2="promote ≥ log(p/α)", d1_sup3="budget M_max",
        d1_ev="Eviction monitor", d1_ev2="LLR CUSUM", d1_ev3="+ MDL rent",
        d1_gov="Governor", d1_gov2="excitation gate", d1_gov3="cadences",
        d1_fb="e_t", d1_set="active set",
        d1_note="Candidates never enter the prediction before promotion (shadow probation).",
        d2_title="D2: Structural lifecycle and its transition rules",
        d2_sub="Every transition is a statistical decision with a controlled error rate",
        d2_dor="in the dictionary", d2_prov="under formal test", d2_act="in the prediction", d2_evi="removed",
        d2_t1="screening (rank)", d2_fut="futility after T_max tests (does not affect type-I error)",
        d2_back="returns to the dictionary (may be re-tested with fresh statistics)",
        d2_rules=["Promotion: the mixture martingale crosses log(p/α); the initial coefficient is the posterior mean.",
                  "Eviction: the CUSUM of the 'without vs. with' log-likelihood ratio crosses h = log(ARL).",
                  "Replacement (full budget): only if the victim already has R ≥ h/2.",
                  "Coupling: evicting the latent state evicts its drive atom.",
                  "Silence (inputs < 10% of long-run power): no evidence is accumulated."],
        d3_title="D3: Provisional test episode (promotion)",
        d3_sub="Self-normalised mixture martingale: valid at any time (Ville's inequality)",
        d3_true="true atom", d3_null="null atom", d3_promo="promotion",
        d3_x="test samples in the episode (mixture τ fixed when the episode opens)",
        d3_note="Under H0 with conditionally symmetric noise: P(∃t: M_t ≥ p/α) ≤ α/p per candidate and episode.",
        d4_title="D4: CUSUM eviction with parsimony rent",
        d4_sub="A useful atom accrues evidence in its favour; silence yields no evidence; a regime change triggers eviction",
        d4_sil="silence", d4_sil2="(evidence frozen)", d4_chg="regime change", d4_evict="eviction",
        d4_useful="useful atom: R ≈ 0",
        d4_note="Without rent: ARL to false eviction ≥ e^h (Lorden). Rent r = h/T_idle removes idle atoms in ~T_idle steps.",
        d5_title="D5: Latent pathway in innovations form",
        d5_sub="Steady-state Kalman predictor of a first-order hidden state, linear in the parameters",
        d5_e="prequential error", d5_x="input driving the state",
        d5_u="Normalised innovation", d5_s="Innovation state s", d5_q="Drive q", d5_q2="input i tested after the latent",
        d5_out="Contribution", d5_out2="learned by NLMS",
        d5_eq="z_t = a·z_(t−1) + b·x_(t,i) + ν_t  ⇒  ŷ_t ⊃ θ_s·s_t + θ_q·q_t  with pole p ≈ a(1−K)",
        d5_notes=["Replaces the v0.2 RTRL recurrent unit (~20 FP) with ~9 FP of first-order filters.",
                  "The pole bank {0, 0.5, 0.8, 0.95} covers τ ≈ 1, 2, 5 and 20 steps; one pole is chosen by test.",
                  "Verified: MSE at 1.17× (median) of the exact Kalman predictor on task I6."]),
}


# ============================================================================ sections
def _sections(lang):
    P = lang == "pt"

    def S(N, D, table, f):
        _h = [('A predição é linear nos parâmetros sobre um conjunto ativo \\(\\mathcal{A}_t\\) de átomos estruturais com significado físico:' if P else 'The prediction is linear in the parameters over an active set \\(\\mathcal{A}_t\\) of physically meaningful structural atoms:'),
              ('orçamento cheio: substituir apenas vítimas com \\(R\\ge h/2\\); um acionamento nunca desloca o seu próprio latente;' if P else 'full budget: replace only victims with \\(R\\ge h/2\\); a drive never displaces its own latent;'),
              ('nenhum episódio é aberto antes do aquecimento (\\(t<20\\)).' if P else 'no episode opens before warm-up (\\(t<20\\)).')]
        _h += [('Dicionário: \\(dL\\) atrasos, \\(|\\mathcal P|\\) estados latentes (um por polo) e \\(d\\) acionamentos; \\(p_{\\text{dict}}=dL+|\\mathcal P|+d\\). No máximo um estado latente e um acionamento ficam ativos (limite de estado único herdado da v0.1).' if P else 'Dictionary: \\(dL\\) delays, \\(|\\mathcal P|\\) latent states (one per pole) and \\(d\\) drives; \\(p_{\\text{dict}}=dL+|\\mathcal P|+d\\). At most one latent state and one drive are active (single-state limit inherited from v0.1).'),
               ('Para um estado oculto \\(z_t=a z_{t-1}+b x_{t,i}+\\nu_t\\) observado como \\(y_t=\\mathbf w^\\top\\mathbf x_t+c z_t+\\varepsilon_t\\), o preditor de Kalman estacionário é linear em filtros de 1ª ordem da inovação e da entrada, com polo \\(p=a(1-K)\\). A LEBRE implementa-o com um banco de polos:' if P else 'For a hidden state \\(z_t=a z_{t-1}+b x_{t,i}+\\nu_t\\) observed as \\(y_t=\\mathbf w^\\top\\mathbf x_t+c z_t+\\varepsilon_t\\), the steady-state Kalman predictor is linear in first-order filters of the innovation and of the input, with pole \\(p=a(1-K)\\). LEBRE implements it with a pole bank:'),
               ('Uma fila rotativa sonda 2 candidatos de atraso por passo e mantém um escore EMA de \\(e_t x_{t-k,i}\\). Os \\(H=4\\) melhores abrem episódios de teste com estatística <em>zerada</em>: a triagem escolhe <em>o que</em> testar e nunca reutiliza os seus dados no teste (divisão temporal da amostra). Os estados latentes estão sempre em teste enquanto não há latente ativo; os acionamentos são testados só depois da promoção do latente.' if P else 'A rotating queue probes 2 delay candidates per step and keeps an EMA score of \\(e_t x_{t-k,i}\\). The best \\(H=4\\) open test episodes with <em>fresh</em> statistics: screening chooses <em>what</em> to test and never reuses its data in the test (temporal sample splitting). Latent states are always under test while no latent is active; drives are tested only after the latent is promoted.'),
               ('ESTABELECIDO: com incrementos condicionalmente simétricos, \\(\\exp(\\lambda S_t-\\lambda^2Q_t/2)\\) é supermartingale para todo λ (de la Peña 1999, Lema 6.1; Howard et al. 2020, Lema 3(d)); a mistura gaussiana sobre λ também é supermartingale, e pela desigualdade de Ville \\(P(\\exists t:M_t\\ge p/\\alpha)\\le\\alpha/p\\). τ é fixado na abertura do episódio (previsível). VERIFICADO: 0 promoções falsas em ' if P else 'ESTABLISHED: with conditionally symmetric increments, \\(\\exp(\\lambda S_t-\\lambda^2Q_t/2)\\) is a supermartingale for every λ (de la Peña 1999, Lemma 6.1; Howard et al. 2020, Lemma 3(d)); the Gaussian mixture over λ is also a supermartingale, and by Ville\'s inequality \\(P(\\exists t:M_t\\ge p/\\alpha)\\le\\alpha/p\\). τ is fixed when the episode opens (predictable). VERIFIED: 0 false promotions in '),
               ('ESTABELECIDO: \\(\\ell_t\\) é exatamente a razão de log-verossimilhança gaussiana entre os preditivos "com" e "sem" o átomo; o CUSUM tem ARL até alarme falso ≥ e^h (Lorden 1971) e é minimax-ótimo (Moustakides 1986) no caso simples. Na LEBRE as hipóteses são compostas, e a otimalidade não se transfere. VERIFICADO: ' if P else 'ESTABLISHED: \\(\\ell_t\\) is exactly the Gaussian log-likelihood ratio between the "with" and "without" predictives; CUSUM has ARL to false alarm ≥ e^h (Lorden 1971) and is minimax optimal (Moustakides 1986) in the simple case. In LEBRE the hypotheses are composite, so optimality does not transfer. VERIFIED: '),
               ('Os recursos são governados em três níveis: (i) orçamento estrutural \\(M_{\\max}=4\\) átomos; (ii) aluguel de parcimônia, que obriga cada átomo a render pelo menos \\(r=h/T_{\\text{idle}}\\approx0{,}0174\\) nats por passo excitado; (iii) cadências fixas de triagem (2/passo), teste (1/2 passos), evidência (1/2 passos) e decisão (1/10 passos).' if P else 'Resources are governed at three levels: (i) structural budget \\(M_{\\max}=4\\) atoms; (ii) parsimony rent, which requires each atom to yield at least \\(r=h/T_{\\text{idle}}\\approx0.0174\\) nats per excited step; (iii) fixed cadences for screening (2/step), testing (1 per 2 steps), evidence (1 per 2 steps) and decisions (1 per 10 steps).'),
               ('Todas as features são adimensionais: entradas padronizadas pelo ambiente, inovação normalizada \\(u/\\hat\\sigma\\), filtros de entradas padronizadas e prior de informação unitária relativo a \\(\\hat\\sigma\\). VERIFICADO: NMSE ' if P else 'All features are dimensionless: inputs standardised by the environment, normalised innovation \\(u/\\hat\\sigma\\), filters of standardised inputs, and a unit-information prior relative to \\(\\hat\\sigma\\). VERIFIED: NMSE ')]
        out = []
        I = N["int"]; arms = I["arms"]; con = I["con"]
        v = arms.loc["V032"]; a0 = arms.loc["V02_A0"]; arx = arms.loc["CTRL_ARX"]
        h1 = con.loc["H1' V032-V02_A0 NMSE"]; h3 = con.loc["H3' V032-CTRL_ARX NMSE"]; h4 = con.loc["H4' V032-V02_A0 struct"]
        p4 = N["p4"]; p4t = N["p4task"]
        rk = p4["mean_rank"].rank(method="min")
        b02 = N.get("b02")

        # ---------------------------------------------------------------- 1
        toc = [("1", "Sumário executivo e guia do documento" if P else "Executive summary and document guide"),
               ("2", "Identidade arquitetural, princípios e classificação" if P else "Architectural identity, principles and classification"),
               ("3", "Formulação matemática" if P else "Mathematical formulation"),
               ("4", "Ciclo de vida estrutural e camada de decisão estatística" if P else "Structural lifecycle and statistical decision layer"),
               ("5", "Governança de recursos e invariância em tempo de fluxo" if P else "Resource governance and stream-time invariance"),
               ("6", "Diagramas arquiteturais (D1–D5)" if P else "Architectural diagrams (D1–D5)"),
               ("7", "Validação empírica" if P else "Empirical validation"),
               ("8", "Contabilidade computacional e envelope embarcado" if P else "Computational accounting and embedded envelope"),
               ("9", "Limites de escopo e reivindicações proibidas" if P else "Scope limits and forbidden claims"),
               ("10", "Matriz de rastreabilidade de parâmetros" if P else "Parameter traceability matrix"),
               ("11", "Registros de decisão arquitetural e decisão final" if P else "Architectural decision records and final decision")]
        tl = "".join(f'<li class="toc-item"><span class="toc-title">{n}. {t}</span><span class="toc-page">§{n}</span></li>' for n, t in toc)
        if P:
            out.append(f"""<div class="page-break"></div><h1>1. Sumário Executivo e Guia do Documento</h1>
<p>A <strong>LEBRE v0.3.2</strong> é a terceira geração da família LEBRE (<em>Lifecycle-governed Evidence-Based Resource Evolution</em>). Ela mantém a identidade
da família: caminho-base sempre ativo, caminho esparso de atrasos discretos, um caminho de estado latente recorrente, ciclo de vida estrutural com
probação em sombra e governança explícita de recursos. O que muda é que <strong>toda decisão estrutural passa a ser um teste estatístico com taxa de erro controlada</strong>,
toda evidência passa a evoluir em tempo de fluxo e o caminho latente passa a ser o preditor de Kalman em forma de inovações.</p>
<div class="alert alert-info"><strong>Status:</strong> especificação de pesquisa <code>NON_CANONICAL</code>. A LEBRE v0.1 (organização do Track B) permanece a referência
canônica congelada (<code>FROZEN_WITH_SCOPE_LIMITS</code>). M3 continua <code>UNOPENED</code> e <code>NOVELTY_CLAIM_READY = NO</code>. Implementação de referência:
<code>lebre_v032.py</code> (SHA-256 <code>ef0d9634…32efe8</code>).</div>
<div class="kv"><div><strong>Interno (I1–I14, N=30, pré-registrado):</strong> NMSE {f(v.nmse)} contra {f(a0.nmse)} da v0.2 A0 (Δ = {f(h1['mean'],4)}, {int(h1['favourable'])}/30 sementes); {f(v.fp,1)} FP/passo contra {f(a0.fp,1)}.</div>
<div><strong>Explicabilidade:</strong> estrutura exata recuperada em {100*v.struct_exact_rate:.1f}% dos checkpoints, contra {100*a0.struct_exact_rate:.1f}% da v0.2.</div>
<div><strong>Validade:</strong> 0 promoções falsas em {N['T3_n']} fluxos nulos (ruído gaussiano, t₃ e heterocedástico); causalidade exata; invariância de escala exata.</div>
<div><strong>Externo:</strong> {('3º lugar no rank médio no BENCH-01 com colunas permutadas' if rk['LEBRE_V032']<=3 else 'posição '+str(int(rk['LEBRE_V032'])))} (rank médio {f(p4.loc['LEBRE_V032','mean_rank'],1)}, contra {f(p4.loc['Track_B','mean_rank'],1)} do Track B)
{('; BENCH-02: '+str(b02['n_tasks'])+' tarefas, posição global '+str(b02['v032_global_position'])+' — decisão pré-registrada <code>'+b02['decision']+'</code>') if b02 else ''}.</div></div>
<h2>Sumário</h2><ul class="toc-list">{tl}</ul>
<h2>Convenções</h2><p>Vetores em negrito (\\(\\mathbf{{x}}_t\\in\\mathbb{{R}}^D\\)), escalares em itálico, tempo discreto por subscrito \\(t\\). "Tempo de fluxo" é o índice de amostras
da corrente de dados. Custos em operações de ponto flutuante por passo (FP/passo), com a mesma taxonomia da v0.1. Evidência em <em>nats</em> (logaritmo natural).
Rótulos de evidência: <code>ESTABELECIDO</code> (resultado da literatura), <code>VERIFICADO</code> (teste empírico deste projeto), <code>DE PROJETO</code> (escolha não derivada).</p>""")
        else:
            out.append(f"""<div class="page-break"></div><h1>1. Executive Summary and Document Guide</h1>
<p><strong>LEBRE v0.3.2</strong> is the third generation of the LEBRE family (<em>Lifecycle-governed Evidence-Based Resource Evolution</em>). It keeps the family identity:
an always-on base pathway, a sparse discrete-delay pathway, one recurrent latent-state pathway, a structural lifecycle with shadow probation and explicit resource governance.
What changes is that <strong>every structural decision is now a statistical test with a controlled error rate</strong>, all evidence evolves in stream time, and the latent
pathway is the Kalman predictor in innovations form.</p>
<div class="alert alert-info"><strong>Status:</strong> <code>NON_CANONICAL</code> research specification. LEBRE v0.1 (Track B organisation) remains the frozen canonical
reference (<code>FROZEN_WITH_SCOPE_LIMITS</code>). M3 remains <code>UNOPENED</code>; <code>NOVELTY_CLAIM_READY = NO</code>. Reference implementation:
<code>lebre_v032.py</code> (SHA-256 <code>ef0d9634…32efe8</code>).</div>
<div class="kv"><div><strong>Internal (I1–I14, N=30, pre-registered):</strong> NMSE {f(v.nmse)} vs {f(a0.nmse)} for v0.2 A0 (Δ = {f(h1['mean'],4)}, {int(h1['favourable'])}/30 seeds); {f(v.fp,1)} FP/step vs {f(a0.fp,1)}.</div>
<div><strong>Explainability:</strong> exact structure recovered at {100*v.struct_exact_rate:.1f}% of checkpoints vs {100*a0.struct_exact_rate:.1f}% for v0.2.</div>
<div><strong>Validity:</strong> 0 false promotions in {N['T3_n']} null streams (Gaussian, t₃ and heteroscedastic noise); exact causality; exact scale invariance.</div>
<div><strong>External:</strong> {('3rd by mean rank on column-permuted BENCH-01' if rk['LEBRE_V032']<=3 else 'position '+str(int(rk['LEBRE_V032'])))} (mean rank {f(p4.loc['LEBRE_V032','mean_rank'],1)} vs {f(p4.loc['Track_B','mean_rank'],1)} for Track B)
{('; BENCH-02: '+str(b02['n_tasks'])+' tasks, global position '+str(b02['v032_global_position'])+' — pre-registered decision <code>'+b02['decision']+'</code>') if b02 else ''}.</div></div>
<h2>Contents</h2><ul class="toc-list">{tl}</ul>
<h2>Conventions</h2><p>Vectors in bold (\\(\\mathbf{{x}}_t\\in\\mathbb{{R}}^D\\)), scalars in italics, discrete time by subscript \\(t\\). "Stream time" is the sample index of the data stream.
Costs are floating-point operations per step (FP/step), with the v0.1 taxonomy. Evidence is in <em>nats</em>. Evidence labels: <code>ESTABLISHED</code> (literature result),
<code>VERIFIED</code> (empirical test in this project), <code>DESIGN</code> (non-derived choice).</p>""")

        # ---------------------------------------------------------------- 2
        K = [("K1", "Elementos distintos com interfaces" if P else "Distinct elements with interfaces", "ISO/IEC/IEEE 42010",
              "9 elementos: base, atrasos, latente, triagem, testes, supervisor, monitor CUSUM, governador, interface de explicação" if P else
              "9 elements: base, delays, latent, screening, tests, supervisor, CUSUM monitor, governor, explanation interface"),
             ("K2", "Relações explícitas (dados × controle)" if P else "Explicit relations (data × control)", "42010; arquiteturas cognitivas" if P else "42010; cognitive architectures",
              "candidatos nunca tocam a predição; o controle altera só o conjunto ativo" if P else "candidates never touch the prediction; control only edits the active set"),
             ("K3", "Princípios de realização e evolução" if P else "Principles of realisation and evolution", "42010",
              "P1–P6 (acima), válidos em tempo de execução" if P else "P1–P6 (above), holding at run time"),
             ("K4", "Infraestrutura fixa, conteúdo aprendido" if P else "Fixed infrastructure, learned content", "Newell; Laird (Soar)",
              "mesma maquinaria sem calibração em D = 1..50 e em dezenas de tarefas externas" if P else "same machinery, uncalibrated, for D = 1..50 and dozens of external tasks"),
             ("K5", "Família parametrizada e especificável" if P else "Parametrised, specifiable family", "42010; NAS",
              "(d, L, polos, M_max, α, ARL, T_idle); referência congelada por hash" if P else "(d, L, poles, M_max, α, ARL, T_idle); hash-frozen reference"),
             ("K6", "Composição não trivial (ablações)" if P else "Non-trivial composition (ablations)", "CAR-01",
              "retirar a auto-normalização, o portão de excitação, o aluguel ou o aquecimento quebra propriedades verificadas" if P else
              "removing self-normalisation, excitation gate, rent or warm-up breaks verified properties"),
             ("K7", "Espaço de topologias com regra de percurso" if P else "Topology space with a traversal rule", "Cascade-Correlation; NAS",
              "grafo linear-dinâmico esparso cuja topologia muda online por teste" if P else "sparse linear-dynamical graph whose topology changes online by test")]
        prin = ([("P1", "Toda decisão estrutural é um teste com erro controlado.", "promoção: Ville + de la Peña; remoção: CUSUM/ARL"),
                 ("P2", "Toda evidência evolui em tempo de fluxo.", "cadências só adicionam espera limitada (lição do ARB10)"),
                 ("P3", "Toda estrutura é cara e paga aluguel.", "aluguel MDL ponderado pela excitação; orçamento M_max"),
                 ("P4", "Silêncio não é evidência.", "portão de excitação persistente"),
                 ("P5", "Candidatos não perturbam a predição.", "probação em sombra; coeficiente inicial = média posterior"),
                 ("P6", "Invariância de escala e explicabilidade por construção.", "features adimensionais; cada átomo tem significado físico")]
                if P else
                [("P1", "Every structural decision is a test with controlled error.", "promotion: Ville + de la Peña; eviction: CUSUM/ARL"),
                 ("P2", "All evidence evolves in stream time.", "cadences only add bounded waiting (ARB10 lesson)"),
                 ("P3", "All structure is costly and pays rent.", "excitation-weighted MDL rent; budget M_max"),
                 ("P4", "Silence is not evidence.", "persistent-excitation gate"),
                 ("P5", "Candidates do not perturb the prediction.", "shadow probation; initial coefficient = posterior mean"),
                 ("P6", "Scale invariance and explainability by construction.", "dimensionless features; every atom has a physical meaning")])
        out.append(f"""<div class="page-break"></div><h1>2. {'Identidade Arquitetural, Princípios e Classificação' if P else 'Architectural Identity, Principles and Classification'}</h1>
<h2>2.1 {'Princípios invariantes' if P else 'Invariant principles'}</h2>{table(['#', 'Princípio' if P else 'Principle', 'Mecanismo' if P else 'Mechanism'], prin)}
<h2>2.2 {'A LEBRE v0.3.2 é uma arquitetura?' if P else 'Is LEBRE v0.3.2 an architecture?'}</h2>
<p>{'Critérios extraídos de quatro tradições com definição publicada do termo: engenharia de sistemas (ISO/IEC/IEEE 42010:2022: "conceitos ou propriedades fundamentais de uma entidade em seu ambiente e princípios que governam sua realização e evolução"), arquiteturas cognitivas (estruturas fixas + conhecimento aprendido; Newell, Laird), arquiteturas de aprendizado (Cascade-Correlation, Dyna, Horde) e busca de arquitetura neural (topologia do grafo computacional; Elsken, Metzen & Hutter 2019).' if P else
'Criteria drawn from four traditions with a published definition of the term: systems engineering (ISO/IEC/IEEE 42010:2022: "fundamental concepts or properties of an entity in its environment and governing principles for the realization and evolution of this entity"), cognitive architectures (fixed structures + learned knowledge; Newell, Laird), learning architectures (Cascade-Correlation, Dyna, Horde) and neural architecture search (topology of the computational graph; Elsken, Metzen & Hutter 2019).'}</p>
{table(['#', 'Critério' if P else 'Criterion', 'Origem' if P else 'Source', 'LEBRE v0.3.2'], [(k, a, b, '✅ ' + c) for k, a, b, c in K])}
<div class="verdict">{'Veredito: SIM — arquitetura de aprendizado estrutural online fundamentada (PRINCIPLED_ONLINE_STRUCTURAL_LEARNING_ARCHITECTURE), status RESEARCH_SPECIFICATION_NON_CANONICAL.' if P else
'Verdict: YES — principled online structural-learning architecture (PRINCIPLED_ONLINE_STRUCTURAL_LEARNING_ARCHITECTURE), status RESEARCH_SPECIFICATION_NON_CANONICAL.'}</div>
<div class="alert alert-danger">{'<strong>Ser arquitetura não é o mesmo que ser competitiva:</strong> no benchmark externo extenso (BENCH-02, 25 tarefas, 24 modelos) a decisão pré-registrada foi <code>NOT_JUSTIFIED_EXTERNALLY</code> (Seção 7.5).' if P else '<strong>Being an architecture is not the same as being competitive:</strong> on the extensive external benchmark (BENCH-02, 25 tasks, 24 models) the pre-registered decision was <code>NOT_JUSTIFIED_EXTERNALLY</code> (Section 7.5).'}</div>
<div class="alert alert-warning">{'<strong>Não é:</strong> uma arquitetura de rede neural, uma nova regra de aprendizado, nem um modelo universal de sequências. Cada primitivo é arte anterior (Kalman, NLMS, martingales de mistura, CUSUM); a reivindicação é a <em>organização</em>, como em Cascade-Correlation, Dyna e Horde. A classe de modelos é linear nos parâmetros (ARX/OBF esparso com estado latente de 1ª ordem).' if P else
'<strong>It is not:</strong> a neural-network architecture, a new learning rule, or a universal sequence model. Every primitive is prior art (Kalman, NLMS, mixture martingales, CUSUM); the claim is the <em>organisation</em>, as for Cascade-Correlation, Dyna and Horde. The model class is linear in the parameters (sparse ARX/OBF with a first-order latent state).'}</div>""")

        # ---------------------------------------------------------------- 3
        out.append(f"""<div class="page-break"></div><h1>3. {'Formulação Matemática' if P else 'Mathematical Formulation'}</h1>
<h2>3.1 {'Modelo preditivo e dicionário de átomos' if P else 'Predictive model and atom dictionary'}</h2>
<p>{_h[0]}</p>
<div class="math-box">$$\\hat y_t=\\boldsymbol\\theta_b^\\top[\\mathbf x_t;1]+\\sum_{{a\\in\\mathcal A_t}}\\theta_a\\,\\varphi_a(t),\\qquad |\\mathcal A_t|\\le M_{{\\max}}$$
$$\\varphi_{{(i,k)}}(t)=x_{{t-k,i}}\\;(1\\le k\\le L),\\qquad \\varphi_{{s,p}}(t)=s_{{p,t-1}},\\qquad \\varphi_{{q,i}}(t)=q_{{i,t-1}}$$</div>
<p>{_h[3]}</p>
<h2>3.2 {'Aprendizado de parâmetros (NLMS)' if P else 'Parameter learning (NLMS)'}</h2>
<div class="math-box">$$e_t=y_t-\\hat y_t,\\qquad \\boldsymbol\\theta\\leftarrow\\boldsymbol\\theta+\\frac{{\\mu\\,e_t\\,\\boldsymbol\\phi_t}}{{\\epsilon+\\lVert\\boldsymbol\\phi_t\\rVert^2}},\\qquad \\mu=0.1\\;\\Rightarrow\\;\\mathcal M\\approx\\tfrac{{\\mu}}{{2-\\mu}}\\approx5.3\\%$$</div>
<p class="small">{'ESTABELECIDO: estabilidade em média quadrática para 0 &lt; μ &lt; 2 e desajuste ≈ μ/(2−μ) sob regressores aproximadamente brancos (Slock 1993; Haykin).' if P else 'ESTABLISHED: mean-square stability for 0 &lt; μ &lt; 2 and misadjustment ≈ μ/(2−μ) under approximately white regressors (Slock 1993; Haykin).'}</p>
<h2>3.3 {'Caminho latente em forma de inovações' if P else 'Latent pathway in innovations form'}</h2>
<p>{_h[4]}</p>
<div class="math-box">$$u_t=e_t+\\sum_{{a\\in\\mathcal A^{{\\text{{lat}}}}_t}}\\theta_a\\varphi_a(t),\\qquad s_{{p,t}}=p\\,s_{{p,t-1}}+(1-p)\\,\\frac{{u_t}}{{\\hat\\sigma_t}},\\qquad q_{{i,t}}=p^\\star q_{{i,t-1}}+(1-p^\\star)\\,x_{{t,i}}$$
$$p\\in\\mathcal P=\\{{0,\\;0.5,\\;0.8,\\;0.95\\}}\\;(\\tau\\approx1,2,5,20),\\qquad p^\\star=\\text{{{'polo do latente ativo' if P else 'pole of the active latent'}}}$$</div>
<p class="small">{'ESTABELECIDO: equivalência entre o preditor de Kalman estacionário e a forma de inovações/ARMAX (Ljung 1999; Anderson &amp; Moore 1979). VERIFICADO: MSE na I6 a ' if P else 'ESTABLISHED: equivalence of the steady-state Kalman predictor and the innovations/ARMAX form (Ljung 1999; Anderson &amp; Moore 1979). VERIFIED: MSE on I6 at '}{f(N['T5'][0],2)}× {'(mediana) e' if P else '(median) and'} {f(N['T5'][1],2)}× {'(máximo) do ótimo exato.' if P else '(max) of the exact optimum.'}</p>
<h2>3.4 {'Escala de ruído, aquecimento e excitação' if P else 'Noise scale, warm-up and excitation'}</h2>
<div class="math-box">$$\\hat\\sigma^2_t=\\hat\\sigma^2_{{t-1}}+\\beta_t\\,(e_t^2-\\hat\\sigma^2_{{t-1}}),\\quad \\beta_t=\\max\\!\\left(\\tfrac1{{t+1}},\\tfrac1{{n_\\sigma}}\\right);\\qquad \\bar P_t=\\bar P_{{t-1}}+\\beta^P_t(\\lVert\\mathbf x_t\\rVert^2-\\bar P_{{t-1}})$$
$$\\text{{{'excitado' if P else 'excited'}}}_t\\iff\\lVert\\mathbf x_t\\rVert^2\\ge\\kappa\\,\\bar P_t\\quad(\\kappa=0.1)$$</div>""")

        # ---------------------------------------------------------------- 4
        out.append(f"""<div class="page-break"></div><h1>4. {'Ciclo de Vida Estrutural e Camada de Decisão Estatística' if P else 'Structural Lifecycle and Statistical Decision Layer'}</h1>
<p>{'Quatro estados: <code>DORMANT</code> (no dicionário) → <code>PROVISIONAL</code> (em teste formal, sem tocar a predição) → <code>ACTIVE</code> (na predição) → <code>EVICTED</code> (volta ao dicionário). Decisões a cada 10 passos; testes e evidência atualizados a cada 2 passos e somente sob excitação.' if P else
'Four states: <code>DORMANT</code> (in the dictionary) → <code>PROVISIONAL</code> (under formal test, not touching the prediction) → <code>ACTIVE</code> (in the prediction) → <code>EVICTED</code> (back to the dictionary). Decisions every 10 steps; tests and evidence updated every 2 steps and only under excitation.'}</p>
<h2>4.1 {'Triagem (DORMANT → PROVISIONAL)' if P else 'Screening (DORMANT → PROVISIONAL)'}</h2>
<p>{_h[5]}</p>
<h2>4.2 {'Promoção (PROVISIONAL → ACTIVE)' if P else 'Promotion (PROVISIONAL → ACTIVE)'}</h2>
<div class="math-box">$$S_t=\\sum_{{j\\le t}} e_j\\varphi_c(j),\\qquad Q_t=\\sum_{{j\\le t}}\\big(e_j\\varphi_c(j)\\big)^2,\\qquad \\tau=\\frac{{\\rho_{{\\text{{rel}}}}}}{{\\hat\\sigma^2_{{t_0}}\\,m_\\varphi}}$$
$$\\log M_t=\\frac{{\\tau S_t^2}}{{2(1+\\tau Q_t)}}-\\tfrac12\\log(1+\\tau Q_t)\\;\\ge\\;\\log\\frac{{p_{{\\text{{dict}}}}}}{{\\alpha}}\\;\\Rightarrow\\;\\text{{promote}},\\qquad \\theta_0=\\frac{{S_t}}{{Q_t/\\hat\\sigma^2_t+m_\\varphi/\\rho_{{\\text{{rel}}}}}}$$</div>
<p class="small">{_h[6]}{N['T3_n']} {'fluxos nulos. Limite: no laço adaptativo a validade é aproximada; a garantia é por episódio.' if P else 'null streams. Limit: in the adaptive loop validity is approximate; the guarantee is per episode.'}</p>
<h2>4.3 {'Remoção (ACTIVE → EVICTED)' if P else 'Eviction (ACTIVE → EVICTED)'}</h2>
<div class="math-box">$$\\ell_t(a)=\\frac{{c_a(2e_t+c_a)}}{{2\\hat\\sigma^2_t}},\\quad c_a=\\theta_a\\varphi_a(t);\\qquad R_t(a)=\\max\\!\\Big(0,\\;R_{{t-1}}(a)-\\ell_t(a)+r\\,\\min\\!\\big(1,\\varphi_a^2/v_a\\big)\\Big)$$
$$R_t(a)>h=\\log(\\text{{ARL}})\\;\\Rightarrow\\;\\text{{evict}},\\qquad r=h/T_{{\\text{{idle}}}}$$</div>
<p class="small">{_h[7]}{N['T4'][0]} {'remoções falsas em' if P else 'false evictions in'} {N['T4'][1]:,} {'passos monitorados.' if P else 'monitored steps.'}</p>
<h2>4.4 {'Regras de acoplamento e orçamento' if P else 'Coupling and budget rules'}</h2>
<ul><li>{'no máximo uma remoção e uma promoção por decisão;' if P else 'at most one eviction and one promotion per decision;'}</li>
<li>{_h[1]}</li>
<li>{'remover o latente remove o acionamento acoplado e fecha os testes de acionamento;' if P else 'evicting the latent evicts the coupled drive and closes drive tests;'}</li>
<li>{_h[2]}</li></ul>
<h2>4.5 {'Interface de explicação' if P else 'Explanation interface'}</h2>
<p>{'A cada instante o modelo emite: pesos da base; cada átomo ativo com significado físico ("x1 atrasado 6 passos", "estado latente τ≈5 alimentado por x0"), coeficiente, evidência acumulada (nats), CUSUM contrário e instante de ativação; e o log completo de eventos do ciclo de vida.' if P else
'At every instant the model emits: base weights; each active atom with its physical meaning ("x1 delayed 6 steps", "latent state τ≈5 driven by x0"), coefficient, accumulated evidence (nats), opposing CUSUM and activation time; and the complete lifecycle event log.'}</p>""")

        # ---------------------------------------------------------------- 5
        out.append(f"""<div class="page-break"></div><h1>5. {'Governança de Recursos e Invariância em Tempo de Fluxo' if P else 'Resource Governance and Stream-Time Invariance'}</h1>
<p>{_h[8]}</p>
<h2>5.1 {'Invariância em tempo de fluxo (lição do ARB10)' if P else 'Stream-time invariance (ARB10 lesson)'}</h2>
<p>{'Na v0.2, decimar a arbitragem com um α por evento dobrava a escala de tempo da evidência. Na v0.3.2 nenhuma estatística é um EMA por evento: somas de teste, CUSUM e σ² evoluem por amostra, e quando a evidência é subamostrada o aluguel é escalado por <code>evidence_every</code> para manter a taxa por passo. Mudar uma cadência altera apenas a espera, limitada pela própria cadência.' if P else
'In v0.2, decimating arbitration with a per-event α doubled the evidence timescale. In v0.3.2 no statistic is a per-event EMA: test sums, CUSUM and σ² evolve per sample, and when evidence is subsampled the rent is scaled by <code>evidence_every</code> to keep the per-step rate. Changing a cadence only changes the waiting time, bounded by the cadence itself.'}</p>
<h2>5.2 {'Equivariância de escala' if P else 'Scale equivariance'}</h2>
<p>{_h[9]}{f(N['T7'][0],4)} / {f(N['T7'][1],4)} / {f(N['T7'][2],4)} {'com y ×10⁻³ / ×1 / ×10³.' if P else 'with y ×10⁻³ / ×1 / ×10³.'}</p>""")

        # ---------------------------------------------------------------- 6
        cap = (lambda k, t: f'<div class="diagram-caption">{t}</div>')
        dl = [("D1", "Plano de dados (predição) separado do plano de controle (ciclo de vida)." if P else "Data plane (prediction) separated from the control plane (lifecycle)."),
              ("D2", "Máquina de estados do ciclo de vida e regras de acoplamento." if P else "Lifecycle state machine and coupling rules."),
              ("D3", "Esquema ilustrativo de um episódio de teste (não são dados medidos)." if P else "Illustrative test episode (not measured data)."),
              ("D4", "Esquema ilustrativo do CUSUM com aluguel e congelamento no silêncio." if P else "Illustrative CUSUM with rent and freezing in silence."),
              ("D5", "Caminho latente: preditor de Kalman estacionário via filtros de 1ª ordem." if P else "Latent pathway: steady-state Kalman predictor via first-order filters.")]
        out.append(f"""<div class="page-break"></div><h1>6. {'Diagramas Arquiteturais (D1–D5)' if P else 'Architectural Diagrams (D1–D5)'}</h1>""")
        for i, (k, c) in enumerate(dl):
            if i in (2, 4):
                out.append('<div class="page-break"></div>')
            out.append(f'<h2>{k}</h2><div class="diagram-container">{D[k]}{cap(k, c)}</div>')

        # ---------------------------------------------------------------- 7
        T3 = N["T3"]
        prop = [("T1", "Causalidade: perturbar y_t e o futuro não altera ŷ_{≤t}" if P else "Causality: perturbing y_t and the future leaves ŷ_{≤t} unchanged", f"diferença máx. {N['T1']:.1f}" if P else f"max diff {N['T1']:.1f}", "✅"),
                ("T2", "Alinhamento de atrasos (k = 1, 7, 32)" if P else "Delay alignment (k = 1, 7, 32)", f"{N['T2']}/30", "✅"),
                ("T3", "Promoções falsas por fluxo (gauss / t₃ / hetero), limite 0,052" if P else "False promotions per stream (gauss / t₃ / hetero), bound 0.052",
                 f"{T3.get('gauss',0):.3f} / {T3.get('student_t3',0):.3f} / {T3.get('hetero',0):.3f}", "✅"),
                ("T4", "Remoções falsas do átomo verdadeiro" if P else "False evictions of the true atom", f"{N['T4'][0]} / {N['T4'][1]:,}", "✅"),
                ("T5", "MSE latente / Kalman ótimo (mediana; máx.)" if P else "Latent MSE / optimal Kalman (median; max)", f"{N['T5'][0]:.2f}; {N['T5'][1]:.2f}", "⚠️"),
                ("T6", "Retenção do latente no silêncio; eventos durante o silêncio" if P else "Latent retained through silence; events during silence", f"{N['T6'][0]}/{N['T6'][1]}; {N['T6'][2]:.2f}", "✅"),
                ("T7", "NMSE com y ×10⁻³ / ×1 / ×10³" if P else "NMSE with y ×10⁻³ / ×1 / ×10³", " / ".join(f"{x:.4f}" for x in N['T7']), "✅"),
                ("T8", "FP/passo na tarefa mais cara (I4)" if P else "FP/step on the most expensive task (I4)", f"{N['T8']:.1f}", "⚠️")]
        irows = [(k, f"{arms.loc[k].nmse:.4f}", f"{arms.loc[k].fp:.1f}", (f"{100 * arms.loc[k].struct_exact_rate:.1f}%" if arms.loc[k].struct_exact_rate == arms.loc[k].struct_exact_rate else "—"))
                 for k in ["V032", "V031", "V02_A0", "CTRL_ARX"]]
        crow = [(c.split(" ")[0], c.split(" ", 1)[1], f"{r['mean']:+.4f}", f"{r['one_sided_upper']:+.4f}" if "struct" not in c else f"{r['one_sided_lower']:+.4f}",
                 f"{int(r['favourable'])}/30", f"{r['p_holm']:.1e}" if r['p_holm'] == r['p_holm'] else "—") for c, r in con.iloc[:3].iterrows()]
        top = p4.sort_values("mean_rank").head(8)
        p4rows = [(m, f"{r.mean_rank:.1f}", f"{r.nmse_mean:.3f}", f"{r.flops:.0f}", int(r.tasks_on_pareto)) for m, r in top.iterrows()]
        p6 = N["p6"]
        p6rows = [(t.replace("_UCI_", " "), f"{r.CTRL_PERSISTENCE:.3f}", f"{r.CTRL_ARX_NLMS:.3f}", f"{r.nmse_median:.3f}", f"{min(r.Track_B, r.C2_NLMS, r.S3_RSONN):.3f}")
                  for t, r in p6.iterrows()]
        out.append(f"""<div class="page-break"></div><h1>7. {'Validação Empírica' if P else 'Empirical Validation'}</h1>
<p class="small">{'Todas as avaliações foram pré-registradas com hash antes da execução, usam sementes nunca usadas no desenvolvimento e mantêm a v0.3.2 congelada e sem calibração. Os baselines externos foram calibrados por tarefa.' if P else
'All evaluations were pre-registered with a hash before execution, use seeds never used in development, and keep v0.3.2 frozen and uncalibrated. External baselines were calibrated per task.'}</p>
<h2>7.1 {'Propriedades verificadas' if P else 'Verified properties'}</h2>{table(['#', 'Propriedade' if P else 'Property', 'Resultado' if P else 'Result', ''], prop)}
<h2>7.2 {'Benchmark interno I1–I14 (confirmatório; sementes 2146..2175)' if P else 'Internal benchmark I1–I14 (confirmatory; seeds 2146..2175)'}</h2>
{table(['Braço' if P else 'Arm', 'NMSE', 'FP/' + ('passo' if P else 'step'), 'Estrutura exata' if P else 'Exact structure'], irows)}
{table(['H', 'Contraste' if P else 'Contrast', 'Δ', 'Limite 95%' if P else '95% bound', 'Favoráveis' if P else 'Favourable', 'p (Holm)'], crow)}
<div class="page-break"></div><h2>7.3 {'BENCH-01 com colunas permutadas (sementes 161..190; 20 modelos)' if P else 'BENCH-01 with permuted columns (seeds 161..190; 20 models)'}</h2>
<p class="small">{'As dependências verdadeiras das tarefas A2–A4 e H1 estão na coluna 0; a permutação remove o artefato que favorecia modelos que só olham essa coluna.' if P else
'The true dependencies of tasks A2–A4 and H1 lie in column 0; permutation removes the artefact that favoured models looking only at that column.'}</p>
{table(['Modelo' if P else 'Model', 'Rank médio' if P else 'Mean rank', 'NMSE médio' if P else 'Mean NMSE', 'FLOPs', 'Pareto'], p4rows)}
<h2>7.4 {'Dados reais nunca usados (UCI; semi-held-out)' if P else 'Never-used real data (UCI; semi-held-out)'}</h2>
{table(['Dataset', 'Persistência' if P else 'Persistence', 'ARX-NLMS', 'LEBRE v0.3.2', 'Melhor baseline' if P else 'Best baseline'], p6rows)}
<div class="alert alert-danger">{'Nos três datasets reais horários a persistência trivial vence todos os modelos; no X3 um único registro errado do dataset (chuva = 9831 mm/h) domina o erro de todos os modelos lineares, inclusive a LEBRE.' if P else
'On the three hourly real datasets trivial persistence beats every model; on X3 a single erroneous dataset record (rain = 9831 mm/h) dominates the error of every linear model, LEBRE included.'}</div>""")
        if b02:
            rk2 = N["b02rank"]; bt = N["b02task"]
            top2 = rk2.head(10)
            cols = [c for c in ["A", "B", "C", "D"] if c in rk2.columns]
            r2 = [(m, f"{r.ALL:.2f}") + tuple((f"{r[c]:.1f}" if r[c] == r[c] else "—") for c in cols) + (int(r.tasks_rank1), int(r.tasks_top3), f"{r.median_skill:+.3f}") for m, r in top2.iterrows()]
            if "LEBRE_V032" not in top2.index:
                r = rk2.loc["LEBRE_V032"]
                r2.append(("LEBRE_V032", f"{r.ALL:.2f}") + tuple(f"{r[c]:.1f}" for c in cols) + (int(r.tasks_rank1), int(r.tasks_top3), f"{r.median_skill:+.3f}"))
            trows = [(r.track, r.task_id, f"{r.v032_nmse:.4f}", f"{r.v032_skill:+.3f}", f"{int(r.v032_rank)}/{int(r.n_models)}", r.best_other, f"{r.best_other_nmse:.4f}")
                     for _, r in bt.iterrows()]
            out.append(f"""<div class="page-break"></div><h2>7.5 BENCH-02 {'— benchmark externo extenso (4 trilhas da literatura)' if P else '— extensive external benchmark (4 literature tracks)'}</h2>
<p>{'Trilhas: A — previsão online de séries temporais (ETTh1/h2/m1/m2, Exchange, Jena Weather, ECL, Traffic; protocolo de FSNet/OneNet em h = 1); B — regressão em fluxo com deriva (Friedman LEA/GRA/GSG, Planes2D, Mv, Bikes, WaterFlow, TrumpApproval; River); C — identificação não linear (Wiener–Hammerstein, Cascaded Tanks, EMPS; predição de 1 passo na partição de teste oficial); D — sistema FIR esparso (K = 1/4/8, entrada branca e colorida, troca abrupta). Baselines: os 15 do BENCH-01B calibrados, filtros adaptativos clássicos (NLMS, RLS, RZA-LMS, IPNLMS), aprendizado em fluxo (River: SGD, HATR, ARF-Reg) e controles (persistência, sazonal ingênuo, ARX-NLMS).' if P else
'Tracks: A — online time-series forecasting (ETTh1/h2/m1/m2, Exchange, Jena Weather, ECL, Traffic; FSNet/OneNet protocol at h = 1); B — streaming regression with drift (Friedman LEA/GRA/GSG, Planes2D, Mv, Bikes, WaterFlow, TrumpApproval; River); C — nonlinear identification (Wiener–Hammerstein, Cascaded Tanks, EMPS; one-step prediction on the official test split); D — sparse FIR system (K = 1/4/8, white and coloured input, abrupt switch). Baselines: the 15 calibrated BENCH-01B models, classical adaptive filters (NLMS, RLS, RZA-LMS, IPNLMS), streaming learners (River: SGD, HATR, ARF-Reg) and controls (persistence, seasonal naive, ARX-NLMS).'}</p>
<div class="verdict {'verdict-warn' if b02['decision'] != 'JUSTIFIED_EXTERNALLY' else ''}">{'Decisão pré-registrada' if P else 'Pre-registered decision'}: {b02['decision']} — {'posição global' if P else 'global position'} {b02['v032_global_position']} ({'rank médio' if P else 'mean rank'} {b02['v032_mean_rank']:.2f}); {'rank 1 em' if P else 'rank 1 on'} {b02['v032_tasks_rank1']}/{b02['n_tasks']}; top-3 {'em' if P else 'on'} {b02['v032_tasks_top3']}/{b02['n_tasks']}; skill &gt; 0 {'contra a persistência em' if P else 'vs persistence on'} {b02['v032_tasks_skill_pos']}/{b02['n_tasks']}; E3 = {b02['E3_fraction']:.2f}.</div>
{table(['Modelo' if P else 'Model', 'Rank ' + ('global' if P else 'overall')] + [('Trilha ' if P else 'Track ') + c for c in cols] + ['#1', 'Top-3', 'Skill med.'], r2)}
<div class="page-break"></div><h3>{'Resultado da LEBRE v0.3.2 por tarefa' if P else 'LEBRE v0.3.2 per task'}</h3>
{table(['Trilha' if P else 'Track', 'Tarefa' if P else 'Task', 'NMSE', 'Skill', 'Rank', 'Melhor outro' if P else 'Best other', 'NMSE'], trows)}""")

        # ---------------------------------------------------------------- 8
        out.append(f"""<div class="page-break"></div><h1>8. {'Contabilidade Computacional e Envelope Embarcado' if P else 'Computational Accounting and Embedded Envelope'}</h1>
{table(['Componente' if P else 'Component', 'FP/' + ('passo' if P else 'step'), ('Escala' if P else 'Scaling')], [
    ('Predição + NLMS (base)' if P else 'Prediction + NLMS (base)', '≈ 6d + 13', 'O(d)'),
    ('Por átomo ativo (predição, NLMS)' if P else 'Per active atom (prediction, NLMS)', '6', 'O(|A|)'),
    ('Evidência CUSUM por átomo (1/2 passos)' if P else 'CUSUM evidence per atom (1 per 2 steps)', '≈ 4.5', 'O(|A|)'),
    ('Banco latente (3 polos + normalização)' if P else 'Latent bank (3 poles + normalisation)', '≈ 11', 'O(|P|)'),
    ('Triagem (2 sondagens)' if P else 'Screening (2 probes)', '8', 'O(1)'),
    ('Testes provisórios (1/2 passos)' if P else 'Provisional tests (1 per 2 steps)', '≈ 2 por candidato' if P else '≈ 2 per candidate', 'O(H + |P|)'),
    ('Decisões (1/10 passos)' if P else 'Decisions (1 per 10 steps)', '≈ 1–7', 'O(H + |P|)')])}
<div class="alert alert-warning">{'Não contados como FP: comparações de ponto flutuante na seleção top-k do dicionário (≈ p_dict comparações por reposição) e o uso de log (≈ 0,001 por passo). No I1–I14 (d = 5) a média fica em ' if P else
'Not counted as FP: floating-point comparisons in the top-k dictionary selection (≈ p_dict comparisons per refill) and log calls (≈ 0.001 per step). On I1–I14 (d = 5) the mean is '}{f(v.fp,1)} FP/{'passo, ≤ 100, mas a tarefa mais cara (I4) chega a' if P else 'step, ≤ 100, but the most expensive task (I4) reaches'} {N['T8']:.1f}. {'Com d = 10..50 o custo é O(d) (≈ 110–370 FP) e a memória (histórico de (L+1)·d amostras + escores de triagem) passa de 1 KB. O armazenamento em fp16 é uma convenção de contabilidade ainda não validada numericamente.' if P else
'With d = 10..50 the cost is O(d) (≈ 110–370 FP) and memory (history of (L+1)·d samples + screening scores) exceeds 1 KB. fp16 storage is an accounting convention not yet numerically validated.'}</div>""")

        # ---------------------------------------------------------------- 9
        lim = ([("Classe de modelos", "linear nos parâmetros; um estado latente de 1ª ordem; atrasos ≤ L = 32"),
                ("Dados reais horários", "a persistência trivial vence em X1–X3; faltam átomos autorregressivos do alvo"),
                ("Outliers de entrada", "sem proteção; um único registro errado domina o erro (X3)"),
                ("Busca com d alto", "a triagem rotativa leva ≈ dL/2 passos por ciclo; a descoberta é lenta com d ≥ 20"),
                ("Garantias", "exatas só sob hipóteses idealizadas; aproximadas no laço adaptativo; otimalidade do CUSUM não transferida"),
                ("Envelope embarcado", "≤ 100 FP e ≤ 1 KB apenas para d pequeno; hardware não validado"),
                ("Competitividade externa (BENCH-02)", "6ª de 24 modelos; decisão pré-registrada NOT_JUSTIFIED_EXTERNALLY; o IPNLMS (2002) vence as 6 condições FIR esparsas e o ARX/persistência vencem a previsão horária"),
                ("Passo de adaptação", "μ fixo e sem ganho proporcional por coeficiente; adaptação lenta em séries próximas de raiz unitária (hipótese)"),
                ("Comparadores ausentes", "DMA, alpha-investing, ARX com RIC e previsores profundos online (FSNet, OneNet)")] if P else
               [("Model class", "linear in the parameters; one first-order latent state; delays ≤ L = 32"),
                ("Hourly real data", "trivial persistence wins on X1–X3; target-autoregressive atoms are missing"),
                ("Input outliers", "unprotected; one erroneous record dominates the error (X3)"),
                ("High-d search", "rotating screening takes ≈ dL/2 steps per cycle; discovery is slow for d ≥ 20"),
                ("Guarantees", "exact only under idealised hypotheses; approximate in the adaptive loop; CUSUM optimality not transferred"),
                ("Embedded envelope", "≤ 100 FP and ≤ 1 KB only for small d; hardware not validated"),
                ("External competitiveness (BENCH-02)", "6th of 24 models; pre-registered decision NOT_JUSTIFIED_EXTERNALLY; IPNLMS (2002) wins all 6 sparse-FIR conditions and ARX/persistence win hourly forecasting"),
                ("Adaptation step", "fixed μ with no per-coefficient proportional gain; slow adaptation on near-unit-root series (hypothesis)"),
                ("Missing comparators", "DMA, alpha-investing, ARX with RIC and deep online forecasters (FSNet, OneNet)")])
        forb = (["novidade ou prioridade científica (NOVELTY_CLAIM_READY = NO)", "estado da arte em previsão de séries temporais",
                 "eficiência energética ou viabilidade em MCU a partir de contagem de FP", "garantias exatas de erro no laço adaptativo",
                 "substituição da LEBRE v0.1 canônica", "validação global ou abertura do M3"] if P else
                ["novelty or scientific priority (NOVELTY_CLAIM_READY = NO)", "state of the art in time-series forecasting",
                 "energy efficiency or MCU feasibility from FP counts", "exact error guarantees in the adaptive loop",
                 "replacement of canonical LEBRE v0.1", "global validation or opening of M3"])
        out.append(f"""<div class="page-break"></div><h1>9. {'Limites de Escopo e Reivindicações Proibidas' if P else 'Scope Limits and Forbidden Claims'}</h1>
{table(['Limite' if P else 'Limit', 'Descrição' if P else 'Description'], lim)}
<h2>{'Reivindicações proibidas' if P else 'Forbidden claims'}</h2><ul>{''.join(f'<li>{x}</li>' for x in forb)}</ul>""")

        # ---------------------------------------------------------------- 10
        D_, E_ = ("DERIVADO", "DE PROJETO") if P else ("DERIVED", "DESIGN")
        params = [("d", "—", "dimensão da tarefa" if P else "task dimension", "—"),
                  ("L", "32", "herdado da v0.2" if P else "inherited from v0.2", E_),
                  ("μ", "0.1", "desajuste μ/(2−μ) ≈ 5,3%" if P else "misadjustment μ/(2−μ) ≈ 5.3%", D_),
                  ("n_σ", "200", "memória da escala de ruído" if P else "noise-scale memory", E_),
                  ("α", "0.05", "erro familiar por episódio" if P else "family-wise error per episode", E_),
                  ("log(p_dict/α)", "8.2 (d=5) … 10.4 (d=50)", "Ville + Bonferroni", D_),
                  ("ARL, h", "6000, 8.70", "h = log ARL (Lorden)", D_),
                  ("T_idle, r", "500, 0.0174", "r = h/T_idle", D_ + " / " + E_),
                  ("ρ_rel", "1.0", "prior de informação unitária" if P else "unit-information prior", D_),
                  ("𝒫", "{0, 0.5, 0.8, 0.95}", "τ ≈ 1, 2, 5, 20", E_),
                  ("M_max", "4", "orçamento estrutural" if P else "structural budget", E_),
                  ("B_probe, H", "2, 4", "triagem / testes simultâneos" if P else "screening / concurrent tests", E_),
                  ("screen_w", "0.2", "só escolhe o que testar" if P else "only chooses what to test", E_),
                  ("decide / test / evidence", "10 / 2 / 2", "cadências (espera limitada)" if P else "cadences (bounded wait)", E_),
                  ("T_max", "200 " + ("testes" if P else "tests"), "futilidade (não afeta o erro tipo I)" if P else "futility (type-I unaffected)", E_),
                  ("κ, n_P", "0.1, 1000", "portão de excitação" if P else "excitation gate", E_),
                  ("n_warm", "20", "aquecimento (F6)" if P else "warm-up (F6)", E_),
                  ("R ≥ h/2", "—", "regra de substituição" if P else "replacement rule", E_),
                  ("σ̂² floor", "10⁻¹⁰ · " + ("pico" if P else "peak"), "robustez numérica" if P else "numerical robustness", E_)]
        out.append(f"""<div class="page-break"></div><h1>10. {'Matriz de Rastreabilidade de Parâmetros' if P else 'Parameter Traceability Matrix'}</h1>
{table(['Parâmetro' if P else 'Parameter', 'Valor' if P else 'Value', 'Origem / papel' if P else 'Origin / role', 'Status'], params)}
<p class="small">{'Nenhum parâmetro foi ajustado aos benchmarks de validação. Os valores da v0.3 foram fixados em 4 iterações de DEV (sementes 3301..3310); as correções F1–F6 vieram de testes de propriedades e de uma falha diagnosticada, e foram avaliadas em sementes novas.' if P else
'No parameter was tuned on the validation benchmarks. The v0.3 values were fixed in 4 DEV iterations (seeds 3301..3310); fixes F1–F6 came from property tests and one diagnosed failure, and were evaluated on fresh seeds.'}</p>""")

        # ---------------------------------------------------------------- 11
        adr = ([("ADR-301", "Toda decisão estrutural é um teste com erro controlado", "substitui EMAs de ganho e limiares ajustados à mão"),
                ("ADR-302", "Evidência em tempo de fluxo", "decimação de decisões não distorce escalas de tempo"),
                ("ADR-303", "Latente em forma de inovações + acionamento", "substitui RTRL; ~9 FP; explicável"),
                ("ADR-304", "Evidência auto-normalizada e equivariância de escala", "validade com caudas pesadas e heterocedasticidade"),
                ("ADR-305", "Silêncio não é evidência", "portão de excitação persistente"),
                ("ADR-306", "Estrutura paga aluguel", "aluguel MDL ponderado pela excitação"),
                ("ADR-307", "A triagem escolhe, o teste decide", "divisão temporal da amostra"),
                ("ADR-308", "Estado latente único e orçamento M_max", "limite de escopo herdado da v0.1"),
                ("ADR-309", "Estimadores de aquecimento por média amostral", "corrige o bloqueio τ ≈ 10¹³ da v0.3.1")] if P else
               [("ADR-301", "Every structural decision is a test with controlled error", "replaces gain EMAs and hand-tuned thresholds"),
                ("ADR-302", "Stream-time evidence", "decision decimation does not distort timescales"),
                ("ADR-303", "Innovations-form latent + drive", "replaces RTRL; ~9 FP; explainable"),
                ("ADR-304", "Self-normalised evidence and scale equivariance", "validity under heavy tails and heteroscedasticity"),
                ("ADR-305", "Silence is not evidence", "persistent-excitation gate"),
                ("ADR-306", "Structure pays rent", "excitation-weighted MDL rent"),
                ("ADR-307", "Screening chooses, the test decides", "temporal sample splitting"),
                ("ADR-308", "Single latent state and budget M_max", "scope limit inherited from v0.1"),
                ("ADR-309", "Sample-mean warm-up estimators", "fixes the τ ≈ 10¹³ blocking of v0.3.1")])
        refs = ["Anderson &amp; Moore (1979) <em>Optimal Filtering</em>", "Chen, Gu &amp; Hero (2009) Sparse LMS for system identification, ICASSP",
                "Benesty &amp; Gay (2002) An improved PNLMS algorithm, ICASSP", "de la Peña (1999) <em>Ann. Probab.</em> 27(1)",
                "Elsken, Metzen &amp; Hutter (2019) Neural Architecture Search: A Survey, <em>JMLR</em> 20",
                "Fahlman &amp; Lebiere (1990) The Cascade-Correlation Learning Architecture, NIPS 2",
                "Foster &amp; George (1994) The Risk Inflation Criterion, <em>Ann. Statist.</em> 22(4)",
                "Gomes et al. (2018) Adaptive random forests for data stream regression, ESANN",
                "Howard, Ramdas, McAuliffe &amp; Sekhon (2020) <em>Probability Surveys</em>; (2021) <em>Ann. Statist.</em> 49(2)",
                "Ikonomovska, Gama &amp; Džeroski (2011) Learning model trees from evolving data streams, <em>DMKD</em>",
                "Ioannou &amp; Sun (1996) <em>Robust Adaptive Control</em>", "ISO/IEC/IEEE 42010:2022 Architecture description",
                "Laird (2012) <em>The Soar Cognitive Architecture</em>", "Ljung (1999) <em>System Identification</em>, 2nd ed.",
                "Lorden (1971) <em>Ann. Math. Statist.</em> 42; Moustakides (1986) <em>Ann. Statist.</em> 14", "Page (1954) Continuous inspection schemes, <em>Biometrika</em>",
                "Pham et al. (2023) FSNet, ICLR; Wen et al. (2023) OneNet, NeurIPS", "Raftery, Kárný &amp; Ettler (2010) Dynamic Model Averaging, <em>Technometrics</em> 52",
                "Schoukens &amp; Noël (2017) Three benchmarks in nonlinear system identification, IFAC", "Shin, Ramdas &amp; Rinaldo (2023) E-detectors, <em>NEJSDS</em>",
                "Slock (1993) <em>IEEE TSP</em> 41", "Sutton (1990) Dyna; Sutton et al. (2011) Horde, AAMAS", "Wahlberg (1991) <em>IEEE TAC</em> 36",
                "Zhou, Foster, Stine &amp; Ungar (2006) Streamwise feature selection, <em>JMLR</em> 7", "Zhou et al. (2021) Informer / ETT datasets, AAAI"]
        dec = b02["decision"] if b02 else "PENDING"
        out.append(f"""<div class="page-break"></div><h1>11. {'Registros de Decisão Arquitetural e Decisão Final' if P else 'Architectural Decision Records and Final Decision'}</h1>
{table(['ADR', 'Decisão' if P else 'Decision', 'Consequência' if P else 'Consequence'], adr)}
<h2>{'Decisão final' if P else 'Final decision'}</h2>
<div class="verdict {'verdict-warn' if dec != 'JUSTIFIED_EXTERNALLY' else ''}">ARCHITECTURE_CLASSIFICATION = PRINCIPLED_ONLINE_STRUCTURAL_LEARNING_ARCHITECTURE<br>
STATUS = RESEARCH_SPECIFICATION_NON_CANONICAL<br>INTERNAL_EVIDENCE = CONFIRMED (H1'–H4', Holm)<br>
EXTERNAL_EVIDENCE = {dec}<br>CANONICAL_REFERENCE = LEBRE v0.1 (FROZEN_WITH_SCOPE_LIMITS)<br>NOVELTY_CLAIM_READY = NO · M3 = UNOPENED</div>
<h2>{'Referências principais' if P else 'Key references'}</h2><ul class="small" style="columns:2;column-gap:18px">{''.join(f'<li>{r}</li>' for r in refs)}</ul>""")
        return out
    return S


# ============================================================================ packs
TEXT = {
    "pt": dict(html_lang="pt-BR", badge="Especificação de Pesquisa v0.3.2",
               title="Especificação da Arquitetura LEBRE v0.3.2",
               subtitle="Evolução fundamentada: decisões estruturais estatisticamente válidas sob orçamento computacional",
               expansion="<strong>Expansão canônica:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br><strong>Linhagem:</strong> LEBRE v0.1 (Track B) → ramo v0.2 → v0.3 → v0.3.1 → <strong>v0.3.2</strong>",
               meta=[("Status da arquitetura", "Especificação de pesquisa — NÃO canônica"),
                     ("Classificação", "PRINCIPLED_ONLINE_STRUCTURAL_LEARNING_ARCHITECTURE"),
                     ("Prontidão para novidade", "NOVELTY_CLAIM_READY = NO"),
                     ("Fronteira M3", "UNOPENED (estado latente único)")],
               footer_l="Projeto de Pesquisa Codinome Lebre", footer_r="Setembro de 2026 • Documento v0.3.2-RESEARCH",
               v01_header="Especificação da Arquitetura LEBRE v0.1 — Documento de Referência",
               v01_status="Status: FROZEN_WITH_SCOPE_LIMITS",
               v01_footer="Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.1",
               page_header="Especificação da Arquitetura LEBRE v0.3.2 — Especificação de Pesquisa",
               page_status="Status: RESEARCH_SPECIFICATION_NON_CANONICAL", page_word='"Página "',
               page_footer="Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.3.2",
               diag=DIAG["pt"], sections=_sections("pt")),
    "en": dict(html_lang="en", badge="Research Specification v0.3.2",
               title="LEBRE v0.3.2 Architecture Specification",
               subtitle="Principled evolution: statistically valid structural decisions under a computational budget",
               expansion="<strong>Canonical expansion:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br><strong>Lineage:</strong> LEBRE v0.1 (Track B) → v0.2 branch → v0.3 → v0.3.1 → <strong>v0.3.2</strong>",
               meta=[("Architecture status", "Research specification — NON-canonical"),
                     ("Classification", "PRINCIPLED_ONLINE_STRUCTURAL_LEARNING_ARCHITECTURE"),
                     ("Novelty readiness", "NOVELTY_CLAIM_READY = NO"),
                     ("M3 boundary", "UNOPENED (single latent state)")],
               footer_l="Codinome Lebre Research Project", footer_r="September 2026 • Document v0.3.2-RESEARCH",
               v01_header="Especificação da Arquitetura LEBRE v0.1 — Documento de Referência",
               v01_status="Status: FROZEN_WITH_SCOPE_LIMITS",
               v01_footer="Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.1",
               page_header="LEBRE v0.3.2 Architecture Specification — Research Specification",
               page_status="Status: RESEARCH_SPECIFICATION_NON_CANONICAL", page_word='"Page "',
               page_footer="Codinome Lebre Research Project • Architecture Specification v0.3.2",
               diag=DIAG["en"], sections=_sections("en")),
}
