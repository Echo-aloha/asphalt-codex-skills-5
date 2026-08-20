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
