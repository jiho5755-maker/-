import streamlit as st
import random
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="🏪 장사의 신 게임 관리 시스템",
    page_icon="💰",
    layout="wide"
)

# 세션 스테이트 초기화
if 'students' not in st.session_state:
    st.session_state.students = {}

if 'current_round' not in st.session_state:
    st.session_state.current_round = 1

if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# 제목
st.title("🏪 장사의 신 게임 관리 시스템")
st.markdown("---")

# 사이드바: 시장 설정
st.sidebar.header("⚙️ 시장 설정 (Admin)")
st.sidebar.markdown("### 💵 시장 기본 설정")

total_money = st.sidebar.number_input(
    "💰 시장 총 화폐량 (원)",
    min_value=10000,
    max_value=10000000,
    value=1000000,
    step=10000,
    help="게임에서 사용할 전체 화폐량을 입력하세요"
)

total_buyers = st.sidebar.number_input(
    "👥 전체 구매자(조교) 수",
    min_value=5,
    max_value=200,
    value=30,
    step=1,
    help="구매자 역할을 하는 조교/선생님 인원수"
)

st.sidebar.markdown("### 🎯 구매자 성향 비율 설정")
st.sidebar.info("💡 세 가지 비율의 합이 100%가 되도록 설정하세요!")

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    big_spender_ratio = st.number_input("🤑 큰손", min_value=0, max_value=100, value=20, step=5)
with col2:
    normal_ratio = st.number_input("😊 일반", min_value=0, max_value=100, value=50, step=5)
with col3:
    frugal_ratio = st.number_input("🤏 짠물", min_value=0, max_value=100, value=30, step=5)

# 비율 합계 체크
total_ratio = big_spender_ratio + normal_ratio + frugal_ratio
if total_ratio != 100:
    st.sidebar.error(f"⚠️ 비율 합계: {total_ratio}% (100%가 되어야 합니다!)")
else:
    st.sidebar.success("✅ 비율 설정 완료!")

# 구매자 그룹별 계산
if total_ratio == 100:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 구매자 그룹 분석")
    
    # 각 그룹별 인원수 계산
    big_spender_count = int(total_buyers * big_spender_ratio / 100)
    normal_count = int(total_buyers * normal_ratio / 100)
    frugal_count = total_buyers - big_spender_count - normal_count  # 나머지 할당
    
    # 각 그룹별 보유 금액 (큰손: 2배, 일반: 1배, 짠물: 0.5배)
    avg_budget = total_money / total_buyers
    big_spender_budget = avg_budget * 2
    normal_budget = avg_budget * 1
    frugal_budget = avg_budget * 0.5
    
    st.sidebar.metric("🤑 큰손", f"{big_spender_count}명", f"{big_spender_budget:,.0f}원/인")
    st.sidebar.metric("😊 일반", f"{normal_count}명", f"{normal_budget:,.0f}원/인")
    st.sidebar.metric("🤏 짠물", f"{frugal_count}명", f"{frugal_budget:,.0f}원/인")

# 라운드 관리
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎮 게임 라운드 관리")
current_round = st.sidebar.radio(
    "현재 라운드",
    [1, 2],
    index=st.session_state.current_round - 1,
    help="1라운드 후 시장 상황을 공유하고 2라운드를 진행하세요"
)
st.session_state.current_round = current_round

if current_round == 1:
    st.sidebar.info("🎯 1라운드: 초기 판매 전략으로 시작!")
else:
    st.sidebar.success("🔥 2라운드: 전략을 수정해서 역전하세요!")

# 데이터 초기화 버튼
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ 전체 데이터 초기화", type="secondary"):
    st.session_state.students = {}
    st.session_state.current_round = 1
    st.sidebar.success("✅ 모든 데이터가 초기화되었습니다!")
    st.rerun()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📝 창업 컨설팅", "💼 판매 관리", "📊 장사의신 대시보드"])

# ===== TAB 1: 창업 컨설팅 =====
with tab1:
    st.header("👨‍🎓 학생 정보 입력")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        student_name = st.text_input(
            "📝 학생 이름",
            placeholder="이름을 입력하세요",
            help="창업할 학생의 이름을 입력하세요",
            key="student_name_consulting"
        )

    with col_right:
        st.write("")  # 간격 조정

    st.markdown("---")

    # 창업 유형 선택
    st.header("🎯 창업 유형 선택")

    business_types = {
        "🔨 뚝딱뚝딱 (제조/만들기)": {
            "cost_ratio": 0.60,
            "effort": 4,
            "description": "직접 만들어서 파는 사업 (예: 팔찌, 쿠키, 비누 등)",
            "key": "manufacturing"
        },
        "🏃 대신하기 (서비스/몸쓰기)": {
            "cost_ratio": 0.20,
            "effort": 5,
            "description": "대신 해주는 서비스 (예: 심부름, 신발끈 묶어주기, 청소 등)",
            "key": "service"
        },
        "🛒 골라오기 (유통/떼오기)": {
            "cost_ratio": 0.50,
            "effort": 3,
            "description": "물건을 사서 되파는 사업 (예: 문구류, 간식 등)",
            "key": "distribution"
        },
        "📚 알려주기 (지식/정보)": {
            "cost_ratio": 0.10,
            "effort": 2,
            "description": "지식이나 정보를 알려주는 사업 (예: 게임 공략법, 과외, 노하우 등)",
            "key": "knowledge"
        },
        "🎪 빌려주기 (대여/공유)": {
            "cost_ratio": 0.40,
            "effort": 1,
            "description": "물건을 빌려주는 사업 (예: 보드게임, 운동용품, 악기 등)",
            "key": "rental"
        },
        "⚙️ 직접 설정하기": {
            "cost_ratio": 0.50,
            "effort": 3,
            "description": "좋은 아이디어가 있다면 직접 설정해보세요!",
            "key": "custom"
        }
    }

    selected_business = st.radio(
        "어떤 사업을 하고 싶나요?",
        options=list(business_types.keys()),
        help="각 사업 유형마다 원가와 노력이 다릅니다"
    )

    st.info(f"💡 {business_types[selected_business]['description']}")
    
    # 직접 설정 모드 - placeholder를 사용하여 항상 같은 공간 차지
    custom_settings_placeholder = st.container()
    
    with custom_settings_placeholder:
        if business_types[selected_business]["key"] == "custom":
            st.markdown("---")
            st.subheader("⚙️ 세부 설정")
            
            custom_col1, custom_col2 = st.columns(2)
            
            with custom_col1:
                custom_cost_ratio = st.slider(
                    "💰 원가율 (%)",
                    min_value=5,
                    max_value=80,
                    value=50,
                    step=5,
                    help="기준 가격 대비 원가 비율 (높을수록 원가가 비쌈)",
                    key="custom_cost_slider"
                ) / 100
            
            with custom_col2:
                custom_effort = st.slider(
                    "🔥 노력/피로도",
                    min_value=1,
                    max_value=5,
                    value=3,
                    step=1,
                    help="사업의 힘든 정도 (1=매우 쉬움, 5=매우 힘듦)",
                    key="custom_effort_slider"
                )
            
            # 커스텀 값 적용
            business_types[selected_business]["cost_ratio"] = custom_cost_ratio
            business_types[selected_business]["effort"] = custom_effort

    st.markdown("---")

    # 상품 등급 선택
    st.header("⭐ 상품 등급 선택")

    grade_types = {
        "💚 일반형 (가성비)": {
            "multiplier": 0.8,
            "target": "🤏 짠물 고객",
            "description": "가격 대비 합리적인 상품",
            "key": "basic"
        },
        "💙 고급형 (퀄리티)": {
            "multiplier": 1.2,
            "target": "😊 일반 고객",
            "description": "품질이 좋은 프리미엄 상품",
            "key": "premium"
        },
        "💜 하이엔드 (명품)": {
            "multiplier": 1.6,
            "target": "🤑 큰손 고객",
            "description": "최고급 럭셔리 상품",
            "key": "luxury"
        }
    }

    selected_grade = st.radio(
        "어떤 등급의 상품을 만들까요?",
        options=list(grade_types.keys()),
        help="등급에 따라 원가와 타겟 고객이 달라집니다"
    )

    st.info(f"💡 {grade_types[selected_grade]['description']}")

    st.markdown("---")

    # 결과 계산 및 출력
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        submit_button = st.button("🎉 창업 컨설팅 결과 보기", type="primary", use_container_width=True, key="submit_consulting")
    
    with col_btn2:
        # 기존 학생인 경우 수정 버튼 표시
        if student_name and student_name in st.session_state.students:
            edit_button = st.button("✏️ 기존 정보 수정하기", type="secondary", use_container_width=True, key="edit_consulting")
        else:
            edit_button = False
    
    if submit_button or edit_button:
        if not student_name:
            st.error("⚠️ 학생 이름을 입력해주세요!")
        elif total_ratio != 100:
            st.error("⚠️ 사이드바에서 구매자 성향 비율을 100%로 맞춰주세요!")
        else:
            # 원가 계산
            avg_budget_per_person = total_money / total_buyers
            target_items_per_person = 4
            base_price = avg_budget_per_person / target_items_per_person
            
            # 유형별 원가 비율 적용
            business_cost_ratio = business_types[selected_business]["cost_ratio"]
            cost_before_grade = base_price * business_cost_ratio
            
            # 등급별 승수 적용
            grade_multiplier = grade_types[selected_grade]["multiplier"]
            recommended_cost = cost_before_grade * grade_multiplier
            
            # 랜덤성 ±10% 부여
            random_factor = random.uniform(0.9, 1.1)
            final_cost = recommended_cost * random_factor
            
            st.balloons()
            
            st.markdown("---")
            st.header(f"🎊 {student_name}님의 창업 컨설팅 결과")
            
            # 학생 데이터 저장 또는 업데이트
            is_update = student_name in st.session_state.students
            
            if is_update:
                st.info(f"✏️ {student_name}님의 정보가 수정되었습니다. 기존 판매 데이터는 유지됩니다.")
                # 기존 데이터 보존
                existing_rounds = st.session_state.students[student_name]["rounds"]
                existing_totals = {
                    "total_revenue": st.session_state.students[student_name]["total_revenue"],
                    "total_cost": st.session_state.students[student_name]["total_cost"],
                    "total_profit": st.session_state.students[student_name]["total_profit"]
                }
            
            # 학생 데이터 저장/업데이트
            st.session_state.students[student_name] = {
                "business_type": selected_business,
                "grade": selected_grade,
                "recommended_cost": final_cost,
                "rounds": existing_rounds if is_update else {
                    1: {"selling_price": 0, "quantity_sold": 0, "revenue": 0, "profit": 0, "cost": 0},
                    2: {"selling_price": 0, "quantity_sold": 0, "revenue": 0, "profit": 0, "cost": 0}
                },
                "total_revenue": existing_totals["total_revenue"] if is_update else 0,
                "total_profit": existing_totals["total_profit"] if is_update else 0,
                "total_cost": existing_totals["total_cost"] if is_update else 0
            }
            
            # 결과 출력
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 💰 추천 원가")
                st.markdown(f"# **{final_cost:,.0f}원**")
                st.caption(f"(기준가: {base_price:,.0f}원)")
            
            with col2:
                st.markdown("### 🔥 노력/피로도")
                effort_level = business_types[selected_business]["effort"]
                stars = "⭐" * effort_level + "☆" * (5 - effort_level)
                st.markdown(f"# {stars}")
                st.caption(f"{effort_level}/5점")
            
            with col3:
                st.markdown("### 🎯 타겟 고객")
                target_customer = grade_types[selected_grade]["target"]
                st.markdown(f"# {target_customer}")
                st.caption("이 고객을 공략하세요!")
            
            st.markdown("---")
            
            # 상세 분석
            st.subheader("📊 상세 분석")
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                st.markdown("#### 💡 사업 분석")
                st.write(f"**선택한 사업:** {selected_business}")
                st.write(f"**선택한 등급:** {selected_grade}")
                st.write(f"**원가율:** {business_cost_ratio * 100:.0f}%")
                st.write(f"**등급 승수:** {grade_multiplier}배")
                
            with analysis_col2:
                st.markdown("#### 💼 시장 정보")
                st.write(f"**시장 총액:** {total_money:,}원")
                st.write(f"**전체 구매자:** {total_buyers}명")
                st.write(f"**1인당 평균 예산:** {avg_budget_per_person:,.0f}원")
                st.write(f"**1인당 구매 목표:** {target_items_per_person}개")
            
            st.markdown("---")
            
            # 창업 조언
            st.subheader("🌟 창업 조언")
            
            advice_box = st.container()
            with advice_box:
                # 유형별 조언
                business_key = business_types[selected_business]["key"]
                if business_key == "service":
                    st.info("👍 **서비스업 팁:** 원가는 낮지만 체력 소모가 큽니다! 무리하지 말고 적정 가격을 받으세요.")
                elif business_key == "manufacturing":
                    st.info("👍 **제조업 팁:** 재료비가 많이 들어갑니다. 미리 재료를 충분히 준비하세요!")
                elif business_key == "distribution":
                    st.info("👍 **유통업 팁:** 어디서 얼마에 살지가 중요합니다. 발품을 팔아 좋은 곳을 찾아보세요!")
                elif business_key == "knowledge":
                    st.info("👍 **지식업 팁:** 원가가 거의 없지만, 내가 가진 지식이 정말 가치 있는지 확인하세요!")
                elif business_key == "rental":
                    st.info("👍 **대여업 팁:** 노력은 적지만 물건이 망가질 위험이 있습니다. 보증금을 받는 것도 고려해보세요!")
                elif business_key == "custom":
                    st.info("👍 **맞춤형 팁:** 자신만의 아이디어로 시장을 공략하세요! 원가와 노력을 잘 조절했다면 성공할 수 있습니다.")
                
                # 등급별 조언
                if grade_types[selected_grade]["key"] == "luxury":
                    st.warning("⚡ **하이엔드 전략:** 소수의 큰손을 공략하세요! 품질과 희소성이 중요합니다.")
                elif grade_types[selected_grade]["key"] == "premium":
                    st.success("✨ **고급형 전략:** 가장 무난한 선택입니다. 일반 고객들이 많으니 꾸준히 팔 수 있어요!")
                else:  # basic
                    st.success("💪 **일반형 전략:** 많은 양을 팔아야 합니다! 속도와 효율이 중요해요.")
            
            st.markdown("---")
            
            # 가격 책정 가이드
            st.subheader("💵 권장 판매가 가이드")
            
            min_price = final_cost * 1.2  # 최소 20% 마진
            target_price = final_cost * 1.5  # 목표 50% 마진
            max_price = final_cost * 2.0  # 최대 100% 마진
            
            price_col1, price_col2, price_col3 = st.columns(3)
            
            with price_col1:
                st.metric("🥉 최소가", f"{min_price:,.0f}원", "20% 마진")
            with price_col2:
                st.metric("🥈 권장가", f"{target_price:,.0f}원", "50% 마진", delta_color="normal")
            with price_col3:
                st.metric("🥇 최대가", f"{max_price:,.0f}원", "100% 마진", delta_color="inverse")
            
            st.success("💡 **다음 단계:** '판매 관리' 탭에서 실제 판매 결과를 입력하세요!")

# ===== TAB 2: 판매 관리 =====
with tab2:
    st.header("💼 판매 관리 시스템")
    
    if len(st.session_state.students) == 0:
        st.warning("⚠️ 먼저 '창업 컨설팅' 탭에서 학생 정보를 등록해주세요!")
    else:
        st.info(f"🎯 현재 진행 중: **{st.session_state.current_round}라운드**")
        
        # 학생 선택
        selected_student = st.selectbox(
            "👨‍🎓 학생 선택",
            options=list(st.session_state.students.keys()),
            help="판매 결과를 입력할 학생을 선택하세요"
        )
        
        if selected_student:
            student_data = st.session_state.students[selected_student]
            
            st.markdown("---")
            
            # 학생 정보 요약
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏪 사업 유형", student_data["business_type"])
            with col2:
                st.metric("⭐ 상품 등급", student_data["grade"])
            with col3:
                st.metric("💰 추천 원가", f"{student_data['recommended_cost']:,.0f}원")
            
            st.markdown("---")
            
            # 라운드별 판매 입력
            st.subheader(f"📝 {st.session_state.current_round}라운드 판매 입력")
            
            round_data = student_data["rounds"][st.session_state.current_round]
            
            input_col1, input_col2 = st.columns(2)
            
            with input_col1:
                selling_price = st.number_input(
                    "💵 판매 단가 (원)",
                    min_value=0,
                    value=int(round_data["selling_price"]) if round_data["selling_price"] > 0 else int(student_data['recommended_cost'] * 1.5),
                    step=100,
                    help="한 개당 판매 가격을 입력하세요",
                    key=f"price_{selected_student}_{st.session_state.current_round}"
                )
            
            with input_col2:
                quantity_sold = st.number_input(
                    "📦 판매 수량 (개)",
                    min_value=0,
                    value=int(round_data["quantity_sold"]),
                    step=1,
                    help="실제 판매한 개수를 입력하세요",
                    key=f"quantity_{selected_student}_{st.session_state.current_round}"
                )
            
            # 실시간 계산
            revenue = selling_price * quantity_sold
            total_cost = student_data['recommended_cost'] * quantity_sold
            profit = revenue - total_cost
            margin_rate = (profit / revenue * 100) if revenue > 0 else 0
            
            st.markdown("---")
            
            # 손익 계산 결과
            st.subheader("📊 손익 계산 결과")
            
            result_col1, result_col2, result_col3, result_col4 = st.columns(4)
            
            with result_col1:
                st.metric("💰 매출액", f"{revenue:,.0f}원", help="판매가 × 판매량")
            
            with result_col2:
                st.metric("💸 총 원가", f"{total_cost:,.0f}원", help="원가 × 판매량")
            
            with result_col3:
                profit_delta = "🟢 흑자" if profit >= 0 else "🔴 적자"
                st.metric("💎 순이익", f"{profit:,.0f}원", profit_delta)
            
            with result_col4:
                st.metric("📈 마진율", f"{margin_rate:.1f}%", help="(순이익 ÷ 매출) × 100")
            
            # 저장 버튼
            if st.button("💾 판매 결과 저장", type="primary", use_container_width=True):
                # 라운드 데이터 저장
                student_data["rounds"][st.session_state.current_round] = {
                    "selling_price": selling_price,
                    "quantity_sold": quantity_sold,
                    "revenue": revenue,
                    "profit": profit,
                    "cost": total_cost
                }
                
                # 총합 계산
                total_revenue = sum(r["revenue"] for r in student_data["rounds"].values())
                total_cost_sum = sum(r["cost"] for r in student_data["rounds"].values())
                total_profit = sum(r["profit"] for r in student_data["rounds"].values())
                
                student_data["total_revenue"] = total_revenue
                student_data["total_cost"] = total_cost_sum
                student_data["total_profit"] = total_profit
                
                st.success(f"✅ {selected_student}님의 {st.session_state.current_round}라운드 데이터가 저장되었습니다!")
                st.balloons()
            
            # 누적 현황
            if student_data["total_revenue"] > 0:
                st.markdown("---")
                st.subheader("📈 누적 현황")
                
                cumul_col1, cumul_col2, cumul_col3 = st.columns(3)
                
                with cumul_col1:
                    st.metric("💰 총 매출", f"{student_data['total_revenue']:,.0f}원")
                
                with cumul_col2:
                    st.metric("💸 총 원가", f"{student_data['total_cost']:,.0f}원")
                
                with cumul_col3:
                    profit_emoji = "🟢" if student_data['total_profit'] >= 0 else "🔴"
                    st.metric("💎 총 순이익", f"{student_data['total_profit']:,.0f}원", f"{profit_emoji}")
                
                # 라운드별 비교
                if student_data["rounds"][1]["revenue"] > 0 and student_data["rounds"][2]["revenue"] > 0:
                    st.markdown("#### 🔄 라운드별 비교")
                    comparison_df = pd.DataFrame({
                        "라운드": ["1라운드", "2라운드"],
                        "판매가": [student_data["rounds"][1]["selling_price"], student_data["rounds"][2]["selling_price"]],
                        "판매량": [student_data["rounds"][1]["quantity_sold"], student_data["rounds"][2]["quantity_sold"]],
                        "매출": [student_data["rounds"][1]["revenue"], student_data["rounds"][2]["revenue"]],
                        "순이익": [student_data["rounds"][1]["profit"], student_data["rounds"][2]["profit"]]
                    })
                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# ===== TAB 3: 장사의신 대시보드 =====
with tab3:
    st.header("📊 장사의신 대시보드")
    
    if len(st.session_state.students) == 0:
        st.warning("⚠️ 아직 등록된 학생이 없습니다!")
    else:
        # 판매 데이터가 있는 학생만 필터링
        students_with_sales = {
            name: data for name, data in st.session_state.students.items()
            if data["total_revenue"] > 0
        }
        
        if len(students_with_sales) == 0:
            st.info("ℹ️ 아직 판매 데이터가 입력되지 않았습니다. '판매 관리' 탭에서 데이터를 입력해주세요!")
        else:
            # 매출 vs 수익 전환 버튼
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                show_revenue = st.button("💰 매출 순위 보기", type="primary", use_container_width=True)
            
            with col_btn2:
                show_profit = st.button("💎 수익 순위 보기", type="secondary", use_container_width=True)
            
            st.markdown("---")
            
            # 매출 순위 표시
            if show_revenue:
                st.subheader("💰 매출 순위")
                
                # 매출 기준 정렬
                revenue_ranking = sorted(
                    students_with_sales.items(),
                    key=lambda x: x[1]["total_revenue"],
                    reverse=True
                )
                
                # 순위 표시
                for idx, (name, data) in enumerate(revenue_ranking, 1):
                    if idx == 1:
                        medal = "🥇"
                    elif idx == 2:
                        medal = "🥈"
                    elif idx == 3:
                        medal = "🥉"
                    else:
                        medal = f"{idx}위"
                    
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                        with col1:
                            st.markdown(f"### {medal}")
                        with col2:
                            st.markdown(f"**{name}**")
                            st.caption(f"{data['business_type'][:15]}")
                        with col3:
                            st.metric("💰 매출", f"{data['total_revenue']:,.0f}원")
                        with col4:
                            total_qty = sum(r["quantity_sold"] for r in data["rounds"].values())
                            st.metric("📦 판매량", f"{total_qty}개")
                    
                    st.markdown("---")
            
            # 수익 순위 표시 (진짜 1등!)
            if show_profit:
                st.balloons()
                st.subheader("💎 수익 순위")
                
                # 수익 기준 정렬
                profit_ranking = sorted(
                    students_with_sales.items(),
                    key=lambda x: x[1]["total_profit"],
                    reverse=True
                )
                
                # 매출 순위와 비교
                revenue_ranking_names = [name for name, _ in sorted(
                    students_with_sales.items(),
                    key=lambda x: x[1]["total_revenue"],
                    reverse=True
                )]
                
                # 순위 표시
                for idx, (name, data) in enumerate(profit_ranking, 1):
                    if idx == 1:
                        medal = "👑"
                        st.markdown("### 🎉 진짜 1등! 🎉")
                    elif idx == 2:
                        medal = "🥈"
                    elif idx == 3:
                        medal = "🥉"
                    else:
                        medal = f"{idx}위"
                    
                    # 매출 순위와 비교
                    revenue_rank = revenue_ranking_names.index(name) + 1
                    rank_change = revenue_rank - idx
                    
                    if rank_change > 0:
                        rank_change_text = f"⬆️ {rank_change}계단 상승!"
                    elif rank_change < 0:
                        rank_change_text = f"⬇️ {abs(rank_change)}계단 하락"
                    else:
                        rank_change_text = "➡️ 순위 유지"
                    
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
                        with col1:
                            st.markdown(f"### {medal}")
                        with col2:
                            st.markdown(f"**{name}**")
                            st.caption(f"{data['business_type'][:15]}")
                        with col3:
                            st.metric("💎 순이익", f"{data['total_profit']:,.0f}원")
                        with col4:
                            margin_rate = (data['total_profit'] / data['total_revenue'] * 100) if data['total_revenue'] > 0 else 0
                            st.metric("📈 마진율", f"{margin_rate:.1f}%")
                        with col5:
                            st.markdown(f"**{rank_change_text}**")
                            st.caption(f"(매출 {revenue_rank}위)")
                    
                    if idx == 1:
                        st.success(f"🎊 {name}님이 가장 효율적으로 사업을 운영했습니다!")
                    
                    st.markdown("---")
            
            # 기본 전체 현황 (버튼 클릭 전)
            if not show_revenue and not show_profit:
                st.subheader("📊 전체 현황")
                st.info("👆 위의 버튼을 눌러서 순위를 확인하세요!")
                
                # 전체 데이터 테이블
                leaderboard_data = []
                for name, data in students_with_sales.items():
                    total_qty = sum(r["quantity_sold"] for r in data["rounds"].values())
                    margin_rate = (data['total_profit'] / data['total_revenue'] * 100) if data['total_revenue'] > 0 else 0
                    
                    leaderboard_data.append({
                        "이름": name,
                        "사업유형": data["business_type"][:10],
                        "총 판매량": f"{total_qty}개",
                        "총 매출": f"{data['total_revenue']:,.0f}원",
                        "총 원가": f"{data['total_cost']:,.0f}원",
                        "순이익": f"{data['total_profit']:,.0f}원",
                        "마진율": f"{margin_rate:.1f}%"
                    })
                
                df = pd.DataFrame(leaderboard_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # 통계
                st.markdown("---")
                st.subheader("📈 전체 통계")
                
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    total_students = len(students_with_sales)
                    st.metric("👥 참여 학생", f"{total_students}명")
                
                with stat_col2:
                    total_market_revenue = sum(d["total_revenue"] for d in students_with_sales.values())
                    st.metric("💰 전체 시장 매출", f"{total_market_revenue:,.0f}원")
                
                with stat_col3:
                    total_market_profit = sum(d["total_profit"] for d in students_with_sales.values())
                    st.metric("💎 전체 시장 수익", f"{total_market_profit:,.0f}원")
                
                with stat_col4:
                    avg_margin = (total_market_profit / total_market_revenue * 100) if total_market_revenue > 0 else 0
                    st.metric("📊 평균 마진율", f"{avg_margin:.1f}%")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🏪 장사의 신 - 경제 교육 게임 v2.0 | Made with ❤️ for Students</p>
</div>
""", unsafe_allow_html=True)
