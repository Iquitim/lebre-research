#!/usr/bin/env bash
# build_profile.sh <task> <tag> — documentation profile on a DEVELOPMENT series: same frozen-port model code (EXT-01
# lebre_c/lebre052.c, unchanged), same compiler flags and simulator as EXT-01 build_run.sh; main_profile.c adds per-block output.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; EXT="$HERE/../../LEBRE-V0.52-EXT-01"; TOOLS="$HERE/../../../tools"
GCC="$TOOLS/gcc/xpack-arm-none-eabi-gcc-15.2.1-1.1/bin"; RENODE="$TOOLS/renode/renode_1.17.0-portable"
cd "$EXT/mcu"; PYTHONIOENCODING=utf-8 python gen_data.py "$1" > /dev/null; cd "$HERE"
CF="-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -O2 -ffp-contract=off -DLB_FLOAT -DREAL=float -std=c99 -ffunction-sections -fdata-sections"
"$GCC/arm-none-eabi-gcc" $CF -c "$EXT/lebre_c/lebre052.c" -o lebre052.o
"$GCC/arm-none-eabi-gcc" $CF -c main_profile.c -o main.o
"$GCC/arm-none-eabi-gcc" $CF -c "$EXT/mcu/startup.c" -o startup.o
"$GCC/arm-none-eabi-gcc" $CF -T "$EXT/mcu/link.ld" -nostartfiles --specs=nano.specs -Wl,--gc-sections startup.o main.o lebre052.o -lm -lc -lnosys -o fw_$2.elf
W="/tmp/claude/lebre_doc"; mkdir -p "$W"; cp fw_$2.elf "$EXT/mcu/platform.repl" "$W/"; rm -f "$W/uart_$2.txt"
cat > "$W/run_$2.resc" <<RESC
using sysbus
mach create "lebre"
machine LoadPlatformDescription @$(cygpath -w "$W/platform.repl")
cpu PerformanceInMips 168
sysbus LoadELF @$(cygpath -w "$W/fw_$2.elf")
usart2 CreateFileBackend @$(cygpath -w "$W/uart_$2.txt") true
emulation RunFor "00:00:45"
quit
RESC
(cd "$RENODE" && timeout 1200 ./renode.exe --console --disable-gui -e "include @$(cygpath -w "$W/run_$2.resc")" > "$HERE/renode_$2.log" 2>&1) || true
cp "$W/uart_$2.txt" "$HERE/profile_$2.txt"; head -20 "$HERE/profile_$2.txt"
