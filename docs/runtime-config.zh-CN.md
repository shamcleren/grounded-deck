# Runtime Configuration

[English](runtime-config.md) | [简体中文](runtime-config.zh-CN.md)

GroundedDeck 现在为 planner 和 quality 模块提供了可插拔的 provider 接口。

deterministic provider 仍然是本地测试和 `make eval` 的默认回归基线。

## 环境变量

- `GROUNDED_DECK_LLM_PROVIDER`
  支持的值：
  - `deterministic`
  - `openai-compatible`
- `GROUNDED_DECK_LLM_MODEL`
  传给所选 provider 的模型名。
- `GROUNDED_DECK_BASE_URL`
  `openai-compatible` 必填。
  预期形式：`https://host/v1`
- `GROUNDED_DECK_API_KEY_ENV`
  可选。
  默认值是 `GROUNDED_DECK_API_KEY`。
- `GROUNDED_DECK_API_KEY`
  由 `GROUNDED_DECK_API_KEY_ENV` 指定名称的 provider 凭证。

## 当前行为

- `deterministic`：
  默认使用，产出与 fixture 稳定一致，并由仓库测试覆盖。
- `openai-compatible`：
  目前已经支持配置加载、请求构造、JSON 响应解析，以及返回 payload 结构的本地校验。
  在线 HTTP 调用路径已经接通，但仓库测试仍然使用 mocked transport，而不依赖真实网络。

## 推荐用法

如果只是做本地仓库验证：

```bash
unset GROUNDED_DECK_LLM_PROVIDER
make eval
```

如果后续要尝试 OpenAI-compatible 后端：

```bash
make init-live-env
export GROUNDED_DECK_LLM_PROVIDER=openai-compatible
export GROUNDED_DECK_LLM_MODEL=gpt-4.1-mini
export GROUNDED_DECK_BASE_URL=https://api.openai.com/v1
export GROUNDED_DECK_API_KEY=YOUR_KEY
```

仓库里还提供了配置模板：[.env.runtime.example](../.env.runtime.example)。
如果仓库根目录存在 `.env.runtime.local`，GroundedDeck 现在会在执行 live verification 相关命令前自动读取它。

`make init-live-env` 会在 `.env.runtime.local` 不存在时，用模板自动创建它。

不过仓库已经提供了 fixture 驱动的本地示例运行入口：

```bash
make example-pipeline
```

它会输出：

- `/tmp/grounded-deck-example/normalized-pack.json`
- `/tmp/grounded-deck-example/slide-spec.json`
- `/tmp/grounded-deck-example/quality-report.json`
- `/tmp/grounded-deck-example/verification-summary.json`

如果要对已配置的非确定性 provider 做可选的在线验证，可以运行：

```bash
make prepare-live-verification
make check-live-env
make live-status
make verify-online
```

如果 `GROUNDED_DECK_LLM_PROVIDER` 最终仍然解析为 `deterministic`，这个命令会直接失败。

`make check-live-env` 会先告诉你当前还缺哪些必需配置，再决定是否执行在线验证。
`make prepare-live-verification` 会生成 `reports/live-verification-checklist.md`。
`make live-status` 会显示环境是否就绪，以及 `/tmp/grounded-deck-online/` 下是否已经存在最近一次验证摘要。

如果执行成功，还会写出：

- `/tmp/grounded-deck-online/verification-summary.json`

如果要把最近一次在线验证尝试沉淀进仓库记忆，可以运行：

```bash
make archive-online-verification
```

它会写出：

- `reports/live-verification-latest.json`
- `reports/live-verification-latest.md`

如果要查看已经归档的验证报告，可以运行：

```bash
make report-live-verification
```

归档报告既可以表示一次成功运行，也可以表示一次带有明确错误信息的失败尝试。
