# PFC5 FISH Patterns

The source anchors are relative to a licensed `<PFC5_HELP_ROOT>`:

- `docproject/source/manual/scripting/fish_scripting/statements/defineend.html`;
- `docproject/source/manual/scripting/fish_scripting/fish_fishcallback.html`;
- `docproject/source/manual/scripting/fish_scripting/statements/whilestepping.html`;
- `common/kernel/doc/manual/command_processing/commands/cmd_set.html`;
- `common/kernel/doc/manual/command_processing/commands/cmd_solve.html`.

## Function and command block

```fish
define update_metric
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

Explicit cycle-point registration and removal use the same function and cycle point:

```text
set fish callback 42.1 @update_force
set fish callback 42.1 remove @update_force
```

The official callback tutorial shows that registrations remain active across
successive `solve` commands. A function may be registered more than once at the same
point and will then be called more than once; one `remove` removes only one instance.
Therefore keep a registration ledger and prove the expected call count.

`whilestepping` is different: placing that statement inside a function automatically
registers the function at cycle point `-1.0`. Do not also issue an explicit callback
for that function unless double execution is intentional and tested.

For any callback-style function:

1. initialize every state variable;
2. choose either `whilestepping` or an explicit `set fish callback`, and record the
   cycle point/event;
3. history a callback counter;
4. verify the counter advances during a short cycle;
5. after restore, use `list fish callback` plus the counter probe before deciding
   whether any registration change is needed.

Creation/deletion callbacks receive the entity pointer. Contact-model event arguments
depend on the event: for example, the PFC5 callback tutorial passes a contact pointer
for `contact_create`, but an array for `contact_activated`. Match the exact event
contract instead of reusing one signature.

Model components cannot be inserted after cycle point `0.0` (timestep evaluation).
Creation callbacks therefore belong at a verified pre-zero point, as in the official
tutorial's negative cycle-point examples.

## Solve halt

```fish
define stop_loading
    stop_loading = measured_drop_reached
end
solve fishhalt stop_loading
```

`solve fishhalt` calls the function each cycle and stops when it returns nonzero.
Keep an independent maximum-cycle or time guard, but remember that multiple solve
limits use OR logic and report which one fired.

For large FISH programs, the official help recommends `set fish autocreate off`.
When it is off, declare intended globals explicitly and keep temporaries `local`.

Exact intrinsics and callback semantics must be probed in the target PFC5 product.
