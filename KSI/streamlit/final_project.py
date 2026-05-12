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
7. 매출 단위는 "조 달러"라고 풀어 쓰지 말고, 대시보드 표기처럼 "$2,066조" 또는 "대시보드 기준 2,066조"처럼 표현한다.
8. apple, samsung, xiaomi, huawei, lg처럼 브랜드명이 나오는 TOP5는 "카테고리"라고 단정하지 말고 "브랜드/품목 기준 TOP5"로 설명한다.
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
    context = "[전체 현황 분석 페이지]\n"
    context += "이 페이지는 전체 매출, 유저 수, 구매 전환율, 퍼널, 일별 추이, 첫방문/재방문 매출, 브랜드/품목 성과를 설명합니다.\n\n"

    overview_display_kpi = {
        "전체": """
핵심 KPI:
- 전체 매출: $2,066조
- 전체 유저 수: 532만 명
- 구매 전환율: 3.95%
- 방문 매출: $1,908조
- View 수: 23백만 건
- Cart 수: 2,316천 건
- Purchase 수: 1,403천 건
- 브랜드/품목 기준 TOP5 매출: apple 1위, samsung 2위, xiaomi 3위, huawei 4위, lg 5위
- 브랜드 현황: 구매 수 1위 samsung, 매출 1위 apple, 전환율 1위 samsung

주의:
- 위 수치는 Tableau 전체 현황 대시보드의 전체 선택 화면에 표시된 핵심 KPI 기준이다.
- 전체 선택 상태에서는 10월/11월을 따로 비교하기보다 전체 합산 화면 기준으로 먼저 설명한다.
""",
        "10월": """
핵심 KPI:
- 전체 매출: $749조
- 전체 유저 수: 302만 명
- 구매 전환율: 4.45%
- 방문 매출: $651.5조
- View 수: 9백만 건
- Cart 수: 573천 건
- Purchase 수: 630천 건
- 브랜드/품목 기준 TOP5 매출: apple 457.8조, samsung 244.6조, xiaomi 28.3조, huawei 5.4조, lucente 2.0조
- 브랜드 현황: 구매 수 1위 samsung, 매출 1위 apple, 전환율 1위 samsung

주의:
- 위 수치는 Tableau 전체 현황 대시보드의 10월 선택 화면에 표시된 핵심 KPI 기준이다.
- 10월 선택 상태에서는 10월 데이터만 설명하고, 11월과 비교하지 않는다.
""",
        "11월": """
핵심 KPI:
- 전체 매출: $1,317조
- 전체 유저 수: 370만 명
- 구매 전환율: 3.64%
- 방문 매출: $1,190조
- View 수: 14백만 건
- Cart 수: 1,743천 건
- Purchase 수: 773천 건
- 브랜드/품목 기준 TOP5 매출: apple 796.5조, samsung 431.5조, xiaomi 52.1조, huawei 6.7조, lg 5.7조
- 브랜드 현황: 구매 수 1위 samsung, 매출 1위 apple, 전환율 1위 samsung

주의:
- 위 수치는 Tableau 전체 현황 대시보드의 11월 선택 화면에 표시된 핵심 KPI 기준이다.
- 11월 선택 상태에서는 11월 데이터만 설명하고, 10월과 비교하지 않는다.
"""
    }

    if selected_month in overview_display_kpi:
        context += overview_display_kpi[selected_month]
        context += "\n답변 지침:\n"
        context += "- 현재 선택 월 기준의 핵심 KPI를 먼저 설명한다.\n"
        context += "- 사용자가 비교를 요청하지 않으면 다른 월과 비교하지 않는다.\n"
        context += "- 매출 단위는 '조 달러'라고 풀어 쓰지 말고, '$749조', '$1,317조'처럼 대시보드 표기 방식으로 말한다.\n"
        context += "- apple, samsung, xiaomi 등은 카테고리가 아니라 브랜드/품목 기준 TOP5로 설명한다.\n"
        return context


def make_retention_context(summary_data, selected_month):
    context = "[유저 행동 & 리텐션 페이지]\n"
    context += "이 페이지는 전체 재방문율, Day1/Day7 재방문율, 일별 리텐션 커브, 첫구매 경과일 코호트, 카테고리별 구매자/비구매자 재방문율을 설명합니다.\n\n"

    retention_display_kpi = {
        "전체": """
핵심 KPI:
- 전체 재방문율: 4.39%
- Day1 재방문율: 0.80%
- Day7 재방문율: 0.38%
- 일별 리텐션 커브: 첫 시점에서 재방문율이 가장 높고, 이후 빠르게 감소한 뒤 낮은 수준에서 완만하게 유지된다.
- 첫구매 경과일 추적 코호트: 첫 구매 이후 시간이 지날수록 재방문 강도가 약해지지만, 일부 구간에서 상대적으로 진한 유지 패턴이 확인된다.
- 카테고리별 구매자 재방문율 TOP5: headphone 0.06%, tv 0.04%, vacuum 0.03%, washer 0.03%, refrigerators 0.02%
- 구매자 vs 비구매자 카테고리 재방문율: electronics, unknown, appliances 카테고리에서 규모가 크게 나타나며, 카테고리별 구매자 재방문율 차이를 비교할 수 있다.

주의:
- 위 수치는 Tableau 유저 행동 & 리텐션 대시보드의 전체 선택 화면에 표시된 값 기준이다.
- 전체 선택 상태에서는 10월/11월을 따로 비교하지 말고 전체 기준 리텐션 KPI를 먼저 설명한다.
""",
        "10월": """
핵심 KPI:
- 전체 재방문율: 4.46%
- Day1 재방문율: 0.90%
- Day7 재방문율: 0.47%
- 일별 리텐션 커브: 첫 시점에서 재방문율이 가장 높고, 이후 빠르게 감소하며 낮은 수준에서 완만하게 이어진다.
- 첫구매 경과일 추적 코호트: 첫 구매 직후 구간에서 상대적으로 재방문 강도가 높고, 시간이 지날수록 점차 약해지는 패턴이 보인다.
- 카테고리별 구매자 재방문율 TOP5: headphone 0.05%, tv 0.03%, washer 0.03%, vacuum 0.02%, refrigerators 0.02%
- 구매자 vs 비구매자 카테고리 재방문율: electronics와 unknown의 규모가 크게 나타나며, 주요 카테고리별 구매자 재방문율 차이를 비교할 수 있다.

주의:
- 위 수치는 Tableau 유저 행동 & 리텐션 대시보드의 10월 선택 화면에 표시된 값 기준이다.
- 10월 선택 상태에서는 10월 데이터만 설명하고, 11월과 비교하지 않는다.
""",
        "11월": """
핵심 KPI:
- 전체 재방문율: 4.66%
- Day1 재방문율: 1.06%
- Day7 재방문율: 0.53%
- 일별 리텐션 커브: 첫 시점에서 재방문율이 가장 높고, 이후 빠르게 하락한 뒤 낮은 수준에서 완만하게 유지된다.
- 첫구매 경과일 추적 코호트: 첫 구매 후 초반 구간에서 상대적으로 재방문 강도가 높고, 일부 경과일 구간에서 유지 패턴이 확인된다.
- 카테고리별 구매자 재방문율 TOP5: headphone 0.05%, tv 0.04%, vacuum 0.03%, washer 0.03%, refrigerators 0.02%
- 구매자 vs 비구매자 카테고리 재방문율: electronics와 unknown 카테고리가 큰 비중을 보이며, 이후 appliances, apparel, computers 등에서 재방문율 차이를 확인할 수 있다.

주의:
- 위 수치는 Tableau 유저 행동 & 리텐션 대시보드의 11월 선택 화면에 표시된 값 기준이다.
- 11월 선택 상태에서는 11월 데이터만 설명하고, 10월과 비교하지 않는다.
"""
    }

    if selected_month in retention_display_kpi:
        context += retention_display_kpi[selected_month]
        context += "\n답변 지침:\n"
        context += "- 현재 선택 월 기준의 리텐션 KPI를 먼저 설명한다.\n"
        context += "- 사용자가 비교를 요청하지 않으면 다른 월과 비교하지 않는다.\n"
        context += "- 전체 재방문율, Day1 재방문율, Day7 재방문율을 반드시 포함한다.\n"
        context += "- 리텐션 커브와 첫구매 경과일 코호트는 핵심 흐름만 짧게 설명한다.\n"
        context += "- 카테고리별 구매자/비구매자 재방문율은 화면에 보이는 주요 차이만 설명한다.\n"
        context += "- 화면에 없는 정확한 수치는 추측하지 않는다.\n"
        context += "- 이 페이지에서는 '첫 방문'이라는 표현보다 '첫 구매 이후' 또는 '첫 구매 경과일 기준'이라는 표현을 사용한다.\n"
        return context


def make_smartphone_context(summary_data, selected_month, selected_brand):
    context = "[스마트폰 브랜드 심화 페이지]\n"
    context += "이 페이지는 스마트폰 전체 매출, 구매자 수, 구매 전환율, 인당 구매액, 스마트폰 퍼널, 시간대별 구매 패턴, 가격대별 구매 결정 시간, 함께 구매한 카테고리, 상품/카테고리 비중을 설명합니다.\n\n"

    smartphone_display_kpi = {
        ("전체", "전체"): """
핵심 KPI:
- [스마트폰] 전체 매출: $1,495조
- 구매자 수: 244만 명
- 구매 전환율: 0.13%
- 인당 구매액: $6억 8천만
- View 수: 7백만 건
- Cart 수: 1,006천 건
- Purchase 수: 609천 건

함께 구매한 카테고리 TOP3:
- audio
- kitchen
- video

가격대별 구매 결정 시간:
- 전체 가격대에서 36시간 초과 비중이 가장 크게 나타난다.
- 이월/저가형과 프리미엄 가격대의 구매 규모가 상대적으로 크다.
- 즉시 구매와 12시간 이내 구매도 일부 존재하지만, 전체적으로는 장시간 비교 후 구매하는 비중이 크다.

상품/카테고리 비중:
- clocks, kitchen, telephone, camera, accessories, notebook, environment, video 등이 크게 나타난다.
- 스마트폰 구매와 함께 생활가전, 액세서리, 디지털 주변 품목이 함께 언급되는 흐름으로 해석할 수 있다.

시간대별 스마트폰 구매 패턴:
- 매출 기준 일별 그래프는 월 중순인 15~17일 전후에 피크가 나타난다.
- 매출 기준 요일별 그래프는 금요일과 토요일이 상대적으로 높다.
- 매출 기준 시간별 그래프는 오후 14~17시 전후에 가장 높고, 저녁 이후 감소한다.
- 구매자 수 기준 일별 그래프도 월 중순 15~17일 전후에 집중된다.
- 구매자 수 기준 요일별 그래프는 금요일과 토요일이 상대적으로 높고, 일요일에는 다소 감소한다.
- 구매자 수 기준 시간별 그래프는 오후 14~16시 전후에 가장 높고, 저녁 이후 빠르게 감소한다.

주의:
- 위 수치는 Tableau 스마트폰 브랜드 심화 대시보드의 전체 월, 전체 브랜드 선택 화면에 표시된 값 기준이다.
- 세부 그래프 해석은 Tableau 기본 화면 및 제공된 필터별 캡처 기준이다.
- 선택 월과 브랜드가 전체인 경우에는 특정 브랜드별 수치를 임의로 설명하지 않는다.
""",

        ("10월", "전체"): """
핵심 KPI:
- [스마트폰] 전체 매출: $565조
- 구매자 수: 130만 명
- 구매 전환율: 0.12%
- 인당 구매액: $4억 7천만
- View 수: 3백만 건
- Cart 수: 335천 건
- Purchase 수: 285천 건

함께 구매한 카테고리 TOP3:
- audio
- kitchen
- clocks

가격대별 구매 결정 시간:
- 전체 가격대에서 36시간 초과 비중이 가장 크게 나타난다.
- 이월/저가형의 구매 규모가 가장 크고, 프리미엄 가격대가 그 뒤를 따른다.
- 보급형과 준프리미엄은 상대적으로 규모가 작지만, 동일하게 장시간 비교 후 구매하는 비중이 크다.

상품/카테고리 비중:
- clocks, kitchen, camera, telephone, accessories, environment, notebook 등이 크게 나타난다.
- 스마트폰 구매와 함께 생활가전, 액세서리, 디지털 주변 품목이 함께 언급되는 흐름으로 해석할 수 있다.

시간대별 스마트폰 구매 패턴:
- 매출 기준 일별 그래프는 월 중순 전후에 상대적으로 높고, 월말에는 낮아지는 흐름을 보인다.
- 매출 기준 요일별 그래프는 화요일~목요일 구간이 높고, 금요일 이후 다소 낮아지는 흐름이다.
- 매출 기준 시간별 그래프는 오전부터 증가해 오후 15~16시 전후에 가장 높고, 18시 이후 빠르게 감소한다.
- 구매자 수 기준 일별 그래프는 중순~20일 전후에 높고, 월말에는 낮아지는 흐름이다.
- 구매자 수 기준 요일별 그래프는 화요일~목요일이 상대적으로 높고, 금요일 이후 감소하는 흐름이다.
- 구매자 수 기준 시간별 그래프는 오후 14~16시 전후에 가장 높고, 저녁 이후 빠르게 감소한다.

주의:
- 위 수치는 Tableau 스마트폰 브랜드 심화 대시보드의 10월, 전체 브랜드 선택 화면에 표시된 값 기준이다.
- 세부 그래프 해석은 Tableau 기본 화면 및 제공된 필터별 캡처 기준이다.
- 선택 월이 10월이고 브랜드가 전체인 경우에는 특정 브랜드별 수치를 임의로 설명하지 않는다.
""",

        ("11월", "전체"): """
핵심 KPI:
- [스마트폰] 전체 매출: $930조
- 구매자 수: 158만 명
- 구매 전환율: 0.12%
- 인당 구매액: $6억 6천만
- View 수: 4백만 건
- Cart 수: 671천 건
- Purchase 수: 324천 건

함께 구매한 카테고리 TOP3:
- audio
- kitchen
- video

가격대별 구매 결정 시간:
- 전체 가격대에서 36시간 초과 비중이 가장 크게 나타난다.
- 이월/저가형과 프리미엄 가격대의 구매 규모가 상대적으로 크다.
- 보급형과 준프리미엄은 상대적으로 규모가 작지만, 동일하게 장시간 비교 후 구매하는 비중이 크다.

상품/카테고리 비중:
- clocks, kitchen, camera, telephone, shoes, notebook, environment, accessories 등이 크게 나타난다.
- 스마트폰 구매와 함께 생활가전, 액세서리, 디지털 주변 품목이 함께 언급되는 흐름으로 해석할 수 있다.

시간대별 스마트폰 구매 패턴:
- 매출 기준 일별 그래프는 월 중순인 15~17일 전후에 매우 뚜렷한 피크가 나타난다.
- 매출 기준 요일별 그래프는 금요일과 토요일이 높고, 월요일~수요일은 상대적으로 낮다.
- 매출 기준 시간별 그래프는 오전부터 증가해 오후 14~17시 전후에 가장 높고, 18시 이후 급격히 감소한다.
- 구매자 수 기준 일별 그래프는 15~17일 전후에 구매자 수가 크게 증가하고 이후 낮은 수준으로 안정된다.
- 구매자 수 기준 요일별 그래프는 금요일과 토요일이 상대적으로 높고, 일요일에는 다소 감소한다.
- 구매자 수 기준 시간별 그래프는 오후 14~16시 전후에 가장 높고, 저녁 이후 빠르게 감소한다.

주의:
- 위 수치는 Tableau 스마트폰 브랜드 심화 대시보드의 11월, 전체 브랜드 선택 화면에 표시된 값 기준이다.
- 세부 그래프 해석은 Tableau 기본 화면 및 제공된 필터별 캡처 기준이다.
- 선택 월이 11월이고 브랜드가 전체인 경우에는 특정 브랜드별 수치를 임의로 설명하지 않는다.
"""
    }

    key = (selected_month, selected_brand)

    if key in smartphone_display_kpi:
        context += smartphone_display_kpi[key]
        context += "\n답변 지침:\n"
        context += "- 현재 선택 월과 선택 브랜드 기준의 KPI를 먼저 설명한다.\n"
        context += "- 사용자가 비교를 요청하지 않으면 다른 월이나 다른 브랜드와 비교하지 않는다.\n"
        context += "- 스마트폰 전체 매출, 구매자 수, 구매 전환율, 인당 구매액, View/Cart/Purchase 수치를 반드시 포함한다.\n"
        context += "- 시간대별 구매 패턴, 가격대별 구매 결정 시간, 함께 구매한 카테고리, 상품/카테고리 비중은 핵심 흐름만 짧게 설명한다.\n"
        context += "- 시간대별 구매 패턴의 세부 필터는 제공된 캡처 기준으로 해석하며, 화면에 없는 정확한 수치는 추측하지 않는다.\n"
        context += "- 선택 브랜드가 전체인 경우에는 특정 브랜드별 수치를 임의로 설명하지 않는다.\n"
        return context

    return """
[스마트폰 브랜드 심화 페이지]
현재 선택한 월/브랜드 조합에 대한 Tableau 화면 기준 요약값이 아직 입력되지 않았습니다.
현재 AI 설명은 전체 브랜드 기준의 주요 KPI와 그래프 패턴 중심으로 제공됩니다.
브랜드를 개별 선택한 경우에는 화면에 보이는 값을 기준으로 직접 확인해야 합니다.
"""

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
    with st.container(border=True, height=1160):
        st.markdown('<div class="section-title">Tableau 대시보드</div>', unsafe_allow_html=True)

        TABLEAU_URL = "https://prod-kr-a.online.tableau.com/t/joeunsol112-263e2c660a/views/10___cloud_/1_?:origin=card_share_link&:embed=y"

        if TABLEAU_URL:
            components.iframe(
                src=TABLEAU_URL,
                width=1200,
                height=900,
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

        st.markdown('<div class="expected-title">대시보드 구성</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="expected-list">
            • 전체 현황 분석<br>
            • 유저 행동 & 리텐션<br>
            • 스마트폰 브랜드 심화
            </div>
            """,
            unsafe_allow_html=True
        )

# =============================================================================
# 오른쪽: AI 챗봇 영역
# =============================================================================
with right_col:
    with st.container(border=True, height=1000):
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
                대시보드의 분석과 설명을 질문할 수 있습니다.<br>
            """,
            unsafe_allow_html=True
        )
        
        dashboard_page = st.selectbox(
            "대시보드 페이지",
            ["전체 현황 분석", "유저 행동 & 리텐션", "스마트폰 브랜드 심화"]
        )
        
        selected_month = st.selectbox(
            "월 선택",
            ["전체", "10월", "11월"]
        )
        
        selected_brand = "전체"
        
        if dashboard_page == "스마트폰 브랜드 심화":
            selected_brand = st.selectbox(
                "스마트폰 브랜드 선택",
                ["전체"]
            )
            
        if dashboard_page == "전체 현황 분석":
            dashboard_context = make_overview_context(summary_data, selected_month)

        elif dashboard_page == "유저 행동 & 리텐션":
            dashboard_context = make_retention_context(summary_data, selected_month)

        elif dashboard_page == "스마트폰 브랜드 심화":
            dashboard_context = make_smartphone_context(
                summary_data,
                selected_month,
                selected_brand
            )
        
        else:
            dashboard_context = "선택한 대시보드 페이지에 맞는 요약 데이터를 찾지 못했습니다."
        
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
                    safe_content = message["content"].replace("$", "\\$")
                    st.markdown(safe_content)


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

아래는 현재 선택한 대시보드 페이지와 필터 기준으로 정리한 Tableau 화면 요약 데이터이다.

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
4. 선택 월이 "전체"인 경우에는 10월/11월 월별 수치를 먼저 나열하지 말고, "전체" 항목의 KPI를 우선 설명한다. 월별 비교는 사용자가 요청한 경우에만 보조적으로 언급한다.
5. 사용자가 요약을 요청하면 아래 순서로 짧게 답한다.
   - 핵심 요약 2~3문장
   - 주요 수치 3~5개
   - 발표용 멘트 1개
6. 원인이나 전략은 사용자가 요청한 경우에만 제안한다.
7. 이상한 번역체 표현을 사용하지 않는다.
8. 매출 단위는 "조 달러"라고 풀어 쓰지 말고, 대시보드 표기처럼 "$2,066조" 또는 "대시보드 기준 2,066조"처럼 표현한다.
9. apple, samsung, xiaomi, huawei, lg처럼 브랜드명이 나오는 TOP5는 "카테고리"라고 단정하지 말고 "브랜드/품목 기준 TOP5"로 설명한다.
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
                error_text = str(e)

                if "503" in error_text or "UNAVAILABLE" in error_text or "high demand" in error_text:
                    st.warning("현재 Gemini 요청이 많아 응답이 지연되고 있습니다. 잠시 후 다시 질문을 보내주세요.")
                else:
                    st.error("Gemini 응답 생성 중 오류가 발생했습니다.")
                    st.write(e)