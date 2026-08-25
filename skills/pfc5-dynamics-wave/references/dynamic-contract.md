# Dynamic And Wave Contract

Minimum checks:

- `lambda = wave_speed / f_max`;
- `lambda / spacing >= declared minimum`, normally at least 10 for a first accuracy gate;
- source direction is `x/y` in 2D and `x/y/z` in 3D;
- timestep is positive and provides a declared number of samples per shortest period;
- local/contact damping and boundary absorption are documented;
- input and response histories share a synchronized time origin;
- energy tracking is enabled before loading when energies are required; only energy
  partitions actually supplied by the active PFC5 body/contact models are reported;
- kinetic/available strain energy and reflection behavior are inspected.

Passing these checks is necessary but not sufficient; contact-law dispersion and
the actual PFC5 runtime still require validation.
