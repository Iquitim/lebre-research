#!/usr/bin/env python3
"""
Compile Condensed Reference PDFs via Edge headless and perform visual QA using pypdfium2.
"""

import os
import sys
import subprocess
from pathlib import Path

WORKSPACE = Path(r".")
HTML_DIR = WORKSPACE / "docs" / "architecture" / "pdf_source"
PDF_DIR = WORKSPACE / "docs" / "architecture" / "pdf"
QA_DIR = WORKSPACE / "scratch" / "pdf_qa"

EDGE_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

tasks = [
    ("LEBRE_CONDENSED_EN.html", "LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf", "en"),
    ("LEBRE_CONDENSED_PTBR.html", "LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf", "ptbr")
]

for html_name, pdf_name, lang in tasks:
    html_path = HTML_DIR / html_name
    pdf_path = PDF_DIR / pdf_name
    
    print(f"[{lang.upper()}] Compiling {html_name} -> {pdf_name}...")
    cmd = [
        EDGE_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--virtual-time-budget=3500",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        str(html_path.resolve())
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not pdf_path.exists():
        print(f"Error compiling {pdf_name}: returncode {res.returncode}")
        print("Stderr:", res.stderr)
        sys.exit(1)
    
    pdf_size = pdf_path.stat().st_size
    print(f"[{lang.upper()}] Success: {pdf_name} ({pdf_size} bytes)")

print("\n--- Performing pypdfium2 QA ---")
import pypdfium2 as pdfium

for html_name, pdf_name, lang in tasks:
    pdf_path = PDF_DIR / pdf_name
    doc = pdfium.PdfDocument(str(pdf_path))
    n_pages = len(doc)
    print(f"\n[{lang.upper()}] Total Pages: {n_pages}")
    
    # Inspect all pages for non-empty text
    empty_pages = []
    for i, page in enumerate(doc):
        text = page.get_textpage().get_text_range()
        if not text.strip() and i > 0: # page 0 is cover (might be mostly graphics)
            empty_pages.append(i + 1)
    
    if empty_pages:
        print(f"Warning: Empty pages detected on {lang.upper()}: {empty_pages}")
    else:
        print(f"All {n_pages} pages have valid rendered content.")
        
    # Render all pages to PNG for thorough visual QA
    print(f"[{lang.upper()}] Rendering all {n_pages} pages to PNG...")
    for idx in range(n_pages):
        page = doc[idx]
        pixmap = page.render(scale=2.0) # 2.0 scale ~= 144-150 DPI
        pil_image = pixmap.to_pil()
        out_img = QA_DIR / f"{lang}_page_{idx+1}.png"
        pil_image.save(out_img)
    print(f"[{lang.upper()}] Successfully rendered {n_pages} page images.")

print("\nCompilation and full page-by-page rendering complete!")

