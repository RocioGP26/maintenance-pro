import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent / "templates"
for path in sorted(root.rglob("*.html")):
    if path.name == "_csrf.html":
        continue
    text = path.read_text(encoding="utf-8")
    if not re.search(r'method=["\']post["\']', text, re.I):
        continue
    if "_csrf.html" in text or "csrf_token()" in text:
        continue
    lines = text.splitlines(keepends=True)
    out = []
    changed = False
    for line in lines:
        out.append(line)
        if (
            re.search(r'<form\b[^>]*method=["\']post["\']', line, re.I)
            and line.rstrip().endswith(">")
        ):
            indent = re.match(r"^(\s*)", line).group(1)
            out.append(f'{indent}  {{% include "_csrf.html" %}}\n')
            changed = True
    if changed:
        path.write_text("".join(out), encoding="utf-8")
        print(path.relative_to(root.parent))
