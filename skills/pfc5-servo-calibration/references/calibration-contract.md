# Calibration Contract

Each run record should contain:

```text
case_id,seed,input_save,parameter_json,target_json,result_json,
equilibrium_metric,peak_metric,status,elapsed,code_hash
```

Servo audit:

- target and reaction use the same units;
- sign is established by a one-step probe;
- effective stiffness and timestep are positive;
- velocity is bounded;
- reaction error and oscillation are exported;
- callback registration is not duplicated after restore.

Two-target audit:

- exactly two active parameters and two residuals;
- finite 2x2 sensitivity matrix;
- determinant/condition threshold passes;
- bounded update remains inside parameter limits;
- proposed point is verified by a real run.
