# Sources (checked 2026-10-27)

## 1. Water-slide Onshape talk
NOT FOUND. Searches (web, YouTube, onshape.com) returned no water-slide mention. Nearest, none mention slides (UNVERIFIED that any is the talk):
- "The Big AI Show & Tell", speakers Greg, Darren, Mike, 09/23/2026, FeatureScript MCP personal projects: https://www.onshape.com/en/resource-center/videos/big-ai-show-and-tell
- "Early Preview: Onshape Labs FeatureScript MCP Server and AI Quick Render" (YouTube; channel/date not shown): https://www.youtube.com/watch?v=TZp3ccr9Z6I
- Engineering.com demo article (tank fill level, ice flotation features): https://www.engineering.com/onshape-is-bracing-for-an-ai-explosion/
Next step: watch the Big AI Show & Tell recording (transcript not checked).

## 2. Hole-to-edge DFM rule
Sources disagree:
- Fabcon, "Sheet Metal Design for Manufacturability Guide" (published 2026-03-02): "Keep at least 1.5–2× material thickness from any part edge." https://fabcon.com/articles/sheet-metal-fabrication/sheet-metal-dfm-guide/ (fetched via https://fabcon.com/articles/?p=127)
- Protolabs: fixed distances, not multiples. Thickness <= 0.036 in: hole 0.062 in from edge; thicker: at least 0.125 in. https://www.protolabs.com/services/sheet-metal-fabrication/design-guidelines/
- Secondary, search-snippet only (UNVERIFIED, not fetched): another FabCon page (?p=275) says 2T from sheared edge; Yijin Solution says >=1T (https://yijinsolution.com/de/sheet-metal-guides/sheet-metal-design-guidelines/); extruded holes ~3T; Xometry "4x" claim only via Scribd copy.
- SendCutSend guidelines page: no rule text retrieved (https://www.sendcutsend.com/guidelines/); /hole-features/ 404.
Recommended citable: Fabcon (1.5-2T), noting Protolabs numeric values.

## 3. FeatureScript signatures
Source: https://cad.onshape.com/FsDoc/library.html (fetched by chunks; text as summarised by fetch tool, not eyeballed raw).
- evDistance(context is Context, arg is map) returns DistanceResult
- qGeometry(queryToFilter is Query, geometryType is GeometryType) returns Query ; GeometryType.CYLINDER = "A surface which forms the side of a right circular cylinder"
- evSurfaceDefinition(context is Context, arg is map) returns map ; arg: face (Query, required), returnBSplinesAsOther (boolean, optional). For a cylinder, result is a Cylinder type with fields coordSystem (CoordSystem), radius (ValueWithUnits). UNVERIFIED: exact result-map key (e.g. surfaceType == SurfaceType.CYLINDER) not confirmed.
- qOwnedByBody(body is Query, entityType is EntityType) returns Query ; also qOwnedByBody(body is Query) and qOwnedByBody(queryToFilter is Query, body is Query)
- qEdgeAdjacent(query is Query, entityType is EntityType) returns Query ; DEPRECATED in favour of qAdjacent with AdjacencyType.EDGE (qAdjacent signature not checked: UNVERIFIED)
- qLoopEdges(seed is Query) returns Query
- Boundary edges of a face: qAdjacent(face, AdjacencyType.EDGE, EntityType.EDGE) (UNVERIFIED signature) or qLoopEdges on a seed edge.
- setErrorEntities(context is Context, id is Id, definition is map)
- reportFeatureInfo(context is Context, id is Id, message is ErrorStringEnum) returns boolean ; (…, message, associatedParameters is array) ; (context, id, customMessage is string)
- reportFeatureWarning(context is Context, id is Id, message is ErrorStringEnum) returns boolean ; (…, customMessage is string) ; (…, message is ErrorStringEnum, associatedParameters is array) ; (…, customMessage is string, associatedParameters is array)
- debug (module debug.fs), key overloads: debug(context is Context, value) ; debug(context, value is Query, color is DebugColor) ; debug(context, value is Vector, color) ; debug(context, point1 is Vector, point2 is Vector) (15 overloads total)
