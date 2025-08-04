# みんなのPython勉強会#116

- [イベントサイト(connpass)](https://startpython.connpass.com/event/361667/)
- [スライド](https://drillan.github.io/stapy116/)
- [サンプルプロジェクト](https://github.com/drillan/stapy116/tree/main/pyqc)

## ドキュメント([sphinx-revealjs](https://sphinx-revealjs.readthedocs.io/))ビルド手順

uvのインストール方法については[公式サイト](https://docs.astral.sh/uv/getting-started/installation/)を参照してください。

次のコマンドでビルド：

```bash
uv run sphinx-build -M revealjs slides slides/_build
```