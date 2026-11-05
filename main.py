import streamlit as st
import pandas as pd
from itertools import combinations
from collections import Counter
import altair as alt

# 페이지 설정
st.set_page_config(page_title="메뉴 연관성 분석 도구", layout="wide")
st.title("🍳 메뉴 연관성 및 조합 분석 시스템")

# 1. 샘플 데이터 생성
if 'menu_data' not in st.session_state:
    st.session_state.menu_data = {
        "2026-11-01": ["돈까스", "제육볶음", "김치찌개", "계란말이", "깍두기"],
        "2026-11-02": ["돈까스", "카레라이스", "우동", "단무지", "샐러드"],
        "2026-11-03": ["제육볶음", "된장찌개", "계란말이", "무생채", "시금치나물"],
        "2026-11-04": ["돈까스", "제육볶음", "김치찌개", "숙주나물", "깍두기"],
        "2026-11-05": ["비빔밥", "계란후라이", "약고추장", "콩나물국", "배추김치"],
        "2026-11-06": ["돈까스", "김치찌개", "계란말이", "샐러드", "깍두기"],
        "2026-11-07": ["제육볶음", "된장찌개", "상추쌈", "마늘장아찌", "배추김치"],
        "2026-11-08": ["짜장면", "탕수육", "짬뽕국물", "단무지", "춘장"],
        "2026-11-09": ["돈까스", "카레라이스", "계란말이", "단무지", "깍두기"],
        "2026-11-10": ["제육볶음", "김치찌개", "계란말이", "무생채", "배추김치"],
        "2026-11-11": ["생선구이", "된장찌개", "숙주나물", "배추김치", "김구이"],
        "2026-11-12": ["소불고기", "미역국", "상추쌈", "배추김치", "깍두기"],
        "2026-11-13": ["닭갈비", "동치미", "볶음밥", "배추김치", "깍두기"],
        "2026-11-14": ["부대찌개", "라면사리", "계란말이", "배추김치", "오뎅볶음"],
        "2026-11-15": ["육개장", "석박지", "고추짱아찌", "배추김치", "김구이"],
        "2026-11-16": ["순두부찌개", "떡갈비", "감자조림", "배추김치", "깍두기"],
        "2026-11-17": ["보쌈", "무김치", "쟁반국수", "배추김치", "상추쌈"],
        "2026-11-18": ["갈비탕", "석박지", "부추무침", "배추김치", "깍두기"],
        "2026-11-19": ["해물파전", "칼국수", "겉절이", "배추김치", "단무지"],
        "2026-11-20": ["찜닭", "당면사리", "동치미", "배추김치", "깍두기"],
    }

# 데이터 전처리 및 모든 메뉴 리스트 추출
all_dates = st.session_state.menu_data.keys()
all_menus = sorted(list(set(menu for menus in st.session_state.menu_data.values() for menu in menus)))

# 2. 연관 규칙 및 빈도 계산
pair_counts = Counter()
menu_solo_counts = Counter()

for date, menus in st.session_state.menu_data.items():
    for menu in menus:
        menu_solo_counts[menu] += 1
    for p in combinations(sorted(menus), 2):
        pair_counts[p] += 1

rules_list = []
for (m1, m2), count in pair_counts.items():
    rules_list.append({
        "메뉴 조합": f"{m1} + {m2}",
        "메뉴 1": m1,
        "메뉴 2": m2,
        "동시 출현 일수": count,
        "메뉴1 단독일수": menu_solo_counts[m1],
        "메뉴2 단독일수": menu_solo_counts[m2]
    })
df_rules = pd.DataFrame(rules_list)

# -------------------------------------------------------------
# 사이드바 필터 영역
# -------------------------------------------------------------
st.sidebar.header("🔍 조건 필터링")

# 최소 동시 일수 슬라이더 (1~10, 기본값 1)
min_co_days = st.sidebar.slider("최소 동시 일수 설정", min_value=1, max_value=10, value=1)

# 특정 메뉴 좁혀 보기
selected_menu = st.sidebar.selectbox("특정 메뉴로 좁혀 보기", ["전체보기"] + all_menus)

# -------------------------------------------------------------
# 데이터 필터링 및 시각화 (그래프 + 표)
# -------------------------------------------------------------
st.subheader("📊 메뉴 동시 출현 연관 규칙 분석")

# 필터링 적용
df_filtered = df_rules[df_rules["동시 출현 일수"] >= min_co_days]
if selected_menu != "전체보기":
    df_filtered = df_filtered[
        (df_filtered["메뉴 1"] == selected_menu) | (df_filtered["메뉴 2"] == selected_menu)
    ]

# 슬라이더 변화에 연동되는 남은 규칙 개수 안내 문구
st.info(f"💡 현재 조건에 맞는 연관 규칙이 총 **{len(df_filtered)}**개 남아 있습니다.")

if not df_filtered.empty:
    # 데이터가 많을 경우 상위 15개만 그래프로 시각화
    df_chart = df_filtered.sort_values(by="동시 출현 일수", ascending=False).head(15)
    
    # [추가] Altair 기반 가로 막대그래프 시각화
    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X("동시 출현 일수:Q", title="동시 출현 일수 (일)"),
        y=alt.Y("메뉴 조합:N", sort="-x", title="메뉴 조합"),
        color=alt.Color("동시 출현 일수:Q", scale=alt.Scale(scheme="blues"), legend=None),
        tooltip=["메뉴 조합", "동시 출현 일수"]
    ).properties(
        title="✨ 조건별 상위 메뉴 조합 동시 출현 빈도 (최대 15개)",
        height=400
    )
    st.altair_chart(chart, use_container_width=True)
    
    # 결과 데이터프레임 표 출력
    st.write("▼ 전체 필터링 결과 표")
    st.dataframe(df_filtered.sort_values(by="동시 출현 일수", ascending=False).reset_index(drop=True), use_container_width=True)
else:
    st.warning("조건에 맞는 연관 규칙 데이터가 없습니다.")

st.markdown("---")

# -------------------------------------------------------------
# 함께 나온 적 없는 짝 화면 구현
# -------------------------------------------------------------
st.subheader("🚫 함께 나온 적 없는 짝 (미조합 메뉴 분석)")
st.write("선택한 메뉴와 한 번도 같이 나오지 않았으면서, 혼자서는 10일 이상 출현한 대중적인 메뉴를 찾아줍니다.")

# 좁혀 보기와 분리된 기준 메뉴 선택 UI
target_menu = st.selectbox("조합을 확인할 기준 메뉴 선택", all_menus, key="uncombined_menu_select")
target_solo_count = menu_solo_counts[target_menu]

# 로직 계산
uncombined_list = []
for other_menu in all_menus:
    if other_menu == target_menu:
        continue
    pair = tuple(sorted([target_menu, other_menu]))
    if pair_counts[pair] == 0 and menu_solo_counts[other_menu] >= 10:
        uncombined_list.append({
            "추천 미조합 메뉴": other_menu,
            "해당 메뉴 단독 출현 일수": menu_solo_counts[other_menu]
        })

df_uncombined = pd.DataFrame(uncombined_list)

st.markdown(f"**선택한 메뉴:** `{target_menu}` (총 출현 일수: **{target_solo_count}**일)")

if not df_uncombined.empty:
    df_uncombined = df_uncombined.sort_values(by="해당 메뉴 단독 출현 일수", ascending=False).reset_index(drop=True)
    st.dataframe(df_uncombined, use_container_width=True)
else:
    st.success(f"🎉 `{target_menu}`와 함께 나온 적 없으면서 10일 이상 출현한 메뉴가 없습니다! (모든 대중적인 메뉴와 최소 1번 이상 조합됨)")

