# 马歇尔试验的底层框架：fistPkg dc.fis

> 本文件提炼自 Itasca fistPkg26 `dc.fis`（PFC 5.0）。马歇尔可以复用其
> 双头控制骨架，但不是巴西劈裂强度试验。弧形几何之外仍需验证墙 ID/轴向、
> 接触、平滑、力/位移、终止和规范后处理。

## 1. 框架定位

`dc.fis` 提供**劈裂（间接拉伸）试验**的支持函数：两个相对压板
（platen/head）沿直径方向压缩圆柱试件，监测 wall-based 轴向力与应变。
马歇尔可复用相对运动和反力采集骨架，但压头几何、试件形成/调温、装置约束、
采样、曲线修正、稳定度/流值和水敏感性分支均不同，不能概括为“只换压头”。

## 2. 官方参数（在 dcParams.p2dat/p3dat 的 `dcSetParams` 中设置）

| 参数 | 含义 | 默认/说明 |
| --- | --- | --- |
| dc_w | 压板宽 | 必填，> 0 |
| dc_d | 压板深（仅 3D） | 3D 必填，2D 为单位厚度 |
| dc_emod | 压板有效模量（linear 接触用） | 缺省回退 mv_emod |
| dc_g0 | 初始压板间距 | 必填，> 0 |
| dc_eRate | 轴向应变率 | 必填，> 0；墙速 = 0.5·dc_eRate·dc_g0 |
| dc_loadCode | 加载阶段代码 | 0 单阶段 / 1 多阶段 |
| dc_loadFac | 荷载终止因子 | 默认 0.9（\|dc_wfa\| ≤ dc_loadFac·峰值 时停） |
| dc_ARatLimit | 平衡比限（ft_eq 参数） | 默认 1.0e-5 |
| dc_stepLimit | 步数限（ft_eq 参数） | 默认 200 万 |

内部量（只读）：

| 量 | 含义 |
| --- | --- |
| dcWp0 / dcWp1 | 下 / 上压板指针 |
| dc_wfa | wall-based 轴向力（正为拉伸） |
| dc_wea | wall-based 轴向应变（正为张开） |
| dc_wda | wall-based 轴向位移（= dc_wea·dc_g0） |
| dc_wfaMax | 轴向力绝对值最大值 |

## 3. 官方流程

```
dcSetupPhase    创建墙 → 去重叠 → 应变清零 → 静力平衡 → 存 <matName>-dc0
dcLoadingPhase  施加轴向应变 → 记录力/应变 → 荷载终止准则 → 存 <matName>-dc1
```

- `dcSetupPhase`：调 `_dcMakeWalls` 建墙 → `clean` 去颗粒-墙重叠 → `ft_SmoothGrainWallInterface` → `dc_wInit`（挂 callback：42.1 力、10.10 应变）→ `ft_eq` 静力平衡 → 存 dc0。
- `dcLoadingPhase`：单阶段（dc_loadCode=0）走 `_dcPerformStage(1, -1.0)`；多阶段走用户提供的 `dcPerformStages`。
- `_dcApplyAxialStrain`：设墙速 `0.5·dc_eRate·dc_g0`，`solve fishhalt _aASTPPdone`，终止准则为 `|dc_wfa| ≤ dc_loadFac·dc_wfaMax`。

## 4. 扩展点 `_dcMakeWalls`

官方 `_dcMakeWalls` 用**平面压板**：

```fish
def _dcMakeWalls
    ft_setGrainWallBehavior('existing', 0.0, dc_emod, 0.0, 0.0, 'linear')
    ft_setGrainWallBehavior('future',   0.0, dc_emod, 0.0, 0.0, 'linear')
    ; 3D：wall generate ... polygon ... makeplanar（宽 dc_w × 深 dc_d 的平面压板）
    ; 2D：wall create ... vertices（线段压板）
    dcWp0 = wall.find(1)   ; 下压板
    dcWp1 = wall.find(2)   ; 上压板
end
```

重定义 `_dcMakeWalls` 是更换弧形压头的最小钩子，不是完整适配的充分
条件。其余 `dc.fis` 逻辑必须按目标 PFC5 版本和标准版次逐项审计后才能复用。

> JTG E20-2011 已被 JTG 3410-2025 替代。现行马歇尔方法已核对为
> T 0709-2025，并需追溯 T 0702-2025 成型。旧 T0709 只用于明确的历史复现。

## 5. 稳定度与流值（规范概念）

- **稳定度 MS**：试件加载过程中出现的峰值荷载（kN）。
- **流值 FL**：对应峰值荷载时的变形（mm）。
- **马歇尔模数 T** = MS / FL。

DEM 输出的是 wall-based 轴向力 `dc_wfa` 与 wall-based 轴向位移 `dc_wda`。
它们只是原始曲线候选量；规范结果必须先统一两压头反力/相对位移、符号和单位，
再按 T 0709-2025 做原点修正，并对峰值不明显的曲线采用当前方法的独立分支。
详见 `jtg-3410-2025-t0709.md`。

PFC5 官方 `wall.force.contact` 返回**作用在该 wall 上的所有接触力之和**，并以
全局坐标表示；第二参数/`.x/.y/.z` 只是在全局坐标中取分量。相对布置的两个
压头应分别记录反力，在声明的加载轴上检查等值反向与不平衡误差，再按一个明确
的单压头、平均幅值或其他装置约定生成标量荷载。不能直接把带符号两反力相加。

`wall.disp` 是可读写的累计 wall displacement。建立预载参考时应同时保存两墙
位置/位移与初始间距，避免恢复存档或手动清零后把不同参考系的量混在一条曲线。

## 6. 监测与裂纹

- 力/应变由 `dc.fis` 的 callback（42.1 / 10.10）自动记录。
- 若试件为胶结材料（PB），配合 `ck.fis`/`ms` 裂纹监测，记录拉伸/剪切裂纹数。
