# Contributing

本仓只接受 PFC 5.0 沥青混合料工作流相关改动。

## 必须满足

- 新增可执行 PFC 文件前，声明 PFC2D/PFC3D、单位、输入、输出和运行验证状态。
- PFC 命令必须来自 PFC 5.0 手册、已授权本地材料或真实运行探针。
- 不提交 PFC 保存状态、项目、DLL、EXE、第三方商业源码、标准全文或本地绝对路径。
- 外部 fistPkg 仅保存契约、校验器和用户私有工作副本的操作说明。
- Python 数据加载默认禁止 pickle；外部命令必须使用参数数组且禁止 shell 解析。
- 更新 Skill 后运行 `python scripts/validate_skills.py --write-index` 和测试。

## 内容组织

- `SKILL.md` 负责触发条件、边界、工作流和输出契约。
- 详细公式与长说明放在 `references/`。
- 可执行或可复用代码放在 `scripts/`，示例输入放在 `examples/` 或 `templates/`。
- 生产参数不得伪装成通用默认值。
