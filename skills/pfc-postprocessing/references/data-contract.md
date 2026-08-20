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

Every production export must state coordinate units, force/stress sign, scale conversion, case/stage, and source PFC 5.0 build.
