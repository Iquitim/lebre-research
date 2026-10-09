# Nota de segurança: caminhos locais em arquivos do repositório (09/10/2026)

**O que foi encontrado:** 42 arquivos com caminhos absolutos da máquina de desenvolvimento (estrutura de pastas, na forma
`<unidade>:/<pasta>/Codinome Lebre/...`). Nenhum arquivo, no estado atual nem em nenhum commit do histórico, contém o
caminho da pasta de usuário do sistema operacional. Um log da avaliação final da v0.53 com caminhos foi enviado e corrigido
no mesmo dia (o commit foi substituído).

**Decisão do responsável pelo projeto:**
- **33 arquivos limpos** neste commit: em scripts `.py`, a raiz absoluta do repositório virou `.` (relativo à raiz, para
  que continuem funcionando de lá); em documentos e logs, virou `<lebre-research>` (ou `<lebre-lab>`).
- **9 arquivos mantidos como estão**, porque fazem parte do congelamento da v0.52 (seus SHA-256 estão nos manifestos de
  congelamento, e a regra do projeto é nunca editar arquivos congelados):
  - `experiments/LEBRE-V0.52-EXT-01/mcu/renode_bdg2.log`
  - `experiments/LEBRE-V0.52-EXT-01/mcu/renode_camels.log`
  - `experiments/LEBRE-V0.52-EXT-01/mcu/renode_ons_vg.log`
  - `experiments/LEBRE-V0.52-EXT-01/mcu/renode_r3_1.log`
  - `experiments/LEBRE-V0.52-EXT-01/mcu/renode_r3_2.log`
  - `experiments/LEBRE-V0.52-EXT-01/mcu/renode_r3_3.log`
  - `experiments/LEBRE-V0.52-EXT-01/mcu/renode_r3_4.log`
  - `experiments/LEBRE-V0.52-EXT-01/mcu/run_ons_vg.resc`
  - `experiments/LEBRE-V0.52-HELDOUT-03/MCU.log`
- O histórico do repositório não foi reescrito (só estrutura de pastas exposta, sem dados pessoais; reescrever mudaria
  todos os hashes de commit citados em documentos, no artigo e nas releases).

**Prevenção:** logs com mensagens de erro do Python contêm caminhos absolutos; são sanitizados antes de qualquer commit.
