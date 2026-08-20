# Asphalt test standards policy

## Current versus legacy

China's Ministry of Transport announced JTG 3410-2025 with an effective date of
2025-10-01 and simultaneous withdrawal of JTG E20-2011. Therefore:

- default new work to JTG 3410-2025;
- use JTG E20-2011/T0709/T0719 only when reproducing legacy data or when the user
  explicitly requires that edition;
- do not assume that method identifiers, dimensions, conditioning, speed, cycle count,
  calculation constants or acceptance criteria stayed unchanged;
- record the exact edition, method ID, clause/table and any machine/specimen correction
  coefficients in the case manifest.

Official announcements:

- [JTG 3410-2025 release](https://xxgk.mot.gov.cn/jigou/glj/202508/t20250822_4175218.html)
- [JTG E20-2011 legacy release](https://xxgk.mot.gov.cn/jigou/glj/202006/t20200623_3312352.html)

## Modeling rule

A DEM model may simplify geometry or loading, but the result must distinguish:

1. normative test value;
2. physical laboratory input;
3. DEM-equivalent input;
4. numerical control parameter.

Never label an equivalent patch load, accelerated cycle, scaled particle size or
post-peak stop factor as a standard requirement.

## Standard roles and method chains

Do not treat every document containing an asphalt requirement as a laboratory test
method. Classify each source before extracting values:

- JTG 3410-2025 owns asphalt and asphalt-mixture laboratory methods;
- JTG 3432-2024 owns aggregate and filler test methods used to establish measured input;
- JTG D50-2017 supplies pavement-design context and target parameters;
- JTG 3450-2019 supplies field-test definitions for independent validation;
- construction, quality-evaluation and maintenance standards supply project/acceptance
  context, not automatic contact parameters;
- subgrade design/construction standards matter only when the model scope includes the
  support structure or coupled pavement response.

Freeze a method chain rather than a single method ID: aggregate characterization,
mixture sampling/preparation, specimen forming, density/void measurement, performance
test, field validation and acceptance decision. See
[standards-method-map.md](standards-method-map.md).

Bind every reviewed package-level method claim to
[standards-source-ledger.json](standards-source-ledger.json). Project intake records may
reuse a ledger source ID and digest, but each method-chain item still owns its method,
locator, reviewer, values and model mapping. A digest identifies the reviewed copy; it
does not replace human confirmation of applicability or interpretation.

## Acceptance rule

The skill may compute a metric only after its formula, sampling interval, units and
correction factors are tied to the chosen standard edition. If the current standard text
is unavailable, return the raw force/displacement or rut-depth history and mark the
normative metric as pending rather than filling a remembered value.

Keep raw observations, corrected observations and the final normative metric in separate
columns. Record the person/date of source review and distinguish a printed-page locator
from the PDF viewer page number. Do not bundle the standard PDF or reproduce complete
tables in a public case.
