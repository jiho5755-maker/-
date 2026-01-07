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

# 구매자 캐릭터 프로필 (랜덤 배정용)
BUYER_CHARACTERS = {
    "big_spender": [
        {
            "name": "사업가 김사장",
            "emoji": "💼",
            "budget": "1,000,000원",
            "personality": "투자 가치 중시, 사업 확장성 평가",
            "speech": ["이거 사업성 있어 보이네요", "투자 가치가 있으면 비싸도 괜찮아요", "품질이 중요하죠"],
            "behavior": "사업 아이템을 평가하듯 질문하고, 확장 가능성을 물어봄"
        },
        {
            "name": "연예인 박스타",
            "emoji": "⭐",
            "budget": "1,000,000원",
            "personality": "트렌디하고 유명한 것 선호, SNS 감성",
            "speech": ["인스타에 올리면 좋겠어요", "요즘 유행하는 거예요?", "이거 힙하네요!"],
            "behavior": "SNS 찍기 좋은지 확인하고, 트렌드에 민감함"
        },
        {
            "name": "의사 이원장",
            "emoji": "⚕️",
            "budget": "1,000,000원",
            "personality": "건강과 품질 최우선, 전문가적 안목",
            "speech": ["건강에 좋은가요?", "품질 보증이 되나요?", "성분이 뭐예요?"],
            "behavior": "꼼꼼하게 따져보지만, 마음에 들면 확실하게 구매"
        },
        {
            "name": "변호사 최법사",
            "emoji": "⚖️",
            "budget": "1,000,000원",
            "personality": "논리적이고 분석적, 계약 조건 중시",
            "speech": ["근거가 뭐죠?", "이 가격이 합리적인 이유가?", "보증은 되나요?"],
            "behavior": "논리적으로 설득되면 구매, 근거 있는 설명 선호"
        },
        {
            "name": "건물주 박건물",
            "emoji": "🏢",
            "budget": "1,000,000원",
            "personality": "여유롭고 느긋함, 마음에 들면 즉시 구매",
            "speech": ["그래요? 재밌네요", "좋아 보이면 사죠", "얼마예요? 아 괜찮네요"],
            "behavior": "친절하고 여유있게 대화, 느낌으로 판단"
        },
        {
            "name": "재벌 3세 윤도련",
            "emoji": "💎",
            "budget": "1,000,000원",
            "personality": "명품 선호, 독특하고 희귀한 것 좋아함",
            "speech": ["이거 한정판이에요?", "특별한 게 뭐예요?", "다른 데는 없죠?"],
            "behavior": "독특함과 희소성에 끌림, 프리미엄 선호"
        }
    ],
    "normal": [
        {
            "name": "직장인 김대리",
            "emoji": "💼",
            "budget": "500,000원",
            "personality": "실용적이고 가성비 중시, 급여날 여유",
            "speech": ["가성비 괜찮은가요?", "이 가격이면 적당하네요", "실용적인가요?"],
            "behavior": "꼼꼼하게 비교하고, 합리적이면 구매"
        },
        {
            "name": "대학생 이학생",
            "emoji": "🎓",
            "budget": "500,000원",
            "personality": "알바비 받은 날, 자기 보상 원함",
            "speech": ["알바비 받았는데", "나한테 선물하려고요", "이거 힙한 거 맞죠?"],
            "behavior": "트렌디하고 자기만족 되는 것 선호"
        },
        {
            "name": "신혼부부 박신혼",
            "emoji": "💑",
            "budget": "500,000원",
            "personality": "신혼집 꾸미기, 실용적이면서 예쁜 것",
            "speech": ["신혼집에 어울릴까요?", "배우자가 좋아할까요?", "실용적이에요?"],
            "behavior": "파트너와 상의하는 듯한 제스처, 신중하게 선택"
        },
        {
            "name": "프리랜서 최자유",
            "emoji": "💻",
            "budget": "500,000원",
            "personality": "자유로운 영혼, 창의적인 것 선호",
            "speech": ["독특하네요", "창의적이에요", "이거 재밌겠다"],
            "behavior": "독창성과 재미를 중시, 감성적 구매"
        },
        {
            "name": "교사 강선생",
            "emoji": "📚",
            "budget": "500,000원",
            "personality": "교육적 가치 중시, 의미있는 구매",
            "speech": ["교육적으로 좋네요", "학생들한테 보여줄까?", "의미있는 것 같아요"],
            "behavior": "스토리와 가치를 중시, 설명을 잘 들음"
        },
        {
            "name": "간호사 윤간호",
            "emoji": "💉",
            "budget": "500,000원",
            "personality": "실용성과 편리성 중시, 야근 많아 간편한 것",
            "speech": ["편리한가요?", "관리하기 쉬워요?", "바빠도 괜찮을까요?"],
            "behavior": "실용적이고 편리한 것 우선, 빠른 결정"
        },
        {
            "name": "공무원 정안정",
            "emoji": "🏛️",
            "budget": "500,000원",
            "personality": "안정적이고 검증된 것 선호",
            "speech": ["믿을 만한가요?", "많이 팔렸어요?", "후기 어때요?"],
            "behavior": "검증되고 안전한 선택 선호, 신중함"
        }
    ],
    "frugal": [
        {
            "name": "주부 김알뜰",
            "emoji": "🏠",
            "budget": "200,000원",
            "personality": "집안 살림 책임, 한 푼이 아까움",
            "speech": ["너무 비싼데...", "좀 깎아주세요", "집에 돈 쓸 데가 많아서"],
            "behavior": "가격 흥정 시도, 할인 여부 확인"
        },
        {
            "name": "은퇴자 박은퇴",
            "emoji": "👴",
            "budget": "200,000원",
            "personality": "연금 생활, 아껴서 써야 함",
            "speech": ["연금으로 살아서...", "꼭 필요한 것만", "더 싼 거 없어요?"],
            "behavior": "필요성을 따져봄, 매우 신중함"
        },
        {
            "name": "취준생 이준비",
            "emoji": "📝",
            "budget": "200,000원",
            "personality": "취업 준비 중, 돈이 너무 없음",
            "speech": ["취업하면 사야지...", "지금은 너무 비싸요", "할인 안 되나요?"],
            "behavior": "사고 싶지만 참는 모습, 가격에 매우 민감"
        },
        {
            "name": "알바생 최최저",
            "emoji": "🍔",
            "budget": "200,000원",
            "personality": "최저시급, 아껴서 모으는 중",
            "speech": ["한 시간 일해야 버는 돈인데", "너무 비싸요", "반값 안 되나요?"],
            "behavior": "시간당 임금으로 환산해서 생각, 아까워함"
        },
        {
            "name": "대학원생 박논문",
            "emoji": "📖",
            "budget": "200,000원",
            "personality": "등록금 내고 남은 돈, 라면으로 연명",
            "speech": ["대학원생이라...", "이거 꼭 필요한가요?", "더 싼 거요?"],
            "behavior": "필요성 따지고, 가격 협상 시도"
        },
        {
            "name": "신입사원 이막내",
            "emoji": "👔",
            "budget": "200,000원",
            "personality": "첫 월급인데 쓸 데가 많음, 빚도 있음",
            "speech": ["첫 월급인데 빠듯해서", "할부 되나요?", "조금만 깎아주세요"],
            "behavior": "사고 싶지만 가격 부담, 망설임"
        },
        {
            "name": "자영업자 정힘듦",
            "emoji": "🏪",
            "budget": "200,000원",
            "personality": "장사 안 돼서 힘듦, 절약 모드",
            "speech": ["요즘 장사가 안 돼서", "딱 필요한 것만", "에이 너무 비싸"],
            "behavior": "필요하면 살지만, 가격 흥정 많이 함"
        }
    ]
}

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

# ==================== 선택적 기능 (토글) ====================

# 이벤트 카드 (관리자가 활성화 가능)
EVENT_CARDS = {
    "positive": [
        {"name": "📱 SNS 입소문", "effect": "구매자 +2명", "impact": {"buyers": 2}},
        {"name": "🎉 명절 특수", "effect": "큰손 구매 확률 +50%", "impact": {"big_spender_boost": 0.5}},
        {"name": "🌟 언론 보도", "effect": "판매가 +20% 효과", "impact": {"price_boost": 0.2}},
        {"name": "🎁 단골 고객", "effect": "무조건 구매 1건", "impact": {"guaranteed_sale": 1}},
    ],
    "negative": [
        {"name": "⚠️ 경쟁자 등장", "effect": "시장 평균가 -10%", "impact": {"market_price_drop": 0.1}},
        {"name": "📉 재료비 상승", "effect": "원가 +20%", "impact": {"cost_increase": 0.2}},
        {"name": "🌧️ 악천후", "effect": "구매자 -1명", "impact": {"buyers": -1}},
        {"name": "💸 임대료 인상", "effect": "고정비 +50,000원", "impact": {"fixed_cost": 50000}},
    ]
}

# 마케팅 투자 옵션
MARKETING_OPTIONS = [
    {"name": "전단지 배포", "cost": 50000, "effect": "구매자 +1명", "buyers": 1},
    {"name": "SNS 광고", "cost": 100000, "effect": "구매 확률 +20%", "conversion_boost": 0.2},
    {"name": "샘플 나눠주기", "cost": 80000, "effect": "단골 고객 1명 확보", "guaranteed_customer": 1},
]

# 비용 세분화
DETAILED_COSTS = {
    "홍보비": {"min": 30000, "max": 100000, "default": 50000, "required": False},
    "자리세": {"min": 20000, "max": 80000, "default": 30000, "required": True},
    "포장재비": {"min": 10000, "max": 50000, "default": 20000, "required": False},
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

def save_student_to_sheets(worksheet, name, student_data):
    """학생 데이터를 Google Sheets에 저장합니다."""
    if not worksheet:
        return False
    
    try:
        all_values = worksheet.get_all_values()
        row_index = None
        
        for idx, row in enumerate(all_values[1:], start=2):
            if row[0] == name:
                row_index = idx
                break
        
        new_row = [
            name,
            student_data['business_type'],
            student_data['cost'],
            student_data['initial_capital'],
            student_data['purchased_quantity'],
            student_data['inventory'],
            student_data['rounds'][1]['selling_price'],
            student_data['rounds'][1]['quantity_sold'],
            student_data['rounds'][1]['revenue'],
            student_data['rounds'][1]['cost_total'],
            student_data['rounds'][1]['profit'],
            student_data['rounds'][2]['selling_price'],
            student_data['rounds'][2]['quantity_sold'],
            student_data['rounds'][2]['revenue'],
            student_data['rounds'][2]['cost_total'],
            student_data['rounds'][2]['profit'],
            student_data['total_revenue'],
            student_data['total_cost'],
            student_data['total_profit'],
            student_data['final_capital'],
            student_data.get('actual_money', 0)
        ]
        
        if row_index:
            worksheet.update(f'A{row_index}:U{row_index}', [new_row])
        else:
            worksheet.append_row(new_row)
        
        time.sleep(1.0)
        return True
    except Exception as e:
        st.error(f"데이터 저장 오류: {str(e)}")
        return False

def load_students_from_sheets(worksheet):
    """Google Sheets에서 학생 데이터를 불러옵니다."""
    if not worksheet:
        return {}
    
    def safe_int(value, default=0):
        """안전하게 정수로 변환"""
        try:
            if value and str(value).strip():
                # 숫자만 추출
                cleaned = ''.join(filter(str.isdigit, str(value)))
                return int(cleaned) if cleaned else default
            return default
        except:
            return default
    
    try:
        all_values = worksheet.get_all_values()
        
        if len(all_values) <= 1:
            return {}
        
        students = {}
        
        for row in all_values[1:]:
            if not row or not row[0]:
                continue
            
            name = row[0]
            
            try:
                cost = safe_int(row[2] if len(row) > 2 else 0, 0)
                
                students[name] = {
                    "business_type": row[1] if len(row) > 1 else "",
                    "cost": cost,
                    "recommended_price": cost * 2 if cost > 0 else 0,
                    "initial_capital": safe_int(row[3] if len(row) > 3 else INITIAL_CAPITAL, INITIAL_CAPITAL),
                    "purchased_quantity": safe_int(row[4] if len(row) > 4 else 0, 0),
                    "inventory": safe_int(row[5] if len(row) > 5 else 0, 0),
                    "rounds": {
                        1: {
                            "selling_price": safe_int(row[6] if len(row) > 6 else 0, 0),
                            "quantity_sold": safe_int(row[7] if len(row) > 7 else 0, 0),
                            "revenue": safe_int(row[8] if len(row) > 8 else 0, 0),
                            "cost_total": safe_int(row[9] if len(row) > 9 else 0, 0),
                            "profit": safe_int(row[10] if len(row) > 10 else 0, 0),
                        },
                        2: {
                            "selling_price": safe_int(row[11] if len(row) > 11 else 0, 0),
                            "quantity_sold": safe_int(row[12] if len(row) > 12 else 0, 0),
                            "revenue": safe_int(row[13] if len(row) > 13 else 0, 0),
                            "cost_total": safe_int(row[14] if len(row) > 14 else 0, 0),
                            "profit": safe_int(row[15] if len(row) > 15 else 0, 0),
                        }
                    },
                    "total_revenue": safe_int(row[16] if len(row) > 16 else 0, 0),
                    "total_cost": safe_int(row[17] if len(row) > 17 else 0, 0),
                    "total_profit": safe_int(row[18] if len(row) > 18 else 0, 0),
                    "final_capital": safe_int(row[19] if len(row) > 19 else INITIAL_CAPITAL, INITIAL_CAPITAL),
                    "actual_money": safe_int(row[20] if len(row) > 20 else 0, 0)
                }
            except Exception as row_error:
                # 개별 행 에러는 건너뛰기
                st.warning(f"⚠️ {name}님 데이터 로드 실패 (건너뜀): {str(row_error)}")
                continue
        
        return students
    except Exception as e:
        st.error(f"❌ 데이터 로드 오류: {str(e)}")
        st.info("💡 새로 시작하려면 Google Sheets의 '학생데이터' 시트를 삭제하고 새로고침하세요.")
        return {}

def delete_all_students_from_sheets(worksheet):
    """Google Sheets에서 모든 학생 데이터를 삭제합니다."""
    if not worksheet:
        return False
    
    try:
        # 헤더 유지하고 데이터만 삭제
        worksheet.clear()
        headers = ["학생이름", "사업유형", "원가", "초기자본", "구매수량", "재고",
                  "1R판매가", "1R판매수", "1R매출", "1R원가", "1R이익",
                  "2R판매가", "2R판매수", "2R매출", "2R원가", "2R이익",
                  "총매출", "총원가", "총순이익", "최종자본", "실물소지금"]
        worksheet.update('A1:U1', [headers])
        time.sleep(1.0)
        return True
    except Exception as e:
        st.error(f"데이터 삭제 오류: {str(e)}")
        return False

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

# 학생 데이터 초기화 (Google Sheets에서 로드)
if 'students' not in st.session_state:
    if st.session_state.use_google_sheets and st.session_state.worksheet:
        st.session_state.students = load_students_from_sheets(st.session_state.worksheet)
    else:
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
        step=10000,
        help="1만원 단위로 입력"
    )
    
    new_total_buyers = st.sidebar.number_input(
        "👥 전체 구매자 수",
        min_value=5,
        max_value=50,
        value=total_buyers,
        step=1
    )
    
    new_game_mode = st.sidebar.radio(
        "🎮 게임 모드",
        ["간단 모드", "전략 모드"],
        index=0 if game_mode == "간단 모드" else 1,
        help="간단 모드: 초등학생용 (재고 관리 없음) | 전략 모드: 고등학생용 (전체 시스템)"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 🎲 선택적 기능 (다음 게임용)")
    st.sidebar.caption("고급 기능을 켜고 끌 수 있습니다")
    
    enable_events = st.sidebar.checkbox(
        "🎴 이벤트 카드",
        value=st.session_state.market_settings.get('enable_events', False),
        help="라운드 중 랜덤 이벤트 발생"
    )
    
    enable_marketing = st.sidebar.checkbox(
        "📢 마케팅 투자",
        value=st.session_state.market_settings.get('enable_marketing', False),
        help="자본으로 광고 투자 가능"
    )
    
    enable_detailed_costs = st.sidebar.checkbox(
        "💰 비용 세분화",
        value=st.session_state.market_settings.get('enable_detailed_costs', False),
        help="홍보비, 자리세 등 세부 비용 추가"
    )
    
    if st.sidebar.button("💾 설정 저장"):
        new_settings = {
            'total_money': new_total_money,
            'total_buyers': new_total_buyers,
            'game_mode': new_game_mode,
            'big_spender_ratio': 20,
            'normal_ratio': 50,
            'frugal_ratio': 30,
            'enable_events': enable_events,
            'enable_marketing': enable_marketing,
            'enable_detailed_costs': enable_detailed_costs
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
    
    # 게임 모드 표시
    if game_mode == "간단 모드":
        st.info("🎮 **간단 모드** | 재고 걱정 없이 판매에만 집중! (초등학생 추천)")
    else:
        st.success("🎮 **전략 모드** | 자본, 재고, 원가를 모두 관리하는 실전 시뮬레이션! (고등학생 추천)")
    
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
        
        st.subheader("2️⃣ AI 창업 아이디어 분석")
        
        student_idea = st.text_area(
            "💡 학생의 창업 아이디어",
            placeholder="예: 손으로 만든 팔찌를 판매하고 싶어요",
            help="학생이 설명한 창업 아이템을 입력하세요",
            key="student_idea"
        )
        
        if student_idea and st.button("🤖 AI 분석 시작", key="analyze_idea"):
            with st.spinner("AI가 아이디어를 분석 중입니다..."):
                try:
                    openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
                    
                    if not openai_api_key:
                        st.error("⚠️ OpenAI API 키가 설정되지 않았습니다.")
                    else:
                        from openai import OpenAI
                        client = OpenAI(api_key=openai_api_key)
                        
                        # AI에게 분석 요청
                        prompt = f"""
다음 학생의 창업 아이디어를 분석하고, 가장 적합한 비즈니스 유형을 추천해주세요.

학생 아이디어: {student_idea}

비즈니스 유형 목록:
{', '.join(BUSINESS_TYPES.keys())}

다음 정보를 포함해서 답변해주세요:
1. 추천 유형 (위 목록 중 1개)
2. 추천 이유 (2-3문장)
3. 성공을 위한 조언 (2-3문장)

형식:
추천유형: [유형명]
이유: [설명]
조언: [설명]
"""
                        
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "당신은 초등학생부터 고등학생까지를 대상으로 하는 창업 교육 전문가입니다."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=500
                        )
                        
                        ai_response = response.choices[0].message.content
                        st.session_state['ai_analysis'] = ai_response
                        st.success("✅ AI 분석 완료!")
                        st.markdown(ai_response)
                
                except Exception as e:
                    st.error(f"⚠️ AI 분석 오류: {str(e)}")
        
        # AI 분석 결과 표시
        if 'ai_analysis' in st.session_state and st.session_state['ai_analysis']:
            with st.expander("📊 AI 분석 결과 보기", expanded=True):
                st.markdown(st.session_state['ai_analysis'])
        
        st.markdown("---")
        
        st.subheader("3️⃣ 창업 유형 선택")
        
        selected_business = st.selectbox(
            "사업 유형",
            options=list(BUSINESS_TYPES.keys()),
            help="학생의 아이디어에 맞는 유형 선택 (AI 추천 참고)"
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
        
        st.subheader("4️⃣ 원가 조정 (관리자)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**AI 추천 원가**: {business_info['cost']:,}원")
        
        with col2:
            adjusted_cost = st.number_input(
                "최종 원가 설정 (1만원 단위)",
                min_value=10000,
                max_value=500000,
                value=business_info['cost'],
                step=10000,
                help="실제 화폐: 10만원권, 5만원권, 1만원권",
                key="cost_adjustment"
            )
        
        if adjusted_cost != business_info['cost']:
            st.warning(f"⚠️ 원가 조정: {business_info['cost']:,}원 → {adjusted_cost:,}원")
        
        # 추천 판매가 자동 계산
        recommended_selling_price = int(adjusted_cost * 2.0)
        
        # 구매자 조건 자동 표시
        st.markdown("---")
        st.subheader("👥 구매자 구매 조건")
        st.caption(f"원가 {adjusted_cost:,}원 기준")
        
        buyer_col1, buyer_col2, buyer_col3 = st.columns(3)
        
        with buyer_col1:
            big_spender_max = int(adjusted_cost * 2.5)
            st.success(f"""
            **💎 큰손 (20%)**  
            {int(adjusted_cost * 1.5):,}원 ~ {big_spender_max:,}원
            
            품질 중시, 비싸도 OK
            """)
        
        with buyer_col2:
            normal_max = int(adjusted_cost * 2.0)
            st.info(f"""
            **😊 일반 (50%)**  
            {int(adjusted_cost * 1.3):,}원 ~ {normal_max:,}원
            
            가성비 중시, 적정가
            """)
        
        with buyer_col3:
            frugal_max = int(adjusted_cost * 1.5)
            st.warning(f"""
            **🤏 짠물 (30%)**  
            {adjusted_cost:,}원 ~ {frugal_max:,}원
            
            저가 선호, 싼 것만
            """)
        
        st.info(f"💡 **추천 판매가 {recommended_selling_price:,}원**: 큰손(2명) + 일반(5명) = 7명 구매 가능!")
        
        st.markdown("---")
        
        st.subheader("5️⃣ 초기 자본금 설정")
        
        custom_capital = st.number_input(
            "💰 이 학생의 초기 자본금",
            min_value=100000,
            max_value=10000000,
            value=INITIAL_CAPITAL,
            step=10000,
            help="기본 500,000원 / 학생별로 다르게 설정 가능",
            key="custom_capital"
        )
        
        if custom_capital != INITIAL_CAPITAL:
            st.warning(f"⚠️ 자본금 조정: {INITIAL_CAPITAL:,}원 → {custom_capital:,}원")
        
        st.markdown("---")
        
        st.subheader("6️⃣ 학생 등록")
        
        if st.button("✅ 학생 등록하기", type="primary", key="register_student"):
            if not student_name:
                st.error("⚠️ 학생 이름을 입력하세요!")
            else:
                # 학생 데이터 생성
                st.session_state.students[student_name] = {
                    "business_type": selected_business,
                    "cost": adjusted_cost,
                    "recommended_price": recommended_selling_price,
                    "initial_capital": custom_capital,
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
                    "final_capital": custom_capital,  # 초기 자본금
                    "actual_money": 0  # 실물 소지금 (나중에 입력)
                }
                
                # Google Sheets에 저장
                if st.session_state.use_google_sheets and st.session_state.worksheet:
                    save_student_to_sheets(st.session_state.worksheet, student_name, st.session_state.students[student_name])
                
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
                
                # STEP 1: 재고 구매 (전략 모드만)
                if game_mode == "전략 모드":
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
                                
                                # Google Sheets에 저장
                                if st.session_state.use_google_sheets and st.session_state.worksheet:
                                    save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                                
                                st.success(f"✅ {purchase_quantity}개 구매 완료!")
                                st.rerun()
                        else:
                            st.warning("⚠️ 구매 수량을 입력하세요")
                    else:
                        st.success(f"✅ 이미 구매 완료: {data['purchased_quantity']}개")
                    
                    st.markdown("---")
                else:
                    # 간단 모드: 재고 관리 없음
                    st.info("🎮 **간단 모드**: 재고 걱정 없이 바로 판매하세요!")
                    st.markdown("---")
                
                # 선택적 기능: 이벤트 카드
                if st.session_state.market_settings.get('enable_events', False):
                    st.markdown("### 🎴 이벤트 카드")
                    
                    if st.button("🎲 이벤트 뽑기", key=f"event_{name}"):
                        import random
                        event_type = random.choice(['positive', 'negative'])
                        event = random.choice(EVENT_CARDS[event_type])
                        
                        if event_type == 'positive':
                            st.success(f"🎉 {event['name']}: {event['effect']}")
                        else:
                            st.warning(f"⚠️ {event['name']}: {event['effect']}")
                        
                        st.info("💡 이 이벤트 효과를 게임에 반영하세요!")
                    
                    st.markdown("---")
                
                # 선택적 기능: 마케팅 투자
                if st.session_state.market_settings.get('enable_marketing', False):
                    st.markdown("### 📢 마케팅 투자")
                    
                    marketing_choice = st.selectbox(
                        "마케팅 옵션 선택",
                        ["선택 안 함"] + [f"{m['name']} ({m['cost']:,}원) - {m['effect']}" for m in MARKETING_OPTIONS],
                        key=f"marketing_{name}"
                    )
                    
                    if marketing_choice != "선택 안 함":
                        selected_marketing = MARKETING_OPTIONS[[f"{m['name']} ({m['cost']:,}원) - {m['effect']}" for m in MARKETING_OPTIONS].index(marketing_choice)]
                        
                        if st.button("✅ 마케팅 투자", key=f"confirm_marketing_{name}"):
                            if data['final_capital'] >= selected_marketing['cost']:
                                st.session_state.students[name]['final_capital'] -= selected_marketing['cost']
                                st.success(f"✅ {selected_marketing['name']} 투자 완료! {selected_marketing['effect']}")
                                st.rerun()
                            else:
                                st.error("⚠️ 자본이 부족합니다")
                    
                    st.markdown("---")
                
                # 선택적 기능: 비용 세분화
                if st.session_state.market_settings.get('enable_detailed_costs', False):
                    st.markdown("### 💰 세부 비용")
                    
                    total_detailed_cost = 0
                    
                    for cost_name, cost_info in DETAILED_COSTS.items():
                        required_text = "(필수)" if cost_info['required'] else "(선택)"
                        
                        cost_value = st.number_input(
                            f"{cost_name} {required_text}",
                            min_value=cost_info['min'],
                            max_value=cost_info['max'],
                            value=cost_info['default'],
                            step=10000,
                            key=f"cost_{cost_name}_{name}"
                        )
                        total_detailed_cost += cost_value
                    
                    st.info(f"💸 총 운영비: {total_detailed_cost:,}원")
                    
                    if st.button("✅ 운영비 지불", key=f"pay_costs_{name}"):
                        if data['final_capital'] >= total_detailed_cost:
                            st.session_state.students[name]['final_capital'] -= total_detailed_cost
                            st.success("✅ 운영비 지불 완료!")
                            st.rerun()
                        else:
                            st.error("⚠️ 자본이 부족합니다")
                    
                    st.markdown("---")
                
                # 실시간 경쟁 현황
                st.markdown("### 📊 실시간 경쟁 현황")
                
                # 현재 라운드에 판매가 기록된 학생들의 가격 정보 수집
                current_round_prices = []
                for other_name, other_data in st.session_state.students.items():
                    if other_name != name:  # 본인 제외
                        round_data_other = other_data['rounds'].get(st.session_state.current_round, {})
                        if 'selling_price' in round_data_other and round_data_other['selling_price'] > 0:
                            current_round_prices.append({
                                'name': other_name,
                                'price': round_data_other['selling_price'],
                                'type': other_data['business_type']
                            })
                
                if current_round_prices:
                    prices_only = [p['price'] for p in current_round_prices]
                    min_price = min(prices_only)
                    max_price = max(prices_only)
                    avg_price = sum(prices_only) // len(prices_only)
                    
                    comp_col1, comp_col2, comp_col3 = st.columns(3)
                    
                    with comp_col1:
                        st.metric("🔻 시장 최저가", f"{min_price:,}원")
                    with comp_col2:
                        st.metric("📊 시장 평균가", f"{avg_price:,}원")
                    with comp_col3:
                        st.metric("🔺 시장 최고가", f"{max_price:,}원")
                    
                    # 같은 업종 경쟁자 정보
                    same_type_competitors = [p for p in current_round_prices if p['type'] == data['business_type']]
                    if same_type_competitors:
                        st.info(f"**{data['business_type']} 업종 경쟁자**: {len(same_type_competitors)}명이 판매 중")
                else:
                    st.info("💡 아직 다른 학생이 판매를 시작하지 않았습니다")
                
                st.markdown("---")
                
                # STEP 2: 판매 입력
                step_num = "1️⃣" if game_mode == "간단 모드" else "2️⃣"
                st.markdown(f"### {step_num} {st.session_state.current_round}라운드 판매")
                
                round_data = data['rounds'][st.session_state.current_round]
                
                # 간단 모드: 재고 체크 없음, 전략 모드: 재고 체크
                can_sell = True if game_mode == "간단 모드" else data['inventory'] > 0
                
                if not can_sell:
                    st.warning("⚠️ 재고가 없습니다. 먼저 재고를 구매하세요.")
                else:
                    sell_col1, sell_col2 = st.columns(2)
                    
                    with sell_col1:
                        selling_price = st.number_input(
                            "판매가 (1만원 단위)",
                            min_value=0,
                            max_value=1000000,
                            value=data['recommended_price'],
                            step=10000,
                            help="10만원권, 5만원권, 1만원권으로 거래",
                            key=f"price_{name}_r{st.session_state.current_round}"
                        )
                    
                    with sell_col2:
                        # 간단 모드: 재고 무제한, 전략 모드: 재고 제한
                        if game_mode == "간단 모드":
                            # 간단 모드는 최대 판매 제한만 적용
                            max_sellable = business_info['max_sales_per_10min'] if business_info['max_sales_per_10min'] else 50
                            help_text = f"간단 모드: 재고 무제한" + (f", 10분 제한 {max_sellable}개" if business_info['max_sales_per_10min'] else "")
                        else:
                            max_sellable = data['inventory']
                            if business_info['max_sales_per_10min']:
                                max_sellable = min(max_sellable, business_info['max_sales_per_10min'])
                            help_text = f"재고 {data['inventory']}개" + (f", 10분 제한 {business_info['max_sales_per_10min']}개" if business_info['max_sales_per_10min'] else "")
                        
                        quantity_sold = st.number_input(
                            f"판매 수량 (최대 {max_sellable}개)",
                            min_value=0,
                            max_value=max_sellable,
                            value=0,
                            step=1,
                            help=help_text,
                            key=f"sold_{name}_r{st.session_state.current_round}"
                        )
                    
                    if quantity_sold > 0:
                        revenue = selling_price * quantity_sold
                        
                        # 대여업 2라운드는 원가 0원 (이미 구매한 물건 재사용)
                        if "빌려주기" in data['business_type'] and st.session_state.current_round == 2:
                            cost_total = 0
                            st.info("🎪 대여업 2라운드: 원가 0원! (물건 재사용)")
                        else:
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
                            
                            # 재고 차감 (전략 모드만)
                            if game_mode == "전략 모드":
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
                            
                            # Google Sheets에 저장
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
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
                
                # 관리자 전용: 데이터 수정/삭제
                if st.session_state.is_admin:
                    st.markdown("---")
                    st.markdown("### ⚙️ 관리자 기능")
                    
                    edit_col1, edit_col2, edit_col3 = st.columns(3)
                    
                    with edit_col1:
                        if st.button("📝 정보 수정", key=f"edit_{name}"):
                            st.session_state[f'editing_{name}'] = True
                            st.rerun()
                    
                    with edit_col2:
                        if st.button("🔄 재고 초기화", key=f"reset_inventory_{name}"):
                            st.session_state.students[name]['purchased_quantity'] = 0
                            st.session_state.students[name]['inventory'] = 0
                            st.session_state.students[name]['final_capital'] = data['initial_capital']
                            
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            st.success("✅ 재고 초기화됨!")
                            st.rerun()
                    
                    with edit_col3:
                        if st.button("🗑️ 학생 삭제", key=f"delete_{name}", type="secondary"):
                            if st.session_state.get(f'confirm_delete_{name}'):
                                del st.session_state.students[name]
                                st.success(f"✅ {name}님 삭제됨!")
                                st.rerun()
                            else:
                                st.session_state[f'confirm_delete_{name}'] = True
                                st.warning("⚠️ 한 번 더 클릭하여 삭제 확인")
                    
                    # 정보 수정 모드
                    if st.session_state.get(f'editing_{name}'):
                        st.markdown("---")
                        st.markdown("#### 📝 정보 수정")
                        
                        edit_form_col1, edit_form_col2 = st.columns(2)
                        
                        with edit_form_col1:
                            new_cost = st.number_input(
                                "원가 수정",
                                min_value=10000,
                                max_value=500000,
                                value=data['cost'],
                                step=10000,
                                key=f"edit_cost_{name}"
                            )
                        
                        with edit_form_col2:
                            new_capital = st.number_input(
                                "초기 자본 수정",
                                min_value=100000,
                                max_value=10000000,
                                value=data['initial_capital'],
                                step=10000,
                                key=f"edit_capital_{name}"
                            )
                        
                        if st.button("✅ 수정 완료", key=f"save_edit_{name}"):
                            st.session_state.students[name]['cost'] = new_cost
                            st.session_state.students[name]['recommended_price'] = new_cost * 2
                            st.session_state.students[name]['initial_capital'] = new_capital
                            
                            # 자본금 변경 시 현재 자본도 조정
                            capital_diff = new_capital - data['initial_capital']
                            st.session_state.students[name]['final_capital'] += capital_diff
                            
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            st.session_state[f'editing_{name}'] = False
                            st.success("✅ 수정 완료!")
                            st.rerun()

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
        
        st.markdown("---")
        
        # 📈 데이터 시각화
        st.subheader("📈 데이터 시각화")
        
        if st.session_state.students:
            viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📊 학생별 비교", "📉 라운드별 추이", "💰 가격 분포"])
            
            with viz_tab1:
                st.markdown("#### 학생별 매출 vs 순이익")
                
                # 데이터 준비
                students_names = list(st.session_state.students.keys())
                revenues = [st.session_state.students[name]['total_revenue'] for name in students_names]
                profits = [st.session_state.students[name]['total_profit'] for name in students_names]
                
                # 차트 데이터프레임
                chart_df = pd.DataFrame({
                    '학생': students_names,
                    '매출': revenues,
                    '순이익': profits
                })
                
                # 막대 차트
                st.bar_chart(chart_df.set_index('학생'))
                
                # 통계 요약
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("평균 매출", f"{sum(revenues)//len(revenues):,}원")
                with col2:
                    st.metric("평균 순이익", f"{sum(profits)//len(profits):,}원")
                with col3:
                    avg_margin = (sum(profits) / sum(revenues) * 100) if sum(revenues) > 0 else 0
                    st.metric("전체 평균 마진율", f"{avg_margin:.1f}%")
            
            with viz_tab2:
                st.markdown("#### 라운드별 실적 추이")
                
                # 라운드별 데이터 수집
                round_data = {name: [] for name in students_names}
                
                for round_num in [1, 2]:
                    for name in students_names:
                        round_info = st.session_state.students[name]['rounds'].get(round_num, {})
                        round_data[name].append(round_info.get('profit', 0))
                
                # 라운드별 차트 데이터
                round_df = pd.DataFrame(round_data, index=['1라운드', '2라운드'])
                
                st.line_chart(round_df)
                
                st.info("💡 라운드별 순이익 변화를 확인하세요. 전략 수정이 효과가 있었나요?")
            
            with viz_tab3:
                st.markdown("#### 판매가 분포")
                
                # 각 학생의 평균 판매가 계산
                avg_prices = []
                for name in students_names:
                    prices = []
                    for round_num in [1, 2]:
                        round_info = st.session_state.students[name]['rounds'].get(round_num, {})
                        if 'selling_price' in round_info and round_info['selling_price'] > 0:
                            prices.append(round_info['selling_price'])
                    
                    if prices:
                        avg_prices.append({
                            '학생': name,
                            '평균 판매가': sum(prices) // len(prices),
                            '원가': st.session_state.students[name]['cost']
                        })
                
                if avg_prices:
                    price_df = pd.DataFrame(avg_prices)
                    
                    # 판매가와 원가 비교
                    chart_data = price_df.set_index('학생')[['평균 판매가', '원가']]
                    st.bar_chart(chart_data)
                    
                    st.success("💡 판매가가 원가보다 높을수록 마진이 높습니다!")
                else:
                    st.info("아직 판매 데이터가 없습니다")
        
        st.markdown("---")
        
        # 최종 정산 (실물 화폐 검증)
        if st.session_state.is_admin:
            st.subheader("💰 최종 정산 (실물 화폐 검증)")
            st.caption("학생들이 실제로 손에 쥔 돈을 세고 시스템과 비교합니다")
            
            for name, data in st.session_state.students.items():
                with st.expander(f"💵 {name} - 소지금 확인"):
                    verify_col1, verify_col2, verify_col3 = st.columns(3)
                    
                    with verify_col1:
                        expected_capital = data['final_capital']
                        st.metric("💻 시스템 계산", f"{expected_capital:,}원")
                        st.caption("초기자본 - 구매비용 + 판매수입")
                    
                    with verify_col2:
                        actual_money = st.number_input(
                            "💰 실제 소지금 (손에 쥔 돈)",
                            min_value=0,
                            max_value=10000000,
                            value=data.get('actual_money', expected_capital),
                            step=10000,
                            key=f"actual_{name}",
                            help="학생이 세어본 실제 돈"
                        )
                        
                        if st.button("✅ 확정", key=f"confirm_{name}"):
                            st.session_state.students[name]['actual_money'] = actual_money
                            
                            # Google Sheets에 저장
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            st.success("기록됨!")
                            st.rerun()
                    
                    with verify_col3:
                        diff = actual_money - expected_capital
                        if diff == 0:
                            st.success("✅ 일치!")
                            st.balloons()
                        elif diff > 0:
                            st.warning(f"💰 {diff:,}원 많음")
                            st.caption("확인 필요")
                        else:
                            st.error(f"💸 {abs(diff):,}원 부족")
                            st.caption("확인 필요")
            
            st.markdown("---")
            
            # 화폐 배분 가이드
            st.subheader("💵 화폐 준비 가이드")
            
            num_students = len(st.session_state.students)
            if num_students > 0:
                guide_col1, guide_col2 = st.columns(2)
                
                with guide_col1:
                    st.markdown("#### 📦 초기 자본 배분")
                    st.write(f"**학생 수**: {num_students}명")
                    st.write(f"**인당 자본**: {INITIAL_CAPITAL:,}원")
                    st.write("")
                    st.info(f"""
                    **필요한 화폐** (학생 {num_students}명 기준):
                    - 10만원권: {num_students * 4}장
                    - 5만원권: {num_students * 2}장
                    - 1만원권: 0장
                    
                    **총액**: {INITIAL_CAPITAL * num_students:,}원
                    """)
                
                with guide_col2:
                    st.markdown("#### 💰 거스름돈 준비")
                    total_market = st.session_state.market_settings.get('total_money', 10000000)
                    st.write(f"**시장 총 화폐**: {total_market:,}원")
                    st.write("")
                    st.success(f"""
                    **거래용 화폐** (구매자 역할):
                    - 10만원권: 50장 이상
                    - 5만원권: 40장 이상
                    - 1만원권: 100장 이상
                    
                    **권장 총액**: {total_market:,}원
                    """)

# ==================== TAB 4: 도구 ====================
with tab4:
    st.header("🎯 게임 도구")
    
    tool_tab1, tool_tab2, tool_tab3, tool_tab4, tool_tab5 = st.tabs([
        "💰 수익 시뮬레이터",
        "📋 구매자 가이드",
        "📊 학습 리포트",
        "⚙️ 유형 밸런스",
        "🗑️ 데이터 관리"
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
                        "판매가 설정 (1만원 단위)",
                        min_value=0,
                        max_value=1000000,
                        value=student_data['recommended_price'],
                        step=10000,
                        help="실제 화폐 단위",
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
            
            # 학생별 구매 가격대 정보
            if st.session_state.students:
                st.markdown("### 📊 학생별 구매 가격 범위")
                st.caption("각 학생의 아이템에 대한 구매 조건")
                
                for name, data in st.session_state.students.items():
                    cost = data['cost']
                    
                    # 각 구매자 유형별 가격대
                    big_spender_range = f"{cost:,}원 ~ {int(cost * 2.5):,}원"
                    normal_range = f"{cost:,}원 ~ {int(cost * 2.0):,}원"
                    frugal_range = f"{cost:,}원 ~ {int(cost * 1.5):,}원"
                    
                    with st.expander(f"**{name}** - {data['business_type']}"):
                        guide_col1, guide_col2, guide_col3 = st.columns(3)
                        
                        with guide_col1:
                            st.markdown(f"""
                            **💎 큰손**  
                            {big_spender_range}  
                            (원가의 ~2.5배)
                            """)
                        
                        with guide_col2:
                            st.markdown(f"""
                            **😊 일반**  
                            {normal_range}  
                            (원가의 ~2.0배)
                            """)
                        
                        with guide_col3:
                            st.markdown(f"""
                            **💰 짠물**  
                            {frugal_range}  
                            (원가의 ~1.5배)
                            """)
                
                st.markdown("---")
            
            # 큰손
            st.markdown("### 💎 큰손 구매자 (상위 20%)")
            
            # 랜덤하게 캐릭터 선택
            selected_big_spenders = random.sample(BUYER_CHARACTERS["big_spender"], min(big_spender_count, len(BUYER_CHARACTERS["big_spender"])))
            
            for i, character in enumerate(selected_big_spenders, 1):
                with st.expander(f"{character['emoji']} 큰손 #{i}: {character['name']}"):
                    st.write(f"""
                    **👤 캐릭터**: {character['name']}  
                    **💰 예산**: {character['budget']}  
                    **🎯 특성**: {character['personality']}  
                    **📋 구매 조건**: **원가 ~ 원가의 2.5배** 가격이면 구매  
                    **💬 말투 예시**:  
                    - "{character['speech'][0]}"  
                    - "{character['speech'][1]}"  
                    - "{character['speech'][2]}"  
                    **🎪 행동 특징**: {character['behavior']}
                    """)
            
            # 일반
            st.markdown("### 😊 일반 구매자 (중간 50%)")
            
            # 랜덤하게 캐릭터 선택
            selected_normal = random.sample(BUYER_CHARACTERS["normal"], min(normal_count, len(BUYER_CHARACTERS["normal"])))
            
            for i, character in enumerate(selected_normal, 1):
                with st.expander(f"{character['emoji']} 일반 #{i}: {character['name']}"):
                    st.write(f"""
                    **👤 캐릭터**: {character['name']}  
                    **💰 예산**: {character['budget']}  
                    **🎯 특성**: {character['personality']}  
                    **📋 구매 조건**: **원가 ~ 원가의 2.0배** 가격이면 구매  
                    **💬 말투 예시**:  
                    - "{character['speech'][0]}"  
                    - "{character['speech'][1]}"  
                    - "{character['speech'][2]}"  
                    **🎪 행동 특징**: {character['behavior']}
                    """)
            
            # 짠물
            st.markdown("### 🤏 짠물 구매자 (하위 30%)")
            
            # 랜덤하게 캐릭터 선택
            selected_frugal = random.sample(BUYER_CHARACTERS["frugal"], min(frugal_count, len(BUYER_CHARACTERS["frugal"])))
            
            for i, character in enumerate(selected_frugal, 1):
                with st.expander(f"{character['emoji']} 짠물 #{i}: {character['name']}"):
                    st.write(f"""
                    **👤 캐릭터**: {character['name']}  
                    **💰 예산**: {character['budget']}  
                    **🎯 특성**: {character['personality']}  
                    **📋 구매 조건**: **원가 ~ 원가의 1.5배** 가격이면 구매  
                    **💬 말투 예시**:  
                    - "{character['speech'][0]}"  
                    - "{character['speech'][1]}"  
                    - "{character['speech'][2]}"  
                    **🎪 행동 특징**: {character['behavior']}
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
    
    with tool_tab4:
        st.subheader("⚙️ 유형 밸런스 조정")
        st.caption("게임 중에도 실시간으로 밸런스 조정 가능 (관리자 전용)")
        
        if not st.session_state.is_admin:
            st.warning("⚠️ 관리자 로그인이 필요합니다.")
        else:
            # 유형별 밸런스 편집
            for business_name, business_data in BUSINESS_TYPES.items():
                with st.expander(f"{business_name}", expanded=False):
                    balance_col1, balance_col2, balance_col3 = st.columns(3)
                    
                    with balance_col1:
                        new_cost = st.number_input(
                            "💰 원가",
                            min_value=10000,
                            max_value=500000,
                            value=business_data['cost'],
                            step=10000,
                            key=f"balance_cost_{business_name}"
                        )
                    
                    with balance_col2:
                        new_price = st.number_input(
                            "💵 추천 판매가",
                            min_value=10000,
                            max_value=1000000,
                            value=business_data['recommended_price'],
                            step=10000,
                            key=f"balance_price_{business_name}"
                        )
                    
                    with balance_col3:
                        if business_data['max_sales_per_10min']:
                            new_limit = st.number_input(
                                "⏱️ 10분 제한",
                                min_value=1,
                                max_value=50,
                                value=business_data['max_sales_per_10min'],
                                step=1,
                                key=f"balance_limit_{business_name}"
                            )
                        else:
                            st.write("⏱️ 10분 제한: 무제한")
                            new_limit = None
                    
                    # 마진율 자동 계산
                    if new_price > 0:
                        calc_margin = ((new_price - new_cost) / new_price) * 100
                        st.info(f"📊 계산된 마진율: {calc_margin:.1f}%")
                    
                    if st.button("✅ 이 유형 밸런스 적용", key=f"apply_balance_{business_name}"):
                        BUSINESS_TYPES[business_name]['cost'] = new_cost
                        BUSINESS_TYPES[business_name]['recommended_price'] = new_price
                        BUSINESS_TYPES[business_name]['margin_rate'] = (new_price - new_cost) / new_price
                        if business_data['max_sales_per_10min'] is not None:
                            BUSINESS_TYPES[business_name]['max_sales_per_10min'] = new_limit
                        
                        st.success(f"✅ {business_name} 밸런스 적용됨!")
                        st.balloons()
            
            st.markdown("---")
            
            # 전체 초기화
            if st.button("🔄 모든 유형 기본값으로 초기화", type="secondary", key="reset_business_types"):
                st.warning("⚠️ 개발 중: 페이지 새로고침하면 기본값으로 돌아갑니다")
    
    with tool_tab5:
        st.subheader("🗑️ 데이터 관리")
        st.caption("게임 데이터 초기화 및 백업 (관리자 전용)")
        
        if not st.session_state.is_admin:
            st.warning("⚠️ 관리자 로그인이 필요합니다.")
        else:
            st.markdown("### 📊 현재 데이터 현황")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("등록된 학생", f"{len(st.session_state.students)}명")
            with col2:
                st.metric("현재 라운드", f"{st.session_state.current_round}라운드")
            with col3:
                total_money = sum(s['final_capital'] for s in st.session_state.students.values())
                st.metric("총 유통 자본", f"{total_money:,}원")
            
            st.markdown("---")
            
            # 개별 학생 삭제
            st.markdown("### 🗑️ 개별 학생 삭제")
            
            if st.session_state.students:
                student_to_delete = st.selectbox(
                    "삭제할 학생 선택",
                    ["선택하세요"] + list(st.session_state.students.keys()),
                    key="student_to_delete"
                )
                
                if student_to_delete != "선택하세요":
                    if st.button(f"🗑️ {student_to_delete} 삭제", type="secondary", key="delete_single_student"):
                        del st.session_state.students[student_to_delete]
                        
                        if st.session_state.use_google_sheets and st.session_state.worksheet:
                            # Google Sheets에서도 삭제 (전체 다시 저장)
                            st.session_state.worksheet.clear()
                            headers = ["학생이름", "사업유형", "원가", "추천판매가", "초기자본", 
                                     "구매수량", "재고", "현재자본", "총매출", "총원가", "총순이익", 
                                     "최종자본", "실물소지금", "라운드데이터"]
                            st.session_state.worksheet.update('A1:N1', [headers])
                            
                            for name, data in st.session_state.students.items():
                                save_student_to_sheets(st.session_state.worksheet, name, data)
                        
                        st.success(f"✅ {student_to_delete}님이 삭제되었습니다!")
                        st.rerun()
            else:
                st.info("등록된 학생이 없습니다.")
            
            st.markdown("---")
            
            # 라운드 초기화
            st.markdown("### 🔄 라운드 초기화")
            st.caption("현재 라운드를 1라운드로 되돌립니다 (학생 데이터는 유지)")
            
            if st.button("🔄 라운드 초기화", type="secondary", key="reset_round"):
                st.session_state.current_round = 1
                st.success("✅ 라운드가 1라운드로 초기화되었습니다!")
                st.rerun()
            
            st.markdown("---")
            
            # 판매 기록 초기화
            st.markdown("### 📊 판매 기록 초기화")
            st.caption("모든 학생의 판매 기록, 재고, 자본을 초기 상태로 되돌립니다")
            
            if st.button("📊 판매 기록 초기화", type="secondary", key="reset_sales_records"):
                if st.session_state.get('confirm_reset_sales'):
                    for name in st.session_state.students:
                        st.session_state.students[name]['purchased_quantity'] = 0
                        st.session_state.students[name]['inventory'] = 0
                        st.session_state.students[name]['final_capital'] = st.session_state.students[name]['initial_capital']
                        st.session_state.students[name]['total_revenue'] = 0
                        st.session_state.students[name]['total_cost'] = 0
                        st.session_state.students[name]['total_profit'] = 0
                        st.session_state.students[name]['rounds'] = {1: {}, 2: {}}
                        st.session_state.students[name]['actual_money'] = 0
                        
                        if st.session_state.use_google_sheets and st.session_state.worksheet:
                            save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                    
                    st.session_state.current_round = 1
                    st.session_state['confirm_reset_sales'] = False
                    st.success("✅ 모든 판매 기록이 초기화되었습니다!")
                    st.rerun()
                else:
                    st.session_state['confirm_reset_sales'] = True
                    st.warning("⚠️ 한 번 더 클릭하여 초기화 확인")
            
            st.markdown("---")
            
            # 전체 데이터 초기화
            st.markdown("### ⚠️ 전체 데이터 초기화")
            st.caption("⚠️ 모든 학생 데이터와 기록을 삭제합니다 (복구 불가능)")
            
            if st.button("🗑️ 전체 데이터 삭제", type="secondary", key="delete_all_data"):
                if st.session_state.get('confirm_delete_all'):
                    st.session_state.students = {}
                    st.session_state.current_round = 1
                    st.session_state.final_reveal = False
                    
                    if st.session_state.use_google_sheets and st.session_state.worksheet:
                        delete_all_students_from_sheets(st.session_state.worksheet)
                    
                    st.session_state['confirm_delete_all'] = False
                    st.success("✅ 모든 데이터가 삭제되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.session_state['confirm_delete_all'] = True
                    st.error("⚠️ 경고: 한 번 더 클릭하면 모든 데이터가 삭제됩니다!")

st.markdown("---")
st.caption("🏪 장사의 신 게임 관리 시스템 V2 - 실전 창업 시뮬레이션")
