import ast,pathlib
FORBIDDEN_GATES={"gate0","gate1","gate2"}
def find_forbidden_gate_imports(paths):
    out=[]
    for path in paths:
        try:t=ast.parse(pathlib.Path(path).read_text(),filename=str(path))
        except SyntaxError as e:out.append(f"{path}: UNPARSEABLE {e.msg}");continue
        for n in ast.walk(t):
            if isinstance(n,ast.Import):
                for a in n.names:
                    if a.name.split('.')[0] in FORBIDDEN_GATES:out.append(f"{path}: import {a.name}")
            elif isinstance(n,ast.ImportFrom) and (n.module or '').split('.')[0] in FORBIDDEN_GATES:out.append(f"{path}: from {n.module} import")
    return out
def scan_gate_sources(root="src/gate3"):
    base=pathlib.Path(root)
    if not base.is_dir():return [],f"GATE3_SOURCE_ROOT_MISSING: {base}"
    fs=sorted(base.rglob("*.py"))
    return (fs,None) if fs else ([],f"GATE3_SOURCE_SCAN_EMPTY: {base}")
