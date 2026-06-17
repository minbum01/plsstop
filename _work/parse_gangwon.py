# -*- coding: utf-8 -*-
import re, json, io, sys

BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
SRC_NAME = "2026년도 제2회 강원특별자치도 공무원 임용시험 응시원서 접수현황(공고용).pdf"

행정직군 = {"행정","세무","전산","사회복지","사서","속기","방호","감사","통계","교정","보호","검찰","직업상담","운전"}
기술직군 = {"공업","농업","녹지","시설","보건","간호","환경","방재안전","방송통신","시설관리","해양수산","의료기술","보건진료","수의","축산","식품위생","조경","데이터"}

def 직군추정(직렬):
    if 직렬 in 행정직군: return "행정직군"
    if 직렬 in 기술직군: return "기술직군"
    return ""

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

text = read(BASE+"/_work/page1_강원.txt") + "\n" + read(BASE+"/_work/raw_강원_body.txt")
lines = [l.strip() for l in text.splitlines()]

# 패턴
data_re = re.compile(r"^(.+?)\s+(\d+)\s+(\d+)\s+([\d.]+)\s*:\s*1$")
label_head_re = re.compile(r"^([가-힣]+?)(\d+급|연구사|연구관|연구직)$")
paren_re = re.compile(r"^\((.+)\)$")

groups = []   # each: {"소계":(sb,js), "cities":[(기관,sb,js,경쟁)]}
labels = []   # each: (직렬,직급,직류,대상)
cur = None
i = 0
while i < len(lines):
    ln = lines[i]
    if not ln or ln.startswith("직렬(직류)명") or ln == "경쟁률" or re.match(r"^\d+$", ln):
        i += 1; continue
    # 라벨 (헤드 + 다음줄 괄호)
    m = label_head_re.match(ln)
    if m and i+1 < len(lines):
        pm = paren_re.match(lines[i+1])
        if pm:
            직렬, 직급 = m.group(1), m.group(2)
            inside = pm.group(1)
            if ":" in inside:
                직류, 대상 = inside.split(":",1)
            else:
                직류, 대상 = inside, "일반"
            labels.append((직렬, 직급, 직류.strip(), 대상.strip()))
            i += 2; continue
    # 데이터행
    dm = data_re.match(ln)
    if dm:
        name, sb, js, comp = dm.group(1).strip(), int(dm.group(2)), int(dm.group(3)), dm.group(4)
        comp = comp + ":1"
        if name in ("총 계","총계"):
            globals()["총계"] = (sb, js)
        elif name in ("소 계","소계"):
            cur = {"소계":(sb,js), "cities":[]}
            groups.append(cur)
        else:
            if cur is None:
                cur = {"소계":None, "cities":[]}; groups.append(cur)
            cur["cities"].append((name, sb, js, comp))
    i += 1

# 검증: 그룹수 vs 라벨수
print("그룹수:", len(groups), " 라벨수:", len(labels))
assert len(groups)==len(labels), "그룹/라벨 개수 불일치!"

rows = []
mismatch = []
sum_sb = sum_js = 0
mapping = []
for g,(직렬,직급,직류,대상) in zip(groups, labels):
    sb_sum = sum(c[1] for c in g["cities"])
    js_sum = sum(c[2] for c in g["cities"])
    sc = g["소계"]
    ok = (sc==(sb_sum,js_sum)) if sc else None
    if sc and not ok:
        mismatch.append((직렬,직류,대상,sc,(sb_sum,js_sum)))
    mapping.append((f"{직렬}{직급}({직류}{':'+대상 if 대상!='일반' else ''})", sc, (sb_sum,js_sum), "OK" if ok else "X"))
    군 = 직군추정(직렬)
    구분 = "공개경쟁" if 직급 in ("9급","8급") else ""  # 수의6급/7급/연구사: 공/경 애매 → 빈칸(데이터는 유지)
    for (기관, sb, js, comp) in g["cities"]:
        sum_sb += sb; sum_js += js
        rows.append(["강원","공무원","2026","2회",구분,기관,군,직렬,직류,직급,대상,
                     str(sb),str(js),comp,"","","","","","","",SRC_NAME,""])

print("총계(문서):", globals().get("총계"))
print("합계(추출): 선발", sum_sb, " 접수", sum_js)
print("총행수:", len(rows))
print("소계불일치:", mismatch if mismatch else "없음")
# 직급 9급/8급 외 (수의 등) 플래그
flags=[]
odd = sorted({(r[7],r[9]) for r in rows if r[9] not in ("9급","8급")})
if odd: flags.append("직급 비9/8급(시험구분 확인필요): "+str(odd))
군없음 = sorted({r[7] for r in rows if r[6]==""})
if 군없음: flags.append("직군 추정불가: "+str(군없음))
print("플래그:", flags if flags else "없음")

print("\n[라벨↔소계 매핑]")
for name, sc, csum, st in mapping:
    print(f"  {st}  {name:22s} 소계{sc} = 시군합{csum}")

print("\n[샘플 행 5개]")
for r in rows[:5]:
    print("  ", r)

out = {"region":"강원","category":"9급접수","source":SRC_NAME,
       "rows":rows,
       "checks":{"sum_선발":sum_sb,"sum_접수":sum_js,
                 "doc_총계_선발":globals().get("총계",(None,None))[0],
                 "doc_총계_접수":globals().get("총계",(None,None))[1]},
       "flags":flags}
with io.open(BASE+"/_work/out/9급_강원.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=1)
print("\n저장: _work/out/9급_강원.json")
