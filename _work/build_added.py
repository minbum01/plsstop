# -*- coding: utf-8 -*-
# v2 뷰어 틀 + 이번에 추가된 행(_work/out/*.json)만 → 합격선_관리_추가분.html
import json, io, glob, os
BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
with io.open(BASE+"/합격선_관리_v2.html", encoding="utf-8") as f:
    lines = f.read().split("\n")

def rawkey(r): return (r[0],r[1],r[2],r[3],r[5],r[7],r[8],r[9],r[10])
_rl0=next(l for l in lines if l.startswith("const RAW=[["))
v2keys=set(rawkey(r) for r in json.loads(_rl0[len("const RAW="):].rstrip(";")))

rows=[]; sources=[]
for p in sorted(glob.glob(BASE+"/_work/out/*.json")):
    d=json.load(io.open(p,encoding="utf-8"))
    rows.extend([r for r in d.get("rows",[]) if rawkey(r) not in v2keys])  # v2 중복 제외
    if d.get("source"): sources.append(d["source"])
print("추가분 행수(v2중복 제외):", len(rows), " 출처파일:", len(set(sources)))

# RAW 교체 (전체를 추가분으로)
for i,l in enumerate(lines):
    if l.startswith("const RAW=[["):
        body=",".join(json.dumps(r,ensure_ascii=False,separators=(",",":")) for r in rows)
        lines[i]="const RAW=["+body+"];"
        break
# DONE/TOTAL/LINKS/ISSUES 라인 교체
for i,l in enumerate(lines):
    if "const DONE=[" in l:
        ds=",".join(json.dumps(s,ensure_ascii=False) for s in dict.fromkeys(sources))
        lines[i]=f"const DONE=[{ds}],TOTAL={len(set(sources))},LINKS={{}},ISSUES=[];"
        break
# 제목 표기
for i,l in enumerate(lines):
    if "<title>" in l:
        lines[i]=l.replace("합격선 관리 v2 (검증본)","합격선 관리 — 2026 접수 추가분")
    if "✅ 합격선 관리 v2 — 검증본" in l:
        lines[i]=l.replace("✅ 합격선 관리 v2 — 검증본","🆕 합격선 관리 — 2026 접수 추가분(9급·교행)")

out=BASE+"/합격선_관리_추가분.html"
with io.open(out,"w",encoding="utf-8") as f:
    f.write("\n".join(lines))
print("저장:", out)
