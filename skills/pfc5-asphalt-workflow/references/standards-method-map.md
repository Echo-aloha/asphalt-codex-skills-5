# 沥青模型规范与方法链

本文件记录规范的作用边界和方法编号，不分发规范正文、完整参数表或验收限值。
下列信息于 2026-08-19 根据合法取得的相应版次核对；实施项目仍须由人工复核
所用条款、勘误、项目专用文件和合同约定。

## 规范角色

| 规范 | 在 PFC5 工作流中的角色 | 不应直接当作什么 |
| --- | --- | --- |
| JTG 3410-2025 | 沥青与沥青混合料取样、成型、体积指标和室内性能试验方法 | 配合比级配或工程验收限值来源 |
| JTG 3432-2024 | 粗集料、细集料和填料的筛分、密度、吸水率、形状及力学试验来源 | DEM 粒径截断或颗粒形状的自动选择器 |
| JTG D50-2017 | 路面结构设计、材料设计参数和结构验算背景 | 单个室内试验的操作规程 |
| JTG F40-2004 | 施工、配合比和过程质量控制的项目来源之一；使用前核对项目采用状态 | 2025 版室内试验方法的替代品 |
| JTG 3450-2019 | 压实度、平整度、抗滑、渗水、车辙和结构响应等现场验证方法 | 室内 DEM 边界条件的默认值来源 |
| JTG 5110-2023 | 养护决策、检查与技术管理的上位标准 | 接触参数标定数据 |
| JTG 5142-2019 | 沥青路面病害调查、评价和养护处治背景 | 微观破坏参数的直接换算公式 |
| JTG 5210-2018 | 公路技术状况检测与评定指标体系 | 试件级本构或材料参数来源 |
| JTG F80/1-2017 | 土建工程质量检验评定与工程验收背景 | PFC 试件生成方法 |
| JTG D30-2015 | 路基设计和路床/地基条件来源 | 沥青混合料接触模型来源 |
| JTG/T 3610-2019 | 路基施工、压实和质量控制背景 | 沥青混合料室内试验方法 |

## JTG 3410-2025 方法链

一个可审计的模型不能只记录最终性能试验编号。至少冻结以下链条；不适用项写
`not_applicable`，未知项写 `pending_source_review`。

1. **取样与试样准备**：室内混合料取样采用 T 0701-2025；试样准备采用
   T 0740-2025。
2. **成型**：马歇尔击实采用 T 0702-2025；轮碾成型采用 T 0703-2025；
   静压和旋转压实分别由 T 0704-2011、T 0736-2025 管理。模型压实是数值
   等效过程，必须说明与所选实验成型方法的差异。
3. **密度与体积指标**：从 T 0705、T 0706、T 0707、T 0708、T 0741、
   T 0717 或 T 0711 中选择与材料和试件相符的方法；记录实测密度、理论最大
   相对密度、空隙率及其来源，不能仅用试件高度代替体积闭合。
4. **马歇尔**：当前方法为 T 0709-2025；标准/大型试件均要求追溯至
   T 0702 成型。荷载-变形曲线、原点修正、峰值不明显时的修正规则、稳定度、
   流值和马歇尔模数必须作为一条后处理链保存。
5. **强度与模量**：根据目标选择 T 0713、T 0714、T 0738、T 0742、
   T 0715 或 T 0716；不得把单轴、劈裂、弯曲和剪切结果互相替代。
6. **疲劳与裂纹扩展**：根据目标选择 T 0739、T 0743、T 0744 或
   T 0765，并保留加载模式、控制模式、温度和失效定义。
7. **高温性能**：车辙采用 T 0719-2025；重复压缩和单轴贯入分别由
   T 0745-2025、T 0746-2025 管理。固定等效循环荷载不能冒充 T 0719
   的往返车轮运动。
8. **低温和水敏感性**：按目标选择 T 0747、T 0748、T 0720，或
   T 0729、T 0730、T 0749、T 0750。模型必须声明是否真正模拟温度/水作用，
   还是仅对相应实验曲线做参数标定。

## JTG 3432-2024 集料输入链

- 级配输入应追溯粗集料 T 0302-2024、细集料 T 0327-2005 或填料
  T 0351/T 0356，而不是从 AC 名称猜测筛分曲线。
- 分档质量转体积时，应选择与材料相符的粗/细集料密度及吸水率方法，并记录
  试验方法、状态和单位；不同材料来源不得无依据共用一个密度。
- 针片状、棱角性、破碎、磨耗、磨光、高温稳定性等试验用于约束形状表示和
  接触假设，但不能直接变成 clump 模板或微观强度参数，仍需图像/宏观试验标定。

## 设计、现场与养护数据的使用边界

- JTG D50-2017 的结构设计参数用于定义模型目标或全路面边界，不替代
  JTG 3410-2025 的材料试验过程。
- JTG 3450-2019 的现场压实度、车辙、渗水、平整度、抗滑和结构响应可作为
  独立验证数据；必须记录空间尺度、测点规则和试件到现场的尺度差异。
- 养护、技术状况和质量评定规范用于确定工程问题与验收语境，不得反演成唯一
  一组 DEM 参数。
- 项目规范、设计文件、施工配合比和实测数据与通用规范冲突时，先冻结适用性
  决策并保留批准记录，不在脚本中静默覆盖。

## 最小来源记录

```yaml
standard_chain:
  - role: <aggregate|sampling|forming|density|performance|field_validation|acceptance>
    designation: <standard edition>
    method_id: <method or clause>
    clause_or_printed_page: <locator>
    source_id: <licensed copy, official source, project record or lab record>
    source_sha256: <digest when a stable source file exists>
    reviewer: <person or review process>
    reviewed_on: <YYYY-MM-DD>
    values_used: [<symbol/unit/provenance>]
    model_mapping: <normative input, measured target, DEM equivalent or numerical control>
```

Each list item owns its provenance. Do not place one edition, source ID or reviewer above
the list when the chain contains multiple standards or project records. Repeat a role
when several methods contribute. The package review baseline is recorded in
[standards-source-ledger.json](standards-source-ledger.json); project-specific values
remain in the copied intake file.

原始规范 PDF 保持外部依赖。公开交付只包含上述来源记录、项目获准使用的输入值
及必要的计算审计，不包含整页扫描、完整标准表或大段条文。
