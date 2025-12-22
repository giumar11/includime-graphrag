# quick CSV validation (required columns + basic checks)
import sys, csv

REQUIRED_NODES = {"id","type","name"}
REQUIRED_EDGES = {"id","src","dst","rel"}

def has_cols(path, required):
    with open(path, newline='', encoding='utf-8') as f:
        header = set(next(csv.reader(f)))
    missing = required - header
    if missing:
        print(f"[ERROR] {path} missing columns: {missing}")
        return False
    return True

ok = True
ok &= has_cols("data/nodes.csv", REQUIRED_NODES)
ok &= has_cols("data/edges.csv", REQUIRED_EDGES)

if not ok:
    sys.exit(1)
print("[OK] CSV structure validated")
