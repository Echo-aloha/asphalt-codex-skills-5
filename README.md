# Asphalt Codex Skills 5

> **Preview release:** `0.1.0-preview.4`. The public API, skill routing, and
> packaging layout may still change before `1.0.0`.

这是一个面向 **ITASCA PFC2D/PFC3D 5.0 沥青混合料建模** 的专用 Skills 包。它覆盖核心建模与 FISH、几何导入、伺服标定、试件生成、标准力学试验、动力与应力波、AE/能量、条件性耦合、Burger 黏弹接触、外部 fistPkg26 基线、Marshall、车辙试验以及离线后处理。

本包不是跨版本 PFC 资料库。所有可执行 `.dat`/FISH 模板都必须以 PFC 5.0 为唯一目标；更高主版本的命令、对象 API、示例和迁移路线不属于本包。

规范输入按“集料表征—取样/试样准备—成型—密度/空隙率—性能试验—现场验证—验收语境”逐节点记录方法和来源。公开包只保留方法映射、[来源台账](skills/pfc5-asphalt-workflow/references/standards-source-ledger.json)和审计规则，不分发 JTG 原文或完整标准表；具体入口见 [`standards-method-map.md`](skills/pfc5-asphalt-workflow/references/standards-method-map.md)。

## 入口

完整项目从 `pfc5-asphalt-workflow` 开始，再按需求路由：

| 任务 | Skill |
| --- | --- |
| 命令骨架、阶段门禁、接触生命周期 | `pfc5-core-modeling` |
| FISH 函数、历史与回调审计 | `pfc5-fish` |
| 伺服控制与多目标标定 | `pfc5-servo-calibration` |
| CAD/网格节点与单元契约 | `pfc5-geometry-import` |
| 压缩、劈裂、拉伸与蠕变指标 | `pfc5-standard-tests` |
| 动载与应力波分辨率 | `pfc5-dynamics-wave` |
| AE 事件聚类与能量核算 | `pfc5-ae-energy` |
| 流体、渗流及求解器耦合契约 | `pfc5-coupling` |
| 试件、级配、体积与空隙率闭合 | `pfc-asphalt-mixture` |
| Burger 接触及标定 | `pfc-burger-viscoelastic` |
| 外部 fistPkg26 检查与基线 | `pfc-fishtank-tests` |
| Marshall 稳定度与流值 | `pfc-marshall-test` |
| 轮碾与车辙 | `pfc-rutting-test` |
| 曲线、场图、玫瑰图、动画 | `pfc-postprocessing` |
| vedo 粒子/力链/裂纹渲染 | `pfc-vedo-postprocess` |
| 包治理和版本门禁 | `pfc-skill-pack` |
| 中国传统色数据配色 | `xxd-data-viz` |

完整清单见 [`references/skill-index.md`](references/skill-index.md)。

<!-- skill-count:start -->
当前包包含 **18 个技能**；数量由 `scripts/validate_skills.py --write-index` 自动维护。
<!-- skill-count:end -->

## 安装与发现

本仓库根目录是一个 Codex plugin，`.codex-plugin/plugin.json` 将全部技能声明在
`./skills/`。下载 release archive 或 clone 仓库后，可通过 Codex 的本地 plugin/
marketplace 流程导入整个包。

如果只需要仓库作用域 Skill，可把所需的 `skills/<skill-name>/` 目录复制或链接到
目标仓库的 `.agents/skills/`。用户级安装则放到 `$HOME/.agents/skills/`。也可以让
`$skill-installer` 从本 GitHub 仓库选择并安装单个 Skill。

Python 核心后处理依赖：

```bash
python -m pip install -r requirements.txt
```

如需 vedo 场景、OpenCV 曲面插值或 MP4 输出：

```bash
python -m pip install -r requirements-visualization.txt
```

PFC 本体、fistPkg、试验标准和商业耦合组件不由 Python requirements 安装，必须由
用户在合法环境中另行提供。

## PFC 5.0 边界

- 只在用户提供的合法 PFC 5.0 与 fistPkg26 环境中运行。
- 不分发 fistPkg、Hill DLL、PFC 项目、保存状态或商业文档。
- 现有接触与未来接触的模型分配必须分别审计。
- 任何脚本在实际 PFC 5.0 运行前只能标记为 `static_validated`，不能声称 `runtime_validated`。
- 级配、试验标准、Burger 参数和试验目标必须来自用户或可追溯来源，不能凭记忆补值。

## 校验

```bash
python scripts/validate_skills.py --write-index
python -m pytest -q
python skills/pfc-postprocessing/scripts/run_demo.py --check-only
python skills/pfc5-asphalt-workflow/scripts/check_runtime_manifest.py
```

Post-processing dependencies are declared in `requirements.txt`; test-only
dependencies are in `requirements-dev.txt`; optional visualization backends are in
`requirements-visualization.txt`.

校验器检查 frontmatter、依赖、链接、危险二进制、绝对路径、密钥、PFC 版本污染、Agent 元数据和 Python 安全模式。

## 来源与致谢

本项目衍生自
[`jiangnan030-del/pfc-codex-skills`](https://github.com/jiangnan030-del/pfc-codex-skills)，
并在其基础上针对 PFC2D/PFC3D 5.0 沥青混合料工作流进行了重构、删减和扩展。
本仓库保留或修改了上游项目中的部分治理结构、发布校验器、后处理脚本、
可视化配置、示例数据和文档；这些上游内容依据 MIT 许可证发布，原版权与许可
声明保留在本仓库的 [`LICENSE`](LICENSE) 和相关 Skill 目录中。

本项目新增的 PFC 5.0 沥青试件、Burger 接触、Marshall、车辙、fistPkg 外部依赖
契约、标准来源台账和运行验证内容由本项目维护。上游仓库中另行采用
AGPL-3.0-or-later 许可的 `dual-target-calibration` 子目录未作为目录、文件或依赖
打包进本仓库；该上游子目录不受根 MIT 许可证重新许可。

审计过的上游基线、保留内容和逐项许可边界见 [`THIRD_PARTY.md`](THIRD_PARTY.md)。

## 许可边界

仓库自有文本与脚本按 [`LICENSE`](LICENSE) 发布。包含上游 MIT 内容且支持单独复制
的 Skill 自带 `LICENSE` 与 `NOTICE.md`，复制单个 Skill 时应一并保留。第三方
PFC/fistPkg/标准资料必须保持外部依赖，使用者自行确认访问权与许可。

第三方与商标边界见 [`THIRD_PARTY.md`](THIRD_PARTY.md)。本项目为独立开源项目，
不隶属于或代表 Itasca Consulting Group, Inc.；产品名仅用于说明兼容目标。
