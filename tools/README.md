# tools/ (not in git)

Toolchains for the simulated-microcontroller measurements. The archives are kept out of git. Their exact SHA-256 values are in `ARTIFACTS_MANIFEST.tsv`.

| Archive | Unpacked to | Upstream |
|---|---|---|
| `tools/gcc.zip` (SHA-256 `bae6a3d1667697ce750c3b13d6d26d80973ecedc2cc87bf04869e83447fd93ea`) | `tools/gcc/xpack-arm-none-eabi-gcc-15.2.1-1.1/` | https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack/releases (v15.2.1-1.1, win32-x64) |
| `tools/renode.zip` (SHA-256 `18bcf145422039e8702c3e5f9864c7787561bfd5deb7a3ee6e168ecf19e2b9db`) | `tools/renode/renode_1.17.0-portable/` | https://github.com/renode/renode/releases (1.17.0, portable Windows) |

The build scripts expect exactly these unpacked paths (`experiments/LEBRE-V0.52-EXT-01/mcu/build_run.sh`).
