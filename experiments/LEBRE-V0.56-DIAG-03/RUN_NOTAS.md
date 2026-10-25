# Notas de execução — diagnóstico do Chile

## 1. Antes da execução (25/10/2026)

- **Arquivo novo (H3):** `07_CAMELS_BR_potential_evapotransp.zip` do CAMELS-BR 1.2 (Zenodo 15025488, CC-BY-4.0),
  SHA-256 `c5f222c80aa0d95440d3419ca91e004f7c40224e6562bfc5139f20b0b1ae79fd`. **Desvio de local:** gravado em
  `data/external_v056/camels_br_pet/`, e não em `data/external_v052/camels_br/` como dizia o plano, para não alterar a
  pasta registrada da v0.52. Lido só o cabeçalho: `year month day pet_gleam pet_era5land`.
- **Coluna escolhida: `pet_gleam`.** Nenhuma das duas é uma fórmula só de temperatura. A `pet_gleam` é do mesmo produto
  (GLEAM) da evapotranspiração real usada até aqui (`aet_gleam`), então a troca isola "real contra potencial", que é o
  que H3 pergunta.

## 2. Execução (25/10/2026)

`diag_chile.py run`: 50 de 50 tarefas sem erro; `diag_chile.py analise`: resultado em `DIAG_CHILE_RESULTADO.json`.

## 3. Adendo declarado antes de rodar: qual economia derruba o ganho no Chile

O resultado mostrou que a correção completa (C0: RLS a cada passo, 5 bandas) melhora a v0.55 em 7,5% nas bacias de CL-V,
enquanto a versão barata (C5: a cada 4, 3 bandas) quase não melhora. Para separar as duas economias, rodam nas mesmas
20 bacias de CL-V as variantes intermediárias do `LEBRE-V0.56-DEV-01`, todas com 3 defasagens do alvo e sem recorte:
C1 (a cada 2, 5 bandas), C2 (a cada 4, 5 bandas), C3 (a cada 1, 3 bandas) e C4 (a cada 2, 3 bandas). Leitura
descritiva: razão v0.55 ÷ variante, com o mesmo bootstrap e a mesma semente do diagnóstico (índices de contraste
próprios). Só exploratório: as bacias de CL-V já foram gastas; nada aqui escolhe uma candidata.
