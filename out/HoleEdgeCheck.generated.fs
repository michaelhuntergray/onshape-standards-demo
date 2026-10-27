// Rule: hole-edge-distance - Minimum distance from a hole to the part edge (sheet metal)
// Source: Fabcon, Sheet Metal Design for Manufacturability Guide (published 2026-03-02, checked 2026-10-27)
// "Keep at least 1.5-2x material thickness from any part edge."
// URL: https://fabcon.com/articles/sheet-metal-fabrication/sheet-metal-dfm-guide/
// Note: 2.0 is the conservative end of that range.
// Why: a hole too close to the edge tears, bulges or distorts when the part is punched, cut or bent.
//
// Method: for each part, the largest planar face is taken as the sheet face and its normal as the
// thickness direction. Thickness is the part's extent along that normal (or a manual value).
// Through-thickness holes are concave cylindrical faces whose axis is parallel to that normal.
// Distance = shortest distance from the hole's rim on the sheet face to the other edges of that
// face (outer boundary, plus any cut-out edges, which is the conservative reading).
// The feature adds no geometry.

const FACTOR_BOUNDS = { (unitless) : [0.1, 2.0, 20] } as RealBoundSpec;
const THICKNESS_BOUNDS = { (millimeter) : [0.01, 2.0, 100] } as LengthBoundSpec;

annotation { "Feature Type Name" : "Hole edge distance check (sheet metal)" }
export const holeEdgeDistanceCheck = defineFeature(function(context is Context, id is Id, definition is map)
    precondition
    {
        annotation { "Name" : "Parts to check", "Filter" : EntityType.BODY && BodyType.SOLID }
        definition.parts is Query;

        annotation { "Name" : "Minimum distance (x material thickness)" }
        isReal(definition.factor, FACTOR_BOUNDS);

        annotation { "Name" : "Enter thickness manually" }
        definition.manualThickness is boolean;

        if (definition.manualThickness)
        {
            annotation { "Name" : "Material thickness" }
            isLength(definition.thickness, THICKNESS_BOUNDS);
        }
    }
    {
        const bodies is array = evaluateQuery(context, definition.parts);
        if (size(bodies) == 0)
            throw regenError("Select at least one part to check.", ["parts"]);

        var failing is array = [];
        var holeCount is number = 0;
        var skipped is number = 0;
        var haveWorst is boolean = false;
        var worstDistance is ValueWithUnits = 0 * meter;
        var worstRequired is ValueWithUnits = 0 * meter;
        var worstMargin is ValueWithUnits = 0 * meter;

        for (var body in bodies)
        {
            // Sheet face: the largest planar face of the part.
            var sheetFace is Query = qNothing();
            var bestArea is ValueWithUnits = 0 * meter ^ 2;
            for (var f in evaluateQuery(context, qGeometry(qOwnedByBody(body, EntityType.FACE), GeometryType.PLANE)))
            {
                const a is ValueWithUnits = evArea(context, { "entities" : f });
                if (a > bestArea)
                {
                    bestArea = a;
                    sheetFace = f;
                }
            }
            if (isQueryEmpty(context, sheetFace))
            {
                skipped += 1;
                continue;
            }

            const sheetPlane is Plane = evPlane(context, { "face" : sheetFace });
            const normal is Vector = sheetPlane.normal;

            var thickness is ValueWithUnits;
            if (definition.manualThickness)
            {
                thickness = definition.thickness;
            }
            else
            {
                const box is Box3d = evBox3d(context, { "topology" : body, "cSys" : coordSystem(sheetPlane), "tight" : true });
                thickness = box.maxCorner[2] - box.minCorner[2];
            }
            const required is ValueWithUnits = definition.factor * thickness;

            // Through-thickness holes: concave cylinders with axis parallel to the sheet normal.
            var holeFaces is array = [];
            for (var f in evaluateQuery(context, qGeometry(qOwnedByBody(body, EntityType.FACE), GeometryType.CYLINDER)))
            {
                const surf = evSurfaceDefinition(context, { "face" : f });
                if (!(surf is Cylinder) || !parallelVectors(surf.coordSystem.zAxis, normal))
                    continue;
                const tangent is Plane = evFaceTangentPlane(context, { "face" : f, "parameter" : vector(0.5, 0.5) });
                var radial is Vector = tangent.origin - surf.coordSystem.origin;
                radial = radial - dot(radial, surf.coordSystem.zAxis) * surf.coordSystem.zAxis;
                if (dot(tangent.normal, radial) < 0 * meter)
                    holeFaces = append(holeFaces, f);
            }
            if (size(holeFaces) == 0)
                continue;

            const sheetEdges is Query = qAdjacent(sheetFace, AdjacencyType.EDGE, EntityType.EDGE);
            const boundary is Query = qSubtraction(sheetEdges, qAdjacent(qUnion(holeFaces), AdjacencyType.EDGE, EntityType.EDGE));
            if (isQueryEmpty(context, boundary))
                continue;

            for (var hole in holeFaces)
            {
                const rim is Query = qIntersection([qAdjacent(hole, AdjacencyType.EDGE, EntityType.EDGE), sheetEdges]);
                if (isQueryEmpty(context, rim))
                    continue;

                var distance is ValueWithUnits;
                try silent
                {
                    distance = evDistance(context, { "side0" : rim, "side1" : boundary }).distance;
                }
                catch
                {
                    skipped += 1;
                    continue;
                }

                holeCount += 1;
                const margin is ValueWithUnits = distance - required;
                if (!haveWorst || margin < worstMargin)
                {
                    haveWorst = true;
                    worstMargin = margin;
                    worstDistance = distance;
                    worstRequired = required;
                }
                if (distance < required - TOLERANCE.zeroLength * meter)
                    failing = append(failing, hole);
            }
        }

        if (!haveWorst)
        {
            reportFeatureWarning(context, id, "No through-thickness holes were found to check"
                    ~ (skipped > 0 ? " (" ~ toString(skipped) ~ " part(s) or hole(s) could not be evaluated)." : "."));
            return;
        }

        const requiredText is string = toString(roundToPrecision(worstRequired / millimeter, 3)) ~ " mm";
        const worstText is string = toString(roundToPrecision(worstDistance / millimeter, 3)) ~ " mm";

        if (size(failing) > 0)
        {
            setErrorEntities(context, id, { "entities" : qUnion(failing) });
            reportFeatureWarning(context, id, toString(size(failing)) ~ " of " ~ toString(holeCount)
                    ~ " hole(s) are closer to the part edge than required. Required: at least "
                    ~ toString(definition.factor) ~ " x thickness (" ~ requiredText
                    ~ "). Worst measured: " ~ worstText ~ ".");
        }
        else
        {
            reportFeatureInfo(context, id, "All " ~ toString(holeCount) ~ " hole(s) pass. Required: at least "
                    ~ requiredText ~ ". Worst measured: " ~ worstText ~ ".");
        }
    });
