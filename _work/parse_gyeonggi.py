# -*- coding: utf-8 -*-
import re, json, io
BASE = r"C:/Users/admin/Documents/이민범 개발/합격선추가"
SRC = "2026년도 제1회(8·9급) 경기도 공개경쟁임용시험 원서접수 현황(확정).pdf"

# 경기 표의 번호순(1~53) 라벨: (직렬, 직급, 직류, 대상)  ← 비전 판독 기준
LABELS = [
 ("간호","8급","간호","일반"),("간호","8급","간호","장애인"),("보건진료","8급","보건진료","일반"),
 ("행정","9급","일반행정","일반"),("행정","9급","일반행정","장애인"),("행정","9급","일반행정","저소득층"),
 ("세무","9급","지방세","일반"),("세무","9급","지방세","장애인"),("세무","9급","지방세","저소득층"),
 ("전산","9급","전산","일반"),("전산","9급","전산","장애인"),("전산","9급","전산","저소득층"),
 ("사회복지","9급","사회복지","일반"),("사회복지","9급","사회복지","장애인"),("사회복지","9급","사회복지","저소득층"),
 ("사서","9급","사서","일반"),("사서","9급","사서","장애인"),("속기","9급","속기","일반"),
 ("공업","9급","일반기계","일반"),("공업","9급","일반기계","장애인"),("공업","9급","일반기계","저소득층"),
 ("공업","9급","일반전기","일반"),("공업","9급","일반전기","장애인"),("공업","9급","일반전기","저소득층"),
 ("공업","9급","일반화공","일반"),
 ("농업","9급","일반농업","일반"),("농업","9급","일반농업","장애인"),("농업","9급","축산","일반"),
 ("녹지","9급","산림자원","일반"),("녹지","9급","산림자원","장애인"),("녹지","9급","조경","일반"),
 ("해양수산","9급","일반수산","일반"),
 ("보건","9급","보건","일반"),("보건","9급","보건","장애인"),
 ("환경","9급","일반환경","일반"),("환경","9급","일반환경","장애인"),("환경","9급","일반환경","저소득층"),
 ("시설","9급","건축","일반"),("시설","9급","건축","장애인"),("시설","9급","건축","저소득층"),
 ("시설","9급","도시계획","일반"),("시설","9급","도시계획","장애인"),("시설","9급","수도토목","일반"),
 ("시설","9급","일반토목","일반"),("시설","9급","일반토목","장애인"),("시설","9급","일반토목","저소득층"),
 ("시설","9급","지적","일반"),("시설","9급","지적","장애인"),
 ("방재안전","9급","방재안전","일반"),("방재안전","9급","방재안전","장애인"),
 ("방송통신","9급","통신기술","일반"),("방송통신","9급","통신기술","장애인"),("방송통신","9급","통신기술","저소득층"),
]

행정직군 = {"행정","세무","전산","사회복지","사서","속기"}
기술직군 = {"공업","농업","녹지","해양수산","보건","간호","환경","시설","방재안전","방송통신","보건진료"}
def 직군(j): return "행정직군" if j in 행정직군 else ("기술직군" if j in 기술직군 else "")

txt = io.open(BASE+"/_work/raw_경기.txt", encoding="utf-8").read()
data_re = re.compile(r"^(.+?)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)\s*:\s*1$")
groups=[]; cur=None
for ln in [l.strip() for l in txt.splitlines()]:
    if not ln: continue
    m = data_re.match(ln)
    if not m: continue
    name = m.group(1).strip()
    sb = int(m.group(2).replace(",","")); js = int(m.group(3).replace(",","")); comp = m.group(4)+":1"
    if name in ("소계","소 계"):
        cur={"소계":(sb,js),"cities":[]}; groups.append(cur)
    elif name in ("총계","총 계"):
        pass
    else:
        # 머릿글 없는 소계/총계(예: "220 1,221", "4,663 25,130")는 name이 숫자 → 스킵
        if re.fullmatch(r"[\d,]+", name): continue
        if cur is None: continue
        cur["cities"].append((name,sb,js,comp))

START = 0  # 이 paste는 번호1(간호)부터
print("그룹수:", len(groups), " (라벨 매핑 시작 번호:", START+1, ")")

rows=[]; mismatch=[]; mapping=[]; sum_sb=sum_js=0; sb8=js8=0
for i,g in enumerate(groups):
    직렬,직급,직류,대상 = LABELS[START+i]
    cs_sb=sum(c[1] for c in g["cities"]); cs_js=sum(c[2] for c in g["cities"])
    ok = g["소계"]==(cs_sb,cs_js)
    if not ok: mismatch.append((START+i+1,직렬,직류,대상,g["소계"],(cs_sb,cs_js)))
    mapping.append((START+i+1,f"{직렬}{직급}({직류}/{대상})",g["소계"],(cs_sb,cs_js),"OK" if ok else "X"))
    군=직군(직렬)
    if 직급=="8급": sb8+=cs_sb; js8+=cs_js
    for (기관,sb,js,comp) in g["cities"]:
        sum_sb+=sb; sum_js+=js
        rows.append(["경기","공무원","2026","1회","공개경쟁",기관,군,직렬,직류,직급,대상,
                     str(sb),str(js),comp,"","","","","","","",SRC,""])

print("8급합계(추출):", (sb8,js8), " ← 문서 8급총계 220/1221 비교")
print("추출 선발합:", sum_sb, " 접수합:", sum_js)
print("총행수:", len(rows))
print("소계불일치:", mismatch if mismatch else "없음")
print("\n[번호 라벨↔소계 매핑]")
for no,name,sc,cs,st in mapping:
    print(f"  {st} #{no:2d} {name:20s} 소계{sc}=시군합{cs}")

out={"region":"경기","category":"9급접수","source":SRC,"rows":rows,
     "checks":{"sum_선발":sum_sb,"sum_접수":sum_js,"8급_선발":sb8,"8급_접수":js8,
               "doc_8급총계":"220/1221","범위":f"번호{START+1}~{START+len(groups)}"},
     "flags":[] if not mismatch else ["소계불일치: "+str(mismatch)]}
io.open(BASE+"/_work/out/9급_경기.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=1))
print("\n저장: _work/out/9급_경기.json (번호 {}~{})".format(START+1,START+len(groups)))
