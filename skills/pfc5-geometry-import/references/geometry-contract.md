# Geometry CSV Contract

Node file:

```csv
id,x,y,z
1,0.0,0.0,0.0
```

For 2D, `z` may be omitted. Element file:

```csv
id,n1,n2,n3,n4
1,1,2,3,
```

Blank trailing node columns are allowed. Every referenced node must exist; an
element must contain at least two distinct nodes. Record whether elements are
segments, faces, tetrahedra, or converter-specific cells.

Polyline files may use `polyline_id,order,x,y,z`; ordering and closure must be
explicit. All coordinates use one declared unit system.

## Native PFC5 handoff

The licensed PFC5 help pages are:

- `common/module/doc/manual/geom_manual/geom_commands/cmd_geometry.import.html`;
- `pfcmodule/doc/manual/wall_manual/wall_commands/cmd_wall_import.html`.

`geometry import` recognizes the Itasca geometry format, a partial AutoCAD 12 DXF
implementation, and text/binary STL. STL nodes/edges at the same location are merged by
default; `nomerge` changes topology and file size and must be disclosed.

`wall import` stitches connected facets from a seed. The surface must be manifold and
orientable, every facet must be inside a previously declared model domain, and walls
can be created during cycling only before cycle point `0.0`. The `nothrow` option may
skip offending facets, so a command that returns is not proof of a closed wall.
