import streamlit as st
import pandas as pd
from google import genai
import streamlit.components.v1 as components

# =============================================================================
# 페이지 기본 설정
# =============================================================================
st.set_page_config(
    page_title="전자상거래 10~11월 행동 분석 대시보드",
    layout="wide"
)

# =============================================================================
# Gemini 클라이언트 설정
# =============================================================================
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_data
def load_summary_data():
    return {
        "overview_kpi": pd.read_json("data/summary_json/01_overview_kpi_summary.json"),
        "overview_funnel": pd.read_json("data/summary_json/01_overview_funnel_summary.json"),
        "overview_category_top5": pd.read_json("data/summary_json/01_overview_category_top5.json"),
        "overview_category_brand": pd.read_json("data/summary_json/01_overview_category_brand_summary.json"),
        "overview_daily": pd.read_json("data/summary_json/01_overview_daily_summary.json"),
        "overview_first_vs_revisit": pd.read_json("data/summary_json/01_overview_first_vs_revisit.json"),

        "retention_kpi": pd.read_json("data/summary_json/02_retention_kpi_summary.json"),
        "retention_day": pd.read_json("data/summary_json/02_retention_day_summary.json"),
        "retention_first_purchase_cohort": pd.read_json("data/summary_json/02_retention_first_purchase_cohort_summary.json"),
        "retention_category_top5": pd.read_json("data/summary_json/02_retention_category_top5.json"),
        "retention_buyer_vs_nonbuyer": pd.read_json("data/summary_json/02_retention_buyer_vs_nonbuyer.json"),

        "smartphone_brand": pd.read_json("data/summary_json/03_smartphone_brand_summary.json"),
        "smartphone_funnel": pd.read_json("data/summary_json/03_smartphone_funnel_summary.json"),
        "smartphone_time": pd.read_json("data/summary_json/03_smartphone_time_summary.json"),
        "smartphone_price_tier": pd.read_json("data/summary_json/03_smartphone_price_tier_summary.json"),
        "smartphone_bundle_top3": pd.read_json("data/summary_json/03_smartphone_bundle_top3.json"),
    }


summary_data = load_summary_data()

# =============================================================================
# 디자인 CSS
# =============================================================================
st.markdown(
    """
    <style>
    /* 전체 페이지 */
    .block-container {
        padding-top: 2.0rem;
        padding-bottom: 2.5rem;
        max-width: 90vw;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    body {
        background-color: #f8fafc;
    }

    /* 상단 제목 */
    .main-title {
        font-size: 38px;
        font-weight: 850;
        color: #111827;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
        padding-top: 4px;
        line-height: 2;
    }

    .sub-text {
        font-size: 16.5px;
        color: #4b5563;
        line-height: 1.65;
        margin-bottom: 24px;
    }

    /* 카드 공통 */
    .section-title {
        font-size: 26px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 14px;
        letter-spacing: -0.3px;
    }

    .section-desc {
        font-size: 14.5px;
        color: #4b5563;
        line-height: 1.65;
        margin-bottom: 18px;
    }

    /* Streamlit container border 디자인 보정 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #dbe2ea;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        background-color: #ffffff;
    }

    /* Tableau placeholder */
    .tableau-placeholder {
        height: 500px;
        border: 2px dashed #b7c7da;
        border-radius: 18px;
        background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #1f2937;
        font-size: 30px;
        font-weight: 850;
        margin-bottom: 12px;
    }

    .tableau-placeholder span {
        font-size: 15px;
        font-weight: 500;
        color: #64748b;
        margin-top: 8px;
    }

    .tableau-info {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 13px 15px;
        color: #1d4ed8;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 18px;
    }

    .expected-title {
        font-size: 20px;
        font-weight: 800;
        color: #111827;
        margin-top: 6px;
        margin-bottom: 10px;
    }

    .expected-list {
        font-size: 14.5px;
        color: #374151;
        line-height: 1.8;
    }

    /* AI 카드 */
    .ai-title {
        font-size: 25px;
        font-weight: 850;
        color: #111827;
        line-height: 1.35;
        letter-spacing: -0.3px;
        margin-bottom: 16px;
    }

    .ai-guide-box {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px 15px;
        color: #374151;
        font-size: 14px;
        line-height: 1.65;
        margin-bottom: 14px;
    }

    .chat-title {
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 10px;
        color: #111827;
    }

    .chat-area {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 8px;
        background-color: #ffffff;
    }

    /* form 디자인 */
    div[data-testid="stForm"] {
        border: 1px solid #e5e7eb;
        border-radius: 15px;
        padding: 13px;
        background-color: #f9fafb;
    }

    textarea {
        border-radius: 12px !important;
    }

    /* 버튼 */
    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 11px;
        border: 1px solid #d1d5db;
        background-color: #ffffff;
        color: #111827;
        font-weight: 600;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        border-color: #60a5fa;
        color: #2563eb;
        background-color: #f8fbff;
    }

    hr {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    /* 채팅 메시지 글자 크기 조정 */
    div[data-testid="stChatMessage"] {
        font-size: 14px;
        line-height: 1.55;
    }

    /* 채팅 메시지 안의 제목 크기 조정 */
    div[data-testid="stChatMessage"] h1 {
        font-size: 22px;
    }

    div[data-testid="stChatMessage"] h2 {
        font-size: 19px;
    }

    div[data-testid="stChatMessage"] h3 {
        font-size: 17px;
    }

    /* 채팅 메시지 리스트 여백 조정 */
    div[data-testid="stChatMessage"] ul {
        margin-top: 4px;
        margin-bottom: 4px;
    }

    div[data-testid="stChatMessage"] li {
        margin-bottom: 4px;
    }
    
    /* Tableau 톤 컬러 맞춤 */
    :root {
        --main-blue: #1f6fa5;
        --mid-blue: #6fa6cf;
        --light-blue: #eaf4fb;
        --soft-blue: #f7fbff;
        --border-blue: #cfe3f3;
        --text-dark: #1f2937;
    }

    /* 전체 배경 */
    .stApp {
        background-color: #f7fbff;
    }

    /* 메인 제목 */
    .main-title {
        color: #111827;
        font-size: 34px;
        font-weight: 900;
        letter-spacing: -0.8px;
        border-left: 8px solid var(--main-blue);
        padding-left: 16px;
        margin-bottom: 8px;
    }

    /* 부제목 */
    .sub-text {
        color: #4b5563;
        font-size: 15.5px;
        line-height: 1.6;
        margin-bottom: 22px;
    }

    /* 카드형 컨테이너 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1.5px solid var(--border-blue) !important;
        border-radius: 20px !important;
        background: #ffffff !important;
        box-shadow: 0 8px 20px rgba(31, 111, 165, 0.08) !important;
    }

    /* 섹션 제목 */
    .section-title,
    .ai-title {
        color: #111827;
        font-weight: 900;
    }

    /* 섹션 제목 앞 포인트 바 */
    .section-title::before,
    .ai-title::before {
        content: "";
        display: inline-block;
        width: 7px;
        height: 22px;
        background-color: var(--main-blue);
        border-radius: 4px;
        margin-right: 9px;
        vertical-align: -4px;
    }

    /* Tableau placeholder */
    .tableau-placeholder {
        height: 610px;
        border: 2px dashed #9fc4df;
        border-radius: 20px;
        background: linear-gradient(135deg, #f8fcff 0%, #eaf4fb 100%);
        color: #1f2937;
    }

    .tableau-placeholder span {
        color: #5b6f82;
    }

    /* 안내 박스 */
    .tableau-info,
    .ai-guide-box {
        background-color: #eaf4fb !important;
        border: 1px solid #cfe3f3 !important;
        color: #27465f !important;
        border-radius: 15px !important;
    }

    /* 예정 화면 구성 */
    .expected-title {
        color: #111827;
        font-weight: 900;
    }

    .expected-list {
        background-color: #f7fbff;
        border: 1px solid #d9eaf5;
        border-radius: 14px;
        padding: 12px 14px;
    }

    /* selectbox, textarea 주변 톤 */
    div[data-baseweb="select"] > div {
        background-color: #f7fbff;
        border-color: #d9eaf5;
        border-radius: 12px;
    }

    /* 버튼 */
    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 14px !important;
        border: 1px solid #b8d6ea !important;
        background-color: #ffffff !important;
        color: #1f2937 !important;
        font-weight: 700 !important;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        border-color: var(--main-blue) !important;
        color: var(--main-blue) !important;
        background-color: #eaf4fb !important;
    }

    /* 채팅 메시지 */
    div[data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 14px;
        font-size: 14px;
        line-height: 1.55;
    }

    /* AI 답변 제목 크기 조정 */
    div[data-testid="stChatMessage"] h1 {
        font-size: 21px;
    }

    div[data-testid="stChatMessage"] h2 {
        font-size: 18px;
    }

    div[data-testid="stChatMessage"] h3 {
        font-size: 16px;
    }

    /* 입력창 */
    textarea {
        background-color: #f7fbff !important;
        border-radius: 14px !important;
    }
    
    </style>
    
    """,
    unsafe_allow_html=True
)

# =============================================================================
# 챗봇 역할 설정
# =============================================================================
SYSTEM_PROMPT = """
너는 전자상거래 행동 분석 프로젝트의 AI 대시보드 해설봇이다.

프로젝트 주제:
- 2019년 10월~11월 전자상거래 고객 행동 분석
- 스마트폰 카테고리 중심의 구매 전환 흐름 분석
- view → cart → purchase 퍼널 분석
- 브랜드별, 월별, 시간대별 구매 전환 차이 해석
- Tableau 대시보드와 함께 사용되는 AI 설명 기능

답변 규칙:
1. 한국어로 답변한다.
2. 데이터 분석 발표자가 바로 읽을 수 있게 자연스럽게 설명한다.
3. 너무 길게 답하지 말고 핵심 위주로 답한다.
4. 확실한 데이터가 없는 경우에는 추측하지 말고 "현재 제공된 데이터만으로는 판단하기 어렵다"고 말한다.
5. 대시보드 해설, 발표 문장, 인사이트 정리를 도와준다.
6. 사용자가 발표용 문장을 요청하면 발표자가 말하는 톤으로 작성한다.
"""
# =============================================================================
# context 생성 함수
# =============================================================================
def format_number(value):
    try:
        return f"{int(value):,}"
    except:
        return str(value)


def make_overview_context(summary_data, selected_month):
    kpi_df = summary_data["overview_kpi"]
    category_df = summary_data["overview_category_top5"]
    daily_df = summary_data["overview_daily"]
    first_vs_df = summary_data["overview_first_vs_revisit"]

    if selected_month != "전체":
        kpi_df = kpi_df[kpi_df["month"] == selected_month]
        category_df = category_df[category_df["month"] == selected_month]
        daily_df = daily_df[daily_df["month"] == selected_month]
        first_vs_df = first_vs_df[first_vs_df["month"] == selected_month]

    context = "[전체 현황 분석 페이지]\n"
    context += "이 페이지는 전체 매출, 유저 수, 구매 전환율, 퍼널, 일별 추이, 첫방문/재방문 매출, 카테고리 성과를 설명합니다.\n\n"

    context += "핵심 KPI:\n"
    for _, row in kpi_df.iterrows():
        context += f"""
- {row['month']}
  - view 수: {format_number(row['view_count'])}
  - cart 수: {format_number(row['cart_count'])}
  - purchase 수: {format_number(row['purchase_count'])}
  - 전체 추정 매출: {row['total_revenue']:,.2f}
  - 전체 유저 수: {format_number(row['total_user_count'])}
  - 구매 유저 수: {format_number(row['purchase_user_count'])}
  - view → purchase 전환율: {row['view_to_purchase_rate']}%
"""

    context += "\n카테고리별 TOP5 추정 매출:\n"
    for _, row in category_df.iterrows():
        context += f"- {row['month']} {row['rank']}위: {row['category_code']} / 매출 {row['revenue']:,.2f} / 구매수 {format_number(row['purchase_count'])}\n"

    context += "\n첫방문 vs 재방문:\n"
    for _, row in first_vs_df.iterrows():
        context += f"- {row['month']} {row['visit_type']}: 매출 {row['revenue']:,.2f}, 매출 비중 {row['revenue_ratio']}%, view→purchase {row['view_to_purchase_rate']}%\n"

    top_daily = daily_df.sort_values("revenue", ascending=False).head(5)
    context += "\n매출이 높았던 일자 TOP5:\n"
    for _, row in top_daily.iterrows():
        context += f"- {row['event_date']}: 매출 {row['revenue']:,.2f}, 일별 유저 {format_number(row['daily_user_count'])}명, view→purchase {row['view_to_purchase_rate']}%\n"

    return context


def make_retention_context(summary_data, selected_month):
    kpi_df = summary_data["retention_kpi"]
    day_df = summary_data["retention_day"]
    cohort_df = summary_data["retention_first_purchase_cohort"]
    category_df = summary_data["retention_category_top5"]
    buyer_df = summary_data["retention_buyer_vs_nonbuyer"]

    if selected_month != "전체":
        kpi_df = kpi_df[kpi_df["month"] == selected_month]
        day_df = day_df[day_df["month"] == selected_month]
        cohort_df = cohort_df[cohort_df["month"] == selected_month]
        category_df = category_df[category_df["month"] == selected_month]
        buyer_df = buyer_df[buyer_df["month"] == selected_month]

    context = "[코호트/리텐션 페이지]\n"
    context += "이 페이지는 전체 재방문율, Day1/Day7 재방문율, n-day 리텐션, 첫구매 경과일 코호트, 카테고리별 구매자/비구매자 재방문율을 설명합니다.\n\n"

    context += "리텐션 핵심 KPI:\n"
    for _, row in kpi_df.iterrows():
        context += f"""
- {row['month']}
  - 전체 유저 수: {format_number(row['total_user_count'])}
  - 재방문 유저 수: {format_number(row['revisit_user_count'])}
  - 전체 재방문율: {row['revisit_rate']}%
  - Day1 재방문율: {row['day1_revisit_rate']}%
  - Day7 재방문율: {row['day7_revisit_rate']}%
"""

    context += "\n카테고리별 구매자 재방문율 TOP5:\n"
    for _, row in category_df.iterrows():
        context += f"- {row['month']} {row['rank']}위: {row['category_code']} / 재방문율 {row['revisit_rate']}% / 구매자 {format_number(row['buyer_count'])}명\n"

    context += "\n구매자 vs 비구매자 카테고리 재방문율 예시:\n"
    sample_buyer = buyer_df.head(12)
    for _, row in sample_buyer.iterrows():
        context += f"- {row['month']} {row['category_code']} {row['group']}: 유저 {format_number(row['user_count'])}명, 재방문율 {row['revisit_rate']}%\n"

        context += "\n월별 n-day 리텐션 주요 구간:\n"
    key_days = day_df[day_df["day_n"].isin([1, 7, 14, 30])]
    for _, row in key_days.iterrows():
        context += f"- {row['month']} Day{int(row['day_n'])}: 리텐션 {row['retention_rate']}%, 유지 유저 {format_number(row['retained_user_count'])}명\n"

    context += "\n첫구매 경과일 코호트 예시:\n"
    cohort_sample = cohort_df[
        (cohort_df["day_n"].isin([0, 1, 7, 14]))
    ].head(12)

    for _, row in cohort_sample.iterrows():
        context += f"- {row['month']} 첫구매일 {int(row['first_purchase_day'])}일차 Day{int(row['day_n'])}: 리텐션 {row['retention_rate']}%, 코호트 유저 {format_number(row['cohort_user_count'])}명\n"
    
    return context


def make_smartphone_context(summary_data, selected_month, selected_brand):
    brand_df = summary_data["smartphone_brand"]
    time_df = summary_data["smartphone_time"]
    price_df = summary_data["smartphone_price_tier"]
    bundle_df = summary_data["smartphone_bundle_top3"]

    # 음수 구매 소요시간 제외
    price_df = price_df[
        (price_df["avg_time_to_purchase_sec"].isna()) |
        (price_df["avg_time_to_purchase_sec"] >= 0)
    ]

    if selected_month != "전체":
        brand_df = brand_df[brand_df["month"] == selected_month]
        time_df = time_df[time_df["month"] == selected_month]
        price_df = price_df[price_df["month"] == selected_month]
        bundle_df = bundle_df[bundle_df["month"] == selected_month]

    if selected_brand != "전체":
        brand_df = brand_df[brand_df["brand"] == selected_brand]
        time_df = time_df[time_df["brand"] == selected_brand]
        price_df = price_df[price_df["brand"] == selected_brand]

    context = "[스마트폰 브랜드 심화 페이지]\n"
    context += "이 페이지는 스마트폰 브랜드별 매출, 구매자 수, 구매 전환율, 인당 구매액, 시간대별 구매 패턴, 가격대별 구매 결정 시간, 함께 구매한 카테고리를 설명합니다.\n\n"

    context += "스마트폰 브랜드 KPI:\n"
    for _, row in brand_df.head(10).iterrows():
        context += f"""
- {row['month']} {row['brand']}
  - view 수: {format_number(row['view_count'])}
  - cart 수: {format_number(row['cart_count'])}
  - purchase 수: {format_number(row['purchase_count'])}
  - 구매 총액: {row['revenue']:,.2f}
  - 구매자 수: {format_number(row['purchase_user_count'])}
  - view → purchase 전환율: {row['view_to_purchase_rate']}%
  - 인당 구매액: {row['revenue_per_purchase_user']:,.2f}
"""

    top_time = time_df.sort_values("purchase_count", ascending=False).head(5)
    context += "\n구매가 많이 발생한 시간대 TOP5:\n"
    for _, row in top_time.iterrows():
        context += f"- {row['month']} {row['brand']} {row['hour']}시({row['time_segment']}): 구매 {format_number(row['purchase_count'])}건, 매출 {row['revenue']:,.2f}\n"

    context += "\n함께 구매한 카테고리 TOP3:\n"
    for _, row in bundle_df.iterrows():
        context += f"- {row['month']} {row['rank']}위: {row['category_code']} / 구매 {format_number(row['purchase_count'])}건 / 구매자 {format_number(row['buyer_count'])}명\n"

        context += "\n가격대별 구매 결정 시간 예시:\n"
    top_price = price_df.sort_values("purchase_count", ascending=False).head(8)

    for _, row in top_price.iterrows():
        avg_sec = row["avg_time_to_purchase_sec"]
        avg_min = avg_sec / 60 if pd.notna(avg_sec) else None

        if avg_min is not None:
            context += f"- {row['month']} {row['brand']} {row['price_tier']} / {row['consider_purchase_tier']} / {row['decision_tier']}: 평균 구매 소요시간 약 {avg_min:.1f}분, 구매 {format_number(row['purchase_count'])}건\n"
        else:
            context += f"- {row['month']} {row['brand']} {row['price_tier']}: 구매 {format_number(row['purchase_count'])}건, 구매 소요시간 정보 없음\n"
    
    return context

# =============================================================================
# 대화 기록 초기화
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요. 전자상거래 행동 분석 대시보드를 설명해주는 AI 챗봇입니다. 궁금한 내용을 입력해주세요."
        }
    ]

# =============================================================================
# 상단 제목
# =============================================================================
st.markdown(
    """
    <div class="main-title">전자상거래 10~11월 행동 분석 대시보드</div>
    <div class="sub-text">
        Tableau 대시보드를 Streamlit에 함께 배치하고,<br>
        Gemini 기반 AI 챗봇이 대시보드의 주요 흐름과 분석 결과를 설명하는 구조입니다.
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# 메인 레이아웃
# =============================================================================
left_col, right_col = st.columns([7, 3], gap="large")

# =============================================================================
# 왼쪽: Tableau 영역
# =============================================================================
with left_col:
    with st.container(border=True, height=920):
        st.markdown('<div class="section-title">Tableau 대시보드</div>', unsafe_allow_html=True)

        TABLEAU_URL = ""

        if TABLEAU_URL:
            components.iframe(
                src=TABLEAU_URL,
                height=560,
                scrolling=True
            )
        else:
            st.markdown(
                """
                <div class="tableau-placeholder">
                    태블로 대시보드
                    <span>Tableau 링크 연결 후 이 영역에 실제 대시보드가 표시됩니다.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="tableau-info">
                    Tableau 링크가 연결되면 이 영역에 실제 대시보드가 표시됩니다.
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown('<div class="expected-title">예정 화면 구성</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="expected-list">
            • 전체 현황 분석<br>
            • 코호트 / 리텐션<br>
            • 스마트폰 브랜드 심화
            </div>
            """,
            unsafe_allow_html=True
        )

# =============================================================================
# 오른쪽: AI 챗봇 영역
# =============================================================================
with right_col:
    with st.container(border=True, height=920):
        st.markdown(
            """
            <div class="ai-title">
                AI 챗봇
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="ai-guide-box">
                대시보드의 분석과 설명을 질문할 수 있습니다.
            </div>
            """,
            unsafe_allow_html=True
        )
        
        dashboard_page = st.selectbox(
            "대시보드 페이지",
            ["전체 현황 분석", "코호트/리텐션", "스마트폰 브랜드 심화"]
        )
        
        selected_month = st.selectbox(
            "월 선택",
            ["전체", "10월", "11월"]
        )
        
        selected_brand = "전체"
        
        if dashboard_page == "스마트폰 브랜드 심화":
            brand_df = summary_data["smartphone_brand"]
            brand_options = ["전체"] + sorted(brand_df["brand"].dropna().unique().tolist())

            selected_brand = st.selectbox(
                "스마트폰 브랜드 선택",
                brand_options
            )
            
        if dashboard_page == "전체 현황 분석":
            dashboard_context = make_overview_context(summary_data, selected_month)

        elif dashboard_page == "코호트/리텐션":
            dashboard_context = make_retention_context(summary_data, selected_month)

        else:
            dashboard_context = make_smartphone_context(
                summary_data,
                selected_month,
                selected_brand
            )     
        
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "안녕하세요. 전자상거래 행동 분석 대시보드를 설명해주는 AI 챗봇입니다. 궁금한 내용을 입력해주세요."
                }
            ]
            st.rerun()

        st.markdown('<div class="chat-title">AI 질문 및 답변</div>', unsafe_allow_html=True)

        chat_history_box = st.container(height=320)

        with chat_history_box:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])


        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "질문 입력",
                placeholder="대시보드나 분석 결과에 대해 질문해보세요.",
                height=90,
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("질문 보내기", use_container_width=True)

        if submitted and user_input.strip():
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )

            conversation_text = ""
            for message in st.session_state.messages[-8:]:
                role = "사용자" if message["role"] == "user" else "AI"
                conversation_text += f"{role}: {message['content']}\n"

            prompt = f"""
{SYSTEM_PROMPT}

현재 사용자가 보고 있는 대시보드 페이지와 필터:
- 대시보드 페이지: {dashboard_page}
- 선택 월: {selected_month}
- 선택 브랜드: {selected_brand}

아래는 현재 필터 기준으로 요약 CSV에서 추출한 데이터이다.

[현재 필터 기준 요약 데이터]
{dashboard_context}

아래는 현재까지의 대화 내용이다.

[대화 내용]
{conversation_text}

사용자의 마지막 질문에 답변해라.

답변 조건:
1. 반드시 위 요약 데이터의 숫자를 근거로 설명한다.
2. Tableau 화면을 직접 본 것처럼 말하지 말고, 제공된 요약 데이터 기준으로 설명한다.
3. 현재 요약 데이터에 없는 내용은 추측하지 않는다.
4. 답변은 가능하면 아래 순서로 작성한다.
   - 핵심 요약
   - 수치 근거
   - 해석
   - 발표용 멘트
5. 너무 길게 쓰지 말고 발표자가 바로 읽을 수 있게 작성한다.
"""

            try:
                with st.spinner("AI가 답변을 생성하는 중입니다..."):
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    ai_response = response.text

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": ai_response
                        }
                    )

                st.rerun()

            except Exception as e:
                st.error("Gemini 응답 생성 중 오류가 발생했습니다.")
                st.write(e)