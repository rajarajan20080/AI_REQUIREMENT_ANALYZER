# Requirements Engineering Datasets — What I Could Actually Retrieve

I went and pulled the real files rather than just describing them. Here's exactly
what's in this bundle, where it came from, and — importantly — which two datasets
in your original list I could **not** find as real, downloadable files.

## ✅ Included (real, verified files)

### 1. `Promise_NFR_dataset_original.csv` — tera-PROMISE NFR dataset (625 requirements)
- The classic PROMISE_exp / NFR dataset (Cleland-Huang et al., PROMISE repository).
- 625 rows: 255 Functional (`F`), 370 Non-Functional across 11 categories
  (Usability, Security, Operational, Performance, Look&Feel, Availability,
  Scalability, Maintainability, Legal, Fault Tolerance, Portability).
- This **is** the "NFR Dataset (~625 labeled requirements)" from your table.
- Source: waadalhoshan/datasets (GitHub), original PROMISE repository data,
  CC BY-SA 3.0, (c) Jane Cleland-Huang.

### 2. `Promise_NFR_dataset.csv` — same corpus, simplified binary format
- Same 625 requirements, just `RequirementText` + binary `NFR` (1/0) column.
- Handy if you only need FR vs. NFR binary classification.

### 3. `PROMISE_exp.arff` / `PROMISE_exp.csv` — expanded PROMISE_exp dataset (969 requirements)
- Lima et al. (2019) expansion of the above: 444 Functional + 525 Non-Functional,
  pulled from 34 additional SRS documents.
- This is the dataset most papers mean by "PROMISE dataset" today (larger than
  the original 625).
- Source: AleksandarMitrevski/se-requirements-classification (GitHub), ARFF
  converted to CSV for convenience (`ProjectID, RequirementText, Class`).

### 4. `PURE_sentence_dump.txt` — PURE (PUblic REquirements dataset)
- 6,871 sentences extracted from real public SRS documents.
- Original PURE (Ferrari, Spagnolo & Gnesi, RE'17) = 79 requirements documents,
  34,268 sentences total, hosted on Zenodo. What I fetched is a plain-text
  sentence dump derived from it (GitHub: MeMartijn/PurePlainDataset) — a subset,
  not the full 34k-sentence XML corpus.
- **Caveat:** your table said "~4,000 requirement statements" — the real PURE
  is sentence-level, not a clean 4,000-row labeled requirement list. If you want
  the full, original XML version (all 79 documents with structured `<req>` tags),
  it's on Zenodo: https://zenodo.org/records/7118517 (I can't fetch Zenodo directly
  from here — network access is restricted to GitHub/package registries — but you
  can download it yourself from that link, or Claude Code/Desktop with unrestricted
  network access could pull it for you).

## ⚠️ Not included — couldn't verify as real downloadable files

- **Desire4Requirements (D4RE), ~15,000+ requirements**: I could not find any
  dataset by this name. "D4RE" in the literature refers to a *workshop series*
  ("Learning from Other Disciplines for Requirements Engineering"), not a
  requirements dataset. I don't want to hand you a fabricated file, so I've left
  this out — if you have a specific paper or link for it, send it over and I'll fetch it.
- **OpenReq Dataset, ~10,000+ requirements**: OpenReq was an EU Horizon 2020
  research project (github.com/OpenReqEU) that produced ~30 microservice tools
  (classifiers, quality checkers, recommenders), not one unified public labeled
  dataset file. There isn't a single "OpenReq dataset" CSV to download — the
  closest real things are the individual tool repos, each with their own small
  sample data for testing that service.

So of your 5 listed sources, 3 are real and now in this folder (PROMISE, PROMISE_exp,
PURE), and 2 (D4RE, OpenReq) don't correspond to concrete public datasets I could locate.

## Suggested next steps
- For FR/NFR binary + NFR sub-type classification: use `PROMISE_exp.csv` (969 rows,
  most commonly used in recent papers) or the original 625-row set for comparability
  with older papers.
- For unlabeled requirements text / language modeling / sentence-level tasks: use
  `PURE_sentence_dump.txt`, or grab the full XML PURE from Zenodo for the complete
  79-document, 34,268-sentence version.
- If you want more labeled data, other real, verifiable RE datasets worth adding:
  NoRBERT (github.com/tobhey/NoRBERT — functional requirement concern labels),
  Dronology, or PROMISE's other sub-repositories (defect prediction, effort
  estimation) — say the word and I'll pull specific ones.
