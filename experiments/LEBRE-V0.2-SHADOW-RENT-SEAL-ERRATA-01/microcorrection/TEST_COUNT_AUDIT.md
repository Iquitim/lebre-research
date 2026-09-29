# Test Count & Suite Hierarchy Audit

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01/microcorrection`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Errata Reference:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Focus Inquiry:** Definitive Disambiguation of "57 passed" vs. "124 tests" in Canonical Regression Suite  
**Author:** Independent Skeptical Senior Reviewer  
**Date:** September 22, 2026  

---

## 1. Executive Summary & Problem Identification

Across LEBRE project documentation, contradictory statements have appeared regarding test suite volume:
- `RESOURCE_COMPACTION_SEAL_FINAL_REPORT.md` (Section 1, Line 18) reported:  
  > *"Canonical Codebase Bitwise Immutable: Zero modifications were made to `src/` (37 files) or `tests/` (57 tests passing)."*
- Other reports and contemporary audit summaries cite **124 tests**.

This audit executed deterministic software verification using both `pytest` and Python's standard `unittest` discovery runner to establish the exact provenance of both numbers.

---

## 2. Forensic Discovery: Root Cause of the 57 vs. 124 Discrepancy

The discrepancy arises entirely from the difference in test runner discovery mechanisms:

### 2.1 The 57 Count: `unittest` Runner Discovery
When executing Python's built-in `unittest` test discovery:
```bash
python -m unittest discover tests
```
The runner searches exclusively for classes inheriting from `unittest.TestCase`. Across `tests/`, there are exactly **9 test files** defining `unittest.TestCase` classes containing exactly **57 test methods**:

1. `test_exp_0001b.py` (`TestEXP0001b`): 9 test methods
2. `test_exp_0001d.py` (`TestEXP0001d`): 7 test methods
3. `test_exp_0002.py` (`TestEXP0002`): 8 test methods
4. `test_exp_0003.py` (`TestEXP0003`): 6 test methods
5. `test_exp_0004.py` (`TestEXP0004`): 6 test methods
6. `test_exp_0005.py` (`TestEXP0005`): 6 test methods
7. `test_exp_0006.py` (`TestEXP0006`): 5 test methods
8. `test_m2_exp_0006.py` (`TestM2Exp0006`): 5 test methods
9. `test_m2_r1.py` (`TestM2R1`): 5 test methods
$$\sum \text{unittest methods} = 9 + 7 + 8 + 6 + 6 + 6 + 5 + 5 + 5 = \mathbf{57 \text{ tests}}$$

Output from `python -m unittest discover tests`:
```
.........................................................
----------------------------------------------------------------------
Ran 57 tests in 0.734s

OK
```
`unittest discover` **completely ignores** the 11 test files that define standalone pytest functions (`def test_*()`). The author of `RESOURCE_COMPACTION_SEAL_FINAL_REPORT.md` used `python -m unittest discover tests` and reported the resulting "57 tests passing".

### 2.2 The 124 Count: `pytest` Comprehensive Discovery
When executing `pytest`:
```bash
python -m pytest tests/
```
The `pytest` runner discovers **both** `unittest.TestCase` classes (57 methods) and all standalone functions matching `test_*` (67 functions) across all 20 test files:

$$\text{Pytest Items} = 57 \text{ (unittest TestCase methods)} + 67 \text{ (standalone functions)} = \mathbf{124 \text{ collected test items}}$$

---

## 3. Comprehensive Test Inventory by File

```
+------------------------------------+-------------------------+----------------------+--------------------+
| Test Filename                      | Test Structure Pattern  | Discovered by unittest| Discovered by pytest|
+------------------------------------+-------------------------+----------------------+--------------------+
| test_bench_01_protocol.py          | Standalone functions    |          0           |         8          |
| test_exp_0001b.py                  | unittest.TestCase       |          9           |         9          |
| test_exp_0001d.py                  | unittest.TestCase       |          7           |         7          |
| test_exp_0002.py                   | unittest.TestCase       |          8           |         8          |
| test_exp_0003.py                   | unittest.TestCase       |          6           |         6          |
| test_exp_0004.py                   | unittest.TestCase       |          6           |         6          |
| test_exp_0005.py                   | unittest.TestCase       |          6           |         6          |
| test_exp_0006.py                   | unittest.TestCase       |          5           |         5          |
| test_exp_0007.py                   | Standalone functions    |          0           |         5          |
| test_exp_0008.py                   | Standalone functions    |          0           |         4          |
| test_exp_0009.py                   | Standalone functions    |          0           |         4          |
| test_exp_0010.py                   | Standalone functions    |          0           |         4          |
| test_m1_r1.py                      | Standalone functions    |          0           |         4          |
| test_m2_exp_0001.py                | Standalone functions    |          0           |         8          |
| test_m2_exp_0002.py                | Standalone functions    |          0           |         8          |
| test_m2_exp_0003.py                | Standalone functions    |          0           |         7          |
| test_m2_exp_0004.py                | Standalone functions    |          0           |         6          |
| test_m2_exp_0005.py                | Standalone functions    |          0           |         9          |
| test_m2_exp_0006.py                | unittest.TestCase       |          5           |         5          |
| test_m2_r1.py                      | unittest.TestCase       |          5           |         5          |
+------------------------------------+-------------------------+----------------------+--------------------+
| TOTALS (20 Test Files)             | Mixed Paradigm          |         57           |       124          |
+------------------------------------+-------------------------+----------------------+--------------------+
```

---

## 4. Deterministic Verification Output

Execution of the canonical regression suite on September 22, 2026 yielded:

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0
rootdir: D:\Projetos\Codinome Lebre
plugins: asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT
collected 124 items

tests\test_bench_01_protocol.py ........                                 [  6%]
tests\test_exp_0001b.py .........                                        [ 13%]
tests\test_exp_0001d.py .......                                          [ 19%]
tests\test_exp_0002.py ........                                          [ 25%]
tests\test_exp_0003.py ......                                            [ 30%]
tests\test_exp_0004.py ......                                            [ 35%]
tests\test_exp_0005.py ......                                            [ 40%]
tests\test_exp_0006.py .....                                             [ 44%]
tests\test_exp_0007.py .....                                             [ 48%]
tests\test_exp_0008.py ....                                              [ 51%]
tests\test_exp_0009.py ....                                              [ 54%]
tests\test_exp_0010.py ....                                              [ 58%]
tests\test_m1_r1.py ....                                                 [ 61%]
tests\test_m2_exp_0001.py ........                                       [ 67%]
tests\test_m2_exp_0002.py ........                                       [ 74%]
tests\test_m2_exp_0003.py .......                                        [ 79%]
tests\test_m2_exp_0004.py ......                                         [ 84%]
tests\test_m2_exp_0005.py .........                                      [ 91%]
tests\test_m2_exp_0006.py .....                                          [ 95%]
tests\test_m2_r1.py .....                                                [100%]

============================= 124 passed in 2.65s =============================
```

---

## 5. Formal Machine-Readable Ledger

```
TEST_FILES_DISCOVERED = 20
PYTEST_ITEMS_COLLECTED = 124
PYTEST_ITEMS_EXECUTED = 124
PYTEST_ITEMS_PASSED = 124
PYTEST_ITEMS_FAILED = 0
PYTEST_ITEMS_SKIPPED = 0
UNITTEST_ITEMS_DISCOVERED = 57
```

### Binding Normative Directive
Henceforth, in all LEBRE project documentation:
- The full regression suite shall be designated as **"124 test items across 20 test files"**.
- The phrase "57 tests" shall be retired or qualified explicitly as *"57 legacy unittest.TestCase methods"*.
- It is strictly prohibited to refer to the 20 test files as "57 files".
