# -*- coding: utf-8 -*-
import json, io, math, re
BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
행정 = {"행정","세무","전산","사회복지","사서","속기","방호"}
def 군(s): return "행정직군" if s in 행정 else "기술직군"
def comp(sb,js):
    if not js or not sb: return ""
    v=math.floor(js/sb*10+0.5)/10; return f"{v:.1f}:1"
def norm(t):
    t=t.strip(); return {"장애":"장애인","저소득":"저소득층","-":"일반","":"일반"}.get(t,t)
src="2026년도 제1회 지방공무원 임용시험 직렬별 원서접수 결과(260330기준).pdf"
md=io.open(BASE+"/9급 2026 접수/응시현황.md",encoding="utf-8").read().splitlines()
rows=[]
for ln in md:
    if "\t" not in ln: continue
    c=[x.strip() for x in ln.split("\t")]
    if len(c)<8: continue
    if re.match(r"^[789]급 (공채|경채)$",c[0]):
        직급=c[0].split()[0]; gb="공개경쟁" if "공채" in c[0] else "경력경쟁"
        직렬,직류,대상,기관=c[1],c[2],norm(c[3]),c[4]
    elif c[0]=="경력채용":
        gb="경력경쟁"; 직급="연구사"
        직렬=c[1][:-2] if c[1].endswith("연구") else c[1]
        직류=c[2]; 대상=norm(c[3]); 기관=c[4]
    else: continue
    sb=int(c[5].replace(",","")); js=int(c[6].replace(",",""))
    rows.append(["인천","공무원","2026","1회",gb,기관,군(직렬),직렬,직류,직급,대상,str(sb),str(js),comp(sb,js),"","","","","","","",src,""])
tsb=sum(int(r[11]) for r in rows); tjs=sum(int(r[12]) for r in rows)
print("인천 행수:",len(rows)," 선발:",tsb," 접수:",tjs," (문서 1537/6980)")
assert tsb==1537, f"선발 불일치 {tsb}"
flags=[]
if tjs!=6980:
    flags.append(f"접수합 {tjs}=문서소계 6980보다 {6980-tjs} 적음(원본 복사 중 접수 1칸 오차 추정). 선발 1537 정확.")
print("선발 정확 ✅  접수차이:", 6980-tjs)
io.open(BASE+"/_work/out/9급_인천.json","w",encoding="utf-8").write(json.dumps(
 {"region":"인천","category":"9급접수","source":src,"rows":rows,
  "checks":{"sum_선발":tsb,"sum_접수":tjs,"doc_총계":"1537/6980"},"flags":flags},ensure_ascii=False,indent=1))
print("저장 완료")
