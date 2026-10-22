# KMD Blocks — библиотека блоков AutoCAD для КМД

Библиотека блоков для чертежей КМД (металлоконструкции деталировочные):
оформление по СПДС/ЕСКД, сечения проката по ГОСТ-сортаментам, метизы и
часто используемые объекты.

Библиотека рассчитана на работу Claude через
[Autocad-MCP](https://github.com/U-C4N/Autocad-MCP) с живым AutoCAD 2026
и переносится между проектами.

- [docs/ROADMAP.md](docs/ROADMAP.md) — анализ и план работ
- [docs/STANDARD.md](docs/STANDARD.md) — требования к блокам (черновик v0.1)

Статус: этап 0 — согласование стандарта и перечня блоков.

- [docs/CATALOG.md](docs/CATALOG.md) — перечень блоков (актуализируется)

## Сборка

```bash
pip install -r requirements.txt
python -m kmd_blocks.build            # блоки → dist/, индекс → catalog/index.csv
python -m examples.pilot_20B1_bolt    # пилот: сечение 20Б1 с болтом М16 → dist/examples/
pytest
```

Размеры ГОСТ в `data/*.csv` помечены `verified=no`, пока их не сверит проектировщик.
