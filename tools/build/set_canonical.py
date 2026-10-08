#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""set_canonical.py — ставит <link rel="canonical"> в HTML-страницы копии на GitHub Pages.
Карта «файл → канонический адрес» читается из canonical.json; тег вставляется сразу после
<meta charset>, существующий canonical заменяется. Запуск: python3 tools/build/set_canonical.py"""
import json, re, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[2]
cmap = json.loads((root / 'tools/build/canonical.json').read_text(encoding='utf-8'))
for rel, url in cmap.items():
    p = root / rel
    if not p.exists():
        print('нет файла:', rel); sys.exit(1)
    s = p.read_text(encoding='utf-8')
    s = re.sub(r'\s*<link rel="canonical" href="[^"]*">', '', s)
    tag = f'\n<link rel="canonical" href="{url}">'
    s, n = re.subn(r'(<meta charset="UTF-8">)', r'\1' + tag.replace('\\', '\\\\'), s, count=1, flags=re.I)
    if n != 1:
        print('не найден <meta charset>:', rel); sys.exit(1)
    p.write_text(s, encoding='utf-8')
    print('canonical →', rel, '→', url)
