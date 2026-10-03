# adk-lab

Google ADKの仕様確認・境界条件検証に特化した、1ファイル完結の実験スクリプト集です。
公式サンプル集の複製は目的にしません。モデル・Agent・tools・schemaは各ファイルに直接記述し、共通化せず重複を許容します。

## Installation

前提：Git、uv、`http://localhost:11434` で稼働中のOllama、導入済みの `qwen3:8b`。APIキーは不要です。

初回はリポジトリを取得し、依存関係を準備します。

```sh
git clone git@github.com:arvelt/adk-lab.git
cd adk-lab
uv sync --python 3.11 --locked
```

取得済みの場合はリポジトリのルートで `uv sync --python 3.11 --locked` を実行します。

## Usage

リポジトリのルートで、モデルの存在とtools対応を確認します。

```sh
ollama list
ollama show qwen3:8b
```

`ollama list` に `qwen3:8b`、`ollama show` のCapabilitiesに `tools` があることを確認し、実験を実行します。

```sh
uv run experiments/basic_agent.py
uv run experiments/output_schema.py
uv run experiments/output_schema_with_tools.py
```

各スクリプトは環境情報と応答を表示します。検証を通過すると `RESULT: PASS` を表示し、終了コード0で終了します。
失敗時は例外を表示し、非ゼロで終了します。全体180秒、モデル呼び出し120秒、最大6回の上限があります。

## Configuration

モデル名と接続先は各スクリプト内の `MODEL` と `API_BASE` で指定します。
接続には `LiteLlm` の `ollama_chat` を使い、各スクリプトが `OLLAMA_API_BASE` を設定します。
モデルや接続先を変える場合は、実行するファイル内の定数を編集してください。

`.env.example` は説明用です。スクリプトは.envを読み込まず、環境変数の事前設定も不要です。

## Reports

[実験一覧](docs/README.md)から、各実験の詳細レポートを参照できます。
