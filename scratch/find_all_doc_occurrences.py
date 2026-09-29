import os, glob, re

target_files = [
    'docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md',
    'docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md',
    'docs/architecture/LEBRE_OVERVIEW_EN.md',
    'docs/architecture/LEBRE_OVERVIEW_PTBR.md',
    'docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md',
    'docs/architecture/LEBRE_ARCHITECTURAL_DECISIONS.md',
    'docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml',
    'docs/architecture/LEBRE_CONSTANT_TRACEABILITY.md',
    'scratch/build_en_html.py',
    'scratch/build_ptbr_html.py',
    'docs/architecture/pdf_source/LEBRE_CONDENSED_EN.html',
    'docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html'
]

patterns = [
    (r'\bfour[\s-]states?\b', 'four_state'),
    (r'\bfour[\s-]phases?\b', 'four_phase'),
    (r'\bquatro[\s-]estados\b', 'quatro_estados'),
    (r'\bquatro[\s-]fases\b', 'quatro_fases'),
    (r'\bgarant[ea](?:s|ndo|do|da|dos|das|m)?\b|\bgarantia\b', 'garante'),
    (r'\bjamais\b', 'jamais'),
    (r'\bnunca\b', 'nunca'),
    (r'\bsempre\b', 'sempre'),
    (r'\bstrictly[\s-]bounded\b|\bstrict[\s-]bound\b|\bhard[\s-]bound\b', 'strictly_bounded'),
    (r'\bflawless\b', 'flawless'),
    (r'\bperfect\b', 'perfect'),
    (r'\bguarantee[ds]?\b', 'guarantee'),
    (r'440(?:\.0)?\s*bytes?', '440_bytes'),
    (r'100\s*flops?(?:/step|/passo)?', '100_flops')
]

for filepath in target_files:
    if not os.path.exists(filepath):
        print(f"NOT FOUND: {filepath}")
        continue
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    print(f"\n==========================================")
    print(f"FILE: {filepath} ({len(lines)} lines)")
    print(f"==========================================")
    for idx, line in enumerate(lines, 1):
        for pat, name in patterns:
            m = re.search(pat, line, re.IGNORECASE)
            if m:
                # safe print
                txt = line.strip().encode('ascii', errors='replace').decode('ascii')
                print(f"  L{idx} [{name}]: {txt[:140]}")
