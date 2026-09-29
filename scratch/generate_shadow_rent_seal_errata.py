import os
import sys

# Delegate to experiments/LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01/generate_shadow_rent_seal_errata.py
target_script = os.path.join(
    os.path.abspath('.'),
    'experiments',
    'LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01',
    'generate_shadow_rent_seal_errata.py'
)

if os.path.exists(target_script):
    import importlib.util
    spec = importlib.util.spec_from_file_location("generate_shadow_rent_seal_errata", target_script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run_reconciliation()
else:
    print(f"Error: Could not locate {target_script}")
    sys.exit(1)
