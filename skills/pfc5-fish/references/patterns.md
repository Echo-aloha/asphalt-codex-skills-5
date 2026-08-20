# PFC5 FISH Patterns

## Function and command block

```fish
def update_metric
    local value = 0.0
    command
        ; PFC command using @value where required
    endcommand
    update_metric = value
end
```

## Numbered histories

```fish
history nstep 20
history id 1 @axial_stress
history id 2 @axial_strain
```

## Callback activation contract

For a `whilestepping` or other callback-style function:

1. initialize every state variable;
2. execute the documented activation step required by the licensed PFC5 runtime;
3. history a callback counter;
4. verify the counter advances during a short cycle;
5. reset/re-register after restore.

Exact intrinsics and callback semantics must be probed in the target PFC5 product.
