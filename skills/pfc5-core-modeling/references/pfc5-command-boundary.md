# PFC5 Command Boundary

Use the licensed PFC 5.0 manual/runtime as syntax authority.

Expected family markers in the maintained probes include:

- model lifecycle commands such as `new`, `domain`, `cycle`, `solve`, `save`;
- PFC5 top-level `cmat default` and `cmat apply`;
- FISH `def ... end`;
- numbered histories such as `history id ... @symbol`;
- PFC5 wall/ball/clump commands verified in the target product.

The audit script detects several known newer-major markers. Detection is not a
complete parser, and absence of findings is not proof of runtime compatibility.
