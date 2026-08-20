# fistPkg (FISHTank) 总览

> Itasca 官方为 PFC 5.0 提供的材料建模支持包（fistPkg / FISHTank）。本文件仅提炼用法与结构，不复制其源码；fistPkg 版权归 Itasca。

## 1. 能力

- **材料生成（Material genesis）**：五种材料——linear（线性）、contact-bonded（接触黏结）、parallel-bonded（平行黏结）、flat-jointed（平节理）、Hill（用户自定义，3D）。
  - 容器形状：polyaxial（多轴/长方体）、cylindrical（圆柱）、spherical（球形）。
  - 颗粒可为 ball 或 clump。
- **材料试验（Material tests）**：压缩（confined 围压 / unconfined 无围压 / uniaxial strain 单轴应变）、劈裂（diametral-compression）、直接拉伸（direct-tension）。
- **微观结构监测**：颗粒级配、微观结构图、胶结材料的裂纹监测。

## 2. 目录布局

```
fistPkgN/
├── fistPkg-README.txt
├── fistPkg-publicMods.txt
├── Documentation/              ; PDF 文档（BPM、FlatJoint、Hill、MatModelingSupport）
└── ExampleProjects/
    ├── fistSrc/                ; ft/ck/ct/dc/tt/hl 与 Hill DLL
    └── MatGen-{Linear,ContactBonded,ParallelBonded,FlatJointed,Hill}/
        └── {CompTest,DiamCompTest,TenTest}/
```

## 3. 五种材料类型

| 材料 | 接触模型 | 典型用途 |
| --- | --- | --- |
| Linear | linear（无黏结） | 无黏结颗粒（砂、集料摩擦） |
| ContactBonded | linearcbond | 弱胶结材料 |
| ParallelBonded | linearpbond | 岩石、胶结颗粒、沥青混合料简化 |
| FlatJointed | flatjoint | 互锁晶粒、致密岩石 |
| Hill (UDM) | Hill 自定义模型 | 含水分效应的晶粒接触（3D） |

> 马歇尔可复用 dc.fis 的双头加载控制骨架，但不能据此等同为巴西劈裂试验；
> 几何、边界、力/位移和规范后处理必须单独验证（见 `pfc-marshall-test`）。

## 4. 三种标准试验

| 试验 | FISH 工具 | 对应沥青应用 |
| --- | --- | --- |
| 压缩 CompTest | ct.fis | 单轴压缩（强度/模量标定） |
| 劈裂 DiamCompTest | dc.fis | 马歇尔稳定度/流值（弧形压头变体） |
| 直接拉伸 TenTest | tt.fis | 抗拉强度 |

## 5. 示例运行方式（README 提炼）

1. 复制 `fistSrc` 与 `MatGen-X` 到工作目录（如 myRUNS）。
2. 打开 2D/3D 的 MatGen-X 项目，运行材料生成。
3. 生成完成后打开对应 XTest（Comp/DiamComp/Ten）项目运行试验。

## 6. 与沥青 skill 的关系

- `pfc-marshall-test`：复用 dc.fis 框架，通过重定义 `_dcMakeWalls` 安装自定义（如弧形）压头。
- `pfc-asphalt-mixture`：试样生成借鉴 MatGen 的"材料生成→试验"阶段化思想。
- 标定顺序（弹性→强度→黏弹性）与 fistPkg 的"先材料后试验"一致。
