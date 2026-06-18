# -*- coding: utf-8 -*-
import json, io, math, re
BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
SRC = "2026년도 국가직 7급 공개경쟁채용시험 원서접수 현황.pdf"
행정={"행정","세무","관세","통계","감사","교정","보호","검찰","출입국관리","외무영사","전산"}
def 군(s): return "행정직군" if s in 행정 else "기술직군"
def comp(sb,js):
    if not js or not sb: return ""
    v=math.floor(js/sb*10+0.5)/10; return f"{v:.1f}:1"
def clean(t):
    t=re.sub(r'[-\U000F0000-\U0010FFFF]',' ',t)  # PUA(깨진문자)→공백
    return re.sub(r'\s+',' ',t).strip()
md=io.open(BASE+"/20267급응시현황.md",encoding="utf-8").read().splitlines()
row_re=re.compile(r'^\d+\s+(.+?)\s+전국\s+(\d+)\s+([\d,]+|-)\s+([\d.]+|-)\s*$')
lab=re.compile(r'^([가-힣]+?)\(([^)]+)\)$')
rows=[];tsb=tjs=0;flags=[]
for l in md:
    l=clean(l)
    m=row_re.match(l)
    if not m: continue
    label,sb,js,cp=m.group(1),int(m.group(2)),m.group(3),m.group(4)
    label=label.replace("공업직","공업")
    lm=lab.match(label)
    if not lm:
        flags.append("파싱실패: "+label); continue
    직렬=lm.group(1); inside=lm.group(2)
    if ":" in inside: 직류,대상=inside.split(":",1)
    else: 직류,대상=inside,"일반"
    직류=직류.strip(); 대상=대상.strip()
    js2=0 if js=="-" else int(js.replace(",",""))
    tsb+=sb; tjs+=js2
    rows.append(["국가직","공무원","2026","","공개경쟁","",군(직렬),직렬,직류,"7급",대상,
                 str(sb),("0" if js=="-" else str(js2)),("" if js=="-" else comp(sb,js2)),
                 "","","","","","","",SRC,("접수0(원본 '-')" if js=="-" else "")])
print("국가직7급 행수:",len(rows)," 선발:",tsb," 접수:",tjs," (합계 668/25650)")
assert tsb==668 and tjs==25650, f"불일치 {tsb}/{tjs}"
print("검산 통과 668/25650 ✅")
io.open(BASE+"/_work/out/국가직7급_2026접수.json","w",encoding="utf-8").write(json.dumps(
 {"region":"국가직","category":"국가직7급2026접수","source":SRC,"rows":rows,
  "checks":{"sum_선발":tsb,"sum_접수":tjs,"doc_총계":"668/25650"},"flags":flags},ensure_ascii=False,indent=1))
print("저장. flags:",flags)
