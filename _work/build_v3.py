# -*- coding: utf-8 -*-
# v2 html + _work/out/*.json  ->  합격선_관리_v3.html  (재실행 가능)
import json, io, glob, os

BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
V2 = BASE + "/합격선_관리_v2.html"
V3 = BASE + "/합격선_관리_v3.html"

with io.open(V2, encoding="utf-8") as f:
    lines = f.read().split("\n")

# 1) 추출행 수집
all_rows = []
sources = []
flags_all = []
files = sorted(glob.glob(BASE + "/_work/out/*.json"))
for p in files:
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    rows = d.get("rows", [])
    all_rows.extend(rows)
    if d.get("source"): sources.append(d["source"])
    for fl in d.get("flags", []):
        flags_all.append(f"[{d.get('region','')}] {fl}")
    print(f"  + {os.path.basename(p)}: {len(rows)}행")

print("총 추가행:", len(all_rows))

# 2) RAW (line index 66) 끝에 삽입: '...]];' -> '...],<newrows>];'
RAW_I = None
for i,l in enumerate(lines):
    if l.startswith("const RAW=[["):
        RAW_I = i; break
assert RAW_I is not None, "RAW 라인 못찾음"
raw_line = lines[RAW_I]
assert raw_line.endswith("]];"), "RAW 끝 형식 예상과 다름: " + raw_line[-10:]
newrows = ",".join(json.dumps(r, ensure_ascii=False, separators=(",",":")) for r in all_rows)
if all_rows:
    lines[RAW_I] = raw_line[:-2] + "," + newrows + "];"

# 3) DONE 에 원본파일명 추가 (중복 제외)
done_i = None
for i,l in enumerate(lines):
    if "const DONE=[" in l:
        done_i = i; break
assert done_i is not None, "DONE 라인 못찾음"
dl = lines[done_i]
new_sources = [s for s in dict.fromkeys(sources) if ('"%s"'%s) not in dl]
assert "],TOTAL=" in dl, "DONE/TOTAL 구분자 못찾음"
if new_sources:
    add = ",".join(json.dumps(s, ensure_ascii=False) for s in new_sources)
    dl = dl.replace("],TOTAL=", "," + add + "],TOTAL=", 1)
    lines[done_i] = dl
    print("DONE 추가 파일:", len(new_sources))

# 4) 저장
with io.open(V3, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("저장 완료:", V3)
if flags_all:
    print("\n[전체 flags]")
    for fl in flags_all: print("  -", fl)
