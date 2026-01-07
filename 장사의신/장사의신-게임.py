import streamlit as st
import random
import pandas as pd
from datetime import datetime
from openai import OpenAI
import os
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# 페이지 설정
st.set_page_config(
    page_title="🏪 장사의 신 게임 관리 시스템 V2",
    page_icon="💰",
    layout="wide"
)

# ==================== 상수 정의 ====================

# 초기 자본금
INITIAL_CAPITAL = 500000

# 유형별 밸런스 설정 (최종 고도화 버전)
BUSINESS_TYPES = {
    "🛒 골라오기 (유통)": {
        "cost": 20000,  # 원가
        "recommended_price": 40000,  # 추천 판매가
        "margin_rate": 0.50,  # 마진율 50%
        "max_sales_per_10min": None,  # 무제한
        "description": "물건을 사서 되파는 사업 (재고 부담, 회전율 승부)",
        "target": "짠물 + 일반",
        "strategy": "많이 팔아서 회전율로 승부. 재고 관리가 핵심!",
        "key": "distribution"
    },
    "🔨 뚝딱뚝딱 (제조)": {
        "cost": 60000,
        "recommended_price": 120000,
        "margin_rate": 0.50,
        "max_sales_per_10min": 8,  # 시간 제약
        "description": "직접 만들어서 파는 사업 (시간 제약, 장인정신)",
        "target": "일반 + 큰손",
        "strategy": "만들 수 있는 만큼만 재료 구매. 고품질 프리미엄!",
        "key": "manufacturing"
    },
    "🏃 대신하기 (서비스)": {
        "cost": 30000,
        "recommended_price": 150000,
        "margin_rate": 0.80,  # 고마진
        "max_sales_per_10min": 5,  # 시간 제약 큼
        "description": "대신 해주는 서비스 (고마진, 수량 제한)",
        "target": "큰손",
        "strategy": "적게 팔아도 마진이 높다. 큰손 타겟!",
        "key": "service"
    },
    "📚 알려주기 (지식)": {
        "cost": 20000,
        "recommended_price": 80000,
        "margin_rate": 0.75,
        "max_sales_per_10min": 10,
        "description": "지식/정보를 알려주는 사업 (저원가, 균형형)",
        "target": "일반",
        "strategy": "원가 부담 없고 마진 높음. 수요 예측이 관건!",
        "key": "knowledge"
    },
    "🎪 빌려주기 (대여)": {
        "cost": 70000,
        "recommended_price": 120000,
        "margin_rate": 0.43,  # 1라운드 / 2라운드는 100%
        "max_sales_per_10min": 6,  # 보유 물건 개수 제한
        "description": "물건을 빌려주는 사업 (장기 투자, 2라운드 대박)",
        "target": "일반 + 큰손",
        "strategy": "1라운드 원금 회수, 2라운드 원가 0원으로 대박!",
        "key": "rental",
        "special": "2라운드 재사용 가능"
    }
}

# 구매자 타입별 구매 조건 (원가 배수 기준)
BUYER_TYPES = {
    "큰손": {"ratio": 0.20, "max_price_multiplier": 2.5, "description": "품질 중시, 비싸도 구매"},
    "일반": {"ratio": 0.50, "max_price_multiplier": 2.0, "description": "가성비 중시, 적정가 선호"},
    "짠물": {"ratio": 0.30, "max_price_multiplier": 1.5, "description": "저가 선호, 싼 것만 구매"}
}

# ==================== Google Sheets 연결 ====================

@st.cache_resource
def get_google_sheets_client():
    """Google Sheets 클라이언트를 초기화합니다."""
    try:
        credentials_dict = None
        if "gcp_service_account" in st.secrets:
            credentials_dict = dict(st.secrets["gcp_service_account"])
        elif os.getenv("GOOGLE_CREDENTIALS"):
            credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        
        if credentials_dict:
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
            client = gspread.authorize(credentials)
            return client
        return None
    except Exception as e:
        st.error(f"Google Sheets 연결 오류: {str(e)}")
        return None

@st.cache_resource(ttl=600)
def get_or_create_spreadsheet():
    """스프레드시트를 가져오거나 생성합니다."""
    client = get_google_sheets_client()
    if not client:
        return None, None
    
    try:
        spreadsheet_url = st.secrets.get("spreadsheet_url", "")
        if spreadsheet_url:
            spreadsheet = client.open_by_url(spreadsheet_url)
        else:
            spreadsheet = client.create("장사의신_게임_데이터_V2")
            st.info(f"📝 새 스프레드시트가 생성되었습니다: {spreadsheet.url}")
        
        try:
            worksheet = spreadsheet.worksheet("학생데이터")
        except:
            worksheet = spreadsheet.add_worksheet(title="학생데이터", rows="100", cols="25")
            worksheet.update('A1:U1', [[
                '이름', '사업유형', '원가', '초기자본', '구매수량', '재고',
                '1R_판매가', '1R_판매량', '1R_매출', '1R_원가총액', '1R_순이익',
                '2R_판매가', '2R_판매량', '2R_매출', '2R_원가총액', '2R_순이익',
                '총매출', '총원가', '총순이익', '최종자본', '실물소지금'
            ]])
        
        return spreadsheet, worksheet
    except Exception as e:
        st.error(f"스프레드시트 접근 오류: {str(e)}")
        return None, None

@st.cache_resource(ttl=600)
def get_or_create_market_settings_sheet(_spreadsheet):
    """시장 설정 시트를 가져오거나 생성합니다."""
    if not _spreadsheet:
        return None
    
    try:
        try:
            settings_sheet = _spreadsheet.worksheet("시장설정")
        except:
            settings_sheet = _spreadsheet.add_worksheet(title="시장설정", rows="10", cols="2")
            settings_sheet.update('A1:B7', [
                ['설정항목', '값'],
                ['시장_총_화폐량', '10000000'],
                ['전체_구매자_수', '10'],
                ['게임_모드', '전략 모드'],
                ['큰손_비율', '20'],
                ['일반_비율', '50'],
                ['짠물_비율', '30']
            ])
        return settings_sheet
    except Exception as e:
        st.error(f"시장설정 시트 오류: {str(e)}")
        return None

def load_market_settings(settings_sheet):
    """시장 설정을 불러옵니다."""
    default_settings = {
        'total_money': 10000000,
        'total_buyers': 10,
        'game_mode': '전략 모드',
        'big_spender_ratio': 20,
        'normal_ratio': 50,
        'frugal_ratio': 30
    }
    
    if not settings_sheet:
        return default_settings
    
    try:
        all_values = settings_sheet.get_all_values()
        settings = {}
        
        for row in all_values[1:]:
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                
                if key == '시장_총_화폐량':
                    settings['total_money'] = int(value)
                elif key == '전체_구매자_수':
                    settings['total_buyers'] = int(value)
                elif key == '게임_모드':
                    settings['game_mode'] = value
                elif key == '큰손_비율':
                    settings['big_spender_ratio'] = int(value)
                elif key == '일반_비율':
                    settings['normal_ratio'] = int(value)
                elif key == '짠물_비율':
                    settings['frugal_ratio'] = int(value)
        
        if not settings or 'total_money' not in settings:
            return default_settings
            
        return settings
    except Exception as e:
        st.error(f"설정 로드 오류: {str(e)}")
        return default_settings

def save_market_settings(settings_sheet, settings):
    """시장 설정을 저장합니다."""
    if not settings_sheet:
        return False
    
    try:
        settings_sheet.update('B2:B7', [
            [str(settings['total_money'])],
            [str(settings['total_buyers'])],
            [settings['game_mode']],
            [str(settings['big_spender_ratio'])],
            [str(settings['normal_ratio'])],
            [str(settings['frugal_ratio'])]
        ])
        time.sleep(1.0)
        return True
    except Exception as e:
        st.error(f"설정 저장 오류: {str(e)}")
        return False

def check_admin_password(password):
    """관리자 비밀번호 확인"""
    try:
        admin_password = st.secrets.get("admin_password", "admin2026")
    except:
        admin_password = "admin2026"
    return password == admin_password

# ==================== 초기화 ====================

# Google Sheets 연결
if 'worksheet' not in st.session_state:
    spreadsheet, worksheet = get_or_create_spreadsheet()
    st.session_state.worksheet = worksheet
    st.session_state.spreadsheet = spreadsheet
    st.session_state.settings_sheet = get_or_create_market_settings_sheet(spreadsheet)

# Google Sheets 사용 여부
if 'use_google_sheets' not in st.session_state:
    st.session_state.use_google_sheets = st.session_state.worksheet is not None

# 시장 설정 로드 (30초마다 갱신)
current_time = time.time()
settings_reload_interval = 30

if 'market_settings' not in st.session_state or \
   (st.session_state.use_google_sheets and 
    ('last_settings_load' not in st.session_state or 
     (current_time - st.session_state.get('last_settings_load', 0)) > settings_reload_interval)):
    
    if st.session_state.use_google_sheets and hasattr(st.session_state, 'settings_sheet'):
        st.session_state.market_settings = load_market_settings(st.session_state.settings_sheet)
        st.session_state.last_settings_load = current_time
    else:
        if 'market_settings' not in st.session_state:
            st.session_state.market_settings = {
                'total_money': 10000000,
                'total_buyers': 10,
                'game_mode': '전략 모드',
                'big_spender_ratio': 20,
                'normal_ratio': 50,
                'frugal_ratio': 30
            }

# 학생 데이터 초기화
if 'students' not in st.session_state:
    st.session_state.students = {}

# 관리자 모드
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# 라운드
if 'current_round' not in st.session_state:
    st.session_state.current_round = 1

# 최종 공개 여부
if 'final_reveal' not in st.session_state:
    st.session_state.final_reveal = False

# ==================== 메인 UI ====================

st.title("🏪 장사의 신 게임 관리 시스템 V2")
st.markdown("### 💡 실전 창업 시뮬레이션 게임")
st.markdown("---")

# 사이드바: 시장 정보
st.sidebar.header("🏪 장사의 신")

# 관리자 로그인
st.sidebar.markdown("### 🔐 관리자 로그인")
admin_password_input = st.sidebar.text_input(
    "비밀번호",
    type="password",
    placeholder="관리자 비밀번호 입력",
    key="admin_password"
)

if admin_password_input:
    if check_admin_password(admin_password_input):
        st.session_state.is_admin = True
        st.sidebar.success("✅ 관리자 모드")
    else:
        st.session_state.is_admin = False
        st.sidebar.error("❌ 비밀번호 오류")
else:
    if st.session_state.is_admin:
        st.sidebar.info("👥 학생 모드로 전환됨")

st.sidebar.markdown("---")

# 시장 정보 표시
st.sidebar.markdown("### 📊 시장 정보")
total_money = st.session_state.market_settings.get('total_money', 10000000)
total_buyers = st.session_state.market_settings.get('total_buyers', 10)
game_mode = st.session_state.market_settings.get('game_mode', '전략 모드')

if st.session_state.is_admin:
    st.sidebar.markdown("#### 🎛️ 시장 설정 (관리자)")
    
    new_total_money = st.sidebar.number_input(
        "💰 시장 총 화폐량",
        min_value=1000000,
        max_value=100000000,
        value=total_money,
        step=1000000
    )
    
    new_total_buyers = st.sidebar.number_input(
        "👥 전체 구매자 수",
        min_value=5,
        max_value=50,
        value=total_buyers,
        step=1
    )
    
    if st.sidebar.button("💾 설정 저장"):
        new_settings = {
            'total_money': new_total_money,
            'total_buyers': new_total_buyers,
            'game_mode': game_mode,
            'big_spender_ratio': 20,
            'normal_ratio': 50,
            'frugal_ratio': 30
        }
        st.session_state.market_settings = new_settings
        
        if st.session_state.use_google_sheets and hasattr(st.session_state, 'settings_sheet'):
            if save_market_settings(st.session_state.settings_sheet, new_settings):
                st.sidebar.success("✅ 설정 저장됨!")
                st.session_state.last_settings_load = time.time()
        st.rerun()
else:
    st.sidebar.info(f"""
    **💰 시장 총 화폐량**: {total_money:,}원  
    **👥 전체 구매자 수**: {total_buyers}명  
    **🎮 게임 모드**: {game_mode}
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💵 초기 자본금")
st.sidebar.success(f"**{INITIAL_CAPITAL:,}원**")
st.sidebar.caption("모든 학생 동일")

# ==================== 메인 탭 ====================

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 창업 컨설팅", 
    "💼 판매 관리", 
    "📊 대시보드",
    "🎯 도구"
])

# ==================== TAB 1: 창업 컨설팅 ====================
with tab1:
    st.header("👨‍🎓 창업 컨설팅")
    
    if not st.session_state.is_admin:
        st.warning("⚠️ 관리자 로그인이 필요합니다.")
    else:
        st.subheader("1️⃣ 학생 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input(
                "📝 학생 이름",
                placeholder="이름 입력",
                key="student_name_input"
            )
        
        with col2:
            st.write("")  # 간격
        
        st.markdown("---")
        
        st.subheader("2️⃣ 창업 유형 선택")
        
        selected_business = st.selectbox(
            "사업 유형",
            options=list(BUSINESS_TYPES.keys()),
            help="학생의 아이디어에 맞는 유형 선택"
        )
        
        business_info = BUSINESS_TYPES[selected_business]
        
        # 유형 정보 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 기본 원가", f"{business_info['cost']:,}원")
        with col2:
            st.metric("💵 추천 판매가", f"{business_info['recommended_price']:,}원")
        with col3:
            margin = business_info['margin_rate'] * 100
            st.metric("📊 마진율", f"{margin:.0f}%")
        with col4:
            if business_info['max_sales_per_10min']:
                st.metric("⏱️ 10분 제한", f"{business_info['max_sales_per_10min']}개")
            else:
                st.metric("⏱️ 10분 제한", "무제한")
        
        st.info(f"**📝 설명**: {business_info['description']}")
        st.success(f"**🎯 전략**: {business_info['strategy']}")
        
        st.markdown("---")
        
        st.subheader("3️⃣ 원가 조정 (관리자)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**AI 추천 원가**: {business_info['cost']:,}원")
        
        with col2:
            adjusted_cost = st.number_input(
                "최종 원가 설정",
                min_value=10000,
                max_value=500000,
                value=business_info['cost'],
                step=10000,
                help="게임 밸런스에 맞게 조정하세요",
                key="cost_adjustment"
            )
        
        if adjusted_cost != business_info['cost']:
            st.warning(f"⚠️ 원가 조정: {business_info['cost']:,}원 → {adjusted_cost:,}원")
        
        # 추천 판매가 자동 계산
        recommended_selling_price = int(adjusted_cost * 2.0)
        
        st.markdown("---")
        
        st.subheader("4️⃣ 학생 등록")
        
        if st.button("✅ 학생 등록하기", type="primary", key="register_student"):
            if not student_name:
                st.error("⚠️ 학생 이름을 입력하세요!")
            else:
                # 학생 데이터 생성
                st.session_state.students[student_name] = {
                    "business_type": selected_business,
                    "cost": adjusted_cost,
                    "recommended_price": recommended_selling_price,
                    "initial_capital": INITIAL_CAPITAL,
                    "purchased_quantity": 0,  # 아직 구매 안 함
                    "inventory": 0,
                    "rounds": {
                        1: {
                            "selling_price": 0,
                            "quantity_sold": 0,
                            "revenue": 0,
                            "cost_total": 0,
                            "profit": 0
                        },
                        2: {
                            "selling_price": 0,
                            "quantity_sold": 0,
                            "revenue": 0,
                            "cost_total": 0,
                            "profit": 0
                        }
                    },
                    "total_revenue": 0,
                    "total_cost": 0,
                    "total_profit": 0,
                    "final_capital": INITIAL_CAPITAL,  # 아직 변화 없음
                    "actual_money": 0  # 실물 소지금 (나중에 입력)
                }
                
                st.balloons()
                st.success(f"✅ {student_name}님이 등록되었습니다!")
                
                # 정보 카드 표시
                st.markdown("---")
                st.subheader(f"📋 {student_name}님 정보")
                
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.info(f"""
                    **🏪 사업 유형**  
                    {selected_business}
                    
                    **💰 설정 원가**  
                    {adjusted_cost:,}원/개
                    """)
                
                with info_col2:
                    st.success(f"""
                    **💵 초기 자본**  
                    {INITIAL_CAPITAL:,}원
                    
                    **📊 추천 판매가**  
                    {recommended_selling_price:,}원
                    """)
                
                with info_col3:
                    max_purchase = INITIAL_CAPITAL // adjusted_cost
                    st.warning(f"""
                    **🛒 최대 구매 가능**  
                    {max_purchase}개
                    
                    **🎯 타겟 고객**  
                    {business_info['target']}
                    """)
                
                st.markdown("---")
                st.markdown("### 📝 다음 단계")
                st.write("1. '💼 판매 관리' 탭으로 이동")
                st.write("2. 재고 구매 수량 입력")
                st.write("3. 판매 시작!")

# ==================== TAB 2: 판매 관리 ====================
with tab2:
    st.header("💼 판매 관리")
    
    if not st.session_state.students:
        st.info("👥 등록된 학생이 없습니다. '창업 컨설팅' 탭에서 학생을 먼저 등록하세요.")
    else:
        st.subheader("📋 등록된 학생 목록")
        
        for idx, (name, data) in enumerate(st.session_state.students.items(), 1):
            with st.expander(f"**{idx}. {name}** - {data['business_type']}", expanded=True):
                
                business_type_key = data['business_type']
                business_info = BUSINESS_TYPES[business_type_key]
                
                # 학생 정보 요약
                summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                
                with summary_col1:
                    st.metric("💰 원가", f"{data['cost']:,}원")
                with summary_col2:
                    st.metric("💵 초기 자본", f"{data['initial_capital']:,}원")
                with summary_col3:
                    st.metric("📦 재고", f"{data['inventory']}개")
                with summary_col4:
                    current_capital = data['final_capital']
                    st.metric("💳 현재 자본", f"{current_capital:,}원")
                
                st.markdown("---")
                
                # STEP 1: 재고 구매
                st.markdown("### 1️⃣ 재고 구매")
                
                if data['purchased_quantity'] == 0:
                    max_can_buy = data['initial_capital'] // data['cost']
                    
                    purchase_quantity = st.number_input(
                        f"{name} - 구매할 수량",
                        min_value=0,
                        max_value=max_can_buy,
                        value=0,
                        step=1,
                        key=f"purchase_{name}",
                        help=f"최대 {max_can_buy}개 구매 가능"
                    )
                    
                    if purchase_quantity > 0:
                        total_cost = purchase_quantity * data['cost']
                        remaining_capital = data['initial_capital'] - total_cost
                        
                        st.info(f"""
                        💰 구매 비용: {total_cost:,}원  
                        💳 남은 자본: {remaining_capital:,}원
                        """)
                        
                        if st.button(f"✅ 구매 확정", key=f"confirm_purchase_{name}"):
                            st.session_state.students[name]['purchased_quantity'] = purchase_quantity
                            st.session_state.students[name]['inventory'] = purchase_quantity
                            st.session_state.students[name]['final_capital'] = remaining_capital
                            st.success(f"✅ {purchase_quantity}개 구매 완료!")
                            st.rerun()
                    else:
                        st.warning("⚠️ 구매 수량을 입력하세요")
                else:
                    st.success(f"✅ 이미 구매 완료: {data['purchased_quantity']}개")
                
                st.markdown("---")
                
                # STEP 2: 판매 입력
                st.markdown(f"### 2️⃣ {st.session_state.current_round}라운드 판매")
                
                round_data = data['rounds'][st.session_state.current_round]
                
                if data['inventory'] == 0:
                    st.warning("⚠️ 재고가 없습니다. 먼저 재고를 구매하세요.")
                else:
                    sell_col1, sell_col2 = st.columns(2)
                    
                    with sell_col1:
                        selling_price = st.number_input(
                            "판매가 (원)",
                            min_value=0,
                            max_value=1000000,
                            value=data['recommended_price'],
                            step=10000,
                            key=f"price_{name}_r{st.session_state.current_round}"
                        )
                    
                    with sell_col2:
                        max_sellable = data['inventory']
                        if business_info['max_sales_per_10min']:
                            max_sellable = min(max_sellable, business_info['max_sales_per_10min'])
                        
                        quantity_sold = st.number_input(
                            f"판매 수량 (최대 {max_sellable}개)",
                            min_value=0,
                            max_value=max_sellable,
                            value=0,
                            step=1,
                            key=f"sold_{name}_r{st.session_state.current_round}"
                        )
                    
                    if quantity_sold > 0:
                        revenue = selling_price * quantity_sold
                        cost_total = data['cost'] * quantity_sold
                        profit = revenue - cost_total
                        
                        result_col1, result_col2, result_col3 = st.columns(3)
                        
                        with result_col1:
                            st.metric("💰 매출", f"{revenue:,}원")
                        with result_col2:
                            st.metric("💸 원가", f"{cost_total:,}원")
                        with result_col3:
                            st.metric("💎 순이익", f"{profit:,}원", delta=f"{profit:,}원")
                        
                        if st.button(f"✅ 판매 기록", key=f"record_{name}_r{st.session_state.current_round}"):
                            # 데이터 업데이트
                            st.session_state.students[name]['rounds'][st.session_state.current_round] = {
                                "selling_price": selling_price,
                                "quantity_sold": quantity_sold,
                                "revenue": revenue,
                                "cost_total": cost_total,
                                "profit": profit
                            }
                            
                            # 재고 차감
                            st.session_state.students[name]['inventory'] -= quantity_sold
                            
                            # 자본 업데이트 (판매 수입 추가)
                            st.session_state.students[name]['final_capital'] += revenue
                            
                            # 총계 업데이트
                            st.session_state.students[name]['total_revenue'] = sum(
                                st.session_state.students[name]['rounds'][r]['revenue'] 
                                for r in [1, 2]
                            )
                            st.session_state.students[name]['total_cost'] = sum(
                                st.session_state.students[name]['rounds'][r]['cost_total'] 
                                for r in [1, 2]
                            )
                            st.session_state.students[name]['total_profit'] = sum(
                                st.session_state.students[name]['rounds'][r]['profit'] 
                                for r in [1, 2]
                            )
                            
                            st.success(f"✅ {quantity_sold}개 판매 기록 완료!")
                            st.balloons()
                            st.rerun()
                
                st.markdown("---")
                
                # 현재 상태
                st.markdown("### 📊 현재 상태")
                
                status_col1, status_col2, status_col3, status_col4 = st.columns(4)
                
                with status_col1:
                    st.info(f"**남은 재고**\n\n{data['inventory']}개")
                with status_col2:
                    st.info(f"**총 매출**\n\n{data['total_revenue']:,}원")
                with status_col3:
                    st.info(f"**총 순이익**\n\n{data['total_profit']:,}원")
                with status_col4:
                    st.info(f"**현재 자본**\n\n{data['final_capital']:,}원")

        st.markdown("---")
        
        # 라운드 관리
        if st.session_state.is_admin:
            st.subheader("🎮 라운드 관리 (관리자)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**현재 라운드**: {st.session_state.current_round}")
            
            with col2:
                if st.button("⏭️ 다음 라운드"):
                    if st.session_state.current_round < 2:
                        st.session_state.current_round += 1
                        st.success(f"✅ {st.session_state.current_round}라운드 시작!")
                        st.rerun()
            
            with col3:
                if st.button("🔄 라운드 초기화"):
                    st.session_state.current_round = 1
                    st.rerun()

# ==================== TAB 3: 대시보드 ====================
with tab3:
    st.header("📊 대시보드")
    
    if not st.session_state.students:
        st.info("👥 등록된 학생이 없습니다.")
    else:
        # 매출 vs 순이익 비교
        st.subheader("🏆 순위 공개")
        
        rank_tab1, rank_tab2 = st.tabs(["💰 매출 순위", "💎 순이익 순위"])
        
        with rank_tab1:
            st.markdown("### 💰 매출 순위")
            
            revenue_ranking = sorted(
                st.session_state.students.items(),
                key=lambda x: x[1]['total_revenue'],
                reverse=True
            )
            
            for rank, (name, data) in enumerate(revenue_ranking, 1):
                medal = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}위"
                
                col1, col2, col3 = st.columns([1, 3, 2])
                
                with col1:
                    st.markdown(f"## {medal}")
                with col2:
                    st.markdown(f"### {name}")
                    st.caption(data['business_type'])
                with col3:
                    st.metric("매출", f"{data['total_revenue']:,}원")
        
        with rank_tab2:
            st.markdown("### 💎 순이익 순위")
            
            if st.session_state.is_admin:
                reveal_col1, reveal_col2 = st.columns([3, 1])
                
                with reveal_col1:
                    if not st.session_state.final_reveal:
                        st.warning("🔒 순이익 순위는 아직 공개되지 않았습니다.")
                
                with reveal_col2:
                    if st.button("🔓 순위 공개", type="primary"):
                        st.session_state.final_reveal = True
                        st.rerun()
            
            if st.session_state.final_reveal:
                profit_ranking = sorted(
                    st.session_state.students.items(),
                    key=lambda x: x[1]['total_profit'],
                    reverse=True
                )
                
                for rank, (name, data) in enumerate(profit_ranking, 1):
                    medal = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}위"
                    
                    # 매출 순위와 비교
                    revenue_rank = [n for n, d in revenue_ranking].index(name) + 1
                    if rank < revenue_rank:
                        trend = f"📈 {revenue_rank}위 → {rank}위 (역전!)"
                        color = "success"
                    elif rank > revenue_rank:
                        trend = f"📉 {revenue_rank}위 → {rank}위"
                        color = "error"
                    else:
                        trend = f"➡️ {rank}위 유지"
                        color = "info"
                    
                    col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"## {medal}")
                    with col2:
                        st.markdown(f"### {name}")
                        st.caption(data['business_type'])
                    with col3:
                        st.metric("순이익", f"{data['total_profit']:,}원")
                    with col4:
                        if color == "success":
                            st.success(trend)
                        elif color == "error":
                            st.error(trend)
                        else:
                            st.info(trend)
        
        st.markdown("---")
        
        # 상세 데이터
        st.subheader("📋 상세 데이터")
        
        df_data = []
        for name, data in st.session_state.students.items():
            df_data.append({
                "이름": name,
                "유형": data['business_type'],
                "원가": f"{data['cost']:,}원",
                "재고": f"{data['inventory']}개",
                "총매출": f"{data['total_revenue']:,}원",
                "총순이익": f"{data['total_profit']:,}원",
                "현재자본": f"{data['final_capital']:,}원"
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)

# ==================== TAB 4: 도구 ====================
with tab4:
    st.header("🎯 게임 도구")
    
    tool_tab1, tool_tab2, tool_tab3 = st.tabs([
        "💰 수익 시뮬레이터",
        "📋 구매자 가이드",
        "📊 학습 리포트"
    ])
    
    with tool_tab1:
        st.subheader("💰 수익 시뮬레이터")
        st.caption("판매가에 따른 예상 수익을 계산해보세요")
        
        if st.session_state.students:
            sim_student = st.selectbox(
                "학생 선택",
                list(st.session_state.students.keys()),
                key="sim_student"
            )
            
            if sim_student:
                student_data = st.session_state.students[sim_student]
                cost = student_data['cost']
                
                sim_col1, sim_col2 = st.columns(2)
                
                with sim_col1:
                    sim_price = st.number_input(
                        "판매가 설정",
                        min_value=0,
                        max_value=1000000,
                        value=student_data['recommended_price'],
                        step=10000,
                        key="sim_price"
                    )
                
                with sim_col2:
                    sim_quantity = st.number_input(
                        "예상 판매 수량",
                        min_value=0,
                        max_value=50,
                        value=10,
                        step=1,
                        key="sim_quantity"
                    )
                
                # 계산
                sim_margin = sim_price - cost
                sim_margin_rate = (sim_margin / sim_price * 100) if sim_price > 0 else 0
                sim_revenue = sim_price * sim_quantity
                sim_profit = sim_margin * sim_quantity
                
                # 결과
                st.markdown("---")
                st.markdown("### 📊 시뮬레이션 결과")
                
                result_col1, result_col2, result_col3, result_col4 = st.columns(4)
                
                with result_col1:
                    st.metric("개당 마진", f"{sim_margin:,}원")
                with result_col2:
                    st.metric("마진율", f"{sim_margin_rate:.1f}%")
                with result_col3:
                    st.metric("예상 매출", f"{sim_revenue:,}원")
                with result_col4:
                    st.metric("예상 순이익", f"{sim_profit:,}원")
                
                # 구매 가능 고객 분석
                st.markdown("---")
                st.markdown("### 👥 구매 가능 고객 분석")
                
                optimal_price = cost * 2.0
                price_ratio = sim_price / cost
                
                if price_ratio <= 1.5:
                    buyer_count = 10  # 모든 고객
                    st.success("💚 모든 고객 유형이 구매 가능합니다!")
                elif price_ratio <= 2.0:
                    buyer_count = 7  # 큰손 + 일반
                    st.info("💙 큰손 + 일반 고객이 구매 가능합니다")
                elif price_ratio <= 2.5:
                    buyer_count = 2  # 큰손만
                    st.warning("💛 큰손만 구매 가능합니다")
                else:
                    buyer_count = 0
                    st.error("💔 가격이 너무 높아 구매가 어렵습니다")
                
                st.caption(f"예상 구매 고객: {buyer_count}명 / {st.session_state.market_settings.get('total_buyers', 10)}명")
    
    with tool_tab2:
        st.subheader("📋 구매자 가이드 생성")
        st.caption("선생님들이 구매자 역할을 할 때 참고할 가이드를 생성합니다")
        
        if st.button("📄 구매자 가이드 생성", type="primary"):
            st.markdown("---")
            st.markdown("## 👥 구매자 역할 가이드")
            
            total_buyers = st.session_state.market_settings.get('total_buyers', 10)
            big_spender_count = int(total_buyers * 0.2)
            normal_count = int(total_buyers * 0.5)
            frugal_count = total_buyers - big_spender_count - normal_count
            
            st.info(f"""
            **총 구매자**: {total_buyers}명  
            - 큰손: {big_spender_count}명 (20%)  
            - 일반: {normal_count}명 (50%)  
            - 짠물: {frugal_count}명 (30%)
            """)
            
            st.markdown("---")
            
            # 큰손
            st.markdown("### 💎 큰손 구매자")
            for i in range(big_spender_count):
                with st.expander(f"큰손 #{i+1}"):
                    st.write(f"""
                    **💰 예산**: 1,000,000원  
                    **🎯 특성**: 품질 중시, 비싸도 괜찮음  
                    **📋 구매 조건**: 원가의 2.5배 이하면 구매  
                    **💬 말투**: "이거 품질 좋아 보이네요!", "조금 비싸도 괜찮아요"
                    """)
            
            # 일반
            st.markdown("### 😊 일반 구매자")
            for i in range(normal_count):
                with st.expander(f"일반 #{i+1}"):
                    st.write(f"""
                    **💰 예산**: 1,000,000원  
                    **🎯 특성**: 가성비 중시, 적당한 가격 선호  
                    **📋 구매 조건**: 원가의 2.0배 이하면 구매  
                    **💬 말투**: "가격이 적당하네요", "이 정도면 괜찮을 것 같아요"
                    """)
            
            # 짠물
            st.markdown("### 🤏 짠물 구매자")
            for i in range(frugal_count):
                with st.expander(f"짠물 #{i+1}"):
                    st.write(f"""
                    **💰 예산**: 1,000,000원  
                    **🎯 특성**: 저가 선호, 무조건 싼 것  
                    **📋 구매 조건**: 원가의 1.5배 이하면 구매  
                    **💬 말투**: "더 싼 거 없어요?", "너무 비싼데..."
                    """)
    
    with tool_tab3:
        st.subheader("📊 학습 리포트")
        st.caption("학생별 성과와 학습 포인트를 요약합니다")
        
        if st.button("📄 리포트 생성", type="primary"):
            st.markdown("---")
            
            for name, data in st.session_state.students.items():
                st.markdown(f"## 🎓 {name}님 학습 리포트")
                
                report_col1, report_col2 = st.columns(2)
                
                with report_col1:
                    st.markdown("### 📋 기본 정보")
                    st.write(f"**유형**: {data['business_type']}")
                    st.write(f"**원가**: {data['cost']:,}원")
                    st.write(f"**초기 자본**: {data['initial_capital']:,}원")
                
                with report_col2:
                    st.markdown("### 💰 최종 성과")
                    st.write(f"**총 매출**: {data['total_revenue']:,}원")
                    st.write(f"**총 순이익**: {data['total_profit']:,}원")
                    st.write(f"**최종 자본**: {data['final_capital']:,}원")
                
                # 평가
                st.markdown("### 📊 평가")
                
                if data['total_profit'] > 800000:
                    st.success("🌟 탁월함! 전략과 실행 모두 완벽했습니다.")
                elif data['total_profit'] > 500000:
                    st.success("✅ 우수! 좋은 전략으로 안정적인 수익을 냈습니다.")
                elif data['total_profit'] > 200000:
                    st.info("💙 양호. 기본은 잘 이해했습니다.")
                else:
                    st.warning("💪 다음엔 더 잘할 수 있어요! 마진 관리에 주목하세요.")
                
                # 배운 점
                st.markdown("### 🎓 배운 점")
                
                margin_rate = (data['total_profit'] / data['total_revenue'] * 100) if data['total_revenue'] > 0 else 0
                
                st.write(f"- 마진율: {margin_rate:.1f}% ({'높음' if margin_rate > 60 else '중간' if margin_rate > 40 else '낮음'})")
                st.write(f"- 재고 관리: {'우수' if data['inventory'] <= 2 else '개선 필요'}")
                st.write("- 창업에서 중요한 것은 매출보다 **순이익**입니다!")
                
                st.markdown("---")

st.markdown("---")
st.caption("🏪 장사의 신 게임 관리 시스템 V2 - 실전 창업 시뮬레이션")
