# Notas de execução — diagnóstico do Chile

## 1. Antes da execução (25/10/2026)

- **Arquivo novo (H3):** `07_CAMELS_BR_potential_evapotransp.zip` do CAMELS-BR 1.2 (Zenodo 15025488, CC-BY-4.0),
  SHA-256 `c5f222c80aa0d95440d3419ca91e004f7c40224e6562bfc5139f20b0b1ae79fd`. **Desvio de local:** gravado em
  `data/external_v056/camels_br_pet/`, e não em `data/external_v052/camels_br/` como dizia o plano, para não alterar a
  pasta registrada da v0.52. Lido só o cabeçalho: `year month day pet_gleam pet_era5land`.
- **Coluna escolhida: `pet_gleam`.** Nenhuma das duas é uma fórmula só de temperatura. A `pet_gleam` é do mesmo produto
  (GLEAM) da evapotranspiração real usada até aqui (`aet_gleam`), então a troca isola "real contra potencial", que é o
  que H3 pergunta.
