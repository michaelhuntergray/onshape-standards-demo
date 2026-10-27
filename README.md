# onshape-standards-demo

> **How it was built:** [HOW-IT-WAS-BUILT.md](HOW-IT-WAS-BUILT.md) records each decision, who made it, and what is verified versus assumed.

This project takes a written manufacturing rule and has AI turn it into a CAD check. It uses one rule, from a public sheet-metal DFM guide:

> "Keep at least 1.5–2× material thickness from any part edge."
> Fabcon, *Sheet Metal Design for Manufacturability Guide* ([link](https://fabcon.com/articles/sheet-metal-fabrication/sheet-metal-dfm-guide/))

The rule is stored as data in [`rules/hole-edge.json`](rules/hole-edge.json), which holds the factor, what is measured, and the citation. That data turns into two checkers:

| Piece | What it is | Status |
|---|---|---|
| `checker/hole_edge.py` | Python and build123d. Reads a STEP file, finds the round holes in the plate face, measures the distance from each hole's rim to the nearest part edge, and gives PASS or FAIL against factor × thickness. | **Runs.** 13 tests pass; through-holes only, exits 2 if none found. |
| `featurescript/HoleEdgeCheck.fs` | The same check as an Onshape custom feature. You pick the plate face; holes that fail turn red and a warning gives the count, the required distance and the worst distance. | **Written, not yet compiled in Onshape.** |
| `generate.sh` + `prompts/` | Sends the rule JSON to Claude (headless Claude Code) and gets a FeatureScript checker back. | **Runs.** One sample output is in `out/`, not compiled. |
| `examples/plate.step` | A 60 × 40 × 2 mm plate with three holes on either side of the 2T = 4 mm limit. | Built by `examples/make_plate.py`. |

## Run it

```sh
uv sync
uv run pytest -q                                         # 13 passed
uv run python examples/make_plate.py                     # writes examples/plate.step
uv run python checker/hole_edge.py examples/plate.step --thickness 2
```

```text
rule: Minimum distance from a hole to the part edge (sheet metal): rim-to-edge >= 2 x 2 mm = 4 mm
hole 1: dia 5.00 at (10.0, 20.0) rim-to-edge 7.50 mm PASS
hole 2: dia 5.00 at (56.0, 20.0) rim-to-edge 1.50 mm FAIL
hole 3: dia 4.00 at (30.0, 34.0) rim-to-edge 4.00 mm PASS
3 holes, 1 fail
```

The exit code is 1 when any hole fails, so the check can gate a CI job or a release. `--factor 1.5` applies the looser end of the guideline.

To draft a checker from a rule with AI, run `./generate.sh rules/hole-edge.json > out/mine.fs`. It needs the `claude` CLI, signed in.

## Put the feature in Onshape

1. Create a new Onshape document, then add a Feature Studio. Keep the two header lines Onshape generates, and paste in everything below the `paste from here` marker in `featurescript/HoleEdgeCheck.fs`.
2. In the Part Studio, import `examples/plate.step`, or sketch a plate with holes. Add **Hole Edge Check**, pick the top face, and set the thickness to 2 mm.
3. Expected result: a warning that reads `1 of 3 holes too close to the edge (required >= 4 mm, closest 1.5 mm)`, with the right-hand hole shown red.

Onshape's FeatureScript MCP Server (Onshape Labs, early preview) can do step 1 from Claude directly. It writes the Feature Studio and reads back the compile errors. Setup: `claude mcp add --transport http onshape https://fs-mcp.labs.onshape.app/mcp`, then sign in to Onshape in the browser.

## Limits (read before quoting this)

- The FeatureScript has **not been compiled or run in Onshape yet**. The Python checker is the tested reference, and the two use the same method.
- The checker handles one rule, flat parts, round through-holes and one plate face. Slots and non-round cut-outs are skipped by the Python checker and count as part edge in the FeatureScript. It does not check holes near bends, which is a separate rule.
- Sources disagree on the factor: Fabcon gives 1.5–2T and Protolabs gives fixed distances. The default of 2.0 is the conservative choice and can be changed. See [docs/sources.md](docs/sources.md).
- AI output is a draft. `generate.sh` output has not been compiled, and a person reviews any checker before relying on it.
