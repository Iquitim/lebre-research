"""cycles_estimate.py — estimates Cortex-M4F cycles from a Renode execution trace (Disassembly format), because Renode
counts instructions but does not model the pipeline. Per-instruction cycle costs follow the Cortex-M4 Technical Reference
Manual (processor instruction timing) and the FPv4-SP FPU timing tables, with fixed assumptions:
  data processing, multiply, multiply-accumulate (32-bit), IT: 1 ; SDIV/UDIV: 7 (range 2-12)
  LDR* single: 2 ; STR* single: 1 ; LDRD/STRD: 3 ; LDM/STM/PUSH/POP: 1 + N registers (+2 if PC is loaded)
  branch taken (B, Bcc, CBZ/CBNZ): 3 (1 + refill 2) ; not taken: 1 ; BL: 4 ; BX/BLX: 3
  VADD/VSUB/VMUL/VNEG/VABS/VCMP/VCVT/VMOV/VMRS: 1 ; VMLA/VMLS/VNMLA/VNMLS/VFMA/VFMS: 3 ; VDIV/VSQRT: 14
  VLDR/VSTR: 2 ; VLDM/VSTM/VPUSH/VPOP: 1 + N registers
Flash wait states are assumed hidden by the prefetch/ART accelerator (zero-wait execution), a documented approximation.
A branch is taken when the next traced PC differs from PC + instruction size. Usage: cycles_estimate.py <trace.txt>"""
import re
import sys
from collections import Counter

ALU = set("mov movs movw movt mvn mvns add adds adc adcs sub subs sbc sbcs rsb rsbs cmp cmn tst teq and ands orr orrs eor eors bic bics "
          "orn lsl lsls lsr lsrs asr asrs ror rors rrx uxtb uxth sxtb sxth ubfx sbfx bfi bfc clz rev rev16 revsh mul muls mla mls "
          "umull smull umlal smlal adr it ite itt itte ittt itee iteee ittee itet nop usat ssat uadd8 sel".split())


def regs(ops):
    m = re.search(r"\{([^}]*)\}", ops)
    if not m:
        return 1
    n = 0
    for part in m.group(1).split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-"); n += int(re.sub(r"\D", "", b)) - int(re.sub(r"\D", "", a)) + 1
        elif part:
            n += 1
    return n


def cost(mn, ops, taken):
    base = mn.split(".")[0]
    b = re.sub(r"(eq|ne|cs|hs|cc|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)$", "", base) if base not in ALU else base
    if b in ALU or base.startswith("it"):
        return 1, "alu"
    if b in ("sdiv", "udiv"):
        return 7, "div"
    if b in ("b", "cbz", "cbnz"):
        return (3 if taken else 1), "branch"
    if b in ("bl",):
        return 4, "call"
    if b in ("bx", "blx"):
        return 3, "call"
    if b in ("ldrd", "strd"):
        return 3, "ldst"
    if b in ("ldm", "ldmia", "ldmdb", "pop"):
        return 1 + regs(ops) + (2 if "pc" in ops else 0), "ldst"
    if b in ("stm", "stmia", "stmdb", "push"):
        return 1 + regs(ops), "ldst"
    if b.startswith("ldr"):
        return 2, "ldst"
    if b.startswith("str"):
        return 1, "ldst"
    if b in ("vdiv", "vsqrt"):
        return 14, "fpdiv"
    if b in ("vmla", "vmls", "vnmla", "vnmls", "vfma", "vfms", "vfnma", "vfnms"):
        return 3, "fpmac"
    if b in ("vldr", "vstr"):
        return 2, "fpldst"
    if b.startswith(("vldm", "vstm", "vpush", "vpop")):
        return 1 + regs(ops), "fpldst"
    if b.startswith("v"):
        return 1, "fp"
    return 1, "other:" + b


if __name__ == "__main__":
    rows = []
    rx = re.compile(r"^0x([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*([^\[]*)")
    with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
        for line in f:
            m = rx.match(line.strip())
            if m:
                rows.append((int(m.group(1), 16), len(m.group(2)) // 2, m.group(3).lower(), m.group(4).strip().lower()))
    cyc, cls, other = 0, Counter(), Counter()
    for j, (pc, size, mn, ops) in enumerate(rows):
        taken = j + 1 < len(rows) and rows[j + 1][0] != pc + size
        c, k = cost(mn, ops, taken)
        cyc += c; cls[k] += c
        if k.startswith("other"):
            other[k] += 1
    n = len(rows)
    print(f"instructions {n}  estimated cycles {cyc}  CPI {cyc / n:.3f}")
    print("cycles by class:", {k: f"{v / cyc:.1%}" for k, v in cls.most_common()})
    if other:
        print("unclassified (counted as 1 cycle):", dict(other.most_common(10)))
