# 制图脚本说明

`generate_all_figures.py` 是本目录唯一正式制图程序，只读取 `workplace/output/` 中整理后的 Q1–Q4 正式 CSV/JSON，并将 16 张 PNG 直接写入 `workplace/essay/asset/`。

运行命令：

```bash
python essay/asset/script/generate_all_figures.py
```

脚本不调用任何求解器，不修改 `data/`、`src/` 或 `output/`。表格为正式结果 CSV 的章节编号副本，不由本制图脚本改写。
