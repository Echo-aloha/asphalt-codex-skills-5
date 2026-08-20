# PFC 5.0 最小运行验证

验证日期：2026-08-18。以下资产在一个合法安装的 PFC3D 5.0 环境中由控制台
逐个执行，均正常返回并生成临时 `.p3sav`。实际测试环境报告为 build 5.00.25；
这只是本次证据的运行环境，不是 Skill 的最低、唯一或强制子版本要求。Skill 的
适用边界仍为 PFC 5.0，其他 PFC5 build 应重新运行这些探针并记录结果。

当前四个源文件的 SHA-256 与证据保留级别记录在
[`runtime-verification-manifest.json`](../skills/pfc5-asphalt-workflow/references/runtime-verification-manifest.json)。
运行 `skills/pfc5-asphalt-workflow/scripts/check_runtime_manifest.py` 可检查记录是否仍与
当前探针一致。由于本次执行未归档控制台日志、进程退出码或临时保存态，清单明确
标记为 `manual-record-no-archived-log`，不得把它表述为全自动运行认证。

| 资产 | 实测结果 | 通过边界 |
| --- | --- | --- |
| `pfc-asphalt-mixture/scripts/minimal_specimen_smoke.p3dat` | 创建 6 面墙、157 个球，执行重力沉降的有限循环并保存 | 仅验证完整边界、颗粒生成和有限命令流；未宣称达到生产平衡或质量—体积闭合 |
| `pfc-burger-viscoelastic/scripts/burger_contact_probe.p3dat` | Burger 接触创建成功；`t≈0.0500` 时局部法向力约 `5.60e5`，并保存 | 仅验证模型属性、局部法向分量、历史和时间求解；参数不是材料标定值 |
| `pfc-marshall-test/scripts/marshall_head_contact_pilot.p3dat` | 两曲面压头末态反力约 `-60.30/+60.30`，闭合量约 `1.28e-5`，并保存 | 仅验证曲面墙、对称接触、反力/位移历史；不是 Marshall 试件或稳定度/流值计算 |
| `pfc-rutting-test/scripts/rutting_contact_pilot.p3dat` | 曲面轮末态竖向反力约 `4.07e4`、平移约 `2.84e-3`、压入约 `9.40e-5`，并保存 | 仅验证曲面轮接触、压入、平移和历史；不是轮载伺服、车辙演化或动态稳定度试验 |

数值仅用于确认运行链路非空，不具有工程单位下的材料或规范意义。临时保存态未
提交仓库。若命令被修改、目标 PFC5 环境改变，或资产被扩展为生产案例，必须重新
运行并更新证据；任何完整沥青模型仍需级配、体积闭合、接触标定、时间步敏感性、
试验对照和独立确认。
