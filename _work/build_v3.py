# -*- coding: utf-8 -*-
# v2 html + _work/out/*.json  ->  합격선_관리_v3.html  (재실행 가능)
import json, io, glob, os

BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
V2 = BASE + "/합격선_관리_v2.html"
V3 = BASE + "/합격선_관리_v3.html"

with io.open(V2, encoding="utf-8") as f:
    lines = f.read().split("\n")

# 0) v2 기존 RAW 키 집합 (중복 추가 방지)
def rawkey(r):  # 지역,시험종류,연도,회차,임용기관,직렬,직류,직급,대상
    return (r[0],r[1],r[2],r[3],r[5],r[7],r[8],r[9],r[10])
_rawline0 = next(l for l in lines if l.startswith("const RAW=[["))
_v2rows = json.loads(_rawline0[len("const RAW="):].rstrip(";"))
v2keys = set(rawkey(r) for r in _v2rows)
print("v2 기존 행:", len(_v2rows))

# 1) 추출행 수집 (v2에 이미 있는 키는 제외)
all_rows = []
sources = []
flags_all = []
skipped = 0
files = sorted(glob.glob(BASE + "/_work/out/*.json"))
for p in files:
    with io.open(p, encoding="utf-8") as f:
        d = json.load(f)
    rows = d.get("rows", [])
    kept = [r for r in rows if rawkey(r) not in v2keys]
    skipped += len(rows) - len(kept)
    all_rows.extend(kept)
    if d.get("source"): sources.append(d["source"])
    for fl in d.get("flags", []):
        flags_all.append(f"[{d.get('region','')}] {fl}")
    print(f"  + {os.path.basename(p)}: {len(kept)}행" + (f" (중복 {len(rows)-len(kept)} 제외)" if len(kept)!=len(rows) else ""))

print("총 추가행:", len(all_rows), " | v2중복 제외:", skipped)

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
