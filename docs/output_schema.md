# output_schema

[実験一覧](README.md) · [スクリプト](../experiments/output_schema.py)

## Question

Pydanticモデルをoutput_schemaに指定すると、最終応答とセッションには何が返るか。

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
uv run experiments/output_schema.py
```

## Observed behavior

`city: str` と `country: str` を持つPydanticモデルをoutput_schemaに指定し、
output_keyを `city_fact` に設定しました。toolsは指定していません。

入力：

```text
The city is Tokyo and the country is Japan. /no_think
```

出力：

```text
FINAL_TEXT: '{\n\n"city": "Tokyo",\n"country": "Japan"\n}'
SESSION_STATE: dict {"city": "Tokyo", "country": "Japan"}
RESULT: PASS
```

終了コードは0でした。最終応答のテキストはJSON文字列で、Pydanticの
`model_validate_json` に通りました。セッションの `city_fact` は同じ値を持つ辞書でした。
スクリプトは抽出値と、最終応答・セッションの一致を検証しています。

## References

- [ADK LlmAgent実装](https://github.com/google/adk-python/blob/main/src/google/adk/agents/llm_agent.py)
- [LiteLlm実装](https://github.com/google/adk-python/blob/main/src/google/adk/models/lite_llm.py)

GitHubのmainは更新されます。上記の結果は記載したバージョンでの実測です。
