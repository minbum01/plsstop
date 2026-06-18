# -*- coding: utf-8 -*-
import json, io, math, re
BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
행정={"행정","세무","전산","사회복지","사서","속기","방호","노동"}
def 군(s): return "행정직군" if s in 행정 else "기술직군"
def comp(sb,js):
    if not js or not sb: return ""
    v=math.floor(js/sb*10+0.5)/10; return f"{v:.1f}:1"
md=io.open(BASE+"/9급 2026 접수/응시현황.md",encoding="utf-8").read().splitlines()
def idxs(name): return [i for i,l in enumerate(md) if l.strip()==name]

# ===== 충남 (탭) : 충남 ~ 다음 제주 =====
s_cn=idxs("충남")[0]
e_cn=min([i for i in idxs("제주") if i>s_cn]+[len(md)])
lab=re.compile(r"^(\d급)\s+(.+?)\(([^)]+)\)$")
SRC_cn="2026년 제2회 충청남도 지방공무원 임용시험 원서접수 결과.xlsx"
cn=[]; cur=None
def emit_cn(기관,sb,js):
    직급,직렬,직류,대상=cur
    js2=0 if js=="-" else int(js.replace(",",""))
    cn.append(["충남","공무원","2026","2회","공개경쟁",기관,군(직렬),직렬,직류,직급,대상,
               str(int(sb.replace(",",""))),str(js2),("" if js=="-" else comp(int(sb.replace(",","")),js2)),
               "","","","","","","",SRC_cn,""])
for l in md[s_cn+1:e_cn]:
    if "\t" not in l: continue
    c=[x.strip() for x in l.split("\t")]
    if not c[0]: continue
    if "임용시험" in c[0] or c[0] in ("소계","계","총 계","총계"): continue
    m=lab.match(c[0])
    if m:
        직급,직렬,inside=m.group(1),m.group(2),m.group(3)
        직류,대상=(inside.split(":",1)+["일반"])[:2]
        cur=(직급,직렬,직류,대상)
        if len(c)>=4: emit_cn(c[1],c[2],c[3])
    elif cur and len(c)>=4 and re.match(r"^[\d,]+$",c[1]):
        emit_cn(c[0],c[1],c[2])
tsb=sum(int(r[11]) for r in cn); tjs=sum(int(r[12]) for r in cn)
print(f"충남 행수:{len(cn)} 선발:{tsb} 접수:{tjs} (문서 1491/7019)")
assert tsb==1491, f"충남 선발 {tsb}"
fl=[] if tjs==7019 else [f"접수합 {tjs}≠7019(차이 {7019-tjs}): 원본 일부 접수 '-'/오차"]
io.open(BASE+"/_work/out/9급_충남.json","w",encoding="utf-8").write(json.dumps(
 {"region":"충남","category":"9급접수","source":SRC_cn,"rows":cn,
  "checks":{"sum_선발":tsb,"sum_접수":tjs,"doc_총계":"1491/7019"},"flags":fl},ensure_ascii=False,indent=1))
print("충남 저장. 접수차이:",7019-tjs)

# ===== 제주 (완본: 마지막 제주 블록) =====
s_jj=idxs("제주")[-1]
SRC_jj="(260327) 2026년 제주특별자치도 제4회 지방공무원 임용시험 접수현황.pdf"
labj=re.compile(r"^(.+?)\(([^)]+)\)\s+(\d급)$")
dataj=re.compile(r"^(.+?)\s+(\d+)\s+(\d+)\s+([\d.]+)\s*:\s*1\s+(\d+)\s+([\d.]+)$")
jj=[]; curj=None
for l in md[s_jj+1:]:
    l=l.strip()
    if not l: continue
    m=labj.match(l)
    if m: curj=(m.group(1),m.group(2),m.group(3)); continue
    d=dataj.match(l)
    if d and curj:
        기관,sb,js=d.group(1),int(d.group(2)),int(d.group(3)); eung,rate=d.group(5),d.group(6)
        직렬,직류,직급=curj
        jj.append(["제주","공무원","2026","4회","공개경쟁",기관,군(직렬),직렬,직류,직급,"일반",
                   str(sb),str(js),comp(sb,js),eung,rate,"","","","","",SRC_jj,""])
tsb=sum(int(r[11]) for r in jj); tjs=sum(int(r[12]) for r in jj); tem=sum(int(r[14]) for r in jj)
print(f"제주 행수:{len(jj)} 선발:{tsb} 접수:{tjs} 응시:{tem} (문서 68/415/328)")
assert tsb==68 and tjs==415 and tem==328, "제주 불일치"
print("제주 검산 통과 ✅")
io.open(BASE+"/_work/out/9급_제주.json","w",encoding="utf-8").write(json.dumps(
 {"region":"제주","category":"9급접수","source":SRC_jj,"rows":jj,
  "checks":{"sum_선발":tsb,"sum_접수":tjs,"sum_응시":tem,"doc_총계":"68/415/328"},
  "flags":["제4회 소규모(간호·사회복지만). 응시인원·응시율 칸 채움."]},ensure_ascii=False,indent=1))
print("제주 저장")
