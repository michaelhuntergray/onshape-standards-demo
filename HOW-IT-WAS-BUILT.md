# How it was built

The decisions, in the order they were made. Each one notes who decided and whether it has been verified.

## 1. Rescoped from topology optimization to standards-driven checking
Decided by Michael. The career-fair demo shows AI reading a design standard and enforcing it on CAD, replacing the topology optimizer. The topology optimizer stays in its own repo.
**Status:** verified (ticket brief).

## 2. One rule: hole-to-edge distance in sheet metal
Proposed by Claude, inside the brief's guidance to pick one DFM rule. It is easy to measure, a published guide states it, and a part that breaks it is easy to see. Minimum wall thickness and ASME drawing rules were rejected for tonight because they need either a thickness map or a drawing.
The sources disagree: Fabcon says 1.5–2T and Protolabs gives fixed distances. The default is 2.0, the conservative end, and it can be changed.
**Status:** verified for Fabcon's wording (docs/sources.md). The other sources are partly UNVERIFIED.

## 3. A Python reference checker first, the FeatureScript second
Decided by Claude. This machine has no Onshape access (no API keys and no MCP session), so the Onshape feature can't be compiled here. The build123d checker gives a result that can be tested tonight. The FeatureScript uses the same method: find closed circular edges on the face, take the rest as the boundary, measure minimum distance.
**Status:** Python verified by 5 pytest tests and a CLI run. FeatureScript assumed; it compiles only once pasted into Onshape.

## 4. The rule is stored as data and the AI writes the code
Decided by Claude. `rules/hole-edge.json` holds the rule and its citation. `generate.sh` sends it to Claude with a fixed prompt and gets a FeatureScript draft back. The rule stays reviewable, and the generated code is treated as a draft.
**Status:** verified that generate.sh runs and returns a defineFeature with setErrorEntities and reportFeature calls (out/). Whether that output compiles is assumed.

## Open questions
- Does `featurescript/HoleEdgeCheck.fs` compile, and does it flag exactly hole 2 on examples/plate.step? This is settled by pasting it into a Feature Studio, or through the Onshape FeatureScript MCP Server.
- Does Onshape treat a full-circle hole edge as one closed edge? The feature's 2πr length test assumes it does.
- The Onshape talk on generating water slides from natural language has not been found. docs/sources.md lists the nearest candidates.
