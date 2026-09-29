# Toolchain

| Tool | Version | Used for | How to obtain |
|---|---|---|---|
| CPython | 3.11.9 | Everything in Python | python.org / Microsoft Store build used on the original machine |
| zig cc (Python package `ziglang`) | 0.16.0 | Host build of the C99 port (`lebre_c/build_host.sh`) | `pip install ziglang==0.16.0` |
| xPack GNU Arm Embedded GCC | 15.2.1-1.1 | Cortex-M4F firmware (`mcu/build_run.sh`) | `tools/gcc.zip` (see `tools/README.md`) |
| Renode (portable) | 1.17.0 | STM32F4 / Cortex-M4F simulation with DWT counter | `tools/renode.zip` (see `tools/README.md`) |
| Microsoft Edge (headless) | system version | HTML → PDF of the specifications | installed with Windows |
| Git Bash | Git for Windows 2.49 | shell scripts (`*.sh`) | git-scm.com |

Firmware flags: `-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -O2 -ffp-contract=off -std=c99`. Renode: `cpu PerformanceInMips 168` with a DWT at 168 MHz, so the cycle counter counts executed instructions (see `experiments/LEBRE-V0.52-EXT-01/EXT_LOG.md`).
