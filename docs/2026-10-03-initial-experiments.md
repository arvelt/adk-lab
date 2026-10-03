# 最初の3実験のレポート

実施日：2026-10-03。
対象：初期実装コミット `6b98cee140eebdcbed8d508d121c5c48df23df71`。
実行手順は[README](../README.md)を参照してください。

## 実行結果

2026-10-03、以下の3本を実行しました。

| ファイル | Question | Observed behavior |
| --- | --- | --- |
| [basic_agent.py](../experiments/basic_agent.py) | 最小AgentでローカルLLMへテキスト入力できるか | 成功。入力「2 + 3」に最終テキスト `5`。 |
| [output_schema.py](../experiments/output_schema.py) | `output_schema` は何を返すか | 成功。最終テキストは `{"city":"Tokyo","country":"Japan"}` 相当のJSON文字列。Pydantic検証に通り、`output_key` によりセッションに同じ値の辞書を保存。 |
| [output_schema_with_tools.py](../experiments/output_schema_with_tools.py) | 同一Agentにtoolsとoutput_schemaを指定できるか | 成功。`get_reading("sample_01")` が実際に1回実行され、`set_model_response` 経由で `{"sample_id":"sample_01","reading":731}` を返し、セッションにも辞書を保存。 |

## 検証環境と仕様の切り分け

- Python 3.11.17 / google-adk 2.11.0 / LiteLLM 1.103.2 / Pydantic 2.13.5 / uv 0.12.22。
- Ollama APIのversionは0.35.1。モデルは `qwen3:8b`（8.2B、Q4_K_M）。
  `ollama list` で存在を確認し、`ollama show qwen3:8b` でtools対応を確認しました。
- モデルへのプロンプトには `/no_think` を付け、Agentのtemperatureを0にしました。
- 3本とも `RESULT: PASS`、終了コード0でした。失敗時は例外を隠さず非ゼロ終了します。
  各実験には全体180秒、モデル呼び出し120秒、最大6回の上限を設けています。
- 併用実験で `LiteLlm.capabilities.output_schema_and_tools` は `False` でした。
  ただしこれはAgent設定の禁止を意味しません。インストール済みADKの
  `flows/llm_flows/basic.py` と `flows/llm_flows/prompt/_schema.py` を確認すると、
  ネイティブ併用ができない経路ではADKが `set_model_response` を追加します。
  実行時にも両リクエストのtoolsは `["set_model_response","get_reading"]`、
  ネイティブresponse_schemaは未設定でした。
- イベントは `get_reading` 呼び出し → ツール結果731 →
  `set_model_response` 呼び出し → 最終JSON、の順でした。
  返されたJSONだけでなく、Python関数内の記録で実際のツール実行も検証しています。
- 併用実験では `JSON_SCHEMA_FOR_FUNC_DECL` のEXPERIMENTAL警告が出ましたが、
  エラーは発生しませんでした。過去に遭遇した制約について、その当時のバージョン・条件は未確認です。
  今回の成功を他のモデル・バージョンの保証にはしません。
- 外部の私有データは使用せず、ツールの731はスクリプト内で定義した架空の測定値です。
  Gemini等への切替やAPIキーの設定は、今回の検証では必要ありませんでした。

確認に使用した公式情報：
[ADKのOllama接続](https://adk.dev/agents/models/ollama/)、
[ADK LlmAgent実装](https://github.com/google/adk-python/blob/main/src/google/adk/agents/llm_agent.py)、
[LiteLlm実装](https://github.com/google/adk-python/blob/main/src/google/adk/models/lite_llm.py)、
[構造化出力の補助ツール経路](https://github.com/google/adk-python/blob/main/src/google/adk/flows/llm_flows/prompt/_schema.py)。
GitHubのmainは更新されるため、上記実行結果はlockファイルのバージョンを基準にしてください。
