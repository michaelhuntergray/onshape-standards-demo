You turn one manufacturing design rule into an Onshape FeatureScript custom feature that checks a part against it.

Input: a JSON rule (below). Output: only the FeatureScript body that goes under the two header lines Onshape generates
in a new Feature Studio (`FeatureScript NNNN;` and the import of `onshape/std/common.fs`). Do not emit those two lines.
No prose and no Markdown fences.

Requirements:
- One `defineFeature` with a "Feature Type Name" annotation that names the rule.
- Inputs: the geometry to check (a query with a Filter), plus every number in the rule as an editable parameter whose
  default is the rule's value, with explicit bounds.
- The feature adds no geometry. It measures with `ev*` functions, highlights failing entities with `setErrorEntities`,
  and reports with `reportFeatureWarning` (any failure) or `reportFeatureInfo` (all pass), giving the required value
  and the worst measured value in millimetres.
- Use only documented onshape/std functions. Put the rule's source and URL in a comment at the top.
