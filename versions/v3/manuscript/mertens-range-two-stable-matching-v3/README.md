# Mertens's range-two stable-matching conjecture and fully supported preference laws

For independent uniform rankings of four neighbors on a labelled range-two cycle,
the note proves stable-partial-matching probability `Theta(q^N)` with one base
for both parities. The same completion construction applies to every fully
supported independent identically distributed law on the 24 rankings.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, use a standard LaTeX distribution:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is included in `note.tex`; BibTeX is unnecessary.

## Mathematical coverage

- The written proof gives the all-length six-site injections, uniform base
  bounds, the positive cases at five and six vertices, and effective base
  enclosures from exact finite counts.
- The weighted extension assumes positive probability for every ranking, the
  same law at every site, and independence. Its written proof does not assume
  reflection symmetry. A restricted-support example explains why the full
  support condition cannot simply be omitted.
- The triangle-packing estimate is for finite simple graphs; its upper and
  lower exponentials need not have the same base.
- The range-one formula is reproved with attribution to Mertens (2005).
- At five vertices the range-two graph is complete; Mertens (2015),
  *Small random instances of the stable roommates problem*, Section 5,
  equation (21b), gives the exact value `p_5=4075/6912`, cited separately
  from the common-base theorem.
- The complete-graph asymptotic is cited from Young and Studebaker (2026),
  Theorem 1.1. It corrects the coefficient at the `p=1` endpoint of Conjecture 5;
  no conclusion about its interior is inferred.

## Finite checks

Python 3.10 or later, standard library:

```sh
python3 verify.py > checker-output.json
```

The checker obtains open-word counts `(1, 24, 576, 13808)` for lengths zero
through three, checks all 16 buffer masks and 14,408 stable cyclic completions
at sizes seven through nine. It also computes exact masses for ranking weights
`1,...,24`, normalized by 300, and all range-one profiles at sizes three through
nine. Rational integration bounds certify that the corrected complete-graph
coefficient is larger than the originally predicted coefficient. The all-length
conclusions use the written proofs and cited theorem, not extrapolation from
the finite computations.

## Formal statements

The PDF links six pinned `.lean` files. `GrowthTransfer.result` states uniform
range-two constant-factor probability bounds for every `n >= 2`, with `N=n+5`,
allowing singles and counting each profile once. The finite-prefix extension,
explicit interval for the base, effective enclosures, weighted rankings,
triangle packing and range-one formula have written proofs. The complete-graph
asymptotic has the cited coverage stated above.

## Contents and license

`note.tex`, `metadata.json`, `coverage.json`, `verify.py`, and
`checker-output.json` are the rebuildable mathematical sources and supporting
checks. The separately supplied `note.pdf` is the typeset note.
`MANIFEST.sha256` records source-member hashes in the source archive.

Copyright 2026 Haobo Ma and Wenlin Zhang.
Creative Commons Attribution 4.0 International (`cc-by-4.0`).
