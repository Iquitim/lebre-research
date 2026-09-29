"""Revision 1, layout step: move the revision note from §1 to a 'revision history' box at the end of §14 and add one cover line
(the note in §1 pushed the document guide onto an extra page). Kept for provenance."""
import os

H = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(H, "v051r1_text.py")
s = open(p, encoding="utf-8").read()

a = s.index('<div class="alert alert-info"><strong>{T("Revisão 1", "Revision 1")}:</strong>')
b = s.index('<div class="alert alert-warning"><strong>{T("Premissa", "Premise")}:</strong>')
note = s[a:b].strip()
s = s[:a] + s[b:]

old = '''out.append(f"""<h1>14. {toc[13]}</h1><ul>{''.join(f'<li>{x}</li>' for x in lim)}</ul>""")'''
assert s.count(old) == 1
new = '''out.append(f"""<h1>14. {toc[13]}</h1><ul>{''.join(f'<li>{x}</li>' for x in lim)}</ul>
<h2>{T("Histórico de revisões", "Revision history")}</h2>
''' + note + '''""")'''
s = s.replace(old, new)

for a_, b_ in [('("Status", "versão de pesquisa promovida por avaliação pré-registrada")]',
                '("Status", "versão de pesquisa promovida por avaliação pré-registrada"), ("Revisão", "1 — correções de texto; arquitetura e resultados inalterados (§14)")]'),
               ('("Status", "research version promoted by pre-registered evaluation")]',
                '("Status", "research version promoted by pre-registered evaluation"), ("Revision", "1 — text corrections; architecture and results unchanged (§14)")]')]:
    assert s.count(a_) == 1, a_
    s = s.replace(a_, b_)
open(p, "w", encoding="utf-8").write(s)
print("ok")
