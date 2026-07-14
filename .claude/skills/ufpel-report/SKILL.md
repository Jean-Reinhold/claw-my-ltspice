---
name: ufpel-report
description: Build UFPel-styled lab report PDFs (official texufpel class) from claw-spice simulations via Docker. Use when asked to write, build, fix, check, or preview a lab report / relatório / PDF, or to turn simulation results, plots, and schematics into a report.
---

# ufpel-report — lab reports build in Docker, nowhere else

The `latex` compose service (texlive image, `latex/` mounted at
`/workspace`) is the ONLY build environment. There is no host TeX
dependency and there must never be one.

## Rules

- ALWAYS build via `./claw-spice report` (or `make report`), which runs
  `scripts/report/build_report.sh`. Never call `latexmk`/`pdflatex` on the
  host; never `pip`/`tlmgr` install anything.
- First build pulls the texlive image (~3GB, one-time). Expect it; do not
  abort.
- All output lands in `latex/build/` (gitignored). The deliverable is
  `latex/build/main.pdf`. Never edit files in `build/` — fix the sources.
- Report sources live in `latex/`: `main.tex` (identification fields and
  document skeleton), `chapters/*.tex` (introducao, metodologia,
  resultados, conclusao, apendices), `bibliografia.bib` (ABNT via the
  bundled `abnt.bst`), `texufpel.cls` (official UFPel class — do not
  edit it).
- One report per branch/experiment: fill the `<...>` placeholders in
  `main.tex` (experiment name, author, professor, disciplina, keywords,
  resumo) and replace the `\fbox` placeholder boxes in the chapters with
  real `\includegraphics` calls before calling a report final.
- `main.tex` already overrides the class's TCC identification texts via
  `\documento`/`\tipodocumento`/`\descricaodocumento` so the cover and
  title page read "Relatório de Laboratório" — keep those overrides when
  editing the preamble.

## Getting simulation artifacts into the report

pdflatex cannot read SVG. Everything claw-spice renders is SVG, so always
convert with `--png` and store the images in `latex/imagens/generated/`
(committed — plots and circuit drawings are part of the report):

```bash
# schematic drawing straight into the report tree (--png converts next to it)
./claw-spice render <circuit>.asc \
    --output latex/imagens/generated/<name>.svg --png

# waveform plot straight into the report tree
./claw-spice raw plot <run>.raw V(out) \
    --output latex/imagens/generated/<name>.svg --png
```

Then in a chapter: `\includegraphics[width=\textwidth]{<name>.png}` —
`imagens/` and `imagens/generated/` are already on `\graphicspath`.

Measurements: transcribe `.meas` results from `./claw-spice log summary`
into the `tab:medidas` table (siunitx `S` columns) and compare against
theory. Paste the exact simulated netlist into the `ap:netlist` appendix.

## Build → read → fix loop (iterate until clean)

1. `./claw-spice report`. On failure the script extracts the first LaTeX
   error block from `latex/build/main.log` — read it there, not by
   scrolling raw latexmk noise.
2. Fix the `.tex` source (never the files in `build/`), rebuild.
3. On success, VISUAL INSPECTION IS MANDATORY: Read the built PDF
   (`latex/build/main.pdf` — pages render as images) and check every page
   you changed plus the sumário: broken layout, overfull lines, missing
   figures/references ("??"), leftover `<placeholder>` fields, unreadable
   schematic renders. Never declare a report done without having looked
   at the rendered pages. Warnings worth chasing live in `main.log`
   (`Overfull \hbox`, `undefined references`).
4. When the user asked only for a check, finish with
   `./claw-spice report clean`; when they asked for the document, keep
   the PDF.

## Hot preview (the Overleaf replacement)

- `./claw-spice report watch` — continuous rebuild (latexmk -pvc) inside
  the container: every save of a `.tex` file rebuilds the PDF.
  Long-running; launch it for the user, don't sit blocking on it.
- `./claw-spice report serve` — auto-refreshing browser viewer at
  http://localhost:8001 that reloads whenever `main.pdf` changes.
- Together they give live editing: change a chapter, the browser updates
  seconds later.
