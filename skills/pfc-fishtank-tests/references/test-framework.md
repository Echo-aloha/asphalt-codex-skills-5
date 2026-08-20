# fistPkg 试验框架与 FISH 工具用法

## 1. FISH 工具用途与调用

| 工具 | 职责 | 关键扩展点 |
| --- | --- | --- |
| `ft.fis` | 主库：墙-颗粒行为设置、平衡、应变/应力量测 | `ft_setGrainWallBehavior`、`ft_eq` |
| `ck.fis` | 检查：级配、配位数、微观结构 | 生成后自检 |
| `ct.fis` | 压缩试验：围压/无围压/单轴应变 | `_ct...` 系列 |
| `dc.fis` | 劈裂试验：压头加载 + 峰后停止 | `_dcMakeWalls`、`_dcSetWallVel` |
| `tt.fis` | 直接拉伸 | — |

### 墙-颗粒行为（ft.fis）

```fish
; 设置既有/未来接触的颗粒-墙行为
ft_setGrainWallBehavior('existing', 0.0, dc_emod, 0.0, 0.0, 'linear')
ft_setGrainWallBehavior('future',  0.0, dc_emod, 0.0, 0.0, 'linear')
```

### 平衡（ft.fis）

```fish
retCode = ft_eq(dc_ARatLimit, dc_stepLimit)
```

## 2. 扩展点：`_dcMakeWalls`

dc.fis 通过 `_dcMakeWalls` 创建压板，官方默认实现为**平面压板**：

```fish
def _dcMakeWalls
    ; OUT: dcWp0/dcWp1 上下压板指针
    ft_setGrainWallBehavior('existing', 0.0, dc_emod, 0.0, 0.0, 'linear')
    ft_setGrainWallBehavior('future',   0.0, dc_emod, 0.0, 0.0, 'linear')
    ; 3D：wall generate ... polygon ... makeplanar（宽 dc_w × 深 dc_d 平面压板）
    ; 2D：wall create ... vertices（线段压板）
    dcWp0 = wall.find(1)   ; 下压板
    dcWp1 = wall.find(2)   ; 上压板
end
```

这是 dc.fis 的最小几何扩展点。非平面压头需要重定义本函数，但不能据此
假定其余逻辑无需验证；还要检查墙 ID、第二坐标轴约定、头部转动/平移约束、
颗粒-墙接触、`ft_SmoothGrainWallInterface`、力/位移符号、峰后停止和流值
后处理。详见 `pfc-marshall-test/references/overview.md`。

## 3. Hill UDM 安装注意

Hill 用户自定义接触模型（3D）需要 DLL：

- 文件：`contactmodelmechanical3dhill005_64.dll`
- 安装：复制到 `PFC500\exe64\plugins\contactmodelmechanical3D`（PFC 5.0 布局）。
- 仅 3D Hill 材料需要；linear/contact-bonded/parallel-bonded/flat-jointed 不需要额外 DLL。

## 4. 版本边界

- fistPkg 面向 PFC 5.0：`cmat default`、`wall create ... face`、FISH 语法均按 5.0 运行时核对。
- 检测到其他主版本目标或命令时停止；本包不负责迁移或兼容层。

## 5. 版权与复用约定

- fistPkg 源码版权归 Itasca，**不得**整段复制进公共 MIT 仓库。
- 正确做法：提炼"调用方式 + 命令模板 + 扩展点"，外部引用 fistPkg 路径，由用户自备官方包。
- 存档 `.sav`、STL、DLL 等二进制不入库，仅脚本与文档入库。
