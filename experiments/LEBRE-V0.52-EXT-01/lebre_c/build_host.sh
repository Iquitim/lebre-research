#!/usr/bin/env bash
# build_host.sh — builds the host (PC) shared libraries of the C99 port used by equiv_test.py and the reserve-3 run.
# Toolchain: zig cc 0.16.0 via the Python package `ziglang` (pip install ziglang==0.16.0). Command recorded from EXT-01.
set -e
cd "$(dirname "$0")"
python -m ziglang cc -O2 -std=c99 -shared -o lebre052_f64.dll lebre052.c api.c
python -m ziglang cc -O2 -std=c99 -DLB_FLOAT -DREAL=float -shared -o lebre052_f32.dll lebre052.c api.c
echo "built lebre052_f64.dll and lebre052_f32.dll"
