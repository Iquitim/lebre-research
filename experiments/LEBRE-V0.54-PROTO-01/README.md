# LEBRE v0.54 — protótipo de desenvolvimento

`lebre054/` parte da biblioteca publicada `lebre==0.2.0` (a v0.53, idêntica ao protótipo promovido): os arquivos copiados
estão listados com SHA-256 em `SHA256_COPIAS.txt` e não são editados. As mudanças da v0.54 ficam em arquivos novos:

- `dormancy.py` — M5a, rascunho 0 (`experiments/LEBRE-V0.54-DESIGN-NOTE-01/ALGORITHM_SPEC_DRAFT_M5a.md`): a M1 dormente
  enquanto não pesa;
- `model054.py` — `Lebre054`, mesma interface de `lebre.Lebre`; `m5a=False` reproduz a v0.53.

Testes (precisam de `lebre==0.2.0` instalada como referência): `python -m pytest -q tests`.
