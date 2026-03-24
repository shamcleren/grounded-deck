# Strongest Demo

[English](STRONGEST-DEMO.md) | [简体中文](STRONGEST-DEMO.zh-CN.md)

## 已选 Demo Case

GroundedDeck 当前最强的 planning demo 是中国新能源汽车出海进入策略案例，位于：

- [strongest-demo-source-pack.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/source-packs/strongest-demo-source-pack.json)

这个案例能约束当前架构不漂移，因为同一个紧凑 source pack 必须同时驱动：

- 中文叙事
- 一个明确的战略建议
- 同一套 deck 中的多种 visual structure
- 每一页内容页上的显式 source bindings

## 工件包

当前确定性 strongest-demo 工件包包括：

- source pack：[strongest-demo-source-pack.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/source-packs/strongest-demo-source-pack.json)
- normalized units：[strongest-demo-normalized-source-units.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/normalized-source-units/strongest-demo-normalized-source-units.json)
- slide spec：[strongest-demo-slide-spec.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/slide-spec/strongest-demo-slide-spec.json)
- quality report：[strongest-demo-quality-report.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/quality-reports/strongest-demo-quality-report.json)

## Success Metrics

只有在以下条件全部成立时，这个 demo 才算“有说服力”：

1. Coverage：每个 normalized source unit 都出现在 `must_include_checks` 中，且 `coverage_ratio = 1.0`。
2. Grounding：每个非封面页都至少保留一个合法 source binding，且 `grounding_ratio = 1.0`。
3. Visual form：planner 为每个 grounded unit 选择了预期的 visual structure，且 `match_ratio = 1.0`。

## 预期 Visual Forms

- `src-01:sec-01` -> `timeline`
- `src-01:sec-02` -> `comparison`
- `src-02:sec-01` -> `process`
- `src-03:sec-01` -> `chart`

## 为什么先做这个 Demo

这个案例是当前最强的产品证明点，因为它在 renderer 之前就能证明 grounded planning quality：

- source pack 足够小，便于人工审查
- 但 deck 仍然需要四种不同的 layout decision
- 输出继续通过 `slide spec` 保持可审计
- 同一套工件未来可以直接复用到 live-provider verification
