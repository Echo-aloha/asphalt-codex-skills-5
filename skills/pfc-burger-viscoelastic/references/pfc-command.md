# Burger 模型 PFC 命令笔记

> 本技能只面向 PFC 5.0。下列命令是待运行探针核对的 PFC5.0 骨架；属性名、
> 单位和接触状态转换必须由可用的 PFC5.0 运行时确认。不要把旧案例数值当作
> 可移植的生产默认值。

## 1. 参数记录模板

| 参数 | 角色 | 值/单位要求 |
| --- | --- | --- |
| bur_knm / bur_ksm | Maxwell 法向/切向刚度 | 由固定离散化后的响应反演，记录单位 |
| bur_cnm / bur_csm | Maxwell 法向/切向黏壶系数 | 由稳态流动段约束，记录单位 |
| bur_knk / bur_ksk | Kelvin 法向/切向刚度 | 由延迟变形幅值约束，记录单位 |
| bur_cnk / bur_csk | Kelvin 法向/切向黏壶系数 | 与 Kelvin 刚度共同决定迟滞时间 |
| bur_fric | 摩擦系数 | 无量纲；由界面假设/试验约束 |

## 2. PFC 5.0 命令骨架（cmat 顶层，运行前探针核对）

以下只展示未来接触默认与现有接触重赋值的控制流，不提供未经标定的参数值：

```fish
define set_burger
    if use_burger = 1
        command
            cmat default type ball-ball model burger property ...
                bur_knk @bur_knk bur_cnk @bur_cnk ...
                bur_knm @bur_knm bur_cnm @bur_cnm ...
                bur_ksk @bur_ksk bur_csk @bur_csk ...
                bur_ksm @bur_ksm bur_csm @bur_csm ...
                bur_fric @bur_fric
            cmat default type ball-facet model linear property ...
                kn @wall_kn ks @wall_ks fric @wall_fric ...
                dp_nratio @wall_dp_nratio dp_sratio @wall_dp_sratio
            ; cmat apply 会重置现有接触的本构状态；执行前保存，执行后重新平衡
            cmat apply
        endcommand
    else
        ; linear 回退（仅用于诊断）
        command
            cmat default type ball-ball model linear property ...
                kn @lin_kn ks @lin_ks fric @lin_fric ...
                dp_nratio @lin_dp_nratio dp_sratio @lin_dp_sratio
            cmat default type ball-facet model linear property ...
                kn @wall_kn ks @wall_ks fric @wall_fric ...
                dp_nratio @wall_dp_nratio dp_sratio @wall_dp_sratio
            cmat apply
        endcommand
    endif
end
```

要点：
- 此骨架假定所有 ball-ball 接触都代表砂浆介导的集料相互作用；若模型显式包含多类颗粒/界面，必须按 PFC5.0 可用的分组与接触选择机制分别赋值。
- 集料-墙（ball-facet）用 linear 高摩擦。
- 不要把 `contact delete` 当作切换模型的通用步骤。删除接触会丢失接触历史并可能改变装配状态；应保存切换前状态，区分未来默认与现有接触重赋值，并在 `cmat apply` 后重新平衡和审计接触数/力。

## 3. 版本边界

本文件只维护 PFC 5.0 `cmat` 骨架。检测到其他主版本命令时应停止并报告
版本不兼容；本包不保留迁移伪代码。

## 4. 拼写与状态注意

- 模型名为 **`burger`**（不带复数）；个别旧文档出现 `burgers` 属笔误，使用前以目标版本官方文档核对。
- PFC 5.0 的 `cmat default` 与 `cmat apply` 分别涉及未来接触默认和现有接触重赋值；具体选择范围与可用语法必须通过 PFC5.0 探针确认。
- Burger 引入黏性后需复核时间步敏感性；时间步设置/查询命令须由 PFC5.0 运行探针确认。

## 5. 快速验证

赋模型后小步 `cycle`，检查：
- 接触数量与类型（`contact list` 确认 burger 接触已建立）。
- 平衡后无颗粒穿透墙、无数值爆炸（时间步过大）。
- 蠕变趋势：恒定荷载下变形随时间增长，卸载后有残留变形（Burger 生效的标志）。
