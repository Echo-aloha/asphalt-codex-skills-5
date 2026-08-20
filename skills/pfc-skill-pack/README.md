# pfc-skill-pack

治理入口，负责保持 `Asphalt-Codex-Skills-5` 为 PFC 5.0 专用沥青包。

发布前运行：

```bash
python scripts/validate_skills.py --write-index
python -m pytest -q
```

第三方 PFC、fistPkg、DLL、项目和保存状态一律保持外部依赖。
