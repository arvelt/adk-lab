# Experiments

実験ごとの確認事項とレポートの一覧です。実行手順は[README](../README.md)を参照してください。

| 実験 | 確認する内容 | レポート |
| --- | --- | --- |
| [basic_agent.py](../experiments/basic_agent.py) | 最小AgentでローカルLLMにテキストを入力し、応答を得られるか | [basic_agent](basic_agent.md) |
| [output_schema.py](../experiments/output_schema.py) | output_schema指定時の最終応答とセッションの値 | [output_schema](output_schema.md) |
| [output_schema_with_tools.py](../experiments/output_schema_with_tools.py) | 同一Agentでtoolsとoutput_schemaを併用した場合の挙動 | [output_schema_with_tools](output_schema_with_tools.md) |

レポートは `docs/<実験スクリプト名>.md` に1実験1ファイルで保存します。
実験を追加したら、この一覧に行を追加します。再検証の記録は同じレポートに実施日と環境を添えて追記します。
