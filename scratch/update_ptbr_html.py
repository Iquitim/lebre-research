import re

with open("scratch/build_ptbr_html.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Use Portuguese D4 SVG
text = text.replace(
    'svg_d4 = read_svg("lebre_shadow_probation")',
    'svg_d4 = read_svg("lebre_shadow_probation_ptbr")'
)

# 2. Remove Confidential Preprint
text = text.replace(
    'content: "Suíte de Pesquisa Codinome Lebre • Pré-print Científico Confidencial";',
    'content: "Projeto de Pesquisa Codinome Lebre • Especificação Arquitetural v0.1";'
)

# 3. Cover CSS
old_cover_css = """
.cover-page {
    page-break-after: always;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 55px 45px 40px 45px;
    background: linear-gradient(145deg, #09111e 0%, #0f172a 60%, #1e293b 100%);
    color: #ffffff;
}

.cover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    padding-bottom: 20px;
}

.cover-logo {
    max-width: 250px;
    height: auto;
}

.cover-badge {
    background: rgba(37, 99, 235, 0.25);
    border: 1px solid #3b82f6;
    color: #60a5fa;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.cover-main {
    margin-top: 30px;
}

.cover-title {
    font-size: 26pt;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin: 0 0 8px 0;
    color: #f8fafc;
}

.cover-subtitle {
    font-size: 14pt;
    font-weight: 400;
    color: #94a3b8;
    margin: 0 0 20px 0;
    line-height: 1.35;
}

.cover-expansion {
    font-size: 10.5pt;
    color: #38bdf8;
    font-weight: 500;
    margin-bottom: 25px;
    padding: 10px 16px;
    background: rgba(14, 165, 233, 0.1);
    border-left: 3px solid #0ea5e9;
    border-radius: 0 8px 8px 0;
}

.cover-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 15px;
}

.cover-meta-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 10px 14px;
    border-radius: 6px;
}

.cover-meta-label {
    font-size: 7pt;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 3px;
}

.cover-meta-value {
    font-size: 8.5pt;
    font-weight: 600;
    color: #e2e8f0;
}

.cover-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 15px;
    font-size: 7.5pt;
    color: #64748b;
    display: flex;
    justify-content: space-between;
}
"""

new_cover_css = """
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
    border-top: 1px solid #cbd5e1;
    padding-top: 14px;
    font-size: 7.5pt;
    color: #64748b;
    display: flex;
    justify-content: space-between;
}
"""

if old_cover_css.strip() in text:
    text = text.replace(old_cover_css.strip(), new_cover_css.strip())
    print("PT-BR Cover CSS replaced successfully.")
else:
    print("Warning: old_cover_css not found exactly in PT-BR.")

# 4. Cover HTML body
old_cover_html = """<!-- CAPA PRINCIPAL -->
<div class="cover-page">
    <div class="cover-header">
        <img class="cover-logo" src="data:image/png;base64,<!-- LOGO_B64 -->" alt="Logotipo da Arquitetura LEBRE">
        <div class="cover-badge">Especificação Formal v0.1</div>
    </div>
    
    <div class="cover-main">
        <div class="cover-title">Especificação da Arquitetura LEBRE</div>
        <div class="cover-subtitle">Guia de Referência Condensado & Visão Geral da Arquitetura</div>
        
        <div class="cover-expansion">
            <strong>Expansão:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br>
            <strong>Nome Histórico:</strong> Organização de Estado Único Track B
        </div>
        
        <div class="cover-meta-grid">
            <div class="cover-meta-card">
                <div class="cover-meta-label">Status da Arquitetura</div>
                <div class="cover-meta-value">Especificação de Referência Congelada com Limites de Escopo</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Classificação da Evidência</div>
                <div class="cover-meta-value">VALIDATED_WITH_SCOPE_LIMITS</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Prontidão para Reivindicação de Novidade</div>
                <div class="cover-meta-value">NOVELTY_CLAIM_READY = NO</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Fronteira do Marco M3</div>
                <div class="cover-meta-value">NÃO ABERTO (Fronteira Multi-Estado Reservada)</div>
            </div>
        </div>
    </div>
    
    <div class="cover-footer">
        <div>Suíte de Autoria: Projeto Científico Codinome Lebre</div>
        <div>Data de Congelamento: Setembro de 2026 • Versão do Documento 0.1-CONDENSED</div>
    </div>
</div>"""

new_cover_html = """<!-- CAPA PRINCIPAL -->
<div class="cover-page">
    <div class="cover-header">
        <div class="cover-logo-panel">
            <img class="cover-logo" src="data:image/png;base64,<!-- LOGO_B64 -->" alt="Logotipo da Arquitetura LEBRE">
        </div>
        <div class="cover-badge">Especificação Formal v0.1</div>
    </div>
    
    <div class="cover-main">
        <div class="cover-title">Especificação da Arquitetura LEBRE</div>
        <div class="cover-subtitle">Guia de Referência Condensado & Visão Geral da Arquitetura</div>
        
        <div class="cover-expansion">
            <strong>Expansão Canônica:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br>
            <strong>Proveniência Histórica:</strong> Organização de Estado Único Track B (Codinome Lebre)
        </div>
        
        <div class="cover-meta-grid">
            <div class="cover-meta-card">
                <div class="cover-meta-label">Status da Arquitetura</div>
                <div class="cover-meta-value">Especificação de Referência Congelada com Limites de Escopo</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Classificação da Evidência</div>
                <div class="cover-meta-value">VALIDATED_WITH_SCOPE_LIMITS</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Prontidão para Reivindicação de Novidade</div>
                <div class="cover-meta-value">NOVELTY_CLAIM_READY = NO</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Fronteira do Marco M3</div>
                <div class="cover-meta-value">NÃO ABERTO (Fronteira Multi-Estado Reservada)</div>
            </div>
        </div>
    </div>
    
    <div class="cover-footer">
        <div>Projeto de Pesquisa: Projeto de Pesquisa Codinome Lebre</div>
        <div>Data de Congelamento: Setembro de 2026 • Versão do Documento 0.1-CONDENSED</div>
    </div>
</div>"""

if old_cover_html in text:
    text = text.replace(old_cover_html, new_cover_html)
    print("PT-BR Cover HTML body replaced successfully.")
else:
    print("Warning: old_cover_html not found exactly in PT-BR.")

# 5. TOC Item 4
text = text.replace(
    '<li class="toc-item"><span class="toc-title">4. Máquina de Estados do Ciclo de Vida Estrutural em Quatro Fases</span><span class="toc-page">Página 6</span></li>',
    '<li class="toc-item"><span class="toc-title">4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados</span><span class="toc-page">Página 6</span></li>'
)

# 6. Section 2 claim bounding
text = text.replace(
    'A LEBRE garante que dependências lineares triviais jamais disparem alocações caras de estados.',
    'Sob os regimes lineares avaliados, a alocação de estados recorrentes não foi disparada quando a linha de base linear foi suficiente.'
)
text = text.replace(
    'A pegada de memória é estritamente delimitada a \\(\\approx 440\\) bytes de RAM de estado de modelo persistente (pesos e registradores de estado), enquanto o débito operacional é restrito a \\(\\le 100\\) FLOPs/passo médios.',
    'A pegada média observada de RAM de estado de modelo persistente é de 440,0 bytes (excluindo stack, código, runtime e buffers de E/S; teto do benchmark \\(R_2\\text{-MEM} \\le 1024\\) bytes), enquanto o débito operacional é restrito a \\(\\le 100\\) FLOPs/passo médios.'
)

# 7. Section 4 Heading and description
text = text.replace(
    '<h1>4. Máquina de Estados do Ciclo de Vida Estrutural em Quatro Fases</h1>\n\n<p>Todo objeto estrutural na LEBRE progride por um ciclo de vida rigorosamente delimitado em quatro estados: <strong>DORMANT</strong> (Dormente), <strong>PROVISIONAL</strong> (Provisional), <strong>ACTIVE / MATURE</strong> (Ativo / Maduro) e <strong>EVICTED</strong> (Desalojado).',
    '<h1>4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados</h1>\n\n<p>Todo objeto estrutural na LEBRE progride por um ciclo de vida rigorosamente delimitado em cinco estados: <strong>DORMANT</strong> (Dormente), <strong>PROVISIONAL</strong> (Provisório), <strong>ACTIVE</strong> (Ativo), <strong>MATURE</strong> (Maduro) e <strong>EVICTED</strong> (Desalojado).'
)

# 8. Figure D2 caption
text = text.replace(
    '<div class="diagram-caption">Figura D2: Ciclo de vida estrutural em quatro estados governando todas as alocações.</div>',
    '<div class="diagram-caption">Figura D2: Ciclo de vida estrutural de cinco estados governando todas as alocações.</div>'
)

# 9. Figure D4 caption
text = text.replace(
    '<div class="diagram-caption">Figura D4: Protocolo de estágio probatório em sombra não interferente. Candidatos provisórios aprendem em paralelo sem acoplamento à saída.</div>',
    '<div class="diagram-caption">Figura D4: Protocolo de estágio probatório em sombra não interferente com barreira estrita de isolamento e portão empírico.</div>'
)

# 10. Comparison table row
text = text.replace(
    '<td>Máquina discreta de quatro estados (Dormant-Prov-Act-Evict)</td>',
    '<td>Máquina discreta de cinco estados (Dormente-Provisório-Ativo-Maduro-Desalojado)</td>'
)

# 11. Reconciled Tables 7.1 and 7.2 in Section 7
old_sec7_tables = """<h2>7.1 Suíte de Benchmarks Sintéticos (Tarefas A1–A8)</h2>
<table>
    <thead>
        <tr>
            <th>ID Tarefa</th>
            <th>Descrição da Tarefa</th>
            <th>Baseline Linear</th>
            <th>RTRL Fixo (\\(N=1\\))</th>
            <th>LEBRE v0.1</th>
            <th>Média FLOPs/passo</th>
            <th>Comportamento Empírico</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>A1</strong></td>
            <td>Regressão Linear Estática Pura</td>
            <td>0.0042</td>
            <td>0.0049</td>
            <td class="highlight-row">0.0041</td>
            <td>38.2</td>
            <td>0 nascimentos recorrentes (Parsimônia intacta)</td>
        </tr>
        <tr>
            <td><strong>A2</strong></td>
            <td>Seleção Esparsa de Features (K=5/50)</td>
            <td>0.0118</td>
            <td>0.0145</td>
            <td class="highlight-row">0.0112</td>
            <td>41.6</td>
            <td>Conjunto ativo de features identificado corretamente</td>
        </tr>
        <tr>
            <td><strong>A3</strong></td>
            <td>Atraso de Entrada Fixo (\\(L=5\\))</td>
            <td>0.1420</td>
            <td>0.0480</td>
            <td class="highlight-row">0.0310</td>
            <td>58.4</td>
            <td>Promove capacidade de atraso/recorrência de forma limpa</td>
        </tr>
        <tr>
            <td><strong>A4</strong></td>
            <td>Sistema Dinâmico Linear (\\(N=1\\))</td>
            <td>0.2840</td>
            <td>0.0210</td>
            <td class="highlight-row">0.0185</td>
            <td>88.1</td>
            <td>Reconstrói localização do polo com precisão</td>
        </tr>
        <tr>
            <td><strong>A5</strong></td>
            <td>Rajadas Quiescentes Poisson (\\(\\lambda=0.01\\))</td>
            <td>0.4150</td>
            <td>0.3890 (Despejado)</td>
            <td class="highlight-row">0.0420</td>
            <td>46.3</td>
            <td>&gt;99% retenção de estado através de lacunas silenciosas</td>
        </tr>
        <tr>
            <td><strong>A6</strong></td>
            <td>Mudança Abrupta de Regime (Dinâmico para Estático)</td>
            <td>0.3120</td>
            <td>0.0980 (Obsoleto)</td>
            <td class="highlight-row">0.0280</td>
            <td>52.7</td>
            <td>Despejo seguro concluído em 42 passos</td>
        </tr>
        <tr>
            <td><strong>A7</strong></td>
            <td>Dinâmica Orientada a Eventos de Taxa Múltipla</td>
            <td>0.3890</td>
            <td>0.1450</td>
            <td class="highlight-row">0.0380</td>
            <td>61.2</td>
            <td>Ponte sobre intervalos de amostragem variáveis</td>
        </tr>
        <tr>
            <td><strong>A8</strong></td>
            <td>Regimes Elásticos Cíclicos (Linear-Atraso-Recorrente)</td>
            <td>0.3450</td>
            <td>0.1120</td>
            <td class="highlight-row">0.0340</td>
            <td>64.5</td>
            <td>Expansão e contração elástica completa</td>
        </tr>
    </tbody>
</table>

<h2>7.2 Suíte de Benchmarks do Mundo Real (Tarefas B1–B5)</h2>
<table>
    <thead>
        <tr>
            <th>ID Tarefa</th>
            <th>Sistema Físico</th>
            <th>Minimal GRU</th>
            <th>Echo State (ESN)</th>
            <th>CCN</th>
            <th>LEBRE v0.1</th>
            <th>Média FLOPs/passo</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>B1</strong></td>
            <td>Tanques em Cascata (Cascaded Tanks)</td>
            <td>0.0412</td>
            <td>0.0489</td>
            <td>0.0185</td>
            <td class="highlight-row">0.0142</td>
            <td>89.4</td>
        </tr>
        <tr>
            <td><strong>B2</strong></td>
            <td>Acionamentos Elétricos Acoplados</td>
            <td>0.0380</td>
            <td>0.0410</td>
            <td>0.0210</td>
            <td class="highlight-row">0.0168</td>
            <td>91.2</td>
        </tr>
        <tr>
            <td><strong>B3</strong></td>
            <td>Processo de Neutralização de pH</td>
            <td>0.0520</td>
            <td>0.0610</td>
            <td>0.0280</td>
            <td class="highlight-row">0.0215</td>
            <td>94.6</td>
        </tr>
        <tr>
            <td><strong>B4</strong></td>
            <td>Benchmark Wiener-Hammerstein</td>
            <td>0.0640</td>
            <td>0.0720</td>
            <td>0.0340</td>
            <td class="highlight-row">0.0260</td>
            <td>93.8</td>
        </tr>
        <tr>
            <td><strong>B5</strong></td>
            <td>Ressonância Não Linear Silverbox</td>
            <td>0.0924</td>
            <td>0.1129</td>
            <td>0.0120</td>
            <td class="highlight-row">0.0094</td>
            <td>90.44</td>
        </tr>
    </tbody>
</table>

<div class="alert alert-info">
<strong>Confirmação de Auditoria Numérica (Correção C):</strong> No Benchmark B5 (Silverbox), os valores numéricos estão auditados contra os registros experimentais congelados: <strong>Minimal GRU = 0,09240</strong>, <strong>ESN = 0,11290</strong>, <strong>CCN = 0,01200</strong> e <strong>LEBRE = 0,00940</strong>. A LEBRE obteve acurácia preditiva superior operando a uma média de 90,44 FLOPs/passo, perfeitamente compatível com o teto de \\(\\le 100\\) FLOPs/passo médios do regime R2-FLOP.
</div>"""

new_sec7_tables = """<h2>7.1 Suíte de Benchmarks Diagnósticos Mecanicistas (Tarefas A1–A8)</h2>
<table>
    <thead>
        <tr>
            <th>ID Tarefa</th>
            <th>Nome da Carga</th>
            <th>RZA-LMS</th>
            <th>CCN</th>
            <th>Minimal GRU</th>
            <th>Online ESN</th>
            <th>LEBRE v0.1</th>
            <th>Média FLOPs</th>
            <th>Comportamento Empírico / Invariante</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>A1</strong></td><td>Deslocamento Esparso de Suporte</td><td>0.0169</td><td>0.0185</td><td>0.7897</td><td>0.7695</td><td class="highlight-row">0.0379</td><td>205.3</td><td>RZA-LMS venceu (0,0169); LEBRE readapta a 205 FLOPs</td></tr>
        <tr><td><strong>A2</strong></td><td>Dependência com Atraso Único</td><td>1.0010</td><td>1.0109</td><td>1.0001</td><td>0.9680</td><td class="highlight-row">1.1327</td><td>97.5</td><td>Fronteira: ESN densa venceu (0,9680); escalar 1,1327</td></tr>
        <tr><td><strong>A3</strong></td><td>Atrasos Múltiplos Dispersos</td><td>1.0002</td><td>1.0107</td><td>1.0002</td><td>0.9593</td><td class="highlight-row">1.1287</td><td>97.5</td><td>Fronteira: ESN densa venceu (0,9593); escalar 1,1287</td></tr>
        <tr><td><strong>A4</strong></td><td>Escalonamento com Longo Atraso</td><td>1.0002</td><td>1.0106</td><td>1.0001</td><td>1.0005</td><td class="highlight-row">1.1356</td><td>97.4</td><td>Fronteira: GRU venceu (1,0001); escalar 1,1356</td></tr>
        <tr><td><strong>A5</strong></td><td>Memória Quiescente Set/Reset</td><td>1.0234</td><td>0.4076</td><td>1.0277</td><td>0.9990</td><td class="highlight-row">0.7901</td><td>68.4</td><td>CCN venceu (0,4076); LEBRE 0,7901; LMS/GRU falharam (&gt;1,02)</td></tr>
        <tr><td><strong>A6</strong></td><td>Roteamento de Contexto</td><td>0.5245</td><td>0.5416</td><td>0.6848</td><td>0.6036</td><td class="highlight-row">0.5668</td><td>56.3</td><td>RZA-LMS venceu (0,5245); LEBRE 0,5668 a 56,3 FLOPs</td></tr>
        <tr><td><strong>A7</strong></td><td>Quiescência Poisson Estendida</td><td>1.0185</td><td>0.6017</td><td>1.0198</td><td>1.0059</td><td class="highlight-row">0.8535</td><td>60.3</td><td>CCN venceu (0,6017); LEBRE 0,8535; LMS/GRU falharam (&gt;1,01)</td></tr>
        <tr><td><strong>A8</strong></td><td>Transição Abrupta Tri-Regime</td><td>0.9807</td><td>0.9916</td><td>0.9807</td><td>1.0209</td><td class="highlight-row">0.9540</td><td>57.6</td><td>LEBRE venceu (0,9540); escala elástica 38&rarr;92&rarr;40 FLOPs</td></tr>
    </tbody>
</table>

<h2>7.2 Suíte de Benchmarks Contínuos do Mundo Real (Tarefas B1–B5)</h2>
<table>
    <thead>
        <tr>
            <th>ID Tarefa</th>
            <th>Fluxo Contínuo</th>
            <th>RZA-LMS</th>
            <th>CCN</th>
            <th>Minimal GRU</th>
            <th>Online ESN</th>
            <th>LEBRE v0.1</th>
            <th>Média FLOPs</th>
            <th>Resultado Selado / Vencedor</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>B1</strong></td><td>Eletricidade NSW Contínua</td><td>0.9787</td><td>0.4632</td><td>2.4146</td><td>1.4238</td><td class="highlight-row">0.8364</td><td>24.0</td><td>CCN venceu (0,4632); LEBRE competitiva a 24,0 FLOPs</td></tr>
        <tr><td><strong>B2</strong></td><td>Temperatura do Clima de Jena</td><td>DIVERGIU</td><td>DIVERGIU</td><td>0.0742</td><td>0.3284</td><td class="highlight-row">0.0248</td><td>69.8</td><td>LEBRE venceu (0,0248); RZA-LMS e CCN divergiram</td></tr>
        <tr><td><strong>B3</strong></td><td>Mistura Dinâmica de Gases</td><td>0.0492</td><td>0.0390</td><td>0.0241</td><td>0.2608</td><td class="highlight-row">0.0020</td><td>79.9</td><td>LEBRE venceu (0,0020); liderou todas as baselines competitivas</td></tr>
        <tr><td><strong>B4</strong></td><td>Identificação de Sistema Silverbox</td><td>0.9993</td><td>0.9963</td><td>0.9999</td><td>0.9136</td><td class="highlight-row">0.9932</td><td>8.0</td><td>Online ESN venceu (0,9136); fronteira documentada de estado escalar</td></tr>
        <tr><td><strong>B5</strong></td><td>Demanda Elétrica Residencial</td><td>0.0912</td><td>0.0120</td><td>0.0924</td><td>0.1129</td><td class="highlight-row">0.0040</td><td>28.3</td><td>LEBRE venceu (0,0040); liderou CCN (0,0120) e GRU (0,0924)</td></tr>
    </tbody>
</table>

<div class="alert alert-info">
<strong>Confirmação de Auditoria Numérica (Correção C):</strong> No Bloco B do benchmark, todas as identidades de tarefas e métricas numéricas foram verificadas diretamente contra os artefatos selados legíveis por máquina (<code>BENCH_01B_AGGREGATE_SUMMARY.csv</code>). Na Tarefa B5 (Demanda Elétrica Residencial), a LEBRE liderou todas as baselines com <strong>0,00403 NMSE</strong> (28,30 FLOPs/passo médios, 248 bytes de RAM). Na Tarefa B4 (Identificação de Sistema Silverbox), a Online ESN obteve <strong>0,91359 NMSE</strong> enquanto a LEBRE operou em <strong>0,99320 NMSE</strong> (8,00 FLOPs/passo, 208 bytes de RAM), confirmando a fronteira de viés indutivo documentada onde reservatórios densos aleatórios superam estados escalares mínimos em dinâmicas físicas não lineares contínuas multi-frequenciais.
</div>"""

if old_sec7_tables in text:
    text = text.replace(old_sec7_tables, new_sec7_tables)
    print("PT-BR Section 7 tables replaced successfully.")
else:
    print("Warning: old_sec7_tables not found exactly in PT-BR.")

with open("scratch/build_ptbr_html.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated scratch/build_ptbr_html.py written successfully.")
