# Overview

## The one-sentence model
Post-processing is the translation layer between “simulation state” and “human judgment.”

## Concept map

```text
PFC model / save states
        ↓
export command flow
        ↓
standard data files
        ↓
Python plotting and animation
        ↓
figures / animations / tables
```

## Why this skill exists

Many PFC teaching materials show how to click through GUI plots, but they do not explain:

- what the exported files mean
- how to reuse them outside one machine
- how to version them in GitHub
- how to regenerate the same figures later

This skill fixes that gap.

## Output families

### 1. Curve plots
Use when the whole specimen can be summarized by one response curve.

### 2. Field plots
Use when the specimen is not uniform and you care about where things happen.

### 3. Rose or fabric plots
Use when direction matters more than position.

### 4. Animations
Use when time order matters more than one frozen state.

### 5. Tables
Use when cases must be compared or screened.

## Typical teaching sequence

1. run the minimal public example
2. inspect the raw CSV files
3. inspect the generated figures
4. match each figure back to the file that created it
5. repeat with a real PFC export directory

## Frequent misunderstandings

- “A save file is already a figure source.” No. A `.sav` is a model state, not a plotting contract.
- “A screenshot is enough.” No. Screenshots are fragile; data-backed figures are reproducible.
- “Animation is special.” Not really. Animation is just ordered frames plus one assembly step.
