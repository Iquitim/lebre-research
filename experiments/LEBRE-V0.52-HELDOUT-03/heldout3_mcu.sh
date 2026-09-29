#!/usr/bin/env bash
# heldout3_mcu.sh — PRE-REGISTERED: the float32 C port on the simulated Cortex-M4F (Renode STM32F4 + DWT) over the first two
# CAMELS-BR and the first two BDG2 series of RESERVA3.json (list order). Output: mcu/<tag>.txt (UART report of the firmware).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; MCU="$HERE/../LEBRE-V0.52-EXT-01/mcu"; mkdir -p "$HERE/mcu"
TASKS=$(cd "$HERE" && python -c "import json; R=json.load(open('RESERVA3.json', encoding='utf-8')); print(chr(10).join(['camels:%d' % g for g in R['camels_br'][:2]] + ['bdg2:' + m for m in R['bdg2'][:2]]))")
i=0
while IFS= read -r t; do
  i=$((i+1)); tag="r3_$i"
  "$MCU/build_run.sh" "$t" "$tag" final < /dev/null > /dev/null 2>&1 || true
  { echo "TASK=$t"; cat "$MCU/uart_$tag.txt"; } > "$HERE/mcu/$tag.txt"
  echo "$t -> $(grep -c END "$HERE/mcu/$tag.txt") report"
done <<< "$TASKS"
