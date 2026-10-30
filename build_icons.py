#!/usr/bin/env python3
# 把 mangrove-icons/*.svg 内联进 mangrove-adventure.src.html，生成单文件 mangrove-adventure.html
# 用法: python3 build_icons.py
import base64, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ICONS_DIR = ROOT / 'mangrove-icons'
SRC = ROOT / 'mangrove-adventure.src.html'
OUT = ROOT / 'mangrove-adventure.html'

def data_uri(path):
    return 'data:image/svg+xml;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

def main():
    icons = {p.stem: data_uri(p) for p in sorted(ICONS_DIR.glob('*.svg'))}
    if not icons:
        sys.exit('no icons found in ' + str(ICONS_DIR))
    html = SRC.read_text(encoding='utf-8')

    used = set()
    def repl(m):
        name = m.group(1)
        if name not in icons:
            sys.exit('missing icon file: %s.svg' % name)
        used.add(name)
        return icons[name]
    html = re.sub(r'\{\{ic:([a-z0-9_-]+)\}\}', repl, html)
    html = html.replace('{{IC_MAP}}', json.dumps(icons, ensure_ascii=False))

    problems = []
    left = re.findall(r'\{\{[^}]{0,40}\}\}', html)
    if left:
        problems.append('leftover tokens: %s' % sorted(set(left)))
    # 表情符号检查：不允许任何 emoji（→ ✕ ✔ ｜ 等文本符号除外）
    allow = set('→✕✔')
    emojis = sorted({c for c in html
                     if ord(c) >= 0x1F000 or (0x2600 <= ord(c) <= 0x27BF and c not in allow)})
    if emojis:
        problems.append('emoji left: %s' % emojis)
    if problems:
        sys.exit('\n'.join(problems))

    OUT.write_text(html, encoding='utf-8')
    unused = sorted(set(icons) - used)
    print('icons inlined: %d / %d files (unused: %s)'
          % (len(used), len(icons), unused or 'none'))
    print('output: %s (%.1f KB)' % (OUT, len(html.encode('utf-8')) / 1024))

if __name__ == '__main__':
    main()
