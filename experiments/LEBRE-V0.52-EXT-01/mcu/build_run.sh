#!/usr/bin/env bash
# build_run.sh <task> <tag> — builds the firmware for one development series and runs it in Renode (headless)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; TOOLS="$HERE/../../../tools"
GCC="$TOOLS/gcc/xpack-arm-none-eabi-gcc-15.2.1-1.1/bin"; RENODE="$TOOLS/renode/renode_1.17.0-portable"
cd "$HERE"; PYTHONIOENCODING=utf-8 python gen_data.py "$1" ${3:-} > /dev/null
CF="-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -O2 -ffp-contract=off -DLB_FLOAT -DREAL=float -std=c99 -ffunction-sections -fdata-sections"
"$GCC/arm-none-eabi-gcc" $CF -c ../lebre_c/lebre052.c -o lebre052.o
"$GCC/arm-none-eabi-gcc" $CF -c main.c -o main.o
"$GCC/arm-none-eabi-gcc" $CF -c startup.c -o startup.o
"$GCC/arm-none-eabi-gcc" $CF -T link.ld -nostartfiles --specs=nano.specs -Wl,--gc-sections -Wl,-Map=fw_$2.map startup.o main.o lebre052.o -lm -lc -lnosys -o fw_$2.elf
"$GCC/arm-none-eabi-size" -A fw_$2.elf | grep -E "^\.(text|data|bss) " > size_$2.txt
W="/tmp/claude/lebre_mcu"; mkdir -p "$W"; cp fw_$2.elf platform.repl "$W/"
rm -f "$W/uart_$2.txt"
cat > "$W/run_$2.resc" <<RESC
using sysbus
mach create "lebre"
machine LoadPlatformDescription @$(cygpath -w "$W/platform.repl")
cpu PerformanceInMips 168
sysbus LoadELF @$(cygpath -w "$W/fw_$2.elf")
usart2 CreateFileBackend @$(cygpath -w "$W/uart_$2.txt") true
${TRACE_PRE:-}emulation RunFor "00:00:40"
cpu ExecutedInstructions
quit
RESC
(cd "$RENODE" && timeout 900 ./renode.exe --console --disable-gui -e "include @$(cygpath -w "$W/run_$2.resc")" > "$HERE/renode_$2.log" 2>&1) || true
cp "$W/uart_$2.txt" "$HERE/" 2>/dev/null; cat "$HERE/uart_$2.txt" 2>/dev/null
