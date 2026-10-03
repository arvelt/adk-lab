# output_schema_with_tools

[実験一覧](README.md) · [スクリプト](../experiments/output_schema_with_tools.py)

## Question

同一のADK Agentにtoolsとoutput_schemaを指定した場合、ツールを実際に実行し、
構造化出力を返せるか。

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
uv run experiments/output_schema_with_tools.py
```

## Observed behavior

`get_reading` をtoolsに指定し、`sample_id: str` と `reading: int` を持つ
Pydanticモデルをoutput_schemaに指定しました。output_keyは `reading` です。
ツールの731はスクリプト内で定義した架空の測定値で、私有データは使っていません。

入力：

```text
Get the reading for sample_01 using get_reading. /no_think
```

実行時の出力：

```text
ADK_REQUEST: {"tools": ["set_model_response", "get_reading"], "native_response_schema": false}
FUNCTION_CALL: get_reading {"sample_id": "sample_01"}
FUNCTION_RESPONSE: get_reading {"sample_id": "sample_01", "reading": 731}
ADK_REQUEST: {"tools": ["set_model_response", "get_reading"], "native_response_schema": false}
FUNCTION_CALL: set_model_response {"sample_id": "sample_01", "reading": 731}
FUNCTION_RESPONSE: set_model_response {"sample_id": "sample_01", "reading": 731}
FINAL_TEXT: '{"sample_id": "sample_01", "reading": 731}'
EXECUTED_TOOL_CALLS: ["sample_01"]
MODEL_CAPABILITIES: {'output_schema_and_tools': False}
SESSION_STATE: dict {"sample_id": "sample_01", "reading": 731}
RESULT: PASS
```

終了コードは0でした。`get_reading` の関数内の記録でも、実際に1回実行されたことを確認しました。
最終JSONはPydantic検証に通り、セッションには同じ値の辞書が保存されました。
`JSON_SCHEMA_FOR_FUNC_DECL` のEXPERIMENTAL警告が出ましたが、エラーは発生しませんでした。

## Interpretation

インストール済みADKの `flows/llm_flows/basic.py` と
`flows/llm_flows/prompt/_schema.py` を確認しました。

今回、`LiteLlm.capabilities.output_schema_and_tools` は `False` でしたが、
Agentへの併用指定は禁止されませんでした。ADKが `set_model_response` を追加し、
その呼び出し結果から最終JSONを生成する補助ツール経路で成功しました。
実行時のリクエストでもネイティブresponse_schemaは未設定でした。

過去に遭遇した制約について、その当時のバージョン・条件は未確認です。
今回の結果は上記の環境での成功を示し、他のモデル・バージョンでの成功を保証するものではありません。

## References

- [ADK LlmAgent実装](https://github.com/google/adk-python/blob/main/src/google/adk/agents/llm_agent.py)
- [LiteLlm実装](https://github.com/google/adk-python/blob/main/src/google/adk/models/lite_llm.py)
- [構造化出力の補助ツール経路](https://github.com/google/adk-python/blob/main/src/google/adk/flows/llm_flows/prompt/_schema.py)

GitHubのmainは更新されます。上記の結果は記載したバージョンでの実測です。
