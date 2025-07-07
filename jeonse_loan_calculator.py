import streamlit as st

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

def recommend_product(age, is_married, annual_income, house_price, hope_loan, guarantee_org):
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
        max_limit = min(house_price * 0.8, 500000000)
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

# 기본 정보 입력
age = st.number_input("나이", min_value=19, max_value=70, step=1)
is_married = st.radio("결혼 여부", ["미혼", "결혼"]) == "결혼"

# 연소득
raw_income = st.text_input("연소득 (만원)", value="6000")
try:
    annual_income = int(raw_income.replace(",", "")) * 10000
    st.caption(f"👉 입력값: {annual_income:,} 원")
except:
    annual_income = 0
    st.error("숫자를 정확히 입력하세요. 예: 6,000")

# 전세금
raw_jeonse = st.text_input("전세금 (원)", value="450000000")
try:
    house_price = int(raw_jeonse.replace(",", ""))
    st.caption(f"👉 입력값: {house_price:,} 원")
except:
    house_price = 0
    st.error("숫자를 정확히 입력하세요. 예: 450,000,000")

# 희망 대출금
raw_hope = st.text_input("희망 대출 금액 (원)", value="300000000")
try:
    hope_loan = int(raw_hope.replace(",", ""))
    st.caption(f"👉 입력값: {hope_loan:,} 원")
except:
    hope_loan = 0
    st.error("숫자를 정확히 입력하세요. 예: 300,000,000")

# 보증기관 / 전세대출 조건
guarantee_org = st.selectbox("보증기관", ["HUG", "HF", "SGI"])
loan_rate = st.number_input("전세대출 이자율 (%)", min_value=0.0, step=0.1)
loan_years = st.number_input("전세대출 기간 (년)", min_value=1, max_value=30)

# 기존 대출 입력
st.markdown("### 🏦 기존 대출 정보 입력")
num_loans = st.number_input("기존 대출 건수", min_value=0, max_value=10, step=1)
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

# 계산 버튼
if st.button("📊 계산 결과 보기"):
    current_dsr = calculate_dsr(existing_loans, annual_income)
    estimated_dsr = calculate_estimated_dsr(hope_loan, loan_rate, loan_years, existing_loans, annual_income)
    product, max_limit, is_approved = recommend_product(age, is_married, annual_income, house_price, hope_loan, guarantee_org)

    st.markdown(f"### 📌 현재 DSR: **{current_dsr:.2f}%**")
    st.markdown(f"### 🧮 전세대출 포함 예상 DSR: **{estimated_dsr:.2f}%**")
    st.markdown(f"### 💡 추천 상품: **{product}**")
    st.markdown(f"### 💰 해당 상품 최대 한도: **{int(max_limit):,} 원**")
    st.markdown(f"### ✅ 희망 대출 가능 여부: **{'가능' if is_approved else '불가'}**")

  
