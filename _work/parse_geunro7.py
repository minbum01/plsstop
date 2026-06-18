# -*- coding: utf-8 -*-
import json, io, math, re
BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
SRC = "2025년도 근로감독 및 산업안전 분야 국가공무원 7급 공개경쟁채용시험 1차 필기시험 응시현황.pdf"
행정={"행정","세무","관세","통계","감사","교정","보호","검찰","출입국관리","외무영사","전산"}
def 군(s): return "행정직군" if s in 행정 else "기술직군"
def ratio(a,b):
    if not a or not b: return ""
    v=math.floor(b/a*10+0.5)/10; return f"{v:.1f}:1"
def rate(eung,tae):
    if not tae: return ""
    return f"{round(eung/tae*100,1)}"
md=io.open(BASE+"/2025 근로감독7급.md",encoding="utf-8").read().splitlines()
lab=re.compile(r'^([가-힣]+)\(([^)]+)\)$')
rowre=re.compile(r'^(.+?\([^)]+\))\s+(\d+)\s+([\d,]+|-)\s+([\d,]+|-)\s*$')
seen={}
for l in md:
    l=l.strip()
    m=rowre.match(l)
    if not m: continue
    label=m.group(1)
    lm=lab.match(label)
    if not lm: continue
    직렬=lm.group(1); inside=lm.group(2)
    직류,대상=(inside.split(":",1)+["일반"])[:2] if ":" in inside else (inside,"일반")
    sb=int(m.group(2)); tae=0 if m.group(3)=="-" else int(m.group(3).replace(",","")); eung=0 if m.group(4)=="-" else int(m.group(4).replace(",",""))
    seen[(직렬,직류.strip(),대상.strip())]=(sb,tae,eung)  # 중복 7회 → dedupe
rows=[];tsb=tt=te=0
for (직렬,직류,대상),(sb,tae,eung) in seen.items():
    tsb+=sb;tt+=tae;te+=eung
    rows.append(["국가직","공무원","2025","","공개경쟁","",군(직렬),직렬,직류,"7급",대상,
                 str(sb),str(tae),ratio(sb,tae),str(eung),rate(eung,tae),"","","","","",SRC,
                 "근로감독·산업안전 분야 / 접수칸=응시대상인원"])
print("근로감독7급 행수:",len(rows)," 선발:",tsb," 응시대상:",tt," 응시:",te," (총계 500/11937/6402)")
assert tsb==500 and tt==11937 and te==6402, f"불일치 {tsb}/{tt}/{te}"
print("검산 통과 500/11937/6402 ✅")
io.open(BASE+"/_work/out/국가직7급_2025근로감독.json","w",encoding="utf-8").write(json.dumps(
 {"region":"국가직","category":"국가직7급2025근로감독","source":SRC,"rows":rows,
  "checks":{"sum_선발":tsb,"sum_응시대상":tt,"sum_응시":te,"doc_총계":"500/11937/6402"},
  "flags":["접수인원 칸에 '응시대상인원' 사용(원본에 접수인원 없음). 응시율=응시/응시대상."]},ensure_ascii=False,indent=1))
print("저장")
