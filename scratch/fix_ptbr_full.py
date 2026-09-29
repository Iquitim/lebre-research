#!/usr/bin/env python3
"""
Update scratch/build_ptbr_html.py with:
1. Pure white high-contrast cover styling & HTML matching English.
2. Canonical 5-state lifecycle terminology.
3. Exact sealed benchmark tables for Block A and Block B (Silverbox=B4, Household Power=B5).
4. Updated Note C with verified sealed values.
Then generate docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html.
"""
from pathlib import Path
import re

PTBR_BUILDER = Path("scratch/build_ptbr_html.py")

with open(PTBR_BUILDER, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Cover CSS
old_cover_css_pattern = re.compile(r"\.cover-page\s*\{.*?\.cover-footer\s*\{.*?\n\}", re.DOTALL)

new_cover_css = """.cover-page {
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
}"""

code = old_cover_css_pattern.sub(new_cover_css, code, count=1)

# 2. Update Cover HTML
old_cover_html_pattern = re.compile(r"<!-- CAPA -->.*?<!-- SEÇÃO 1", re.DOTALL)

new_cover_html = """<!-- CAPA -->
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

<!-- SEÇÃO 1"""

code = old_cover_html_pattern.sub(new_cover_html, code, count=1)

# 3. Update TOC and Section 4 title to Five-State
code = code.replace(
    '<li class="toc-item"><span class="toc-title">4. Máquina de Estados do Ciclo de Vida Estrutural</span>',
    '<li class="toc-item"><span class="toc-title">4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados</span>'
)
code = code.replace(
    '<li class="toc-item"><span class="toc-title">7. Suíte de Validação Empírica</span>',
    '<li class="toc-item"><span class="toc-title">7. Suíte de Validação Empírica (Benchmarks A1–A8 & B1–B5)</span>'
)
code = code.replace(
    '<h1>4. Máquina de Estados do Ciclo de Vida Estrutural</h1>',
    '<h1>4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados</h1>'
)

# 4. Update Section 7 Tables and Note C
old_sec7_pattern = re.compile(r"<!-- SEÇÃO 7:.*?<!-- SEÇÃO 8:", re.DOTALL)

new_sec7_content = """<!-- SEÇÃO 7: SUÍTE DE VALIDAÇÃO EMPÍRICA -->
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

<!-- SEÇÃO 8:"""

code = old_sec7_pattern.sub(new_sec7_content, code, count=1)

with open(PTBR_BUILDER, "w", encoding="utf-8") as f:
    f.write(code)

print(f"Cleanly updated {PTBR_BUILDER}.")
