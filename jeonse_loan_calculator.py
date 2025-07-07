import streamlit as st
import io
from datetime import datetime

def calculate_monthly_payment(principal, years, rate, repay_type):
    months = years * 12
    monthly_rate = rate / 100 / 12

    if repay_type == "원리금균등":
        if monthly_rate == 0:
            return principal / months
        return principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    elif repay_type == "원금균등":
        monthly_principal = principal / months
        return monthly_principal + (principal * monthly_rate)
    elif repay_type == "만기일시":
        return principal * monthly_rate
    return 0

def calculate_dsr(existing_loans, annual_income):
    total_annual_payment = 0
    for loan in existing_loans:
        monthly = calculate_monthly_payment(
            loan["amount"], loan["period"], loan["rate"], loan["repay_type"]
        )
        total_annual_payment += monthly * 12
    return (total_annual_payment / annual_income) * 100 if annual_income > 0 else 0

def recommend_product(age, is_married, annual_income, market_price, hope_loan, guarantee_org):
    product = ""
    max_limit = 0
    if age <= 34 and annual_income <= 70000000:
        product = "청년 전세자금대출"
        max_limit = 200000000 if guarantee_org == "HUG" else 100000000
    elif is_married and annual_income <= 80000000:
        product = "신혼부부 전세자금대출"
        max_limit = 240000000
    else:
        product = "일반 전세자금대출"
        max_limit = min(market_price * 0.8, 500000000)
    is_approved = hope_loan <= max_limit
    return product, max_limit, is_approved

def calculate_estimated_dsr(hope_loan, rate, years, existing_loans, income):
    new_monthly = calculate_monthly_payment(hope_loan, years, rate, "원리금균등")
    total_annual_payment = new_monthly * 12
    for loan in existing_loans:
        monthly = calculate_monthly_payment(
            loan["amount"], loan["period"], loan["rate"], loan["repay_type"]
        )
        total_annual_payment += monthly * 12
    return (total_annual_payment / income) * 100 if income > 0 else 0

# --- UI 시작 ---
st.title("📊 전세자금대출 한도 계산기 with DSR")

if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {}

age = st.number_input("나이", min_value=19, max_value=70, step=1, value=st.session_state.user_inputs.get("age", 32))
is_married = st.radio("결혼 여부", ["미혼", "결혼"], index=1 if st.session_state.user_inputs.get("is_married", True) else 0) == "결혼"

raw_income = st.text_input("연소득 (만원)", value=st.session_state.user_inputs.get("raw_income", "6000"))
try:
    annual_income = int(raw_income.replace(",", "")) * 10000
    st.caption(f"👉 입력값: {annual_income:,} 원")
except:
    annual_income = 0
    st.error("숫자를 정확히 입력하세요. 예: 6,000")

raw_market_price = st.text_input("아파트 시세 (원)", value=st.session_state.user_inputs.get("raw_market_price", "500000000"))
try:
    market_price = int(raw_market_price.replace(",", ""))
    st.caption(f"👉 입력값: {market_price:,} 원")
except:
    market_price = 0
    st.error("숫자를 정확히 입력하세요. 예: 500,000,000")

raw_jeonse = st.text_input("전세 보증금 (원)", value=st.session_state.user_inputs.get("raw_jeonse", "450000000"))
try:
    house_price = int(raw_jeonse.replace(",", ""))
    st.caption(f"👉 입력값: {house_price:,} 원")
except:
    house_price = 0
    st.error("숫자를 정확히 입력하세요. 예: 450,000,000")

raw_hope = st.text_input("희망 대출 금액 (원)", value=st.session_state.user_inputs.get("raw_hope", "300000000"))
try:
    hope_loan = int(raw_hope.replace(",", ""))
    st.caption(f"👉 입력값: {hope_loan:,} 원")
except:
    hope_loan = 0
    st.error("숫자를 정확히 입력하세요. 예: 300,000,000")

guarantee_org = st.selectbox("보증기관", ["HUG", "HF", "SGI"], index=["HUG", "HF", "SGI"].index(st.session_state.user_inputs.get("guarantee_org", "HUG")))
loan_rate = st.number_input("전세대출 이자율 (%)", min_value=0.0, step=0.1, value=st.session_state.user_inputs.get("loan_rate", 3.5))
loan_years = st.number_input("전세대출 기간 (년)", min_value=1, max_value=30, value=st.session_state.user_inputs.get("loan_years", 2))

st.markdown("### 🏦 기존 대출 정보 입력")
num_loans = st.number_input("기존 대출 건수", min_value=0, max_value=10, step=1, value=st.session_state.user_inputs.get("num_loans", 1))
existing_loans = []
for i in range(num_loans):
    st.markdown(f"#### 👉 기존 대출 {i+1}")
    raw_amt = st.text_input(f"대출금액 {i+1} (원)", value="100000000", key=f"amt_{i}")
    try:
        amount = int(raw_amt.replace(",", ""))
        st.caption(f"👉 입력값: {amount:,} 원")
    except:
        amount = 0
        st.error("숫자를 정확히 입력하세요.", key=f"err_amt_{i}")
    period = st.number_input(f"대출기간 {i+1} (년)", min_value=1, max_value=40, key=f"prd_{i}")
    rate = st.number_input(f"이자율 {i+1} (%)", min_value=0.0, step=0.1, key=f"rate_{i}")
    repay_type = st.selectbox(f"상환방식 {i+1}", ["원리금균등", "원금균등", "만기일시"], key=f"repay_{i}")
    existing_loans.append({
        "amount": amount,
        "period": period,
        "rate": rate,
        "repay_type": repay_type
    })

if st.button("📊 계산 결과 보기"):
    # 입력값 저장
    st.session_state.user_inputs = {
        "age": age,
        "is_married": is_married,
        "raw_income": raw_income,
        "raw_market_price": raw_market_price,
        "raw_jeonse": raw_jeonse,
        "raw_hope": raw_hope,
        "guarantee_org": guarantee_org,
        "loan_rate": loan_rate,
        "loan_years": loan_years,
        "num_loans": num_loans
    }

    current_dsr = calculate_dsr(existing_loans, annual_income)
    estimated_dsr = calculate_estimated_dsr(hope_loan, loan_rate, loan_years, existing_loans, annual_income)
    product, max_limit, is_approved = recommend_product(age, is_married, annual_income, market_price, hope_loan, guarantee_org)

    st.markdown(f"### 📌 현재 DSR: **{current_dsr:.2f}%**")
    st.markdown(f"### 🧮 전세대출 포함 예상 DSR: **{estimated_dsr:.2f}%**")
    st.markdown(f"### 💡 추천 상품: **{product}**")
    st.markdown(f"### 💰 해당 상품 최대 한도: **{int(max_limit):,} 원**")
    st.markdown(f"### ✅ 희망 대출 가능 여부: **{'가능' if is_approved else '불가'}**")

    # SGI 보증료 안내
    if guarantee_org == "SGI":
        sgi_fee = hope_loan * 0.01
        st.markdown(f"💸 SGI 보증료 추정: **{int(sgi_fee):,} 원** (대출금에서 차감될 수 있음)")

    # 최대 대출 가능 역산
    if estimated_dsr > 70 and loan_rate > 0:
        r = loan_rate / 100 / 12
        n = loan_years * 12
        max_annual_repay = annual_income * 0.7
        existing_annual = sum(
            calculate_monthly_payment(l["amount"], l["period"], l["rate"], l["repay_type"]) * 12 for l in existing_loans
        )
        remain_annual = max_annual_repay - existing_annual

        if remain_annual > 0:
            max_possible_loan = (remain_annual / 12) * ((1 + r)**n - 1) / (r * (1 + r)**n)
            st.markdown(f"🔁 현재 소득 기준으로 가능한 최대 대출금: **{int(max_possible_loan):,} 원** (DSR 70% 기준)")

    # 보고서 다운로드 기능
    result_text = f"""
    전세자금대출 한도 계산 보고서 - {datetime.now().strftime('%Y-%m-%d')}

    [기본 정보]
    나이: {age}
    결혼 여부: {'결혼' if is_married else '미혼'}
    연소득: {annual_income:,} 원
    아파트 시세: {market_price:,} 원
    전세금: {house_price:,} 원
    희망 대출금: {hope_loan:,} 원
    보증기관: {guarantee_org}

    [계산 결과]
    현재 DSR: {current_dsr:.2f}%
    전세대출 포함 예상 DSR: {estimated_dsr:.2f}%
    추천 상품: {product}
    최대 대출 한도: {int(max_limit):,} 원
    대출 가능 여부: {'가능' if is_approved else '불가'}
    """
    st.download_button(
        label="📄 보고서 다운로드 (TXT)",
        data=io.StringIO(result_text),
        file_name="jeonse_loan_report.txt",
        mime="text/plain"
    )

    

 
