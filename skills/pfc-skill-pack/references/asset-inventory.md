# PFC 5 Asset Inventory Policy

## Bundled source

可包含小型、可审计、许可明确的 PFC 5.0 `.dat`/FISH 探针、Python 工具、CSV/YAML/JSON 模板和示例数据。所有路径必须可移植，参数必须标明单位和证据等级。

## External dependencies

fistPkg、商业手册、试验标准全文、DLL、EXE、项目和保存状态不得随包分发。Skill 只保存输入/输出契约、只读校验器、合法来源占位符和私有工作副本步骤。

## Generated outputs

图像、视频、缓存、日志、保存状态和运行结果默认不进入发布包。只有极小、确定性、用于自动测试的示例数据可以保留。

## Acceptance checklist

- PFC2D/PFC3D 5.0 目标明确；
- 来源和许可边界明确；
- 无私有绝对路径或密钥；
- 无不透明二进制或 pickle 依赖；
- 跨技能依赖已声明；
- 静态与运行验证状态没有混淆。
