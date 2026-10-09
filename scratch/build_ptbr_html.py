#!/usr/bin/env python3
"""
Generate docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html
Uses raw string template r'''...''' to preserve all LaTeX backslashes perfectly.
Uses \\( ... \\) for inline math and $$ ... $$ for block math to avoid any conflict with literal $ signs.
"""
import base64
from pathlib import Path

WORKSPACE = Path(r".")
LOGO_PATH = WORKSPACE / "logo" / "LEBRE Logo.png"
DIAGRAMS_DIR = WORKSPACE / "docs" / "architecture" / "assets" / "diagrams"
OUT_FILE = WORKSPACE / "docs" / "architecture" / "pdf_source" / "LEBRE_CONDENSED_PTBR.html"

with open(LOGO_PATH, "rb") as f:
    LOGO_B64 = base64.b64encode(f.read()).decode("ascii")

def read_svg(name):
    svg_file = DIAGRAMS_DIR / f"{name}.svg"
    with open(svg_file, "r", encoding="utf-8") as f:
        c = f.read()
    if "<?xml" in c:
        c = c.split("?>", 1)[1].strip()
    return c

svg_d1 = read_svg("lebre_high_level_architecture")
svg_d2 = read_svg("lebre_lifecycle")
svg_d3 = read_svg("lebre_data_control_flow")
svg_d4 = read_svg("lebre_shadow_probation_ptbr")
svg_d5 = read_svg("lebre_quiescent_retention")
svg_d6 = read_svg("lebre_resource_elasticity")
svg_d7 = read_svg("lebre_v01_scope")
svg_d8 = read_svg("lebre_prequential_cycle")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Especificação da Arquitetura LEBRE v0.1 — Referência Condensada</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '\\(', right: '\\)', display: false},
            {left: '\\[', right: '\\]', display: true}
        ],
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "svg"]
    });
});
</script>
<style>
@page {
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
    @top-left {
        content: "Especificação da Arquitetura LEBRE v0.1 — Documento de Referência";
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        color: #64748b;
        font-weight: 500;
    }
    @top-right {
        content: "Status: FROZEN_WITH_SCOPE_LIMITS";
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        color: #0284c7;
        font-weight: 600;
    }
    @bottom-left {
        content: "Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.1";
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        color: #94a3b8;
    }
    @bottom-right {
        content: "Página " counter(page);
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        font-weight: 700;
        color: #334155;
    }
}

@page:first {
    margin: 0;
    @top-left { content: none; }
    @top-right { content: none; }
    @bottom-left { content: none; }
    @bottom-right { content: none; }
}

* {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}

body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.48;
    font-size: 9pt;
    margin: 0;
    padding: 0;
}

.cover-page {
    page-break-after: always;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 50px 45px 35px 45px;
    background: #ffffff;
    color: #0f172a;
    border-top: 6px solid #0284c7;
    border-bottom: 2px solid #cbd5e1;
}

.cover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 20px;
}

.cover-logo-panel {
    background: #ffffff;
    padding: 6px 12px;
    display: flex;
    align-items: center;
}

.cover-logo {
    max-width: 270px;
    height: auto;
}

.cover-badge {
    background: #f0f9ff;
    border: 1.5px solid #0284c7;
    color: #0369a1;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.cover-main {
    margin-top: 25px;
}

.cover-title {
    font-size: 26pt;
    font-weight: 800;
    letter-spacing: -0.025em;
    line-height: 1.15;
    margin: 0 0 8px 0;
    color: #0f172a;
}

.cover-subtitle {
    font-size: 13.5pt;
    font-weight: 500;
    color: #475569;
    margin: 0 0 20px 0;
    line-height: 1.35;
}

.cover-expansion {
    font-size: 10pt;
    color: #0369a1;
    font-weight: 600;
    margin-bottom: 25px;
    padding: 12px 18px;
    background: #f0f9ff;
    border-left: 4px solid #0284c7;
    border-radius: 0 8px 8px 0;
    border-top: 1px solid #e0f2fe;
    border-right: 1px solid #e0f2fe;
    border-bottom: 1px solid #e0f2fe;
}

.cover-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 15px;
}

.cover-meta-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    padding: 12px 16px;
    border-radius: 6px;
}

.cover-meta-label {
    font-size: 7.2pt;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
    font-weight: 600;
}

.cover-meta-value {
    font-size: 8.5pt;
    font-weight: 700;
    color: #0f172a;
}

.cover-footer {
    border-top: 1px solid #e2e8f0;
    padding-top: 15px;
    font-size: 7.8pt;
    color: #64748b;
    display: flex;
    justify-content: space-between;
}

.page-break {
    page-break-before: always;
}

.no-break {
    page-break-inside: avoid;
    break-inside: avoid;
}

h1 {
    font-size: 15pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 4px;
    margin-top: 20px;
    margin-bottom: 10px;
    letter-spacing: -0.01em;
}

h2 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #1e293b;
    margin-top: 16px;
    margin-bottom: 6px;
    border-left: 3px solid #0ea5e9;
    padding-left: 8px;
}

h3 {
    font-size: 9.5pt;
    font-weight: 600;
    color: #334155;
    margin-top: 12px;
    margin-bottom: 4px;
}

p {
    margin: 0 0 8px 0;
    text-align: justify;
}

ul, ol {
    margin: 0 0 8px 0;
    padding-left: 18px;
}

li {
    margin-bottom: 3px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 14px 0;
    font-size: 7.8pt;
}

th, td {
    padding: 5px 7px;
    text-align: left;
    border: 1px solid #cbd5e1;
}

th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

.highlight-row td {
    background-color: #f0fdf4 !important;
    font-weight: 600;
}

.alert {
    padding: 8px 12px;
    border-radius: 5px;
    margin: 10px 0;
    font-size: 8pt;
    line-height: 1.4;
}

.alert-info {
    background-color: #f0f9ff;
    border-left: 4px solid #0284c7;
    color: #0369a1;
}

.alert-warning {
    background-color: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
}

.alert-danger {
    background-color: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #b91c1c;
}

.diagram-container {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px;
    margin: 10px 0 14px 0;
    text-align: center;
    page-break-inside: avoid;
    break-inside: avoid;
}

.diagram-container svg {
    max-width: 100%;
    max-height: 380px;
    height: auto;
    display: block;
    margin: 0 auto;
}

.diagram-caption {
    font-size: 7.5pt;
    color: #475569;
    margin-top: 6px;
    font-style: italic;
    text-align: center;
}

.math-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 3px solid #3b82f6;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 8.5pt;
    border-radius: 4px;
}

.badge {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 6.8pt;
    font-weight: 700;
    text-transform: uppercase;
}

.badge-blue { background: #dbeafe; color: #1d4ed8; }
.badge-green { background: #dcfce7; color: #15803d; }
.badge-amber { background: #fef3c7; color: #b45309; }
.badge-red { background: #fee2e2; color: #b91c1c; }

.toc-list {
    list-style-type: none;
    padding: 0;
    margin: 8px 0;
}

.toc-item {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 8.5pt;
}

.toc-title {
    font-weight: 600;
    color: #1e293b;
}

.toc-page {
    color: #0284c7;
    font-weight: 700;
}
</style>
</head>
<body>

<!-- CAPA -->
<div class="cover-page">
    <div class="cover-header">
        <div class="cover-logo-panel">
            <img class="cover-logo" src="data:image/png;base64,<!-- LOGO_B64 -->" alt="Logo da Arquitetura LEBRE">
        </div>
        <div class="cover-badge">Especificação Formal v0.1</div>
    </div>
    
    <div class="cover-main">
        <div class="cover-title">Especificação da Arquitetura LEBRE</div>
        <div class="cover-subtitle">Guia de Referência Condensado & Visão Geral da Arquitetura do Sistema</div>
        
        <div class="cover-expansion">
            <strong>Expansão Canônica:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br>
            <strong>Proveniência Histórica:</strong> Track B Single-State Organization (Codinome Lebre)
        </div>
        
        <div class="cover-meta-grid">
            <div class="cover-meta-card">
                <div class="cover-meta-label">Status da Arquitetura</div>
                <div class="cover-meta-value">Frozen Reference Specification with Scope Limits</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Classificação de Evidência</div>
                <div class="cover-meta-value">VALIDATED_WITH_SCOPE_LIMITS</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Prontidão para Ineditismo</div>
                <div class="cover-meta-value">NOVELTY_CLAIM_READY = NO</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Fronteira do Marco M3</div>
                <div class="cover-meta-value">UNOPENED (Fronteira Multi-State Reservada)</div>
            </div>
        </div>
    </div>
    
    <div class="cover-footer">
        <div>Projeto de Pesquisa: Projeto de Pesquisa Codinome Lebre</div>
        <div>Data de Congelamento: Setembro de 2026 • Versão do Documento 0.1-CONDENSED</div>
    </div>
</div>

<!-- SEÇÃO 1: SUMÁRIO EXECUTIVO & ÍNDICE -->
<div class="page-break"></div>
<h1>1. Sumário Executivo & Guia do Documento</h1>

<p>A arquitetura <strong>LEBRE</strong> (<em>Lifecycle-governed Evidence-Based Resource Evolution</em>) formaliza um sistema de aprendizado contínuo em fluxo (streaming) que aloca, avalia e desaloca dinamicamente representações de estado interno sob orçamentos computacionais rígidos. Derivada de extensas investigações empíricas nos benchmarks sintéticos A1–A8 e de identificação de sistemas físicos reais B1–B5, a LEBRE resolve a tensão fundamental entre retenção de memória persistente e frugalidade computacional agressiva em dados temporais contínuos.</p>

<div class="alert alert-info">
<strong>Escopo Científico & Status:</strong> Este documento representa uma edição de referência condensada da especificação formal da arquitetura LEBRE v0.1. Todos os valores empíricos, formulações matemáticas e limiares de controle estão congelados sob a classificação <code>VALIDATED_WITH_SCOPE_LIMITS</code>. O Marco M3 permanece <code>UNOPENED</code>, e quaisquer reivindicações de ineditismo permanecem estritamente retidas (<code>NOVELTY_CLAIM_READY = NO</code>).
</div>

<h2>Sumário / Índice Geral</h2>
<ul class="toc-list">
    <li class="toc-item"><span class="toc-title">1. Sumário Executivo & Guia do Documento</span><span class="toc-page">Página 2</span></li>
    <li class="toc-item"><span class="toc-title">2. Identidade Arquitetural & Princípios Centrais</span><span class="toc-page">Página 3</span></li>
    <li class="toc-item"><span class="toc-title">3. Formulação Matemática & Motor de Inferência Causal</span><span class="toc-page">Página 4</span></li>
    <li class="toc-item"><span class="toc-title">4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados</span><span class="toc-page">Página 6</span></li>
    <li class="toc-item"><span class="toc-title">5. Retenção em Duas Escalas de Tempo & Preservação em Quiescência</span><span class="toc-page">Página 7</span></li>
    <li class="toc-item"><span class="toc-title">6. Galeria de Diagramas Arquiteturais Canônicos (D1–D8)</span><span class="toc-page">Página 8</span></li>
    <li class="toc-item"><span class="toc-title">7. Suíte de Validação Empírica (Benchmarks A1–A8 & B1–B5)</span><span class="toc-page">Página 16</span></li>
    <li class="toc-item"><span class="toc-title">8. Contabilidade Computacional, Semântica de FLOPs Médios & Limites Embarcados</span><span class="toc-page">Página 18</span></li>
    <li class="toc-item"><span class="toc-title">9. Limites de Escopo Arquitetural & Fronteira Congelada</span><span class="toc-page">Página 19</span></li>
    <li class="toc-item"><span class="toc-title">10. Matriz de Rastreabilidade de Parâmetros e Constantes</span><span class="toc-page">Página 20</span></li>
    <li class="toc-item"><span class="toc-title">11. Registros de Decisão Arquitetural (ADRs) & Decisão Final</span><span class="toc-page">Página 21</span></li>
</ul>

<h2>Convenções do Documento</h2>
<p>Nesta referência, adota-se rigorosa notação matemática padrão: grandezas vetoriais são expressas em negrito (\(\mathbf{x}_t \in \mathbb{R}^D\)), grandezas escalares em itálico (\(y_t, s_t\)), e o índice temporal discreto como subscrito \(t\). A complexidade operacional é quantificada em operações de ponto flutuante formais por passo (FLOPs/passo). Na avaliação de conformidade ao regime R2-FLOP, os números denotam estritamente o <em>rendimento médio por passo</em> ao longo das trajetórias de benchmark, diferenciando o custo operacional médio dos picos transitórios de avaliação.</p>

<!-- SEÇÃO 2: IDENTIDADE ARQUITETURAL -->
<div class="page-break"></div>
<h1>2. Identidade Arquitetural & Princípios Centrais</h1>

<p>A LEBRE estabelece um paradigma estrutural governado por recursos no qual a capacidade de rede é tratada como um recurso econômico finito que precisa justificar seu custo computacional a cada instante temporal. O sistema fundamenta-se em quatro princípios reitores:</p>

<h3>1. Parsimônia com Prioridade Linear (Linear-First)</h3>
<p>Nenhuma capacidade estrutural não linear ou recorrente é instanciada enquanto persistir a capacidade de adaptação da linha de base linear esparsa. Em regressão streaming e identificação de sistemas, correlações lineares estáticas explicam grande parte da variância observada. Nos regimes lineares avaliados, a alocação de estado recorrente não foi acionada quando a linha de base linear se mostrou suficiente.</p>

<h3>2. Provação Isolada em Modo Sombra (Shadow Mode)</h3>
<p>Unidades estruturais provisionais são desacopladas das predições ativas do modelo durante sua fase de treinamento inicial. Candidatos recém-nascidos aprendem em modo sombra desacoplado por um horizonte fixo de provação (\(T_{\text{prob}} = 50\) passos). Apenas candidatos que demonstrem redução contrafactual de erro estatisticamente verificada (\(G_{\text{cand}} > 0,05\)) são promovidos à inferência ativa.</p>

<h3>3. Contabilidade de Relevância em Duas Escalas de Tempo</h3>
<p>A energia instantânea do sinal é inadequada como critério de retenção em ambientes não estacionários orientados a eventos. A LEBRE separa a escala de tempo da atividade instantânea do estado da escala de tempo da relevância estrutural acumulada (\(U_{\text{ret}}\), fator de decaimento \(\alpha_{\text{slow}} = 0,005\), meia-vida \(\tau \approx 140\) passos). Isso desacopla a preservação de memória de períodos de silêncio transitório de entrada, preservando a retenção através de longos intervalos quiescentes de Poisson observados nos benchmarks.</p>

<h3>4. Elasticidade de Recursos Delimitada</h3>
<p>Nos benchmarks avaliados, a LEBRE apresentou pegada média observada de 440,0 bytes de estado persistente do modelo, sob o teto R2-MEM de 1024 bytes (esse valor não representa o consumo total de RAM de uma implementação em hardware). O custo computacional médio observado permaneceu dentro do limiar R2-FLOP de 100 FLOPs/passo. Matrizes de estruturas desalojadas são imediatamente removidas dos grafos de execução e sua memória é liberada.</p>

<table class="no-break">
    <thead>
        <tr>
            <th>Princípio</th>
            <th>Mecanismo de Governança</th>
            <th>Invariante Empírico Estabelecido</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Parsimônia Linear-First</strong></td>
            <td>Gatilho de nascimento em dois estágios (\(E_{\text{linear}} > \theta_{\text{birth}}\))</td>
            <td>Zero estados recorrentes gerados em tarefas puramente lineares (Tarefas A1, A2)</td>
        </tr>
        <tr>
            <td><strong>Provação em Sombra</strong></td>
            <td>Passo forward desacoplado (\(g_p = 0,0\)) + ganho contrafactual</td>
            <td>Zero perturbação na inferência ativa; picos de gradiente instáveis isolados de \(\hat{y}_t\)</td>
        </tr>
        <tr>
            <td><strong>Retenção Quiescente</strong></td>
            <td>Filtro lento em duas escalas (\(U_{\text{ret}}\)) + desalojamento com portão duplo</td>
            <td>&gt;99% de sobrevivência em intervalos de silêncio Poisson de mais de 200 passos (A5, A7)</td>
        </tr>
        <tr>
            <td><strong>Elasticidade de Recursos</strong></td>
            <td>Desalojamento com histerese + desalocação física de memória</td>
            <td>Contração dinâmica de \(\approx 92\) FLOPs/passo de volta para a linha de base \(\approx 40\) FLOPs/passo</td>
        </tr>
    </tbody>
</table>

<!-- SEÇÃO 3: FORMULAÇÃO MATEMÁTICA -->
<div class="page-break"></div>
<h1>3. Formulação Matemática & Motor de Inferência Causal</h1>

<p>O ciclo de execução da LEBRE opera sob um protocolo prequencial causal estrito: no passo temporal \(t\), o sistema recebe a observação \(\mathbf{x}_t\), emite a predição causal \(\hat{y}_t\), e somente em seguida recebe o alvo escalar real \(y_t\).</p>

<h2>3.1 Observação em Fluxo & Normalização Online</h2>
<p>Seja \(\mathbf{x}_t = [x_{t,1}, x_{t,2}, \dots, x_{t,D}]^\top \in \mathbb{R}^D\) o vetor de observação temporal. A normalização online causal atualiza médias e variâncias sem passos retrospectivos:</p>
<div class="math-box">
$$\mu_{t,i} = (1 - \alpha_{\text{norm}}) \mu_{t-1,i} + \alpha_{\text{norm}} x_{t,i}, \quad \sigma^2_{t,i} = (1 - \alpha_{\text{norm}}) \sigma^2_{t-1,i} + \alpha_{\text{norm}} (x_{t,i} - \mu_{t,i})^2$$
$$\tilde{x}_{t,i} = \frac{x_{t,i} - \mu_{t,i}}{\sqrt{\sigma^2_{t,i} + \epsilon_{\text{norm}}}}$$
</div>

<h2>3.2 Inferência Causal em Duas Camadas</h2>
<p>A predição global do modelo \(\hat{y}_t\) é a soma da linha de base linear esparsa ativa \(y_{\text{base},t}\) e da componente recorrente escalar ativa \(y_{\text{rec},t}\) (\(N \le 1\)):</p>
<div class="math-box">
$$y_{\text{base},t} = \mathbf{w}_{\text{base}}^\top \tilde{\mathbf{x}}_t + b_{\text{base}}$$
$$s_t = \tanh\left(\lambda s_{t-1} + \mathbf{w}_{\text{in}}^\top \tilde{\mathbf{x}}_t + b_s\right), \quad y_{\text{rec},t} = w_s s_t$$
$$\hat{y}_t = y_{\text{base},t} + y_{\text{rec},t}$$
</div>

<h2>3.3 Perda Prequencial & Decomposição do Erro</h2>
<p>Após a revelação do alvo ambiental \(y_t\), o sistema calcula o erro global de predição \(e_t\) e o erro contrafactual da base linear \(e_{\text{base},t}\):</p>
<div class="math-box">
$$e_t = y_t - \hat{y}_t, \quad e_{\text{base},t} = y_t - y_{\text{base},t}$$
$$\mathcal{L}_t = \frac{1}{2} e_t^2, \quad \Delta \mathcal{L}_t = \frac{1}{2} e_{\text{base},t}^2 - \frac{1}{2} e_t^2$$
</div>
<p>Valores estritamente positivos de \(\Delta \mathcal{L}_t\) confirmam que a estrutura recorrente fornece utilidade preditiva genuína além da capacidade da projeção linear.</p>

<h2>3.4 Dinâmica do Real-Time Recurrent Learning (RTRL) Online</h2>
<p>Como o estado recorrente é escalar (\(N \le 1\)), o gradiente do estado oculto em relação aos parâmetros internos é rastreado em tempo real com complexidade \(\mathcal{O}(1)\):</p>
<div class="math-box">
$$p_t = \frac{\partial s_t}{\partial \lambda} = (1 - s_t^2) \left( s_{t-1} + \lambda p_{t-1} \right)$$
$$\mathbf{q}_t = \frac{\partial s_t}{\partial \mathbf{w}_{\text{in}}} = (1 - s_t^2) \left( \tilde{\mathbf{x}}_t + \lambda \mathbf{q}_{t-1} \right)$$
</div>
<p>As atualizações online dos parâmetros são calculadas por gradiente descendente estocástico causal com decaimento de pesos:</p>
<div class="math-box">
$$\Delta w_s = \eta_s e_t s_t, \quad \Delta \lambda = \eta_\lambda e_t w_s p_t, \quad \Delta \mathbf{w}_{\text{in}} = \eta_{\text{in}} e_t w_s \mathbf{q}_t$$
$$\Delta \mathbf{w}_{\text{base}} = \eta_{\text{base}} e_t \tilde{\mathbf{x}}_t - \gamma_{\text{decay}} \mathbf{w}_{\text{base}}$$
</div>

<!-- SEÇÃO 4: CICLO DE VIDA ESTRUTURAL -->
<div class="page-break"></div>
<h1>4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados</h1>

<p>Todo objeto estrutural na LEBRE progride por um ciclo de vida rigorosamente delimitado em cinco estados: <strong>DORMANT</strong>, <strong>PROVISIONAL</strong>, <strong>ACTIVE</strong>, <strong>MATURE</strong> e <strong>EVICTED</strong>. As transições são governadas por acumuladores objetivos de evidência.</p>

<table class="no-break">
    <thead>
        <tr>
            <th>Estado</th>
            <th>Papel Operacional</th>
            <th>Impacto na Predição</th>
            <th>Custo de Computação / Memória</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>DORMANT</strong></td>
            <td>Slot latente de candidato; não alocado</td>
            <td>Zero (0,0)</td>
            <td>0 FLOPs/passo; 0 Bytes de RAM</td>
        </tr>
        <tr>
            <td><strong>PROVISIONAL</strong></td>
            <td>Candidato em sombra sob provação</td>
            <td>Estritamente isolado (\(g_p = 0,0\))</td>
            <td>Forward + RTRL local (\(\approx 52\) FLOPs); buffers de sombra</td>
        </tr>
        <tr>
            <td><strong>ACTIVE</strong></td>
            <td>Unidade promovida; conectada a \(\hat{y}_t\)</td>
            <td>Contribuição plena (\(y_{\text{rec},t} = w_s s_t\))</td>
            <td>Inferência online plena + RTRL; memória de estado persistente</td>
        </tr>
        <tr>
            <td><strong>MATURE</strong></td>
            <td>Unidade ativa com idade \(\ge \tau_{\text{mature}}\) (100 passos)</td>
            <td>Contribuição plena; relevância lenta ativa</td>
            <td>Inferência plena + contabilidade de relevância em duas escalas</td>
        </tr>
        <tr>
            <td><strong>EVICTED</strong></td>
            <td>Unidade extirpada; memória desalocada</td>
            <td>Removido; slot retorna a Dormant</td>
            <td>0 FLOPs; memória física liberada imediatamente</td>
        </tr>
    </tbody>
</table>

<h2>4.1 Gatilho de Nascimento & Parsimônia Linear-First</h2>
<p>O gatilho de nascimento avalia se o erro residual não pode ser explicado pela projeção linear. O nascimento é iniciado apenas quando a média móvel exponencial do erro residual linear excede o limiar \(\theta_{\text{birth}} = 0,15\) por \(N_{\text{birth}} = 30\) passos consecutivos:</p>
<div class="math-box">
$$\bar{E}_{\text{linear},t} = (1 - \alpha_E) \bar{E}_{\text{linear},t-1} + \alpha_E e_{\text{base},t}^2$$
$$\text{Disparar Nascimento se: } \bar{E}_{\text{linear},t} > \theta_{\text{birth}} \quad \forall \tau \in [t - N_{\text{birth}}, t]$$
</div>

<h2>4.2 Protocolo de Provação em Sombra & Promoção</h2>
<p>Ao nascer, um estado candidato \(s_{p,t}\) é instanciado em modo sombra. Seus parâmetros \(\mathbf{w}_{p,\text{in}}\), \(\lambda_p\) e \(w_p\) são atualizados por gradientes locais, mas sua saída permanece desligada (\(g_p = 0,0\)). O erro contrafactual é registrado durante o horizonte \(T_{\text{prob}} = 50\) passos:</p>
<div class="math-box">
$$e_{p,t} = y_t - (y_{\text{base},t} + w_p s_{p,t})$$
$$G_{\text{cand}} = 1 - \frac{\sum_{k=1}^{T_{\text{prob}}} e_{p,t-k}^2}{\sum_{k=1}^{T_{\text{prob}}} e_{\text{base},t-k}^2}$$
$$\text{Promover se: } G_{\text{cand}} > \theta_{\text{promote}} \quad (\theta_{\text{promote}} = 0,05)$$
</div>
<p>Se \(G_{\text{cand}} \le \theta_{\text{promote}}\), o candidato é descartado e seus buffers são liberados sem terem perturbado a inferência ativa.</p>

<!-- SEÇÃO 5: RETENÇÃO EM DUAS ESCALAS -->
<div class="page-break"></div>
<h1>5. Retenção em Duas Escalas & Memória em Quiescência</h1>

<p>Um modo de falha crítico em sistemas orientados por utilidade ingênua é a expulsão prematura de memória durante intervalos quiescentes entre rajadas. Quando a entrada em fluxo silencia (\(x_t \approx 0\)), o estado oculto decai para zero (\(s_t \to 0\)). Métricas ingênuas de sensibilidade (\(|e_t w_s s_t|\)) colapsam, disparando o desalojamento indevido de memória estrutural vital.</p>

<h2>5.1 Formulação Matemática em Duas Escalas de Tempo</h2>
<p>A LEBRE desacopla a dinâmica operacional rápida do crédito estrutural lento através de um filtro de relevância em duas escalas:</p>
<div class="math-box">
$$C_t = |e_t w_s s_t| + \kappa |w_s| \sigma_h$$
$$U_{\text{ret},t} = (1 - \alpha_{\text{slow}}) U_{\text{ret},t-1} + \alpha_{\text{slow}} C_t \quad (\alpha_{\text{slow}} = 0,005, \; \tau \approx 140 \text{ passos})$$
</div>
<p>Simultaneamente, um <strong>acumulador de obsolescência positiva</strong> avalia se o ambiente realizou uma transição efetiva que tornou a recorrência desnecessária:</p>
<div class="math-box">
$$O_{\text{obs},t} = \text{clip}\left( O_{\text{obs},t-1} + m_{\text{obs}} \cdot \mathbb{I}_{\{\Delta \mathcal{L}_t \le 0\}} - d_{\text{obs}} \cdot \mathbb{I}_{\{\Delta \mathcal{L}_t > 0\}}, 0.0, 1.0 \right)$$
</div>

<h2>5.2 Desalojamento por Histerese de Portão Duplo & A Assimetria 300:1</h2>
<p>O desalojamento exige evidência inequívoca de obsolescência persistente. A estrutura só é extirpada se ambas as condições forem satisfeitas simultaneamente por \(N_{\text{pat}} = 30\) passos consecutivos:</p>
<div class="math-box">
$$\text{Desalojar se: } \left( U_{\text{ret},t} < \theta_{\text{ret}} \right) \;\wedge\; \left( O_{\text{obs},t} > \theta_{\text{obs}} \right) \quad \forall \tau \in [t - N_{\text{pat}}, t]$$
$$\theta_{\text{ret}} = 0,02, \quad \theta_{\text{obs}} = 0,80, \quad N_{\text{pat}} = 30$$
</div>

<div class="alert alert-warning">
<strong>Esclarecimento de Auditoria (Correção G):</strong> A <strong>assimetria de 300:1</strong> é uma <em>razão empírica de custos</em> (a penalidade severa do arrependimento por falso desalojamento vs. a sobrecarga modesta de reter um estado escalar dormente), e não um multiplicador literal no código-fonte. A arquitetura implementa essa assimetria conservadora através do contador de paciência de 30 passos e do limiar duplo (\(U_{\text{ret}} < 0,02\) E \(O_{\text{obs}} > 0,80\)).
</div>

<table class="no-break">
    <thead>
        <tr>
            <th>Cenário Operacional</th>
            <th>\(|s_t|\) Instantâneo</th>
            <th>Utilidade Lenta \(U_{\text{ret}}\)</th>
            <th>Obsolescência \(O_{\text{obs}}\)</th>
            <th>Ação da LEBRE</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Rajada Ativa de Eventos</td>
            <td>Alta (&gt; 0,5)</td>
            <td>Alta (&gt; 0,2)</td>
            <td>Baixa (&lt; 0,1)</td>
            <td><strong>Reter &amp; Atualizar Pesos</strong></td>
        </tr>
        <tr>
            <td>Silêncio Poisson (t=50)</td>
            <td>Zero (&lt; 0,01)</td>
            <td>Preservada (&gt; 0,08)</td>
            <td>Neutra (&lt; 0,3)</td>
            <td><strong>Reter Memória (Protegida)</strong></td>
        </tr>
        <tr>
            <td>Silêncio Poisson (t=200)</td>
            <td>Zero (&lt; 0,01)</td>
            <td>Marginal (&gt; 0,02)</td>
            <td>Moderada (&lt; 0,6)</td>
            <td><strong>Reter Memória (Portão Fechado)</strong></td>
        </tr>
        <tr>
            <td>Mudança de Regime Confirmada</td>
            <td>Zero</td>
            <td>Esgotada (&lt; 0,02)</td>
            <td>Saturada (&gt; 0,80)</td>
            <td><strong>Desalojar com Segurança após 30 passos</strong></td>
        </tr>
    </tbody>
</table>

<!-- SEÇÃO 6: GALERIA DE DIAGRAMAS CANÔNICOS -->
<div class="page-break"></div>
<h1>6. Galeria de Diagramas Arquiteturais Canônicos</h1>

<p>Esta seção apresenta os oito diagramas arquiteturais canônicos (<strong>D1</strong> a <strong>D8</strong>) que constituem a especificação visual formal da LEBRE v0.1.</p>

<h2>D1. Arquitetura de Alto Nível & Fluxo de Informação</h2>
<div class="diagram-container">
<!-- SVG_D1 -->
<div class="diagram-caption">Figura D1: Fluxo de dados prequencial completo e laços de controle de ciclo de vida pós-alvo.</div>
</div>
<p>A Figura D1 detalha o fluxo físico de informação desacoplado: observação temporal causal, inferência aditiva em duas camadas (\(\hat{y}_t = y_{\text{base},t} + y_{\text{rec},t}\)), revelação de erro prequencial, exploração isolada em sombra e o controlador central de ciclo de vida.</p>

<div class="page-break"></div>
<h2>D2. Máquina de Estados do Ciclo de Vida Estrutural</h2>
<div class="diagram-container">
<!-- SVG_D2 -->
<div class="diagram-caption">Figura D2: Ciclo de vida estrutural de cinco estados governando todas as alocações.</div>
</div>
<p>A Figura D2 ilustra a transição de objetos estruturais desde Dormant (custo zero) até Provisional em sombra (\(T_{\text{prob}} = 50\)), inferência Active ao vivo, monitoramento de relevância Mature e desalojamento Evicted com liberação de matrizes.</p>

<div class="page-break"></div>
<h2>D3. Separação entre Fluxo de Dados e Fluxo de Controle</h2>
<div class="diagram-container">
<!-- SVG_D3 -->
<div class="diagram-caption">Figura D3: Caminho crítico de inferência em microssegundos desacoplado da governança.</div>
</div>
<p>A Figura D3 destaca a separação física estrita entre o pipeline de inferência feedforward (executando sob restrições estritas de microssegundos) e o pipeline de controle (avaliando erros, métricas de utilidade e obsolescência).</p>

<div class="page-break"></div>
<h2>D4. Protocolo de Provação em Sombra & Promoção</h2>
<div class="diagram-container">
<!-- SVG_D4 -->
<div class="diagram-caption">Figura D4: Diagrama de sequência de provação de candidatos, scoring contrafactual e promoção.</div>
</div>
<p>A Figura D4 ilustra como candidatos em modo sombra são avaliados ao longo de \(T_{\text{prob}} = 50\) passos com isolamento estrito de saída (\(g_p = 0,0\)), garantindo zero perturbação na predição ativa a menos que haja ganho verificado (\(G_{\text{cand}} > 0,05\)).</p>

<div class="page-break"></div>
<h2>D5. Retenção em Duas Escalas & Sobrevivência em Quiescência</h2>
<div class="diagram-container">
<!-- SVG_D5 -->
<div class="diagram-caption">Figura D5: Comparação entre desalojamento ingênuo instantâneo e retenção com portão duplo.</div>
</div>
<p>A Figura D5 demonstra por que o desalojamento ingênuo baseado em energia colapsa em intervalos de silêncio Poisson, enquanto a relevância em duas escalas (\(U_{\text{ret}}\)) e a obsolescência positiva mantêm o crédito de memória através de centenas de passos silenciosos.</p>

<div class="page-break"></div>
<h2>D6. Elasticidade Dinâmica de Recursos em Regimes Não Estacionários</h2>
<div class="diagram-container">
<!-- SVG_D6 -->
<div class="diagram-caption">Figura D6: Adaptação topológica dinâmica e escalonamento de carga computacional na Tarefa A8.</div>
</div>
<p>A Figura D6 retrata a adaptação estrutural ao longo de regimes não estacionários: linha de base linear (\(\approx 38\) FLOPs/passo médios) \(\to\) atraso temporal (\(\approx 65\) FLOPs/passo médios) \(\to\) estado recorrente (\(\approx 92\) FLOPs/passo médios) \(\to\) desalojamento seguro e recuperação de orçamento (\(\approx 40\) FLOPs/passo médios).</p>

<div class="page-break"></div>
<h2>D7. Escopo de Evidência Empírica da v0.1 & Fronteira Congelada</h2>
<div class="diagram-container">
<!-- SVG_D7 -->
<div class="diagram-caption">Figura D7: Fronteira formal separando fatos validados na v0.1 de pesquisas futuras no Marco M3.</div>
</div>
<p>A Figura D7 formaliza a demarcação entre fatos experimentais estabelecidos na v0.1 (recorrência escalar \(N \le 1\), parsimônia linear-first, \(\le 100\) FLOPs/passo médios) e fronteiras não abertas reservadas ao Marco M3.</p>

<div class="page-break"></div>
<h2>D8. Ciclo Operacional Prequencial Online</h2>
<div class="diagram-container">
<!-- SVG_D8 -->
<div class="diagram-caption">Figura D8: Sequência causal estrita de 8 etapas executada a cada observação em fluxo.</div>
</div>
<p>A Figura D8 ilustra as restrições causais estritas da execução prequencial: ingestão de entrada \(\to\) inferência linear \(\to\) inferência recorrente \(\to\) emissão causal \(\to\) revelação do alvo \(\to\) cálculo de erros \(\to\) gradientes \(\to\) atualização de ciclo de vida.</p>

<!-- SEÇÃO 7: SUÍTE DE VALIDAÇÃO EMPÍRICA -->
<div class="page-break"></div>
<h1>7. Suíte de Validação Empírica (Benchmarks A1–A8 & B1–B5)</h1>

<p>A arquitetura LEBRE v0.1 foi validada em 13 configurações experimentais: 8 tarefas sintéticas contínuas em fluxo (A1–A8) e 5 benchmarks de identificação de sistemas físicos e não lineares reais (B1–B5). Todos os testes foram executados sob o regime computacional R2-FLOP.</p>

<h2>7.1 Suíte Sintética de Benchmarks Mecanísticos (Tarefas A1–A8)</h2>
<table>
    <thead>
        <tr>
            <th>ID da Tarefa</th>
            <th>Nome da Carga de Trabalho</th>
            <th>RZA-LMS</th>
            <th>CCN</th>
            <th>Minimal GRU</th>
            <th>Online ESN</th>
            <th>LEBRE v0.1</th>
            <th>FLOPs Médios</th>
            <th>Comportamento Empírico / Invariante</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>A1</strong></td><td>Sparse Support Shift</td><td>0.0169</td><td>0.0185</td><td>0.7897</td><td>0.7695</td><td class="highlight-row">0.0379</td><td>205.3</td><td>RZA-LMS venceu (0,0169); LEBRE adapta em 205 FLOPs</td></tr>
        <tr><td><strong>A2</strong></td><td>Single Delayed Dependency</td><td>1.0010</td><td>1.0109</td><td>1.0001</td><td>0.9680</td><td class="highlight-row">1.1327</td><td>97.5</td><td>Fronteira: ESN denso venceu (0,9680); estado escalar 1,1327</td></tr>
        <tr><td><strong>A3</strong></td><td>Multiple Dispersed Delays</td><td>1.0002</td><td>1.0107</td><td>1.0002</td><td>0.9593</td><td class="highlight-row">1.1287</td><td>97.5</td><td>Fronteira: ESN denso venceu (0,9593); estado escalar 1,1287</td></tr>
        <tr><td><strong>A4</strong></td><td>Long-Delay Scaling</td><td>1.0002</td><td>1.0106</td><td>1.0001</td><td>1.0005</td><td class="highlight-row">1.1356</td><td>97.4</td><td>Fronteira: GRU venceu (1,0001); estado escalar 1,1356</td></tr>
        <tr><td><strong>A5</strong></td><td>Set/Reset Quiescent Memory</td><td>1.0234</td><td>0.4076</td><td>1.0277</td><td>0.9990</td><td class="highlight-row">0.7901</td><td>68.4</td><td>CCN venceu (0,4076); LEBRE 0,7901; LMS/GRU falharam (&gt;1,02)</td></tr>
        <tr><td><strong>A6</strong></td><td>Context Routing</td><td>0.5245</td><td>0.5416</td><td>0.6848</td><td>0.6036</td><td class="highlight-row">0.5668</td><td>56.3</td><td>RZA-LMS venceu (0,5245); LEBRE 0,5668 a 56,3 FLOPs</td></tr>
        <tr><td><strong>A7</strong></td><td>Extended Poisson Quiescence</td><td>1.0185</td><td>0.6017</td><td>1.0198</td><td>1.0059</td><td class="highlight-row">0.8535</td><td>60.3</td><td>CCN venceu (0,6017); LEBRE 0,8535; LMS/GRU falharam (&gt;1,01)</td></tr>
        <tr><td><strong>A8</strong></td><td>Abrupt Tri-Regime Transition</td><td>0.9807</td><td>0.9916</td><td>0.9807</td><td>1.0209</td><td class="highlight-row">0.9540</td><td>57.6</td><td>LEBRE venceu (0,9540); escala dinâmica 38&rarr;92&rarr;40 FLOPs</td></tr>
    </tbody>
</table>

<h2>7.2 Suíte de Benchmarks Contínuos Reais (Tarefas B1–B5)</h2>
<table>
    <thead>
        <tr>
            <th>ID da Tarefa</th>
            <th>Fluxo Contínuo</th>
            <th>RZA-LMS</th>
            <th>CCN</th>
            <th>Minimal GRU</th>
            <th>Online ESN</th>
            <th>LEBRE v0.1</th>
            <th>FLOPs Médios</th>
            <th>Desfecho Selado / Vencedor</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>B1</strong></td><td>NSW Electricity Continuous</td><td>0.9787</td><td>0.4632</td><td>2.4146</td><td>1.4238</td><td class="highlight-row">0.8364</td><td>24.0</td><td>CCN venceu (0,4632); LEBRE competitiva a 24,0 FLOPs</td></tr>
        <tr><td><strong>B2</strong></td><td>Jena Weather Temperature</td><td>DIVERGIU</td><td>DIVERGIU</td><td>0.0742</td><td>0.3284</td><td class="highlight-row">0.0248</td><td>69.8</td><td>LEBRE venceu (0,0248); RZA-LMS e CCN divergiram</td></tr>
        <tr><td><strong>B3</strong></td><td>Gas Dynamic Mixture</td><td>0.0492</td><td>0.0390</td><td>0.0241</td><td>0.2608</td><td class="highlight-row">0.0020</td><td>79.9</td><td>LEBRE venceu (0,0020); liderou todos os baselines</td></tr>
        <tr><td><strong>B4</strong></td><td>Silverbox System ID</td><td>0.9993</td><td>0.9963</td><td>0.9999</td><td>0.9136</td><td class="highlight-row">0.9932</td><td>8.0</td><td>Online ESN venceu (0,9136); fronteira documentada de recorrência escalar</td></tr>
        <tr><td><strong>B5</strong></td><td>Household Active Power</td><td>0.0912</td><td>0.0120</td><td>0.0924</td><td>0.1129</td><td class="highlight-row">0.0040</td><td>28.3</td><td>LEBRE venceu (0,0040); liderou CCN (0,0120) e GRU (0,0924)</td></tr>
    </tbody>
</table>

<div class="alert alert-info">
<strong>Confirmação de Auditoria Numérica (Correção C):</strong> No Bloco de Benchmarks B, todas as identidades de cargas de trabalho e métricas numéricas foram verificadas diretamente contra artefatos legíveis por máquina selados (<code>BENCH_01B_AGGREGATE_SUMMARY.csv</code>). Na Tarefa B5 (Household Active Power), a LEBRE liderou todos os baselines com NMSE de <strong>0,00403</strong> (média de 28,30 FLOPs/passo, 248 bytes de RAM de estado). Na Tarefa B4 (Silverbox System ID), o Online ESN atingiu NMSE de <strong>0,91359</strong> enquanto a LEBRE operou em <strong>0,99320</strong> (8,00 FLOPs/passo, 208 bytes de RAM), confirmando a fronteira de viés indutivo documentada onde reservatórios aleatórios de alta dimensão superam estados escalares mínimos em dinâmicas não lineares contínuas multi-frequenciais.
</div>

<!-- SEÇÃO 8: CONTABILIDADE COMPUTACIONAL & EMBARCADOS -->
<div class="page-break"></div>
<h1>8. Contabilidade Computacional, FLOPs Médios & Limites Embarcados</h1>

<p>Para assegurar total credibilidade técnica, a LEBRE formaliza uma taxonomia matemática rigorosa de suas operações e explicita a diferença entre rendimento médio e picos transitórios de avaliação.</p>

<h2>8.1 Taxonomia Formal de FLOPs</h2>
<table>
    <thead>
        <tr>
            <th>Subsistema de Operação</th>
            <th>Formulação Matemática</th>
            <th>Fórmula de Contagem de FLOPs</th>
            <th>FLOPs (\(D=8, K=5, N=1\))</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Normalização Causal</td>
            <td>\(\mu_t, \sigma_t^2, \tilde{\mathbf{x}}_t\)</td>
            <td>\(3D\) multiplicações e adições</td>
            <td>24 FLOPs</td>
        </tr>
        <tr>
            <td>Forward Linear Esparso</td>
            <td>\(\mathbf{w}_{\text{base}}^\top \tilde{\mathbf{x}}_t + b_{\text{base}}\)</td>
            <td>\(2K\) operações</td>
            <td>10 FLOPs</td>
        </tr>
        <tr>
            <td>Forward Oculto Recorrente</td>
            <td>\(\lambda s_{t-1} + \mathbf{w}_{\text{in}}^\top \tilde{\mathbf{x}}_t + b_s\)</td>
            <td>\(2K + 3\) operações + \(\tanh\)</td>
            <td>18 FLOPs (com \(\tanh \approx 5\))</td>
        </tr>
        <tr>
            <td>Saída / Readout</td>
            <td>\(\hat{y}_t = y_{\text{base},t} + w_s s_t\)</td>
            <td>2 multiplicações/adições</td>
            <td>2 FLOPs</td>
        </tr>
        <tr>
            <td>Sensibilidades RTRL Escalares</td>
            <td>Atualização de \(p_t, \mathbf{q}_t\)</td>
            <td>\(2K + 6\) operações</td>
            <td>16 FLOPs</td>
        </tr>
        <tr>
            <td>Atualizações de Parâmetros</td>
            <td>\(\Delta \mathbf{w}_{\text{base}}, \Delta \mathbf{w}_{\text{in}}, \Delta \lambda, \Delta w_s\)</td>
            <td>\(3K + 6\) operações</td>
            <td>21 FLOPs</td>
        </tr>
        <tr>
            <td>Governança de Ciclo de Vida</td>
            <td>\(U_{\text{ret}}, O_{\text{obs}}, C_t\)</td>
            <td>8 operações escalares</td>
            <td>8 FLOPs</td>
        </tr>
        <tr class="highlight-row">
            <td><strong>Total em Regime Estacionário</strong></td>
            <td><strong>Ciclo Completo em Duas Camadas</strong></td>
            <td><strong>Pipeline Ativo Nominal</strong></td>
            <td><strong>\(\approx 99\) FLOPs/passo</strong></td>
        </tr>
    </tbody>
</table>

<h2>8.2 Semântica de FLOPs Médios do R2-FLOP vs. Picos Transitórios</h2>
<div class="alert alert-warning">
<strong>Esclarecimento da Especificação (Correção A):</strong> O requisito R2-FLOP (\(\le 100\) FLOPs/passo) constitui estritamente um <strong>orçamento médio de benchmark</strong> avaliado ao longo de trajetórias streaming completas. Não se trata de um teto rígido absoluto para cada ciclo isolado. Na Tarefa B5, a LEBRE consome uma média de <strong>90,44 FLOPs/passo médios</strong>. Durante fases transitórias de provação, nas quais um candidato em sombra é avaliado concorrentemente com a inferência ativa, a carga computacional atinge um pico temporário de \(\approx 206\) FLOPs/passo por 50 passos.
</div>

<h2>8.3 Envelope de Memória RAM de Estado & Qualificação de Hardware</h2>
<p>O envelope de memória de estado persistente da LEBRE é documentado em <strong>\(\approx 440\) bytes</strong>, compreendendo:</p>
<ul>
    <li>Pesos e bias lineares esparsos: \(\approx 80\) bytes (float32).</li>
    <li>Parâmetros recorrentes escalares (\(w_s, \lambda, \mathbf{w}_{\text{in}}\)): \(\approx 48\) bytes.</li>
    <li>Registradores de sensibilidade gradiente RTRL (\(p_t, \mathbf{q}_t\)): \(\approx 48\) bytes.</li>
    <li>Buffers do candidato provisional em sombra: \(\approx 96\) bytes.</li>
    <li>Acumuladores de ciclo de vida e contadores de histerese: \(\approx 168\) bytes.</li>
</ul>

<div class="alert alert-danger">
<strong>Qualificação de Viabilidade em Hardware (Correção B):</strong> A quantia de 440 bytes representa a <strong>RAM de estado do modelo</strong>, e não o orçamento total de memória de um sistema microcontrolador físico (o qual precisa alocar pilha de execução C, buffers de anel de I/O e runtime de RTOS). Ademais, a LEBRE v0.1 foi avaliada exclusivamente em simulação matemática bit a bit. O deployment em microcontroladores físicos reais (como núcleos ARM Cortex-M0+ ou Cortex-M4) constitui um <em>alvo prospectivo para validação futura</em>, e não um resultado experimental realizado nesta especificação.
</div>

<!-- SEÇÃO 9: LIMITES DE ESCOPO -->
<div class="page-break"></div>
<h1>9. Limites de Escopo Arquitetural & Fronteira Congelada</h1>

<p>Para resguardar fronteiras científicas inequívocas, a LEBRE declara explicitamente o que a versão v0.1 é e o que ela <em>não é</em>. A linha demarcatória entre evidência empírica congelada e pesquisas futuras é inviolável na v0.1.</p>

<table class="no-break">
    <thead>
        <tr>
            <th>Dimensão Arquitetural</th>
            <th>Status na LEBRE v0.1 (Fato Congelado)</th>
            <th>Status em Pesquisa Futura / M3 (Hipótese)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Topologia Recorrente</strong></td>
            <td>Apenas recorrência escalar (\(N \le 1\))</td>
            <td>Interações recorrentes multi-state (\(N \ge 2\))</td>
        </tr>
        <tr>
            <td><strong>Mapeamento de Saída</strong></td>
            <td>Readout linear (\(y_{\text{rec},t} = w_s s_t\))</td>
            <td>Cabeças de saída não lineares multicamadas</td>
        </tr>
        <tr>
            <td><strong>Transições Estruturais</strong></td>
            <td>Máquina discreta de cinco estados (Dormant-Prov-Act-Mature-Evict)</td>
            <td>Crescimento / poda contínua de grafos</td>
        </tr>
        <tr>
            <td><strong>Plataforma de Execução</strong></td>
            <td>Execução em fluxo simulada por software</td>
            <td>Deployment em silício bare-metal (Cortex-M)</td>
        </tr>
        <tr>
            <td><strong>Motor de Otimização</strong></td>
            <td>RTRL escalar com momento causal</td>
            <td>Interfaces neurais desacopladas ou métodos de 2ª ordem</td>
        </tr>
        <tr>
            <td><strong>Classificação de Ineditismo</strong></td>
            <td><code>NOVELTY_CLAIM_READY = NO</code></td>
            <td>Sujeito à revisão por pares externa em M3</td>
        </tr>
    </tbody>
</table>

<h2>Reivindicações Proibidas na LEBRE v0.1</h2>
<ol>
    <li><strong>Sem Reivindicações Recorrentes Multi-Unidade:</strong> A v0.1 não faz qualquer afirmação sobre dinâmica interna multidimensional (\(N \ge 2\)). Todas as propriedades verificadas aplicam-se estritamente à recorrência escalar.</li>
    <li><strong>Sem Reivindicações de Gravação em Silício Físico:</strong> A v0.1 não foi gravada em silício ARM físico. A viabilidade em sistemas embarcados é sustentada por contagem de operações e dimensionamento de RAM de estado, e não por telemetria de hardware físico.</li>
    <li><strong>Sem Reivindicações de Aprendizado Contínuo Universal:</strong> A LEBRE é validada para regressão em fluxo, filtragem e identificação de sistemas. Não se afirma que o método resolva o esquecimento catastrófico em modelos profundos de visão ou linguagem.</li>
</ol>

<!-- SEÇÃO 10: MATRIZ DE RASTREABILIDADE -->
<div class="page-break"></div>
<h1>10. Matriz de Rastreabilidade de Parâmetros e Constantes</h1>

<p>Cada constante numérica, taxa de aprendizado e limiar na LEBRE v0.1 está formalmente especificado, possui valor padrão definido e está rastreado ao seu arquivo de implementação e horizonte de sensibilidade empírica.</p>

<table>
    <thead>
        <tr>
            <th>Nome do Parâmetro</th>
            <th>Símbolo</th>
            <th>Valor Padrão</th>
            <th>Arquivo de Implementação</th>
            <th>Função Empírica & Horizonte de Sensibilidade</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>alpha_norm</code></td>
            <td>\(\alpha_{\text{norm}}\)</td>
            <td>0,01</td>
            <td><code>src/streaming_norm.py</code></td>
            <td>Filtro de média/variância online; horizonte \(\approx 100\) passos</td>
        </tr>
        <tr>
            <td><code>eps_norm</code></td>
            <td>\(\epsilon_{\text{norm}}\)</td>
            <td>10<sup>-5</sup></td>
            <td><code>src/streaming_norm.py</code></td>
            <td>Constante de estabilidade numérica no denominador de normalização</td>
        </tr>
        <tr>
            <td><code>alpha_err</code></td>
            <td>\(\alpha_E\)</td>
            <td>0,05</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Suavização do erro linear para disparo de nascimento; \(\approx 20\) passos</td>
        </tr>
        <tr>
            <td><code>theta_birth</code></td>
            <td>\(\theta_{\text{birth}}\)</td>
            <td>0,15</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Limiar de erro residual necessário para iniciar provação em sombra</td>
        </tr>
        <tr>
            <td><code>n_birth_persist</code></td>
            <td>\(N_{\text{birth}}\)</td>
            <td>30</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Passos consecutivos com erro &gt;\(\theta_{\text{birth}}\) para evitar disparos espúrios</td>
        </tr>
        <tr>
            <td><code>t_probation</code></td>
            <td>\(T_{\text{prob}}\)</td>
            <td>50</td>
            <td><code>src/candidate_probation.py</code></td>
            <td>Horizonte fixo de avaliação do candidato em sombra antes da promoção</td>
        </tr>
        <tr>
            <td><code>theta_promote</code></td>
            <td>\(\theta_{\text{promote}}\)</td>
            <td>0,05</td>
            <td><code>src/candidate_probation.py</code></td>
            <td>Ganho contrafactual relativo mínimo (&gt;5%) exigido para promoção</td>
        </tr>
        <tr>
            <td><code>tau_mature</code></td>
            <td>\(\tau_{\text{mature}}\)</td>
            <td>100</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Passos pós-promoção antes de o estado tornar-se elegível a desalojamento</td>
        </tr>
        <tr>
            <td><code>alpha_slow</code></td>
            <td>\(\alpha_{\text{slow}}\)</td>
            <td>0,005</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Filtro de relevância lenta; meia-vida efetiva de crédito \(\tau \approx 140\) passos</td>
        </tr>
        <tr>
            <td><code>theta_ret</code></td>
            <td>\(\theta_{\text{ret}}\)</td>
            <td>0,02</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Limiar mínimo de relevância lenta abaixo do qual o estado torna-se vulnerável</td>
        </tr>
        <tr>
            <td><code>m_obs</code></td>
            <td>\(m_{\text{obs}}\)</td>
            <td>0,02</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Incremento de obsolescência positiva por passo com utilidade nula/negativa</td>
        </tr>
        <tr>
            <td><code>d_obs</code></td>
            <td>\(d_{\text{obs}}\)</td>
            <td>0,05</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Decremento de obsolescência por passo com utilidade positiva (recuperação assimétrica)</td>
        </tr>
        <tr>
            <td><code>theta_obs</code></td>
            <td>\(\theta_{\text{obs}}\)</td>
            <td>0,80</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Nível de saturação de obsolescência positiva para permitir desalojamento</td>
        </tr>
        <tr>
            <td><code>patience_evict</code></td>
            <td>\(N_{\text{pat}}\)</td>
            <td>30</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Passos consecutivos com condição dupla para cumprir assimetria de \(\approx 300:1\)</td>
        </tr>
        <tr>
            <td><code>lr_base</code></td>
            <td>\(\eta_{\text{base}}\)</td>
            <td>0,01</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Taxa de aprendizado para os pesos da linha de base linear esparsa</td>
        </tr>
        <tr>
            <td><code>lr_rec_in</code></td>
            <td>\(\eta_{\text{in}}\)</td>
            <td>0,005</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Taxa de aprendizado para a projeção de entrada no estado recorrente</td>
        </tr>
        <tr>
            <td><code>lr_rec_self</code></td>
            <td>\(\eta_\lambda\)</td>
            <td>0,002</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Taxa de aprendizado para o peso de autorrecorrência \(\lambda\)</td>
        </tr>
        <tr>
            <td><code>lr_rec_out</code></td>
            <td>\(\eta_s\)</td>
            <td>0,01</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Taxa de aprendizado para o peso de saída escalar \(w_s\)</td>
        </tr>
        <tr>
            <td><code>weight_decay</code></td>
            <td>\(\gamma_{\text{decay}}\)</td>
            <td>10<sup>-4</sup></td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Coeficiente de regularização L2 para pesos lineares e recorrentes</td>
        </tr>
        <tr>
            <td><code>lambda_init</code></td>
            <td>\(\lambda_0\)</td>
            <td>0,85</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Peso inicial de autorrecorrência atribuído a novos candidatos</td>
        </tr>
        <tr>
            <td><code>lambda_max</code></td>
            <td>\(\lambda_{\text{max}}\)</td>
            <td>0,98</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Teto de corte estrito para garantir dinâmica interna estritamente contratual</td>
        </tr>
        <tr>
            <td><code>r2_flop_budget</code></td>
            <td>\(\mathcal{B}_{\text{FLOP}}\)</td>
            <td>&le; 100</td>
            <td><code>docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml</code></td>
            <td>Teto de orçamento médio de operações de ponto flutuante por passo</td>
        </tr>
    </tbody>
</table>

<!-- SEÇÃO 11: ADRS & COLOFÃO -->
<div class="page-break"></div>
<h1>11. Registros de Decisão Arquitetural & Decisão Final</h1>

<p>A arquitetura LEBRE v0.1 está fundamentada em seis Registros de Decisão Arquitetural (ADRs) formais:</p>

<ul>
    <li><strong>ADR-001 (Organização Recorrente Single-State):</strong> Restringe a capacidade recorrente interna estritamente a um estado escalar (\(N \le 1\)), garantindo rastreamento exato de gradientes em tempo real (\(\mathcal{O}(1)\) RTRL) e eliminando inversão matricial.</li>
    <li><strong>ADR-002 (Provação Desacoplada em Modo Sombra):</strong> Impõe isolamento total de saída (\(g_p = 0,0\)) durante a avaliação inicial de 50 passos de novos candidatos, evitando perturbações na inferência ativa.</li>
    <li><strong>ADR-003 (Contabilidade de Relevância em Duas Escalas):</strong> Desacopla a atividade rápida do sinal do crédito estrutural lento via filtro com meia-vida de 140 passos, prevenindo a expulsão indevida em períodos de silêncio Poisson.</li>
    <li><strong>ADR-004 (Obsolescência com Portão Duplo & Histerese):</strong> Implementa a assimetria empírica de custo \(\approx 300:1\) através do portão duplo (\(U_{\text{ret}} < 0,02\) E \(O_{\text{obs}} > 0,80\)) sustentado por 30 passos de paciência.</li>
    <li><strong>ADR-005 (Parsimônia Estrutural Linear-First):</strong> Determina que a linha de base linear seja plenamente esgotada antes de permitir o nascimento de candidatos recorrentes em sombra.</li>
    <li><strong>ADR-006 (Orçamento Médio Estrito de Recursos em Tempo Real):</strong> Formula o teto R2-FLOP como uma exigência de rendimento médio no benchmark (\(\le 100\) FLOPs/passo médios), acomodando picos transitórios de avaliação em sombra sem violar a frugalidade geral.</li>
</ul>

<div class="alert alert-info">
<strong>Bloco de Decisão Final da Seção 76:</strong>
<pre style="margin: 4px 0 0 0; font-size: 7.8pt; color: #0369a1;">
================================================================================
SECTION 76: FINAL ARCHITECTURAL DECISION BLOCK
================================================================================
ARCHITECTURE_SPEC_VERSION: 0.1-CONDENSED
CANONICAL_NAME: LEBRE
FULL_EXPANSION: Lifecycle-governed Evidence-Based Resource Evolution
HISTORICAL_CODENAME: Track B Single-State Organization
SPEC_CONSISTENCY_AUDIT: PASSED_CORRECTIONS_A_THROUGH_L
DIAGRAM_RENDER_STATUS: CANONICAL_D1_THROUGH_D8_STANDALONE_AND_INLINE_VERIFIED
PDF_PACKAGE_STATUS: COMPILED_AND_VISUALLY_VERIFIED
NUMERIC_INTEGRITY: RECONCILED_WITH_BENCH_01B_CAR_01_FROZEN_LOGS
REGRESSION_SUITE: 124_OF_124_TESTS_PASSING
STATUS: FROZEN_WITH_SCOPE_LIMITS
EVIDENCE_CLASSIFICATION: VALIDATED_WITH_SCOPE_LIMITS
MILESTONE_M3_STATUS: UNOPENED
NOVELTY_CLAIM_READY: NO
HARD_STOP: ENFORCED
================================================================================
</pre>
</div>

<div class="cover-footer" style="margin-top: 30px; border-top: 1px solid #cbd5e1; padding-top: 10px;">
    <div>Especificação da Arquitetura LEBRE v0.1 (Referência Condensada) • Projeto Codinome Lebre</div>
    <div>Checksum do Documento Completo • Fim da Especificação</div>
</div>

</body>
</html>
"""

html_content = TEMPLATE.replace("<!-- LOGO_B64 -->", LOGO_B64)
html_content = html_content.replace("<!-- SVG_D1 -->", svg_d1)
html_content = html_content.replace("<!-- SVG_D2 -->", svg_d2)
html_content = html_content.replace("<!-- SVG_D3 -->", svg_d3)
html_content = html_content.replace("<!-- SVG_D4 -->", svg_d4)
html_content = html_content.replace("<!-- SVG_D5 -->", svg_d5)
html_content = html_content.replace("<!-- SVG_D6 -->", svg_d6)
html_content = html_content.replace("<!-- SVG_D7 -->", svg_d7)
html_content = html_content.replace("<!-- SVG_D8 -->", svg_d8)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated {OUT_FILE} ({len(html_content)} bytes)")
