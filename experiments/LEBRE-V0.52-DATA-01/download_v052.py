#!/usr/bin/env python3
"""download_v052.py — reproducible download of the public input-driven datasets selected in DATASET_SELECTION.md.

Writes everything under data/external_v052/<source>/, skips files already present, and records for every file its
source URL, licence, size and SHA-256 in data/external_v052/MANIFEST.csv and data/external_v052/SHA256SUMS.txt.
Nothing is transformed here: files are stored exactly as published.
"""
import csv
import hashlib
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "data", "external_v052")
UA = {"User-Agent": "Mozilla/5.0 (research download; LEBRE project)"}

LIC_ONS = "CC-BY (ONS Dados Abertos)"
LIC_CAMELS = "CC-BY-4.0 (Chagas et al. 2020, ESSD; Zenodo 15025488 v1.2)"
LIC_BDG2 = "CC-BY-4.0 (Miller et al. 2020, Scientific Data; Zenodo 3887306)"
LIC_TANKS = "CC-BY-SA-4.0 (Schoukens, Mattsson, Wigren & Noel; 4TU doi:10.4121/12960104)"
LIC_WH = "no explicit licence; research use with citation (Schoukens, Suykens & Ljung, SYSID 2009) — DEVELOPMENT ONLY"


def ckan_resources(dataset_id, fmt):
    url = f"https://dados.ons.org.br/api/3/action/package_show?id={dataset_id}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        res = json.load(r)["result"]["resources"]
    return [x["url"] for x in res if x["format"].upper() in fmt]


def jobs():
    j = []
    for u in ckan_resources("dados_hidrologicos_ho", {"PARQUET", "PDF"}):
        j.append(("ons_hourly", u, LIC_ONS))
    for u in ckan_resources("dados-hidrologicos-res", {"PARQUET", "PDF"}):
        j.append(("ons_daily", u, LIC_ONS))
    z = "https://zenodo.org/records/15025488/files/{}?download=1"
    for f in ["01_CAMELS_BR_attributes.zip", "03_CAMELS_BR_streamflow_selected_catchments.zip",
              "05_CAMELS_BR_precipitation.zip", "06_CAMELS_BR_actual_evapotransp.zip", "09_CAMELS_BR_temperature.zip"]:
        j.append(("camels_br", z.format(f), LIC_CAMELS))
    j.append(("bdg2", "https://zenodo.org/records/3887306/files/buds-lab/building-data-genome-project-2-v1.0.zip?download=1", LIC_BDG2))
    t = "https://data.4tu.nl/file/d4810b78-6cdd-48fe-8950-9bd601e5f47f/"
    j.append(("cascaded_tanks", t + "3b697e42-01a4-4979-a370-813a456c36f5#CascadedTanksFiles.zip", LIC_TANKS))
    j.append(("cascaded_tanks", t + "767edeb4-c4fc-45f8-a287-f1b1bd920b57#TanksBenchmark.pdf", LIC_TANKS))
    # Wiener-Hammerstein dropped (25/09/2026): host certificate cannot be verified and no explicit licence; dev-only anyway.
    return j


def fname(url):
    if "#" in url:
        return url.split("#", 1)[1]
    return url.split("?")[0].rstrip("/").split("/")[-1]


def get(url, path):
    tmp = path + ".part"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url.split("#")[0], headers=UA), timeout=300) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.replace(tmp, path)
            return
        except Exception as e:  # network hiccup: retry with backoff
            print(f"  retry {attempt + 1} {url}: {e}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    J = list(dict.fromkeys(jobs()))  # the ONS catalogue lists a few resources twice
    print(f"{len(J)} files", flush=True)
    for i, (src, url, lic) in enumerate(J, 1):
        d = os.path.join(OUT, src); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, fname(url))
        if not os.path.exists(p):
            get(url, p)
        rows.append({"source": src, "file": os.path.relpath(p, ROOT).replace("\\", "/"), "url": url.split("#")[0],
                     "licence": lic, "bytes": os.path.getsize(p), "sha256": sha256(p)})
        if i % 10 == 0 or i == len(J):
            print(f"{i}/{len(J)} {src} {fname(url)}", flush=True)
    with open(os.path.join(OUT, "MANIFEST.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(f"{r['sha256']} *{r['file']}\n")
    print("total bytes", sum(r["bytes"] for r in rows))


if __name__ == "__main__":
    sys.exit(main())
