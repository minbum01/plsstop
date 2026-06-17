# -*- coding: utf-8 -*-
import json, io, math, re
BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
SRC="(공고용)2026년도+제3회+전북특별자치도+지방공무원+임용시험+원서접수+현황.pdf"
행정={"행정","세무","전산","사회복지","사서","속기","방호"}
def 군(s): return "행정직군" if s in 행정 else "기술직군"
def comp(sb,js):
    if not js or not sb: return ""
    v=math.floor(js/sb*10+0.5)/10; return f"{v:.1f}:1"
def 대상of(tag):
    if "장애" in tag: return "장애인"
    if "저소득" in tag: return "저소득층"
    return "일반"
lab=re.compile(r"^([가-힣]+)(\d)급\(([^)]+)\)\s*(.*)$")
tagre=re.compile(r"^\[([^\]]+)\]\s*(.*)$")
datare=re.compile(r"^(.+?)\s+(\d+)\s+([\d,]+|-)\s+([\d.]+|-)(?:\s+(.*))?$")
md=io.open(BASE+"/9급 2026 접수/응시현황.md",encoding="utf-8").read().splitlines()
# 전북 구간만
start=md.index("전북"); 
end=len(md)
for i in range(start+1,len(md)):
    if md[i].strip()=="제주": end=i; break
seg=[l.strip() for l in md[start+1:end] if l.strip()]

rows=[]; cur=None  # cur=(직렬,직류,직급,대상)
def emit(기관,sb,js,bigo=""):
    기관=기관.replace("도 일괄","도일괄").strip()
    직렬,직류,직급,대상=cur
    rows.append(["전북","공무원","2026","3회","공개경쟁",기관,군(직렬),직렬,직류,직급,대상,
                 str(sb),("0" if js=="-" else str(int(js.replace(",","")))),
                 ("" if js=="-" else comp(sb,int(js.replace(",","")))),"","","","","","","",SRC,bigo])
def parse_data(s):
    m=datare.match(s)
    if not m: return None
    기관,sb,js,cp,bigo=m.group(1),int(m.group(2)),m.group(3),m.group(4),(m.group(5) or "").strip()
    if 기관.replace(" ","") in ("계","소계","합계"): return "skip"
    return (기관,sb,js,bigo)
for ln in seg:
    if ln.startswith("2026년도") or ln.startswith("계 "): continue
    m=lab.match(ln)
    if m and "급(" in ln:
        직렬,급,직류,rest=m.group(1),m.group(2),m.group(3),m.group(4).strip()
        cur=(직렬,직류,급+"급","일반")
        if rest:
            d=parse_data(rest)
            if d and d!="skip": emit(*[d[0],d[1],d[2],d[3]])
        continue
    t=tagre.match(ln)
    if t:
        tag,rest=t.group(1),t.group(2).strip()
        if cur: cur=(cur[0],cur[1],cur[2],대상of(tag))
        if rest:
            d=parse_data(rest)
            if d and d!="skip": emit(d[0],d[1],d[2],d[3])
        continue
    if ln.startswith("소계") or ln.startswith("소 계"): continue
    d=parse_data(ln)
    if d and d!="skip" and cur: emit(d[0],d[1],d[2],d[3])

tsb=sum(int(r[11]) for r in rows); tjs=sum(int(r[12]) for r in rows)
covered=sorted(set((r[7],r[8]) for r in rows))
print("전북 행수:",len(rows)," 선발합:",tsb," (문서 계 1182)")
print("커버된 직렬/직류 끝:", covered[-3:])
io.open(BASE+"/_work/out/9급_전북.json","w",encoding="utf-8").write(json.dumps(
 {"region":"전북","category":"9급접수","source":SRC,"rows":rows,
  "checks":{"sum_선발":tsb,"sum_접수":tjs,"doc_총계":"1182/7519"},
  "flags":([] if tsb==1182 else [f"선발합 {tsb}<1182: 방재안전 직렬부터 끝까지 미붙임(약 {1182-tsb} 부족)"])},ensure_ascii=False,indent=1))
print("저장(임시). 부족분:", 1182-tsb)
