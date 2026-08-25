# PFC 5 Asphalt Data Contract

## Global response

`stress_strain.csv` requires `strain,stress_mpa`. Optional columns may include load, displacement, flow, rut depth, pass/cycle count, temperature, and crack counters when their units are documented.

## Ball fields

`plotdata_ball_fields.csv` requires:

`x,y,disp_x,disp_y,vel_x,vel_y,radius`

## Stress fields

`plotdata_stress.csv` requires `x,y` plus `stress_xx/stress_yy/stress_xy` or aliases `sxx/syy/sxy`.

## Porosity

`plotdata_porosity.csv` requires `x,y,porosity`.

## Orientations

`plotdata_fracture_orientations.csv` or `contact_orientations.csv` requires `angle_deg`. Optional `type`, `magnitude`, `cx`, and `cy` columns must be documented.

## Frames

Animation input is a directory of PNG files whose names contain sortable integers. The ordering script records the normalized order in `frames_manifest.csv`.

## Rutting history and coupled-load evidence

`rutting_history.csv` requires:

```text
solver_time_s,equivalent_physical_time_s,time_scale_lambda,solver_cycle,
one_way_pass,round_trip,commanded_vertical_n,vertical_reaction_n,
commanded_horizontal_n,horizontal_reaction_n,rut_depth_mm,
forward_face_deformation_mm,reverse_face_deformation_mm,lateral_heave_mm,
surrogate_route
```

- All loads/reactions are signed in the declared global axes; pressure is not stored in
  a force column.
- `time_scale_lambda` follows the case-declared convention and must stay positive.
  Record whether the row is unaccelerated, moving, cyclic or fixed-patch in
  `surrogate_route`; a label does not prove equivalence.
- `rut_depth_mm` must name its source in the case manifest: seven-position/approved
  mean, wheel-track statistic or another diagnostic. Do not silently substitute the
  deepest particle displacement.
- Forward/reverse faces are defined relative to the signed horizontal-load direction.

Optional histories should retain commanded position/velocity, wheel position,
temperature, reference-surface ID, reaction-area definition, energy, slip/断键 counts,
contact-model populations and boundary-case ID.

`rutting_shear_profile.csv` requires:

```text
sample_id,depth_mid_mm,shear_component,shear_stress_mpa,
measure_radius_mm,weighting_rule
```

The case manifest additionally records coordinate axes, stress sign, measure-region
centres, overlap policy, empty-region handling and sample time/pass. Keep signed raw
components; any magnitude/absolute-value profile is a separate transformed column.

Every production export must state coordinate units, force/stress sign, scale conversion, case/stage, and source PFC 5.0 build.
