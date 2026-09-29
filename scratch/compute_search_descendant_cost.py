#!/usr/bin/env python3
"""
compute_search_descendant_cost.py

Aggregates descendant probation costs by cell class from DENSE_CELL_PROVENANCE.csv
and DENSE_GRID_UTILIZATION_AUDIT.csv.
Outputs SEARCH_DESCENDANT_COST.csv in the experiment directory.
"""

import os
import pandas as pd
import numpy as np

EXP_DIR = "experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01"

df_prov = pd.read_csv(os.path.join(EXP_DIR, "DENSE_CELL_PROVENANCE.csv"))
df_util = pd.read_csv(os.path.join(EXP_DIR, "DENSE_GRID_UTILIZATION_AUDIT.csv"))

# FLOP constants from sealed compute model:
# Probation duration = 50 steps
# Per probation episode:
# - Forward: 50 * 1 = 50 FLOPs
# - Observation: (50 / 5) * 1 = 10 FLOPs
# - Learning: (50 / 10) * 2 = 10 FLOPs
# Total probation FLOPs per born candidate = 70 FLOPs (if rejected after full probation)
# Probe cost per visit = 4 FLOPs
PROBATION_FLOPS_PER_CANDIDATE = 70.0 # Failed probation
PROBE_FLOPS_PER_VISIT = 4.0

# Group by cell class
class_summary = []
grouped = df_prov.groupby('cell_class')

total_visits_all = df_prov['total_visits'].sum()
total_births_all = df_prov['candidate_births'].sum()
total_promotions_all = df_prov['promotions'].sum()

for c_class, grp in grouped:
    n_cells = len(grp)
    tot_visits = grp['total_visits'].sum()
    tot_crossings = grp['threshold_crossings'].sum()
    tot_births = grp['candidate_births'].sum()
    tot_prom = grp['promotions'].sum()
    tot_top1 = grp['top1_steps'].sum()
    
    direct_probe_fp = tot_visits * PROBE_FLOPS_PER_VISIT
    # Failed probation births = births - promotions
    failed_births = max(0, tot_births - tot_prom)
    descendant_failed_fp = failed_births * PROBATION_FLOPS_PER_CANDIDATE
    descendant_promoted_fp = tot_prom * PROBATION_FLOPS_PER_CANDIDATE
    total_descendant_fp = descendant_failed_fp + descendant_promoted_fp
    total_cell_cost_fp = direct_probe_fp + total_descendant_fp
    
    descendant_to_direct_ratio = total_descendant_fp / direct_probe_fp if direct_probe_fp > 0 else 0.0
    spurious_waste_fraction = descendant_failed_fp / total_descendant_fp if total_descendant_fp > 0 else 0.0
    
    class_summary.append({
        'cell_class': c_class,
        'cell_count': n_cells,
        'fraction_of_total_cells': n_cells / 160.0,
        'total_visits': tot_visits,
        'direct_probe_flops': direct_probe_fp,
        'threshold_crossings': tot_crossings,
        'candidate_births': tot_births,
        'promotions': tot_prom,
        'failed_probations': failed_births,
        'descendant_failed_probation_flops': descendant_failed_fp,
        'descendant_promoted_probation_flops': descendant_promoted_fp,
        'total_descendant_flops': total_descendant_fp,
        'total_cell_cost_flops': total_cell_cost_fp,
        'descendant_to_direct_ratio': descendant_to_direct_ratio,
        'spurious_waste_fraction': spurious_waste_fraction,
        'mean_descendant_flops_per_cell': total_descendant_fp / n_cells
    })

df_desc = pd.DataFrame(class_summary).sort_values(by='total_descendant_flops', ascending=False)
out_path = os.path.join(EXP_DIR, "SEARCH_DESCENDANT_COST.csv")
df_desc.to_csv(out_path, index=False)
print(f"Wrote {out_path}")
print(df_desc[['cell_class', 'cell_count', 'candidate_births', 'promotions', 'total_descendant_flops', 'spurious_waste_fraction']])
