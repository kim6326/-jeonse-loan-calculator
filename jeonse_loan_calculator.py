import streamlit as st

def calculate_monthly_payment(principal, years, rate, repay_type):
    months = years * 12
    monthly_rate = rate / 100 / 12

    if repay_type == "\uc6d0\ub9ac\uae08\uaddc\ub2e8":
        if monthly_rate == 0:
            return principal / months
        return principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    
    elif repay_type == "\uc6d0\uae08\uaddc\ub2e8":
        monthly_principal = principal / months
        return monthly_principal + (principal * monthly_rate)

    elif repay_type == "\ub9cc\uae30\uc77c\uc2dc":
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
        product = "\uccad\ub144 \uc804\uc138\uc790\uae08\ub300\출"
        max_limit = 200000000 if guarantee_org == "HUG" else 100000000
    elif is_married and annual_income <= 80000000:
        product = "\uc2e0\ud6c8\ubd80\ubd80 \uc804\uc138\uc790\uae08\ub300\출"
        max_limit = 240000000
    else:
        product = "\uc77c\ubc18 \uc804\uc138\uc790\uae08\ub300\출"
        max_limit = min(house_price * 0.8, 500000000)

    is_approved = hope_loan <= max_limit
    return product, max_limit, is_approved

def calculate_estimated_dsr(hope_loan, rate, years, existing_loans, income):
    new_monthly = calculate_monthly_payment(hope_loan, years, rate, "\uc6d0\ub9ac\uae08\uaddc\ub2e8")
    total_annual_payment = new_monthly * 12
    for loan in existing_loans:
        monthly = calculate_monthly_payment(
            loan["amount"], loan["period"], loan["rate"], loan["repay_type"]
        )
        total_annual_payment += monthly * 12
    return (total_annual_payment / income) * 100 if income > 0 else 0

# Streamlit UI
st.title("\uc804\uc138\uc790\uae08\ub300\출 \ud55c\ub3c4 \uacc4\uc0b0\uae30 with DSR")

age = st.number_input("\ub098\uc774", min_value=19, max_value=70, step=1)
is_married = st.radio("\uacb0\ud63c \uc5ec\ubd80", ["\ubbf8\ud63c", "\uacb0\ud63c"]) == "\uacb0\ud63c"
annual_income = st.number_input("\uc5f0\uc18c\ub4dd (\ub9cc\uc6d0)", min_value=0, step=100) * 10000
house_price = st.number_input("\uc804\uc138\uae08 (\uc6d0)", min_value=0, step=1000000)
hope_loan = st.number_input("\ud53c\ubc95 \ub300\출 \uae08\uc561 (\uc6d0)", min_value=0, step=1000000)
guarantee_org = st.selectbox("\ubcf4\uc99d\uae30\uad00", ["HUG", "HF", "SGI"])
loan_rate = st.number_input("\uc804\uc138\ub300\출 \uc774\uc790\uc728 (%)", min_value=0.0, step=0.1)
loan_years = st.number_input("\uc804\uc138\ub300\출 \uae30\uac04 (\ub144)", min_value=1, max_value=30)

st.markdown("### \uae30\uc874 \ub300\출 \uc815\ubcf4")
num_loans = st.number_input("\uae30\uc874 \ub300\출 \uac74\uc218", min_value=0, max_value=10, step=1)
existing_loans = []
for i in range(num_loans):
    st.markdown(f"#### 👉 \uae30\uc874 \ub300\출 {i+1}")
    amount = st.number_input(f"\ub300\출\uae08\uc561 {i+1} (\uc6d0)", min_value=0, step=1000000)
    period = st.number_input(f"\ub300\출\uae30\uac04 {i+1} (\ub144)", min_value=1, max_value=40)
    rate = st.number_input(f"\uc774\uc790\uc728 {i+1} (%)", min_value=0.0, step=0.1)
    repay_type = st.selectbox(f"\uc0ac\ud56d\ubc29\uc2dd {i+1}", ["\uc6d0\ub9ac\uae08\uaddc\ub2e8", "\uc6d0\uae08\uaddc\ub2e8", "\ub9cc\uae30\uc77c\uc2dc"], key=f"repay_{i}")
    existing_loans.append({"amount": amount, "period": period, "rate": rate, "repay_type": repay_type})

if st.button("\uacc4\uc0b0 \uacb0\uacfc \ubcf4\uae30"):
    current_dsr = calculate_dsr(existing_loans, annual_income)
    estimated_dsr = calculate_estimated_dsr(hope_loan, loan_rate, loan_years, existing_loans, annual_income)
    product, max_limit, is_approved = recommend_product(age, is_married, annual_income, house_price, hope_loan, guarantee_org)

    st.markdown(f"### 📌 \ud604\uc7ac DSR: **{current_dsr:.2f}%**")
    st.markdown(f"### 🧮 \uc804\uc138\ub300\출 \ud3ec\ud568 \uc608\uc0b0 DSR: **{estimated_dsr:.2f}%**")
    st.markdown(f"### 💡 \ucd5c\uc801 \uc801\uc6a9 \uac00\ub2a5 \uc0c1\ud488: **{product}**")
    st.markdown(f"### 💰 \ud574\ub2f9 \uc0c1\ud488 \ub300\출 \ub300\ud55c \ucd5c\ub300 \ud55c\ub3c4: **{int(max_limit):,} \uc6d0**")
    st.markdown(f"### ✅ \ud53c\ubc95 \ub300\출 \uac00\ub2a5 \uc5ec\ubd80: **{'\uac00\ub2a5' if is_approved else '\ubd88\uac00'}**")
