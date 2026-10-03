# basic_agent

[実験一覧](README.md) · [スクリプト](../experiments/basic_agent.py)

## Question

最小のADK Agentで、ローカルLLMにテキストを入力し、応答を得られるか。

## Environment

実施日：2026-10-03。対象コミット：`350f7c200c326aaed23c2da618db51280aea4f05`。

| 項目 | 値 |
| --- | --- |
| Python | 3.11.17 |
| google-adk | 2.11.0 |
| LiteLLM | 1.103.2 |
| Pydantic | 2.13.5 |
| uv | 0.12.22 |
| Ollama API | 0.35.1 |
| モデル | qwen3:8b（8.2B、Q4_K_M） |
| 接続方法 | LiteLlm、`ollama_chat/qwen3:8b`、`http://localhost:11434` |

プロンプトに `/no_think` を付け、temperatureは0に設定しました。
全体180秒、モデル呼び出し120秒、最大6回の上限があります。

## Usage

リポジトリのルートで実行します。

```sh
uv run experiments/basic_agent.py
```

## Observed behavior

入力：

```text
What is 2 + 3? Answer with only the number. /no_think
```

出力：

```text
FINAL_TEXT: '5'
RESULT: PASS
```

終了コードは0でした。Agentにはtoolsやoutput_schemaを指定していません。
最終イベントからテキストを取り出し、値が `5` であることを検証しました。

## References

- [ADKのOllama接続](https://adk.dev/agents/models/ollama/)
- [LiteLlm実装](https://github.com/google/adk-python/blob/main/src/google/adk/models/lite_llm.py)

GitHubのmainは更新されます。上記の結果は記載したバージョンでの実測です。
