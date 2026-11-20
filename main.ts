// news-image-20261120 — "Sum up 20 November's world news in one image".
// The entry is the image beside this file: entry.png, a 1024x1024 newspaper
// front page drawn by draw.py (Python/Pillow, no network) from the 40 verified
// 20 Nov 2026 headlines in the research file (final version: landfall complete,
// COP31 no deal, Nasdaq's 2026 gain gone, GTA VI $2.36bn estimate, Kyiv + Poland).
// This program only copies it to the grader's output directory, so both runs
// write byte-identical output.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
