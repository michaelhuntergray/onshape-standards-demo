# Demo: 90-second screen recording

Have these open before you start: a terminal in the repo, `rules/hole-edge.json` in an editor, and the Onshape document if the feature has been pasted in.

| Time | On screen | Say |
|---|---|---|
| 0:00–0:10 | The rule quote at the top of the README | "Design guides say to keep holes at least 1.5 to 2 times the material thickness from the edge. Nobody checks that by hand on every part." |
| 0:10–0:25 | `rules/hole-edge.json` | "I store the rule as data: the factor, what gets measured, and the citation." |
| 0:25–0:45 | Run `./generate.sh rules/hole-edge.json` (or show `out/`) | "Claude reads the rule and writes an Onshape FeatureScript feature that enforces it." |
| 0:45–1:05 | Run `uv run python checker/hole_edge.py examples/plate.step --thickness 2` | "The same check runs on a STEP file. The hole on the right is 1.5 mm from the edge and the rule needs 4, so it fails." |
| 1:05–1:20 | Onshape: Hole Edge Check, failing hole in red (**only if it has compiled**) | "Inside Onshape it's a custom feature: pick the face and the bad hole lights up." |
| 1:20–1:30 | The README Limits section | "One rule and flat parts so far. The next step is a library of rules from published standards." |

If the Onshape step hasn't been verified, skip the 1:05 row. Don't show anything that hasn't run.

## Resume bullet (true as of this commit)

- Built a Python/build123d DFM checker that turns a cited sheet-metal rule (hole-to-edge ≥ 2× thickness) into an automated STEP-file check with tests. Used Claude to generate the matching Onshape FeatureScript feature from the rule.

After the feature compiles and runs in Onshape, change the second sentence to: "...and deployed it as an Onshape FeatureScript custom feature that highlights violating holes."
