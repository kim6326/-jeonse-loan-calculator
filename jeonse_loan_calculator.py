import streamlit as st
from datetime import datetime

# ... [기존 함수 정의 생략] ...
# (함수 부분은 그대로 유지됨)

# --- UI 시작 ---
st.title("📊 전세자금대출 한도 계산기 with DSR")

if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {}

# ... [입력 UI 생략] ...

use_stress_rate = st.checkbox("📈 스트레스 금리 적용 (DSR 계산 시 +0.6%)")
effective_rate = loan_rate + 0.6 if use_stress_rate else loan_rate

# 금리 정보 시각화
st.markdown(f"👤 고객 안내용 금리: **{loan_rate:.2f}%**")
if use_stress_rate:
    st.markdown(f"📈 내부 DSR 계산용 스트레스 금리: **{effective_rate:.2f}%**")

# 생활안정자금 추가 여부
st.markdown("---")
st.markdown("### 💼 생활안정자금 여부")
want_life_loan = st.checkbox("생활안정자금 추가 신청")

if want_life_loan:
    st.info("ℹ️ 생활안정자금은 세입자 본인 명의로 실행되며, 집주인 동의는 불필요합니다. 전세자금대출과 달리 임대차와 무관한 생활비 용도 대출이기 때문입니다."))

            life_years = st.number_input("생활안정자금 대출 기간 (년)", min_value=1, max_value=10, value=3)
            life_rate = st.number_input("생활안정자금 금리 (%)", min_value=0.0, value=4.13)
            life_amount = st.number_input("신청할 생활안정자금 금액 (원)", min_value=0, max_value=int(remaining_limit), value=0, step=1000000)

            if life_amount > 0:
                def calc_monthly_life(principal, years, rate):
                    months = years * 12
                    monthly_rate = rate / 100 / 12
                    return principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1) if monthly_rate > 0 else principal / months

                life_monthly_payment = calc_monthly_life(life_amount, life_years, life_rate)
                st.markdown(f"📆 생활안정자금 월 예상 상환액: **{int(life_monthly_payment):,} 원**")
        else:
            st.warning("생활안정자금 여유 한도가 없습니다. 보증한도 또는 규제 조건에 의해 제한됩니다.")

# ... [기존 대출 입력 및 결과 계산 UI 생략] ...

# 결과 출력 후 다운로드 버튼 (기존 코드 유지)
