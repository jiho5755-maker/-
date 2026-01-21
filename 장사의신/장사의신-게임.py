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
import plotly.graph_objects as go
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="🏪 장사의 신 게임 관리 시스템 V2",
    page_icon="💰",
    layout="wide"
)

# ==================== 상수 정의 ====================

# 초기 자본금
INITIAL_CAPITAL = 500000

# 구매자 캐릭터 프로필 V2 (현실적인 가격 범위 포함)
BUYER_CHARACTERS = {
    "big_spender": [  # 최상위 6명 (큰손)
        {
            "name": "사업가 김사장",
            "emoji": "💼",
            "budget": "2,000,000원",
            "numeric_budget": 2000000,
            "personality": "투자 가치 중시, 사업 확장성 평가",
            "price_multiplier": {"min": 1.8, "max": 3.0, "sweet": 2.3},
            "category_bonus": {"서비스": 1.3, "제조": 1.2, "유통": 0.9, "대여": 1.0, "지식": 1.1},
            "speech": ["이거 사업성 있어 보이네요", "투자 가치가 있으면 비싸도 괜찮아요", "품질이 중요하죠"],
            "behavior": "사업 아이템을 평가하듯 질문하고, 확장 가능성을 물어봄"
        },
        {
            "name": "연예인 박스타",
            "emoji": "⭐",
            "budget": "1,500,000원",
            "numeric_budget": 1500000,
            "personality": "트렌디하고 유명한 것 선호, SNS 감성",
            "price_multiplier": {"min": 2.0, "max": 3.5, "sweet": 2.6},
            "category_bonus": {"서비스": 1.0, "제조": 1.5, "유통": 1.3, "대여": 0.8, "지식": 0.9},
            "speech": ["인스타에 올리면 좋겠어요", "요즘 유행하는 거예요?", "이거 힙하네요!"],
            "behavior": "SNS 찍기 좋은지 확인하고, 트렌드에 민감함"
        },
        {
            "name": "의사 이원장",
            "emoji": "⚕️",
            "budget": "1,200,000원",
            "numeric_budget": 1200000,
            "personality": "건강과 품질 최우선, 전문가적 안목",
            "price_multiplier": {"min": 1.9, "max": 3.2, "sweet": 2.5},
            "category_bonus": {"서비스": 1.4, "제조": 1.3, "유통": 0.8, "대여": 0.7, "지식": 1.2},
            "speech": ["건강에 좋은가요?", "품질 보증이 되나요?", "성분이 뭐예요?"],
            "behavior": "꼼꼼하게 따져보지만, 마음에 들면 확실하게 구매"
        },
        {
            "name": "변호사 최법사",
            "emoji": "⚖️",
            "budget": "1,000,000원",
            "numeric_budget": 1000000,
            "personality": "논리적이고 분석적, 계약 조건 중시",
            "price_multiplier": {"min": 1.7, "max": 2.8, "sweet": 2.2},
            "category_bonus": {"서비스": 1.2, "제조": 1.0, "유통": 0.9, "대여": 1.0, "지식": 1.4},
            "speech": ["근거가 뭐죠?", "이 가격이 합리적인 이유가?", "보증은 되나요?"],
            "behavior": "논리적으로 설득되면 구매, 근거 있는 설명 선호"
        },
        {
            "name": "건물주 박건물",
            "emoji": "🏢",
            "budget": "1,000,000원",
            "numeric_budget": 1000000,
            "personality": "여유롭고 느긋함, 마음에 들면 즉시 구매",
            "price_multiplier": {"min": 1.6, "max": 3.0, "sweet": 2.3},
            "category_bonus": {"서비스": 1.1, "제조": 1.1, "유통": 1.0, "대여": 1.2, "지식": 0.9},
            "speech": ["그래요? 재밌네요", "좋아 보이면 사죠", "얼마예요? 아 괜찮네요"],
            "behavior": "친절하고 여유있게 대화, 느낌으로 판단"
        },
        {
            "name": "재벌 3세 윤도련",
            "emoji": "💎",
            "budget": "1,800,000원",
            "numeric_budget": 1800000,
            "personality": "명품 선호, 독특하고 희귀한 것 좋아함",
            "price_multiplier": {"min": 2.2, "max": 4.0, "sweet": 3.0},
            "category_bonus": {"서비스": 1.2, "제조": 1.6, "유통": 0.7, "대여": 1.0, "지식": 0.8},
            "speech": ["이거 한정판이에요?", "특별한 게 뭐예요?", "다른 데는 없죠?"],
            "behavior": "독특함과 희소성에 끌림, 프리미엄 선호"
        }
    ],
    "normal": [  # 중간층 6명
        {
            "name": "직장인 김대리",
            "emoji": "💼",
            "budget": "600,000원",
            "numeric_budget": 600000,
            "personality": "실용적이고 가성비 중시, 급여날 여유",
            "price_multiplier": {"min": 1.3, "max": 2.0, "sweet": 1.6},
            "category_bonus": {"서비스": 0.9, "제조": 1.0, "유통": 1.2, "대여": 1.0, "지식": 1.3},
            "speech": ["가성비 괜찮은가요?", "이 가격이면 적당하네요", "실용적인가요?"],
            "behavior": "꼼꼼하게 비교하고, 합리적이면 구매"
        },
        {
            "name": "대학생 이학생",
            "emoji": "🎓",
            "budget": "400,000원",
            "numeric_budget": 400000,
            "personality": "알바비 받은 날, 자기 보상 원함",
            "price_multiplier": {"min": 1.2, "max": 1.9, "sweet": 1.5},
            "category_bonus": {"서비스": 0.8, "제조": 1.2, "유통": 1.1, "대여": 0.9, "지식": 1.0},
            "speech": ["알바비 받았는데", "나한테 선물하려고요", "이거 힙한 거 맞죠?"],
            "behavior": "트렌디하고 자기만족 되는 것 선호"
        },
        {
            "name": "신혼부부 박신혼",
            "emoji": "💑",
            "budget": "700,000원",
            "numeric_budget": 700000,
            "personality": "신혼집 꾸미기, 실용적이면서 예쁜 것",
            "price_multiplier": {"min": 1.4, "max": 2.1, "sweet": 1.7},
            "category_bonus": {"서비스": 1.3, "제조": 1.2, "유통": 1.0, "대여": 1.1, "지식": 0.9},
            "speech": ["신혼집에 어울릴까요?", "배우자가 좋아할까요?", "실용적이에요?"],
            "behavior": "파트너와 상의하는 듯한 제스처, 신중하게 선택"
        },
        {
            "name": "프리랜서 최자유",
            "emoji": "💻",
            "budget": "500,000원",
            "numeric_budget": 500000,
            "personality": "자유로운 영혼, 창의적인 것 선호",
            "price_multiplier": {"min": 1.3, "max": 2.2, "sweet": 1.7},
            "category_bonus": {"서비스": 1.0, "제조": 1.4, "유통": 0.9, "대여": 1.0, "지식": 1.2},
            "speech": ["독특하네요", "창의적이에요", "이거 재밌겠다"],
            "behavior": "독창성과 재미를 중시, 감성적 구매"
        },
        {
            "name": "교사 강선생",
            "emoji": "📚",
            "budget": "550,000원",
            "numeric_budget": 550000,
            "personality": "교육적 가치 중시, 의미있는 구매",
            "price_multiplier": {"min": 1.3, "max": 2.0, "sweet": 1.6},
            "category_bonus": {"서비스": 0.9, "제조": 1.1, "유통": 1.0, "대여": 1.0, "지식": 1.5},
            "speech": ["교육적으로 좋네요", "학생들한테 보여줄까?", "의미있는 것 같아요"],
            "behavior": "스토리와 가치를 중시, 설명을 잘 들음"
        },
        {
            "name": "간호사 윤간호",
            "emoji": "💉",
            "budget": "500,000원",
            "numeric_budget": 500000,
            "personality": "실용성과 편리성 중시, 야근 많아 간편한 것",
            "price_multiplier": {"min": 1.2, "max": 1.8, "sweet": 1.5},
            "category_bonus": {"서비스": 1.4, "제조": 0.9, "유통": 1.0, "대여": 1.1, "지식": 1.0},
            "speech": ["편리한가요?", "관리하기 쉬워요?", "바빠도 괜찮을까요?"],
            "behavior": "실용적이고 편리한 것 우선, 빠른 결정"
        }
    ],
    "frugal": [  # 짠물파 6명
        {
            "name": "주부 김알뜰",
            "emoji": "🏠",
            "budget": "250,000원",
            "numeric_budget": 250000,
            "personality": "집안 살림 책임, 한 푼이 아까움",
            "price_multiplier": {"min": 1.0, "max": 1.5, "sweet": 1.2},
            "category_bonus": {"서비스": 0.7, "제조": 0.9, "유통": 1.2, "대여": 1.0, "지식": 0.8},
            "speech": ["너무 비싼데...", "좀 깎아주세요", "집에 돈 쓸 데가 많아서"],
            "behavior": "가격 흥정 시도, 할인 여부 확인"
        },
        {
            "name": "은퇴자 박은퇴",
            "emoji": "👴",
            "budget": "200,000원",
            "numeric_budget": 200000,
            "personality": "연금 생활, 아껴서 써야 함",
            "price_multiplier": {"min": 1.0, "max": 1.4, "sweet": 1.1},
            "category_bonus": {"서비스": 0.8, "제조": 0.9, "유통": 1.1, "대여": 0.9, "지식": 0.9},
            "speech": ["연금으로 살아서...", "꼭 필요한 것만", "더 싼 거 없어요?"],
            "behavior": "필요성을 따져봄, 매우 신중함"
        },
        {
            "name": "취준생 이준비",
            "emoji": "📝",
            "budget": "180,000원",
            "numeric_budget": 180000,
            "personality": "취업 준비 중, 돈이 너무 없음",
            "price_multiplier": {"min": 1.0, "max": 1.5, "sweet": 1.2},
            "category_bonus": {"서비스": 0.7, "제조": 0.9, "유통": 1.1, "대여": 0.8, "지식": 1.2},
            "speech": ["취업하면 사야지...", "지금은 너무 비싸요", "할인 안 되나요?"],
            "behavior": "사고 싶지만 참는 모습, 가격에 매우 민감"
        },
        {
            "name": "알바생 최최저",
            "emoji": "🍔",
            "budget": "150,000원",
            "numeric_budget": 150000,
            "personality": "최저시급, 아껴서 모으는 중",
            "price_multiplier": {"min": 1.0, "max": 1.4, "sweet": 1.1},
            "category_bonus": {"서비스": 0.7, "제조": 0.8, "유통": 1.2, "대여": 0.9, "지식": 0.9},
            "speech": ["한 시간 일해야 버는 돈인데", "너무 비싸요", "반값 안 되나요?"],
            "behavior": "시간당 임금으로 환산해서 생각, 아까워함"
        },
        {
            "name": "대학원생 박논문",
            "emoji": "📖",
            "budget": "220,000원",
            "numeric_budget": 220000,
            "personality": "등록금 내고 남은 돈, 라면으로 연명",
            "price_multiplier": {"min": 1.0, "max": 1.5, "sweet": 1.2},
            "category_bonus": {"서비스": 0.7, "제조": 0.8, "유통": 1.1, "대여": 0.9, "지식": 1.3},
            "speech": ["대학원생이라...", "이거 꼭 필요한가요?", "더 싼 거요?"],
            "behavior": "필요성 따지고, 가격 협상 시도"
        },
        {
            "name": "신입사원 이막내",
            "emoji": "👔",
            "budget": "300,000원",
            "numeric_budget": 300000,
            "personality": "첫 월급인데 쓸 데가 많음, 빚도 있음",
            "price_multiplier": {"min": 1.0, "max": 1.5, "sweet": 1.2},
            "category_bonus": {"서비스": 0.8, "제조": 0.9, "유통": 1.1, "대여": 1.0, "지식": 1.1},
            "speech": ["첫 월급인데 빠듯해서", "할부 되나요?", "조금만 깎아주세요"],
            "behavior": "사고 싶지만 가격 부담, 망설임"
        }
    ]
}

# ==================== 사업 유형 초기화 함수 ====================
def init_default_business_types():
    """기본 사업 유형 반환"""
    return {
        "🛒 골라오기 (유통)": {
            "cost": 20000,
            "recommended_price": 40000,
            "margin_rate": 0.50,
            "max_sales_per_10min": None,
            "description": "물건을 사서 되파는 사업 (재고 부담, 회전율 승부)",
            "target": "짠물 + 일반",
            "strategy": "많이 팔아서 회전율로 승부. 재고 관리가 핵심!",
            "key": "distribution"
        },
        "🔨 뚝딱뚝딱 (제조)": {
            "cost": 60000,
            "recommended_price": 120000,
            "margin_rate": 0.50,
            "max_sales_per_10min": 8,
            "description": "직접 만들어서 파는 사업 (시간 제약, 장인정신)",
            "target": "일반 + 큰손",
            "strategy": "만들 수 있는 만큼만 재료 구매. 고품질 프리미엄!",
            "key": "manufacturing"
        },
        "🏃 대신하기 (서비스)": {
            "cost": 30000,
            "recommended_price": 150000,
            "margin_rate": 0.80,
            "max_sales_per_10min": 5,
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
            "margin_rate": 0.43,
            "max_sales_per_10min": 6,
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
        {"name": "📱 SNS 입소문", "effect": "다음 판매량 +30%", "impact": {"sales_boost": 0.3}, "duration": 1},
        {"name": "🎉 명절 특수", "effect": "판매가 +20% 적용", "impact": {"price_boost": 0.2}, "duration": 1},
        {"name": "🌟 언론 보도", "effect": "이번 라운드 판매 +2개", "impact": {"guaranteed_sales": 2}, "duration": 1},
        {"name": "🎁 단골 고객", "effect": "무조건 판매 1건 성공", "impact": {"guaranteed_sales": 1}, "duration": 1},
        {"name": "💎 VIP 고객 방문", "effect": "판매가 2배 받기", "impact": {"price_multiplier": 2.0}, "duration": 1},
        {"name": "🎊 대박 이벤트", "effect": "수익 +50%", "impact": {"profit_boost": 0.5}, "duration": 1},
        {"name": "📸 인플루언서 방문", "effect": "다음 라운드 판매량 2배", "impact": {"sales_multiplier": 2.0}, "duration": 2},
        {"name": "🏆 우수 매장 선정", "effect": "고객 신뢰도 UP, 가격 +15%", "impact": {"price_boost": 0.15}, "duration": 2},
    ],
    "negative": [
        {"name": "⚠️ 경쟁자 등장", "effect": "판매가 -15% 강제", "impact": {"price_penalty": 0.15}, "duration": 1},
        {"name": "📉 재료비 상승", "effect": "원가 +30% 증가", "impact": {"cost_increase": 0.3}, "duration": 2},
        {"name": "🌧️ 악천후", "effect": "판매량 -50%", "impact": {"sales_penalty": 0.5}, "duration": 1},
        {"name": "💸 임대료 인상", "effect": "고정비 50,000원 추가", "impact": {"fixed_cost": 50000}, "duration": 1},
        {"name": "🚨 제품 하자", "effect": "판매 중단 & 환불 -30,000원", "impact": {"refund": 30000, "sales_stop": True}, "duration": 1},
        {"name": "😷 직원 결근", "effect": "운영 비용 +20,000원", "impact": {"operating_cost": 20000}, "duration": 1},
        {"name": "⚡ 정전 사고", "effect": "이번 라운드 판매량 -3개", "impact": {"sales_reduction": 3}, "duration": 1},
    ],
    "neutral": [
        {"name": "🎲 행운의 주사위", "effect": "랜덤 효과 (좋을수도, 나쁠수도)", "impact": {"random": True}, "duration": 1},
        {"name": "📰 시장 조사", "effect": "경쟁자 정보 공개", "impact": {"info_reveal": True}, "duration": 1},
        {"name": "🔄 재고 교환권", "effect": "재고 일부 현금화 가능", "impact": {"inventory_cash": 0.7}, "duration": 1},
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

# ==================== 경제 시스템 V2 ====================

class MarketEconomyEngine:
    """
    게임 밸런스를 유지하면서 실제 경제 원리를 반영하는 시스템
    """
    
    def __init__(self, market_settings, initial_capital):
        self.market_money = max(market_settings.get('total_money', 10000000), 1000000)
        self.buyer_count = max(market_settings.get('total_buyers', 10), 3)
        self.initial_capital = initial_capital
        self.game_mode = market_settings.get('game_mode', '전략 모드')
        
        # 게임 밸런스 기준선
        self.BALANCE_CONSTANTS = {
            'TARGET_MARGIN_MIN': 1.5,
            'TARGET_MARGIN_MAX': 2.5,
            'MIN_PURCHASE_QUANTITY': 5,
            'COST_TO_CAPITAL_RATIO_MIN': 0.15,
            'COST_TO_CAPITAL_RATIO_MAX': 0.35,
            'EXPECTED_STUDENTS_MIN': 5,
            'EXPECTED_STUDENTS_MAX': 10,
            'SATURATION_HEALTHY_MAX': 0.8,
            'COMPETITION_BALANCED': 1.0,
        }
    
    def calculate_safe_economics(self, current_students_count=0):
        """안전장치가 포함된 경제 지표 계산"""
        
        # 예상 학생 수
        expected_total_students = self._estimate_total_students(current_students_count)
        
        # 1인당 평균 구매력
        avg_buying_power = self.market_money / self.buyer_count
        
        # 총 예상 공급 자본
        total_supply = self.initial_capital * expected_total_students
        
        # 시장 포화도 (안전 범위: 0.2 ~ 1.5)
        raw_saturation = total_supply / self.market_money
        market_saturation = max(0.2, min(raw_saturation, 1.5))
        
        # 경쟁 강도 (안전 범위: 0.3 ~ 2.0)
        raw_competition = expected_total_students / self.buyer_count
        competition_intensity = max(0.3, min(raw_competition, 2.0))
        
        # 기준 가격 레벨
        base_price_level = avg_buying_power / 1000000
        
        # 포화도 보정
        saturation_factor = 1.0 if market_saturation <= 0.8 else (0.8 / market_saturation)
        price_level = base_price_level * saturation_factor
        
        # 원가 범위 계산
        cost_by_capital_min = self.initial_capital * self.BALANCE_CONSTANTS['COST_TO_CAPITAL_RATIO_MIN']
        cost_by_capital_max = self.initial_capital * self.BALANCE_CONSTANTS['COST_TO_CAPITAL_RATIO_MAX']
        
        cost_by_market_min = avg_buying_power * 0.05
        cost_by_market_max = avg_buying_power * 0.20
        
        ABSOLUTE_MIN_COST = 10000
        ABSOLUTE_MAX_COST = 200000
        
        optimal_min_cost = max(cost_by_capital_min, cost_by_market_min * 0.8, ABSOLUTE_MIN_COST)
        optimal_max_cost = min(cost_by_capital_max, cost_by_market_max * 1.2, ABSOLUTE_MAX_COST)
        
        if optimal_min_cost >= optimal_max_cost:
            mid_cost = (cost_by_capital_min + cost_by_market_max) / 2
            optimal_min_cost = mid_cost * 0.8
            optimal_max_cost = mid_cost * 1.2
        
        optimal_min_cost = self._round_to_10k(optimal_min_cost)
        optimal_max_cost = self._round_to_10k(optimal_max_cost)
        
        # 마진율 계산
        if competition_intensity >= 1.5:
            markup_range = (1.3, 1.7)
            strategy = "저마진 고회전"
            risk_level = "높음"
        elif competition_intensity >= 1.0:
            markup_range = (1.5, 2.0)
            strategy = "균형 전략"
            risk_level = "보통"
        elif competition_intensity >= 0.6:
            markup_range = (1.8, 2.3)
            strategy = "적정 마진"
            risk_level = "낮음"
        else:
            markup_range = (2.0, 2.5)
            strategy = "고마진 전략"
            risk_level = "매우 낮음"
        
        market_health = self._diagnose_market_health(market_saturation, competition_intensity, price_level)
        recommendations = self._generate_recommendations(market_saturation, competition_intensity, current_students_count)
        
        return {
            'market_money': self.market_money,
            'buyer_count': self.buyer_count,
            'expected_students': expected_total_students,
            'initial_capital': self.initial_capital,
            'avg_buying_power': int(avg_buying_power),
            'market_saturation': round(market_saturation, 2),
            'competition_intensity': round(competition_intensity, 2),
            'price_level': round(price_level, 2),
            'optimal_min_cost': int(optimal_min_cost),
            'optimal_max_cost': int(optimal_max_cost),
            'markup_min': markup_range[0],
            'markup_max': markup_range[1],
            'strategy': strategy,
            'risk_level': risk_level,
            'market_health': market_health,
            'recommendations': recommendations,
            'warnings': self._generate_warnings(market_saturation, competition_intensity),
            'educational_insight': self._generate_educational_insight(avg_buying_power, market_saturation, competition_intensity)
        }
    
    def _estimate_total_students(self, current_count):
        """예상 총 학생 수 추정"""
        if current_count == 0:
            return 7
        elif current_count <= 3:
            return 8
        elif current_count <= 6:
            return current_count + 2
        else:
            return current_count
    
    def _round_to_10k(self, value):
        """10,000원 단위로 반올림"""
        return int(round(value / 10000) * 10000)
    
    def _diagnose_market_health(self, saturation, competition, price_level):
        """시장 건강도 진단"""
        if saturation > 1.2 and competition > 1.5:
            return {'status': '🔥 과열', 'description': '공급 과잉, 치열한 경쟁', 'color': 'error'}
        elif saturation > 0.9 and competition > 1.2:
            return {'status': '⚠️ 포화', 'description': '경쟁 심화, 차별화 필요', 'color': 'warning'}
        elif saturation < 0.5 and competition < 0.7:
            return {'status': '💎 블루오션', 'description': '기회의 시장, 높은 마진 가능', 'color': 'success'}
        elif saturation < 0.8 and competition < 1.0:
            return {'status': '✅ 건강', 'description': '균형 잡힌 시장', 'color': 'info'}
        else:
            return {'status': '📊 보통', 'description': '표준적인 시장 환경', 'color': 'info'}
    
    def _generate_recommendations(self, saturation, competition, current_students):
        """상황별 권장사항"""
        recs = []
        if saturation > 1.0:
            recs.append("💡 공급이 많습니다. 가격을 낮추거나 차별화하세요.")
        if competition > 1.3:
            recs.append("💡 경쟁이 치열합니다. 독특한 아이템이나 서비스로 차별화하세요.")
        if current_students >= 8:
            recs.append("💡 학생이 많습니다. 틈새 시장을 공략하세요.")
        if saturation < 0.5:
            recs.append("💡 수요가 풍부합니다. 품질을 높이고 프리미엄 가격을 책정하세요.")
        return recs if recs else ["✅ 좋은 시장 환경입니다. 표준 전략을 사용하세요."]
    
    def _generate_warnings(self, saturation, competition):
        """경고 메시지"""
        warnings = []
        if saturation > 1.3:
            warnings.append("⚠️ 심각한 공급 과잉! 판매가 어려울 수 있습니다.")
        if competition > 1.8:
            warnings.append("⚠️ 과도한 경쟁! 가격 경쟁에 빠질 위험이 있습니다.")
        return warnings
    
    def _generate_educational_insight(self, buying_power, saturation, competition):
        """교육적 인사이트"""
        if self.game_mode == "간단 모드":
            return f"1인당 구매력은 {buying_power:,}원입니다. 이 정도 가격이면 살 수 있을까요?"
        else:
            supply_demand = "공급 > 수요" if saturation > 0.8 else "수요 > 공급"
            competition_desc = "학생이 많아 경쟁 치열" if competition > 1.0 else "독점 기회 있음"
            return f"""**경제 원리 이해하기:**
- 1인당 구매력: {buying_power:,}원 → 이것이 가격 기준선입니다
- 시장 포화도: {saturation:.2f} → {supply_demand}
- 경쟁 강도: {competition:.2f} → {competition_desc}

실제 시장에서도 이런 요소들이 가격을 결정합니다!"""
    
    def calculate_optimal_price_by_buyer_segments(self, cost, business_type, buyer_characters):
        """구매자 세그먼트별 최적 가격 계산"""
        all_budgets = []
        all_sweet_spots = []
        
        # 모든 구매자 타입의 예산과 선호 가격 수집
        for buyer_type in ["big_spender", "normal", "frugal"]:
            for buyer in buyer_characters.get(buyer_type, []):
                if "numeric_budget" in buyer:
                    all_budgets.append(buyer["numeric_budget"])
                
                # 각 구매자의 스윗스팟 계산
                price_range = calculate_buyer_price_range(buyer, cost, business_type)
                all_sweet_spots.append(price_range["sweet_spot"])
        
        if not all_budgets or not all_sweet_spots:
            # Fallback: 기본 마진율 적용
            return {
                "recommended_price": int(cost * 2.0),
                "price_min": int(cost * 1.5),
                "price_max": int(cost * 2.5),
                "target_segment": "전체"
            }
        
        # 통계 분석
        avg_budget = sum(all_budgets) / len(all_budgets)
        median_sweet = sorted(all_sweet_spots)[len(all_sweet_spots) // 2]
        
        # 예산 세그먼트 분석
        high_budget = [b for b in all_budgets if b >= 1000000]
        mid_budget = [b for b in all_budgets if 400000 <= b < 1000000]
        low_budget = [b for b in all_budgets if b < 400000]
        
        # 타겟 세그먼트 결정
        if cost * 2.5 <= sum(low_budget) / max(len(low_budget), 1):
            target_segment = "짠물파 (가성비)"
            recommended_price = int(cost * 1.3)
            price_range = (int(cost * 1.2), int(cost * 1.5))
        elif cost * 2.0 <= sum(mid_budget) / max(len(mid_budget), 1):
            target_segment = "일반 고객 (균형)"
            recommended_price = int(cost * 1.7)
            price_range = (int(cost * 1.4), int(cost * 2.0))
        else:
            target_segment = "큰손 (프리미엄)"
            recommended_price = int(cost * 2.3)
            price_range = (int(cost * 1.8), int(cost * 3.0))
        
        # 10,000원 단위 반올림
        recommended_price = int(round(recommended_price / 10000) * 10000)
        price_range = (
            int(round(price_range[0] / 10000) * 10000),
            int(round(price_range[1] / 10000) * 10000)
        )
        
        return {
            "recommended_price": recommended_price,
            "price_min": price_range[0],
            "price_max": price_range[1],
            "target_segment": target_segment,
            "median_sweet_spot": median_sweet,
            "avg_buyer_budget": int(avg_budget)
        }

def calculate_buyer_price_range(buyer, item_cost, business_type):
    """
    구매자별 실제 구매 가능 가격 범위 계산
    """
    # 기본 배수 (기존 시스템과 호환)
    if "price_multiplier" in buyer:
        min_mult = buyer["price_multiplier"]["min"]
        max_mult = buyer["price_multiplier"]["max"]
        sweet_mult = buyer["price_multiplier"]["sweet"]
    else:
        # fallback: 기존 시스템
        if "1,000,000" in buyer.get("budget", ""):
            min_mult, max_mult, sweet_mult = 1.8, 3.0, 2.3
        elif "500,000" in buyer.get("budget", ""):
            min_mult, max_mult, sweet_mult = 1.3, 2.0, 1.6
        else:
            min_mult, max_mult, sweet_mult = 1.0, 1.5, 1.2
    
    # 카테고리 보너스
    category_key = "유통" if "골라오기" in business_type else \
                  "제조" if "뚝딱뚝딱" in business_type else \
                  "서비스" if "대신하기" in business_type else \
                  "대여" if "빌려주기" in business_type else \
                  "지식" if "알려주기" in business_type else "유통"
    
    if "category_bonus" in buyer:
        bonus = buyer["category_bonus"].get(category_key, 1.0)
    else:
        bonus = 1.0
    
    # 최종 가격 범위
    price_min = int(item_cost * min_mult * bonus)
    price_max = int(item_cost * max_mult * bonus)
    price_sweet = int(item_cost * sweet_mult * bonus)
    
    # 10,000원 단위 반올림
    price_min = int(round(price_min / 10000) * 10000)
    price_max = int(round(price_max / 10000) * 10000)
    price_sweet = int(round(price_sweet / 10000) * 10000)
    
    return {
        "min": price_min,
        "max": price_max,
        "sweet_spot": price_sweet
    }

def get_ai_recommendation_with_economics(idea, market_settings, students):
    """
    경제 시스템을 반영한 AI 추천
    """
    try:
        # 경제 지표 계산
        economy = MarketEconomyEngine(market_settings, INITIAL_CAPITAL)
        economics = economy.calculate_safe_economics(len(students))
        
        # OpenAI 키 확인
        openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
        if not openai_api_key:
            return _generate_rule_based_recommendation(idea, economics)
        
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        # AI 프롬프트 생성
        prompt = f"""
다음 학생의 창업 아이디어를 분석하고, 현재 경제 환경에 최적화된 설정을 추천해주세요.

📝 학생 아이디어: {idea}

🏦 경제 환경:
- 1인당 구매력: {economics['avg_buying_power']:,}원 (가격 기준선)
- 시장 포화도: {economics['market_saturation']} ({economics['market_health']['description']})
- 경쟁 강도: {economics['competition_intensity']} ({economics['strategy']})
- 적정 원가 범위: {economics['optimal_min_cost']:,}원 ~ {economics['optimal_max_cost']:,}원
- 적정 마진율: {economics['markup_min']:.1f}배 ~ {economics['markup_max']:.1f}배

📋 비즈니스 유형: {', '.join(st.session_state.business_types.keys())}

다음을 JSON 형식으로 답변:
{{
    "recommended_type": "추천 유형 (위 목록 중 1개)",
    "cost": "원가 ({economics['optimal_min_cost']} ~ {economics['optimal_max_cost']} 범위 내)",
    "price_range_min": "최저 판매가 (원가 × {economics['markup_min']:.1f} 이상)",
    "price_range_max": "최고 판매가 (원가 × {economics['markup_max']:.1f} 이하)",
    "max_sales_per_10min": "10분 제한 (숫자 또는 null)",
    "reason": "이 경제 환경에 적합한 이유",
    "strategy": "가격 전략"
}}

**필수:** 모든 금액은 10,000원 단위로 반올림
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 창업 교육 전문가이자 게임 경제 디자이너입니다. 반드시 JSON 형식으로만 답변하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        ai_result = json.loads(response.choices[0].message.content)
        
        # 유효성 검증 및 보정
        validated = _validate_ai_response(ai_result, economics)
        validated['economics'] = economics
        validated['source'] = 'ai'
        
        return validated
        
    except Exception as e:
        # AI 실패 시 규칙 기반 fallback
        economy = MarketEconomyEngine(market_settings, INITIAL_CAPITAL)
        economics = economy.calculate_safe_economics(len(students))
        result = _generate_rule_based_recommendation(idea, economics)
        result['source'] = 'fallback'
        result['error'] = str(e)
        return result

def _validate_ai_response(ai_data, economics):
    """AI 응답 검증 및 보정"""
    validated = {}
    
    # 유형
    validated['recommended_type'] = ai_data.get('recommended_type', '🛒 골라오기 (유통)')
    
    # 원가
    cost = int(ai_data.get('cost', economics['optimal_min_cost']))
    cost = max(economics['optimal_min_cost'], min(cost, economics['optimal_max_cost']))
    cost = int(round(cost / 10000) * 10000)
    validated['cost'] = cost
    
    # 판매가 범위
    price_min = int(ai_data.get('price_range_min', cost * economics['markup_min']))
    price_max = int(ai_data.get('price_range_max', cost * economics['markup_max']))
    
    # 마진율 검증
    if price_min < cost * economics['markup_min'] * 0.9:
        price_min = int(cost * economics['markup_min'])
    if price_max > cost * economics['markup_max'] * 1.1:
        price_max = int(cost * economics['markup_max'])
    
    validated['price_range_min'] = int(round(price_min / 10000) * 10000)
    validated['price_range_max'] = int(round(price_max / 10000) * 10000)
    validated['max_sales_per_10min'] = ai_data.get('max_sales_per_10min')
    validated['reason'] = ai_data.get('reason', '시장 환경을 고려한 추천입니다.')
    validated['strategy'] = ai_data.get('strategy', economics['strategy'])
    
    return validated

def _generate_rule_based_recommendation(idea, economics):
    """규칙 기반 추천 (AI 실패 시)"""
    idea_lower = idea.lower()
    
    if any(word in idea_lower for word in ['만들', '제작', '손수', '직접']):
        recommended_type = "🔨 뚝딱뚝딱 (제조)"
    elif any(word in idea_lower for word in ['대신', '서비스', '도와']):
        recommended_type = "🏃 대신하기 (서비스)"
    elif any(word in idea_lower for word in ['빌려', '대여', '렌탈']):
        recommended_type = "🎪 빌려주기 (대여)"
    else:
        recommended_type = "🛒 골라오기 (유통)"
    
    cost = (economics['optimal_min_cost'] + economics['optimal_max_cost']) // 2
    cost = int(round(cost / 10000) * 10000)
    
    price_min = int(cost * economics['markup_min'])
    price_max = int(cost * economics['markup_max'])
    
    return {
        'recommended_type': recommended_type,
        'cost': cost,
        'price_range_min': price_min,
        'price_range_max': price_max,
        'max_sales_per_10min': 8,
        'reason': f"시장 환경을 고려한 추천입니다. ({economics['strategy']})",
        'strategy': economics['strategy'],
        'economics': economics
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

def delete_student_from_sheets(worksheet, name):
    """Google Sheets에서 학생 데이터를 삭제합니다."""
    if not worksheet:
        return False
    
    try:
        all_values = worksheet.get_all_values()
        row_index = None
        
        for idx, row in enumerate(all_values[1:], start=2):
            if row[0] == name:
                row_index = idx
                break
        
        if row_index:
            worksheet.delete_rows(row_index)
            time.sleep(1.0)
            return True
        else:
            return False
    except Exception as e:
        st.error(f"데이터 삭제 오류: {str(e)}")
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

# 사업 유형 초기화 (동적 관리 가능)
if 'business_types' not in st.session_state:
    st.session_state.business_types = init_default_business_types()

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
    
    # 초기 자본금 설정 추가
    new_initial_capital = st.sidebar.number_input(
        "💵 초기 자본금",
        min_value=100000,
        max_value=10000000,
        value=st.session_state.market_settings.get('initial_capital', INITIAL_CAPITAL),
        step=10000,
        help="모든 학생에게 동일하게 지급되는 시작 자본금 (1만원 단위)"
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
            'initial_capital': new_initial_capital,
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
    **💵 초기 자본금**: {st.session_state.market_settings.get('initial_capital', INITIAL_CAPITAL):,}원
    """)

st.sidebar.markdown("---")
# 초기 자본금은 이제 시장 설정에서 조정 가능하므로 제거
# st.sidebar.markdown("### 💵 초기 자본금")
# st.sidebar.success(f"**{INITIAL_CAPITAL:,}원**")
# st.sidebar.caption("모든 학생 동일")

# ==================== 사업 유형 관리 (관리자 전용) ====================
if st.session_state.is_admin:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏭 사업 유형 관리")
    
    with st.sidebar.expander("📋 사업 유형 목록", expanded=False):
        for business_name, business_data in st.session_state.business_types.items():
            st.caption(f"**{business_name}**")
            st.caption(f"💰 원가: {business_data['cost']:,}원 | 💸 추천가: {business_data['recommended_price']:,}원")
    
    with st.sidebar.expander("➕ 새 사업 유형 추가", expanded=False):
        new_business_name = st.text_input("사업 유형 이름 (예: 🎨 그림그리기 (창작))", key="new_business_name")
        new_business_cost = st.number_input("원가 (원)", min_value=1000, max_value=1000000, value=30000, step=1000, key="new_business_cost")
        new_business_price = st.number_input("추천 판매가 (원)", min_value=1000, max_value=10000000, value=60000, step=1000, key="new_business_price")
        new_business_limit = st.number_input("10분당 판매 제한 (무제한은 0)", min_value=0, max_value=50, value=0, step=1, key="new_business_limit")
        new_business_desc = st.text_area("설명", value="새로운 사업 유형입니다", key="new_business_desc")
        new_business_target = st.text_input("타겟 고객", value="일반", key="new_business_target")
        new_business_strategy = st.text_area("전략 팁", value="고객 니즈 파악이 핵심!", key="new_business_strategy")
        
        if st.button("✅ 추가", key="add_business_type"):
            if new_business_name and new_business_name not in st.session_state.business_types:
                st.session_state.business_types[new_business_name] = {
                    "cost": new_business_cost,
                    "recommended_price": new_business_price,
                    "margin_rate": (new_business_price - new_business_cost) / new_business_price if new_business_price > 0 else 0,
                    "max_sales_per_10min": new_business_limit if new_business_limit > 0 else None,
                    "description": new_business_desc,
                    "target": new_business_target,
                    "strategy": new_business_strategy,
                    "key": f"custom_{len(st.session_state.business_types)}"
                }
                st.sidebar.success(f"✅ {new_business_name} 추가됨!")
                st.rerun()
            else:
                st.sidebar.error("❌ 이름을 입력하거나 중복되지 않게 해주세요")
    
    with st.sidebar.expander("✏️ 사업 유형 수정/삭제", expanded=False):
        selected_to_edit = st.selectbox("수정할 사업 유형", list(st.session_state.business_types.keys()), key="edit_business_select")
        
        if selected_to_edit:
            current_data = st.session_state.business_types[selected_to_edit]
            
            st.caption("**현재 설정:**")
            st.caption(f"💰 원가: {current_data['cost']:,}원")
            st.caption(f"💸 추천가: {current_data['recommended_price']:,}원")
            st.caption(f"🎯 제한: {current_data['max_sales_per_10min'] if current_data['max_sales_per_10min'] else '무제한'}")
            
            edit_cost = st.number_input("새 원가 (원)", value=current_data['cost'], key="edit_cost")
            edit_price = st.number_input("새 추천가 (원)", value=current_data['recommended_price'], key="edit_price")
            edit_limit = st.number_input("새 제한 (0=무제한)", value=current_data['max_sales_per_10min'] if current_data['max_sales_per_10min'] else 0, key="edit_limit")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 수정 저장", key="save_edit"):
                    st.session_state.business_types[selected_to_edit]['cost'] = edit_cost
                    st.session_state.business_types[selected_to_edit]['recommended_price'] = edit_price
                    st.session_state.business_types[selected_to_edit]['margin_rate'] = (edit_price - edit_cost) / edit_price if edit_price > 0 else 0
                    st.session_state.business_types[selected_to_edit]['max_sales_per_10min'] = edit_limit if edit_limit > 0 else None
                    st.sidebar.success("✅ 수정됨!")
                    st.rerun()
            
            with col2:
                if st.button("🗑️ 삭제", key="delete_business"):
                    if len(st.session_state.business_types) > 1:
                        del st.session_state.business_types[selected_to_edit]
                        st.sidebar.success("✅ 삭제됨!")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ 최소 1개는 유지해야 합니다")

# 구매자 캐릭터 자동 할당
if st.session_state.is_admin:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎲 구매자 할당")
    
    if st.sidebar.button("🎭 구매자 자동 할당", help="게임에 참여할 구매자 캐릭터를 자동으로 선택합니다"):
        total_buyers = st.session_state.market_settings.get('total_buyers', 10)
        
        # 비율대로 캐릭터 할당
        big_count = int(total_buyers * 0.2)
        normal_count = int(total_buyers * 0.5)
        frugal_count = total_buyers - big_count - normal_count
        
        assigned_buyers = []
        
        # 큰손
        available_big = BUYER_CHARACTERS['big_spender']
        assigned_buyers.extend(random.sample(available_big, min(big_count, len(available_big))))
        
        # 일반
        available_normal = BUYER_CHARACTERS['normal']
        assigned_buyers.extend(random.sample(available_normal, min(normal_count, len(available_normal))))
        
        # 짠물
        available_frugal = BUYER_CHARACTERS['frugal']
        assigned_buyers.extend(random.sample(available_frugal, min(frugal_count, len(available_frugal))))
        
        st.session_state['assigned_buyers'] = assigned_buyers
        st.sidebar.success(f"✅ {len(assigned_buyers)}명 할당 완료!")
        st.rerun()
    
    # 할당된 구매자 표시
    if st.session_state.get('assigned_buyers'):
        with st.sidebar.expander(f"👥 할당된 구매자 ({len(st.session_state['assigned_buyers'])}명)", expanded=False):
            for idx, buyer in enumerate(st.session_state['assigned_buyers'], 1):
                st.write(f"{idx}. {buyer['emoji']} {buyer['name']}")

# ==================== 메인 탭 ====================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 창업 컨설팅", 
    "💼 판매 관리", 
    "📊 대시보드",
    "🎯 도구",
    "🏆 실시간 경쟁 현황"
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
        # 사업계획서 작성 시스템
        st.subheader("📝 사업계획서 작성 (선택사항)")
        st.caption("게임 시작 전, 학생이 자신의 창업 아이디어를 구체화할 수 있습니다")
        
        with st.expander("✍️ 사업계획서 작성하기", expanded=False):
            plan_col1, plan_col2 = st.columns(2)
            
            with plan_col1:
                item_name = st.text_input(
                    "💡 아이템명",
                    help="예: 손수건, 대필 서비스, 자전거 대여 등",
                    key="plan_item_name"
                )
                
                item_description = st.text_area(
                    "📄 아이템 설명",
                    help="무엇을 파는지 구체적으로 설명하세요 (2-3줄)",
                    height=100,
                    key="plan_description"
                )
                
                target_customer = st.text_input(
                    "🎯 목표 고객",
                    help="예: 초등학생, 운동을 좋아하는 사람, 바쁜 직장인 등",
                    key="plan_target"
                )
                
                unique_value = st.text_area(
                    "⭐ 차별점/강점",
                    help="다른 사람과 다른 나만의 특별함은?",
                    height=100,
                    key="plan_unique"
                )
            
            with plan_col2:
                estimated_cost = st.number_input(
                    "💰 예상 원가 (1만원 단위)",
                    min_value=0,
                    max_value=500000,
                    value=50000,
                    step=10000,
                    help="이 아이템을 만들거나 구매하는 데 드는 비용",
                    key="plan_cost"
                )
                
                estimated_price = st.number_input(
                    "💵 예상 판매가 (1만원 단위)",
                    min_value=0,
                    max_value=1000000,
                    value=100000,
                    step=10000,
                    help="얼마에 팔 계획인가요?",
                    key="plan_price"
                )
                
                estimated_quantity = st.number_input(
                    "📦 목표 판매량",
                    min_value=0,
                    max_value=100,
                    value=5,
                    step=1,
                    help="몇 개를 팔 계획인가요?",
                    key="plan_quantity"
                )
                
                if estimated_price > 0 and estimated_cost > 0:
                    estimated_profit = (estimated_price - estimated_cost) * estimated_quantity
                    st.metric("🎯 목표 수익", f"{estimated_profit:,}원")
                    
                    margin_rate = ((estimated_price - estimated_cost) / estimated_price) * 100
                    st.metric("📊 예상 마진율", f"{margin_rate:.1f}%")
            
            if st.button("💾 사업계획서 저장", type="primary", key="save_business_plan"):
                if not item_name:
                    st.error("⚠️ 아이템명을 입력하세요!")
                else:
                    business_plan = {
                        "아이템명": item_name,
                        "아이템_설명": item_description,
                        "목표_고객": target_customer,
                        "차별점_강점": unique_value,
                        "예상_원가": estimated_cost,
                        "예상_판매가": estimated_price,
                        "목표_판매량": estimated_quantity,
                        "목표_수익": (estimated_price - estimated_cost) * estimated_quantity,
                        "작성일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state['business_plan'] = business_plan
                    st.success("✅ 사업계획서가 저장되었습니다!")
                    st.balloons()
        
        # 저장된 계획서 조회
        if st.session_state.get('business_plan'):
            with st.expander("📄 내 사업계획서 보기"):
                plan = st.session_state['business_plan']
                
                st.markdown(f"""
                ### 💡 {plan['아이템명']}
                
                **📄 설명**: {plan['아이템_설명']}
                
                **🎯 목표 고객**: {plan['목표_고객']}
                
                **⭐ 차별점**: {plan['차별점_강점']}
                
                ---
                
                **💰 예상 원가**: {plan['예상_원가']:,}원  
                **💵 예상 판매가**: {plan['예상_판매가']:,}원  
                **📦 목표 판매량**: {plan['목표_판매량']}개  
                **🎯 목표 수익**: {plan['목표_수익']:,}원
                
                *작성일: {plan['작성일시']}*
                """)
        
        st.markdown("---")
        
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
            with st.spinner("AI가 시장 환경을 분석하고 최적 전략을 제안하고 있습니다..."):
                # 새로운 경제 기반 AI 추천
                recommendation = get_ai_recommendation_with_economics(
                    student_idea, 
                    st.session_state.market_settings,
                    st.session_state.students
                )
                
                st.session_state['ai_recommendation'] = recommendation
                st.success("✅ AI 분석 완료!")
                
                # 경제 환경 표시
                if 'economics' in recommendation:
                    eco = recommendation['economics']
                    
                    st.markdown("### 📊 현재 경제 환경")
                    eco_col1, eco_col2, eco_col3 = st.columns(3)
                    
                    with eco_col1:
                        st.metric("1인당 구매력", f"{eco['avg_buying_power']:,}원", "가격 기준선")
                    with eco_col2:
                        st.metric("시장 상태", eco['market_health']['status'])
                    with eco_col3:
                        st.metric("추천 전략", eco['strategy'])
                    
                    if eco.get('warnings'):
                        for warning in eco['warnings']:
                            st.warning(warning)
                
                # AI 추천 결과
                st.markdown("### 💡 AI 추천")
                
                rec_col1, rec_col2 = st.columns(2)
                
                with rec_col1:
                    st.info(f"""
                    **🏪 추천 유형**: {recommendation['recommended_type']}  
                    **💰 추천 원가**: {recommendation['cost']:,}원  
                    **💵 추천 판매가 범위**: {recommendation['price_range_min']:,}원 ~ {recommendation['price_range_max']:,}원  
                    **⏱️ 10분 제한**: {recommendation['max_sales_per_10min'] if recommendation['max_sales_per_10min'] else '무제한'}
                    """)
                
                with rec_col2:
                    st.markdown(f"""
                    **이유**: {recommendation['reason']}
                    
                    **전략**: {recommendation['strategy']}
                    """)
                
                # 자동 적용 버튼
                if st.button("✨ AI 추천 자동 적용", key="apply_ai"):
                    rec = st.session_state['ai_recommendation']
                    st.session_state['applied_ai_type'] = rec['recommended_type']
                    st.session_state['applied_ai_cost'] = rec['cost']
                    st.session_state['applied_ai_price_min'] = rec['price_range_min']
                    st.session_state['applied_ai_price_max'] = rec['price_range_max']
                    st.session_state['auto_apply_ai'] = True
                    st.success("✨ AI 추천이 적용됩니다!")
                    st.rerun()
        
        # AI 분석 결과 표시 (축소 가능)
        if 'ai_recommendation' in st.session_state and st.session_state['ai_recommendation']:
            with st.expander("📊 AI 분석 결과 다시 보기", expanded=False):
                rec = st.session_state['ai_recommendation']
                
                # 보기 좋게 표시
                st.markdown("### 💡 AI 추천 요약")
                
                result_col1, result_col2 = st.columns(2)
                
                with result_col1:
                    st.info(f"""
                    **🏪 추천 유형**: {rec['recommended_type']}  
                    **💰 추천 원가**: {rec['cost']:,}원  
                    **💵 판매가 범위**: {rec['price_range_min']:,}원 ~ {rec['price_range_max']:,}원  
                    **⏱️ 10분 제한**: {rec['max_sales_per_10min'] if rec['max_sales_per_10min'] else '무제한'}
                    """)
                
                with result_col2:
                    st.markdown(f"""
                    **💭 추천 이유**  
                    {rec.get('reason', 'N/A')}
                    
                    **🎯 전략**  
                    {rec.get('strategy', 'N/A')}
                    """)
                
                # 시장 분석 정보
                if 'economics' in rec:
                    st.markdown("### 📊 시장 환경 분석")
                    eco = rec['economics']
                    
                    eco_col1, eco_col2, eco_col3 = st.columns(3)
                    with eco_col1:
                        st.metric("평균 구매력", f"{eco.get('avg_buying_power', 0):,}원")
                    with eco_col2:
                        st.metric("시장 포화도", f"{eco.get('market_saturation', 0):.1%}")
                    with eco_col3:
                        st.metric("경쟁 강도", f"{eco.get('competition_intensity', 0):.2f}")
                    
                    if 'market_health' in eco:
                        health = eco['market_health']
                        st.write(f"**시장 상태**: {health['status']} - {health['description']}")
        
        st.markdown("---")
        
        st.subheader("3️⃣ 창업 유형 선택")
        
        # AI 추천 적용 시 자동 선택
        default_index = 0
        if st.session_state.get('applied_ai_type') and st.session_state['applied_ai_type'] in st.session_state.business_types.keys():
            default_index = list(st.session_state.business_types.keys()).index(st.session_state['applied_ai_type'])
        
        selected_business = st.selectbox(
            "사업 유형",
            options=list(st.session_state.business_types.keys()),
            index=default_index,
            help="학생의 아이디어에 맞는 유형 선택 (AI 추천 참고 또는 수동 선택)"
        )
        
        business_info = st.session_state.business_types.get(selected_business, {})
        
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
        
        # AI 추천 자동 적용
        if st.session_state.get('auto_apply_ai') and st.session_state.get('ai_recommendation'):
            ai_rec = st.session_state['ai_recommendation']
            default_cost = ai_rec['cost']
            recommended_min = ai_rec['price_range_min']
            recommended_max = ai_rec['price_range_max']
            st.session_state['auto_apply_ai'] = False
            st.success("✨ AI 추천이 자동 적용되었습니다!")
        else:
            default_cost = business_info['cost']
            recommended_min = business_info['recommended_price']
            recommended_max = int(business_info['recommended_price'] * 1.3)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**기본 원가**: {business_info['cost']:,}원")
        
        with col2:
            adjusted_cost = st.number_input(
                "최종 원가 설정 (1만원 단위)",
                min_value=10000,
                max_value=500000,
                value=default_cost,
                step=10000,
                help="AI 추천 원가 또는 수동 조정 (10만/5만/1만원권)",
                key="cost_adjustment"
            )
        
        if adjusted_cost != business_info['cost']:
            st.info(f"📝 원가 조정: {business_info['cost']:,}원 → {adjusted_cost:,}원")
        
        # 추천 판매가 범위 표시 (MarketEconomyEngine으로 동적 계산)
        st.markdown("---")
        st.subheader("💵 추천 판매가 범위 (시장 상황 반영)")
        
        # MarketEconomyEngine으로 동적 범위 계산
        try:
            market_engine = MarketEconomyEngine(
                st.session_state.market_settings,
                INITIAL_CAPITAL
            )
            
            # 현재 등록된 학생 수 전달
            current_students = len(st.session_state.students) if hasattr(st.session_state, 'students') else 0
            economics = market_engine.calculate_safe_economics(current_students)
            
            # 동적 마진율 적용
            dynamic_markup_min = economics['markup_min']
            dynamic_markup_max = economics['markup_max']
            
            calculated_min = int(adjusted_cost * dynamic_markup_min)
            calculated_max = int(adjusted_cost * dynamic_markup_max)
            
            # 1만원 단위로 반올림
            recommended_min = int(round(calculated_min / 10000) * 10000)
            recommended_max = int(round(calculated_max / 10000) * 10000)
            
            # 시장 상황 표시
            market_status = economics['market_health']['status']
            
            st.info(f"""
            {market_status}  
            {economics['market_health']['description']}  
            
            💡 **추천 전략**: {economics['strategy']}
            """)
            
            range_col1, range_col2, range_col3 = st.columns(3)
            
            with range_col1:
                st.metric("최저가", f"{recommended_min:,}원", f"원가 x {dynamic_markup_min:.1f}")
            with range_col2:
                recommended_mid = (recommended_min + recommended_max) // 2
                recommended_mid = int(round(recommended_mid / 10000) * 10000)
                st.metric("중간가 (참고)", f"{recommended_mid:,}원", "균형잡힌 선택")
            with range_col3:
                st.metric("최고가", f"{recommended_max:,}원", f"원가 x {dynamic_markup_max:.1f}")
        
        except Exception as e:
            # 에러 발생 시 기본값 사용
            st.warning(f"⚠️ 동적 가격 계산 중 문제가 발생했습니다. 기본 범위를 사용합니다.")
            recommended_min = business_info['recommended_price']
            recommended_max = int(business_info['recommended_price'] * 1.3)
            recommended_mid = (recommended_min + recommended_max) // 2
            
            range_col1, range_col2, range_col3 = st.columns(3)
            
            with range_col1:
                st.metric("최저가", f"{recommended_min:,}원")
            with range_col2:
                st.metric("중간가 (참고)", f"{recommended_mid:,}원")
            with range_col3:
                st.metric("최고가", f"{recommended_max:,}원")
        
        st.success(f"💡 학생에게: **{recommended_min:,}원 ~ {recommended_max:,}원** 사이에서 가격을 정해보세요!")
        
        # 추천 판매가 (기록용)
        recommended_selling_price = recommended_mid
        
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
        
        # 특수 설정: 대출금 / 합동팀
        st.subheader("5️⃣ 특수 설정 (선택사항)")
        
        special_col1, special_col2 = st.columns(2)
        
        with special_col1:
            st.markdown("#### 💰 대출금 설정")
            st.caption("플랫폼 사업 등 초기 투자가 큰 경우")
            
            has_loan = st.checkbox("대출금 지급", value=False, key="has_loan")
            loan_amount = 0
            loan_interest = 0
            
            if has_loan:
                loan_amount = st.number_input(
                    "대출 금액 (원)",
                    min_value=0,
                    max_value=5000000,
                    value=300000,
                    step=10000,
                    key="loan_amount"
                )
                loan_interest = st.number_input(
                    "이자율 (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=10.0,
                    step=1.0,
                    key="loan_interest",
                    help="정산 시 원금 + 이자 상환"
                )
                
                repayment = loan_amount * (1 + loan_interest / 100)
                st.info(f"💳 상환 금액: {repayment:,.0f}원 (원금 {loan_amount:,}원 + 이자 {loan_amount * loan_interest / 100:,.0f}원)")
        
        with special_col2:
            st.markdown("#### 👥 합동 팀 설정")
            st.caption("서비스 사업 등 팀 프로젝트")
            
            is_team = st.checkbox("팀 프로젝트", value=False, key="is_team")
            team_members = []
            profit_share = {}
            
            if is_team:
                team_size = st.number_input(
                    "팀원 수 (본인 포함)",
                    min_value=2,
                    max_value=10,
                    value=4,
                    step=1,
                    key="team_size"
                )
                
                st.caption("**팀원 이름 및 분배율 입력**")
                
                total_share = 0
                for i in range(team_size):
                    member_col1, member_col2 = st.columns([3, 2])
                    with member_col1:
                        member_name = st.text_input(
                            f"팀원 {i+1}",
                            value=student_name if i == 0 else f"팀원{i+1}",
                            key=f"team_member_{i}"
                        )
                    with member_col2:
                        member_share = st.number_input(
                            f"분배율 (%)",
                            min_value=0,
                            max_value=100,
                            value=100 // team_size,
                            step=5,
                            key=f"team_share_{i}"
                        )
                    
                    team_members.append(member_name)
                    profit_share[member_name] = member_share
                    total_share += member_share
                
                if total_share != 100:
                    st.warning(f"⚠️ 분배율 합계: {total_share}% (100%가 되어야 합니다)")
                else:
                    st.success("✅ 분배율 합계: 100%")
        
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
                    "purchased_quantity": 0,
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
                    "final_capital": custom_capital,
                    "actual_money": 0,
                    "inventory_loss": 0,
                    "actual_profit": 0,
                    "inventory_efficiency": 0,
                    # 특수 설정
                    "has_loan": has_loan,
                    "loan_amount": loan_amount,
                    "loan_interest": loan_interest,
                    "loan_repaid": False,
                    "is_team": is_team,
                    "team_members": team_members,
                    "profit_share": profit_share,
                    "team_settlement": {}
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
                business_info = st.session_state.business_types.get(business_type_key, st.session_state.business_types.get("🛒 골라오기 (유통)", {}))
                
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
                
                # 관리자 전용: 데이터 관리
                if st.session_state.is_admin:
                    with st.expander("⚙️ 관리자 설정 (데이터 관리)", expanded=False):
                        st.markdown("#### 💰 자본금 조정")
                        adjust_col1, adjust_col2 = st.columns(2)
                        
                        with adjust_col1:
                            new_initial_capital = st.number_input(
                                "초기 자본금 재설정",
                                min_value=0,
                                max_value=10000000,
                                value=data['initial_capital'],
                                step=10000,
                                key=f"adjust_initial_{name}",
                                help="대출금 지급이나 개별 조정용"
                            )
                        
                        with adjust_col2:
                            new_current_capital = st.number_input(
                                "현재 자본금 재설정",
                                min_value=0,
                                max_value=10000000,
                                value=data['final_capital'],
                                step=10000,
                                key=f"adjust_current_{name}",
                                help="긴급 조정용 (오입력 수정 등)"
                            )
                        
                        if st.button("💾 자본금 조정 저장", key=f"save_capital_{name}"):
                            st.session_state.students[name]['initial_capital'] = new_initial_capital
                            st.session_state.students[name]['final_capital'] = new_current_capital
                            
                            # Google Sheets에 저장
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            st.success(f"✅ {name}님의 자본금이 조정되었습니다!")
                            st.rerun()
                        
                        st.markdown("---")
                        st.markdown("#### 📝 사업 정보 수정")
                        
                        edit_col1, edit_col2 = st.columns(2)
                        
                        with edit_col1:
                            new_business_type = st.selectbox(
                                "사업 유형",
                                list(st.session_state.business_types.keys()),
                                index=list(st.session_state.business_types.keys()).index(data['business_type']) if data['business_type'] in st.session_state.business_types.keys() else 0,
                                key=f"edit_business_{name}"
                            )
                            
                            new_cost = st.number_input(
                                "원가 (원)",
                                min_value=0,
                                max_value=10000000,
                                value=data['cost'],
                                step=1000,
                                key=f"edit_cost_{name}"
                            )
                        
                        with edit_col2:
                            new_recommended_price = st.number_input(
                                "추천 판매가 (원)",
                                min_value=0,
                                max_value=10000000,
                                value=data['recommended_price'],
                                step=1000,
                                key=f"edit_price_{name}"
                            )
                            
                            new_inventory = st.number_input(
                                "재고 (개)",
                                min_value=0,
                                max_value=10000,
                                value=data['inventory'],
                                step=1,
                                key=f"edit_inventory_{name}"
                            )
                        
                        if st.button("💾 사업 정보 저장", key=f"save_business_{name}"):
                            st.session_state.students[name]['business_type'] = new_business_type
                            st.session_state.students[name]['cost'] = new_cost
                            st.session_state.students[name]['recommended_price'] = new_recommended_price
                            st.session_state.students[name]['inventory'] = new_inventory
                            
                            # Google Sheets에 저장
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            st.success(f"✅ {name}님의 사업 정보가 수정되었습니다!")
                            st.rerun()
                        
                        st.markdown("---")
                        st.markdown("#### 🗑️ 학생 삭제")
                        st.warning("⚠️ 삭제하면 모든 데이터가 영구적으로 사라집니다!")
                        
                        if st.button(f"🗑️ {name} 삭제", key=f"delete_{name}", type="secondary"):
                            del st.session_state.students[name]
                            
                            # Google Sheets에서 삭제
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                delete_student_from_sheets(st.session_state.worksheet, name)
                            
                            st.success(f"✅ {name}님이 삭제되었습니다!")
                            st.rerun()
                
                st.markdown("---")
                
                # STEP 1: 재고 구매 (전략 모드만)
                if game_mode == "전략 모드":
                    st.markdown("### 1️⃣ 재고 구매")
                    
                    # 현재 자본으로 추가 구매 가능한 수량 계산
                    max_can_buy = data['final_capital'] // data['cost']
                    
                    if max_can_buy > 0:
                        purchase_quantity = st.number_input(
                            f"{name} - 구매할 수량 (추가 구매 가능)",
                            min_value=0,
                            max_value=max_can_buy,
                            value=0,
                            step=1,
                            key=f"purchase_{name}",
                            help=f"현재 자본으로 최대 {max_can_buy}개 구매 가능"
                        )
                        
                        if purchase_quantity > 0:
                            total_cost = purchase_quantity * data['cost']
                            remaining_capital = data['final_capital'] - total_cost
                            
                            st.info(f"""
                            💰 구매 비용: {total_cost:,}원  
                            💳 남은 자본: {remaining_capital:,}원  
                            📦 구매 후 재고: {data['inventory'] + purchase_quantity}개
                            """)
                            
                            if st.button(f"✅ 구매 확정", key=f"confirm_purchase_{name}"):
                                # 기존 구매량에 추가
                                st.session_state.students[name]['purchased_quantity'] += purchase_quantity
                                st.session_state.students[name]['inventory'] += purchase_quantity
                                st.session_state.students[name]['final_capital'] = remaining_capital
                                
                                # Google Sheets에 저장
                                if st.session_state.use_google_sheets and st.session_state.worksheet:
                                    save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                                
                                st.success(f"✅ {purchase_quantity}개 추가 구매 완료!")
                                st.rerun()
                        else:
                            if data['purchased_quantity'] > 0:
                                st.success(f"✅ 현재 재고: {data['inventory']}개 (총 구매: {data['purchased_quantity']}개)")
                            else:
                                st.warning("⚠️ 구매 수량을 입력하세요")
                    else:
                        if data['inventory'] > 0:
                            st.info(f"""
                            📦 현재 재고: {data['inventory']}개  
                            💳 현재 자본: {data['final_capital']:,}원  
                            
                            ⚠️ 자본이 부족하여 추가 구매 불가
                            """)
                        else:
                            st.error("⚠️ 자본이 부족합니다. 재고를 구매할 수 없습니다.")
                    
                    st.markdown("---")
                else:
                    # 간단 모드: 재고 관리 없음
                    st.info("🎮 **간단 모드**: 재고 걱정 없이 바로 판매하세요!")
                    st.markdown("---")
                
                # 선택적 기능: 이벤트 카드
                if st.session_state.market_settings.get('enable_events', False):
                    st.markdown("### 🎴 이벤트 카드")
                    
                    # 현재 활성 이벤트 표시
                    active_events = data.get('active_events', [])
                    if active_events:
                        st.info("📌 **활성 이벤트:**")
                        for evt in active_events:
                            remaining = evt.get('remaining_duration', 0)
                            st.caption(f"• {evt['name']}: {evt['effect']} (남은 라운드: {remaining})")
                    
                    event_col1, event_col2 = st.columns(2)
                    
                    with event_col1:
                        if st.button("🎲 이벤트 뽑기", key=f"event_{name}"):
                            import random
                            event_type = random.choice(['positive', 'negative', 'neutral'])
                            event = random.choice(EVENT_CARDS[event_type]).copy()
                            event['remaining_duration'] = event.get('duration', 1)
                            event['type'] = event_type
                            
                            # 학생 데이터에 이벤트 추가
                            if 'active_events' not in st.session_state.students[name]:
                                st.session_state.students[name]['active_events'] = []
                            
                            st.session_state.students[name]['active_events'].append(event)
                            
                            # Google Sheets에 저장
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            if event_type == 'positive':
                                st.success(f"🎉 {event['name']}: {event['effect']}")
                            elif event_type == 'negative':
                                st.error(f"⚠️ {event['name']}: {event['effect']}")
                            else:
                                st.info(f"📰 {event['name']}: {event['effect']}")
                            
                            st.rerun()
                    
                    with event_col2:
                        if active_events and st.button("🗑️ 이벤트 초기화", key=f"clear_events_{name}"):
                            st.session_state.students[name]['active_events'] = []
                            
                            # Google Sheets에 저장
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            st.success("✅ 이벤트가 초기화되었습니다!")
                            st.rerun()
                    
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
                            
                            # 전략 모드: 재고 손실 및 실제 순이익 계산
                            if game_mode == "전략 모드":
                                inventory_loss = st.session_state.students[name]['inventory'] * st.session_state.students[name]['cost']
                                st.session_state.students[name]['inventory_loss'] = inventory_loss
                                st.session_state.students[name]['actual_profit'] = (
                                    st.session_state.students[name]['final_capital'] - 
                                    st.session_state.students[name]['initial_capital']
                                )
                                
                                # 재고 효율 계산
                                purchased = st.session_state.students[name]['purchased_quantity']
                                if purchased > 0:
                                    sold = purchased - st.session_state.students[name]['inventory']
                                    st.session_state.students[name]['inventory_efficiency'] = (sold / purchased * 100)
                                else:
                                    st.session_state.students[name]['inventory_efficiency'] = 0
                            else:
                                # 간단 모드: 재고 개념 없음, total_profit이 곧 actual_profit
                                st.session_state.students[name]['inventory_loss'] = 0
                                st.session_state.students[name]['actual_profit'] = st.session_state.students[name]['total_profit']
                                st.session_state.students[name]['inventory_efficiency'] = 100
                            
                            # Google Sheets에 저장
                            if st.session_state.use_google_sheets and st.session_state.worksheet:
                                save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                            
                            st.success(f"✅ {quantity_sold}개 판매 기록 완료!")
                            st.balloons()
                            st.rerun()
                
                st.markdown("---")
                
                # 현재 상태
                st.markdown("### 📊 현재 상태")
                
                # 전략 모드: 재고 포함
                if game_mode == "전략 모드":
                    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
                    
                    with status_col1:
                        st.info(f"**남은 재고**\n\n{data['inventory']}개")
                    with status_col2:
                        st.info(f"**총 매출**\n\n{data['total_revenue']:,}원")
                    with status_col3:
                        st.info(f"**기록 순이익**\n\n{data['total_profit']:,}원")
                    with status_col4:
                        st.info(f"**현재 자본**\n\n{data['final_capital']:,}원")
                    
                    # 재고 손실 경고 (2라운드 이후)
                    if st.session_state.current_round >= 2 and data['inventory'] > 0:
                        st.warning(f"""
                        ### 📦 재고 손실 분석
                        
                        **남은 재고**: {data['inventory']}개  
                        **재고 손실**: {data['inventory_loss']:,}원 ({data['inventory']}개 × {data['cost']:,}원)
                        
                        ---
                        
                        **기록된 순이익**: {data['total_profit']:,}원  
                        **재고 손실**: -{data['inventory_loss']:,}원  
                        **💰 실제 순이익**: **{data['actual_profit']:,}원**
                        
                        ---
                        
                        **재고 효율**: {data['inventory_efficiency']:.1f}% (판매율)
                        """)
                        
                        # 재고 효율 평가
                        if data['inventory_efficiency'] >= 90:
                            st.success("🌟 **재고 관리 탁월!** 구매한 재고의 90% 이상을 판매했습니다!")
                        elif data['inventory_efficiency'] >= 70:
                            st.info("✅ **재고 관리 양호** 구매한 재고의 70% 이상을 판매했습니다.")
                        elif data['inventory_efficiency'] >= 50:
                            st.warning("⚠️ **재고 관리 개선 필요** 판매율이 50~70%입니다.")
                        else:
                            st.error("❌ **과다 재고 경고** 판매율이 50% 미만입니다. 재고 손실이 큽니다!")
                    
                    elif st.session_state.current_round >= 2 and data['inventory'] == 0:
                        st.success(f"""
                        ### 🎉 완벽한 재고 관리!
                        
                        **재고 효율**: 100% (재고 소진 완료)  
                        **실제 순이익**: {data['actual_profit']:,}원
                        
                        모든 재고를 판매하여 재고 손실이 없습니다! 
                        """)
                
                else:
                    # 간단 모드: 재고 없음
                    status_col1, status_col2, status_col3 = st.columns(3)
                    
                    with status_col1:
                        st.info(f"**총 매출**\n\n{data['total_revenue']:,}원")
                    with status_col2:
                        st.info(f"**총 원가**\n\n{data['total_cost']:,}원")
                    with status_col3:
                        st.info(f"**순이익**\n\n{data['total_profit']:,}원")
                
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
                # 전략 모드: 실제 순이익 사용, 간단 모드: total_profit 사용
                if game_mode == "전략 모드":
                    profit_ranking = sorted(
                        st.session_state.students.items(),
                        key=lambda x: x[1].get('actual_profit', x[1]['total_profit']),
                        reverse=True
                    )
                else:
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
                    
                    # 전략 모드: 재고 손실 표시, 간단 모드: 간단하게
                    if game_mode == "전략 모드":
                        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
                    else:
                        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"## {medal}")
                    with col2:
                        st.markdown(f"### {name}")
                        st.caption(data['business_type'])
                    with col3:
                        if game_mode == "전략 모드":
                            actual_profit = data.get('actual_profit', data['total_profit'])
                            inventory_loss = data.get('inventory_loss', 0)
                            st.metric("실제 순이익", f"{actual_profit:,}원")
                            if inventory_loss > 0:
                                st.caption(f"재고 손실: -{inventory_loss:,}원")
                        else:
                            st.metric("순이익", f"{data['total_profit']:,}원")
                    with col4:
                        if color == "success":
                            st.success(trend)
                        elif color == "error":
                            st.error(trend)
                        else:
                            st.info(trend)
                    
                    if game_mode == "전략 모드":
                        with col5:
                            efficiency = data.get('inventory_efficiency', 0)
                            if efficiency >= 90:
                                st.success(f"📦 {efficiency:.0f}%")
                            elif efficiency >= 70:
                                st.info(f"📦 {efficiency:.0f}%")
                            else:
                                st.warning(f"📦 {efficiency:.0f}%")
                    
                    st.markdown("---")
        
        st.markdown("---")
        
        # 상세 데이터
        st.subheader("📋 상세 데이터")
        
        df_data = []
        for name, data in st.session_state.students.items():
            row = {
                "이름": name,
                "유형": data['business_type'],
                "원가": f"{data['cost']:,}원",
                "총매출": f"{data['total_revenue']:,}원",
            }
            
            # 전략 모드: 재고 정보 추가
            if game_mode == "전략 모드":
                row["재고"] = f"{data['inventory']}개"
                row["재고손실"] = f"{data.get('inventory_loss', 0):,}원"
                row["기록순이익"] = f"{data['total_profit']:,}원"
                row["실제순이익"] = f"{data.get('actual_profit', data['total_profit']):,}원"
                row["재고효율"] = f"{data.get('inventory_efficiency', 0):.0f}%"
                row["현재자본"] = f"{data['final_capital']:,}원"
            else:
                row["순이익"] = f"{data['total_profit']:,}원"
            
            df_data.append(row)
        
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
                costs = [st.session_state.students[name]['total_cost'] for name in students_names]
                
                # Plotly 인터랙티브 차트
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='💰 매출',
                    x=students_names,
                    y=revenues,
                    marker_color='lightblue',
                    text=revenues,
                    texttemplate='%{text:,}원',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>매출: %{y:,}원<extra></extra>'
                ))
                
                fig.add_trace(go.Bar(
                    name='✅ 순이익',
                    x=students_names,
                    y=profits,
                    marker_color='lightgreen',
                    text=profits,
                    texttemplate='%{text:,}원',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>순이익: %{y:,}원<extra></extra>'
                ))
                
                fig.add_trace(go.Bar(
                    name='💸 원가',
                    x=students_names,
                    y=costs,
                    marker_color='lightcoral',
                    text=costs,
                    texttemplate='%{text:,}원',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>원가: %{y:,}원<extra></extra>'
                ))
                
                fig.update_layout(
                    title='학생별 매출 vs 순이익 vs 원가',
                    xaxis_title='학생',
                    yaxis_title='금액 (원)',
                    barmode='group',
                    height=500,
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
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
                
                # Plotly 라인 차트
                fig2 = go.Figure()
                
                for name in students_names:
                    fig2.add_trace(go.Scatter(
                        x=['1라운드', '2라운드'],
                        y=round_data[name],
                        mode='lines+markers+text',
                        name=name,
                        text=[f"{v:,}원" for v in round_data[name]],
                        textposition='top center',
                        line=dict(width=3),
                        marker=dict(size=10),
                        hovertemplate='<b>%{fullData.name}</b><br>%{x}: %{y:,}원<extra></extra>'
                    ))
                
                fig2.update_layout(
                    title='라운드별 순이익 변화',
                    xaxis_title='라운드',
                    yaxis_title='순이익 (원)',
                    height=500,
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
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
                    
                    # Plotly 막대 차트 (가격 vs 원가)
                    fig3 = go.Figure()
                    
                    fig3.add_trace(go.Bar(
                        name='💵 평균 판매가',
                        x=price_df['학생'],
                        y=price_df['평균 판매가'],
                        marker_color='gold',
                        text=price_df['평균 판매가'],
                        texttemplate='%{text:,}원',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>평균 판매가: %{y:,}원<extra></extra>'
                    ))
                    
                    fig3.add_trace(go.Bar(
                        name='💰 원가',
                        x=price_df['학생'],
                        y=price_df['원가'],
                        marker_color='lightcoral',
                        text=price_df['원가'],
                        texttemplate='%{text:,}원',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>원가: %{y:,}원<extra></extra>'
                    ))
                    
                    fig3.update_layout(
                        title='평균 판매가 vs 원가',
                        xaxis_title='학생',
                        yaxis_title='금액 (원)',
                        barmode='group',
                        height=500,
                        hovermode='x unified',
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    st.success("💡 판매가가 원가보다 높을수록 마진이 높습니다!")
                else:
                    st.info("아직 판매 데이터가 없습니다")
        
        st.markdown("---")
        
        # 게임 종료 및 최종 정산 (관리자 전용)
        if st.session_state.is_admin and st.session_state.current_round >= 2:
            st.subheader("🏁 게임 종료 & 최종 정산")
            st.caption("2라운드가 종료되었습니다. 최종 정산을 진행하세요.")
            
            if st.button("🔒 게임 종료 & 재고 손실 최종 반영", type="primary"):
                for name, data in st.session_state.students.items():
                    # 전략 모드: 재고 손실 최종 계산
                    if game_mode == "전략 모드":
                        inventory_loss = data['inventory'] * data['cost']
                        actual_profit = data['final_capital'] - data['initial_capital']
                        
                        # 재고 효율 계산
                        purchased = data['purchased_quantity']
                        if purchased > 0:
                            sold = purchased - data['inventory']
                            inventory_efficiency = (sold / purchased * 100)
                        else:
                            inventory_efficiency = 100
                        
                        st.session_state.students[name]['inventory_loss'] = inventory_loss
                        st.session_state.students[name]['actual_profit'] = actual_profit
                        st.session_state.students[name]['inventory_efficiency'] = inventory_efficiency
                    else:
                        # 간단 모드: 재고 개념 없음
                        st.session_state.students[name]['inventory_loss'] = 0
                        st.session_state.students[name]['actual_profit'] = data['total_profit']
                        st.session_state.students[name]['inventory_efficiency'] = 100
                    
                    # Google Sheets에 저장
                    if st.session_state.use_google_sheets and st.session_state.worksheet:
                        save_student_to_sheets(st.session_state.worksheet, name, st.session_state.students[name])
                
                st.success("✅ 게임 종료 및 최종 정산 완료!")
                st.balloons()
                st.rerun()
            
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
        else:
            st.info("ℹ️ 아직 등록된 학생이 없습니다. '창업 컨설팅' 탭에서 먼저 학생을 등록하세요.")
    
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
            
            # 전체 구매자 가격표 (한눈에 보기)
            if not st.session_state.students:
                st.warning("⚠️ 아직 등록된 학생이 없습니다. 먼저 '창업 컨설팅' 탭에서 학생을 등록하세요.")
            else:
                st.markdown("### 📊 전체 구매자 가격표 (한눈에 보기)")
                st.caption("학생별 구매자별 구매 가능 가격 범위")
                
                # 학생별로 구매자 가격 계산
                guide_table = []
                
                all_buyers = []
                for category, buyers in BUYER_CHARACTERS.items():
                    all_buyers.extend([(category, buyer) for buyer in buyers])
                
                for category, buyer in all_buyers:
                    row = {
                        "유형": "💎 큰손" if category == "big_spender" else "😊 일반" if category == "normal" else "🤏 짠물",
                        "구매자": f"{buyer['emoji']} {buyer['name']}",
                        "예산": buyer.get('budget', 'N/A'),
                        "성향": buyer.get('personality', 'N/A')[:20] + "..."
                    }
                    
                    # 각 학생별 구매 가능 가격
                    for student_name, student_data in st.session_state.students.items():
                        price_range = calculate_buyer_price_range(
                            buyer,
                            student_data['cost'],
                            student_data['business_type']
                        )
                        row[f"{student_name}"] = f"{price_range['sweet_spot']:,}원 ({price_range['min']:,}~{price_range['max']:,})"
                    
                    guide_table.append(row)
                
                guide_df = pd.DataFrame(guide_table)
                st.dataframe(guide_df, use_container_width=True, hide_index=True, height=600)
                
                # CSV 다운로드
                csv = guide_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드 (인쇄용)",
                    data=csv,
                    file_name="구매자_가이드.csv",
                    mime="text/csv",
                    help="Excel에서 열어서 인쇄할 수 있습니다"
                )
                
                st.markdown("---")
                
                # 학생별 상세 정보 (접을 수 있음)
                st.markdown("### 📋 학생별 상세 구매 조건")
                
                for name, data in st.session_state.students.items():
                    cost = data['cost']
                    business_type = data['business_type']
                    
                    with st.expander(f"**{name}** - {business_type} (원가: {cost:,}원)"):
                        # 모든 캐릭터의 예상 가격대 계산
                        st.markdown("#### 💎 큰손 구매자들")
                        big_df_data = []
                        for buyer in BUYER_CHARACTERS["big_spender"]:
                            price_range = calculate_buyer_price_range(buyer, cost, business_type)
                            big_df_data.append({
                                "구매자": f"{buyer['emoji']} {buyer['name']}",
                                "최저가": f"{price_range['min']:,}원",
                                "적정가": f"{price_range['sweet_spot']:,}원",
                                "최고가": f"{price_range['max']:,}원"
                            })
                        
                        if big_df_data:
                            st.dataframe(pd.DataFrame(big_df_data), use_container_width=True, hide_index=True)
                        
                        st.markdown("#### 😊 일반 구매자들")
                        normal_df_data = []
                        for buyer in BUYER_CHARACTERS["normal"]:
                            price_range = calculate_buyer_price_range(buyer, cost, business_type)
                            normal_df_data.append({
                                "구매자": f"{buyer['emoji']} {buyer['name']}",
                                "최저가": f"{price_range['min']:,}원",
                                "적정가": f"{price_range['sweet_spot']:,}원",
                                "최고가": f"{price_range['max']:,}원"
                            })
                        
                        if normal_df_data:
                            st.dataframe(pd.DataFrame(normal_df_data), use_container_width=True, hide_index=True)
                        
                        st.markdown("#### 💰 짠물 구매자들")
                        frugal_df_data = []
                        for buyer in BUYER_CHARACTERS["frugal"]:
                            price_range = calculate_buyer_price_range(buyer, cost, business_type)
                            frugal_df_data.append({
                                "구매자": f"{buyer['emoji']} {buyer['name']}",
                                "최저가": f"{price_range['min']:,}원",
                                "적정가": f"{price_range['sweet_spot']:,}원",
                                "최고가": f"{price_range['max']:,}원"
                            })
                        
                        if frugal_df_data:
                            st.dataframe(pd.DataFrame(frugal_df_data), use_container_width=True, hide_index=True)
                
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
        
        report_type = st.radio(
            "리포트 유형",
            ["📄 전체 클래스 종합", "🎓 개별 학생 상세"],
            horizontal=True
        )
        
        if report_type == "📄 전체 클래스 종합":
            if st.button("📄 전체 리포트 생성", type="primary"):
                st.markdown("---")
                st.markdown("# 📊 장사의 신 - 전체 클래스 종합 리포트")
                st.caption(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
                
                if not st.session_state.students:
                    st.warning("⚠️ 아직 등록된 학생이 없습니다.")
                else:
                    # 1. 전체 통계
                    st.markdown("## 📈 전체 통계")
                    
                    total_students = len(st.session_state.students)
                    total_revenue = sum(s['total_revenue'] for s in st.session_state.students.values())
                    total_profit = sum(s['total_profit'] for s in st.session_state.students.values())
                    avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                    
                    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                    
                    with stat_col1:
                        st.metric("👥 참여 학생", f"{total_students}명")
                    with stat_col2:
                        st.metric("💰 총 매출", f"{total_revenue:,}원")
                    with stat_col3:
                        st.metric("✅ 총 순이익", f"{total_profit:,}원")
                    with stat_col4:
                        st.metric("📊 평균 마진율", f"{avg_margin:.1f}%")
                    
                    # 2. 교육 목표 달성도
                    st.markdown("## 🎯 교육 목표 달성도")
                    
                    # 마진 이해도
                    high_margin_count = sum(1 for s in st.session_state.students.values() 
                                           if s['total_revenue'] > 0 and (s['total_profit'] / s['total_revenue'] * 100) > 50)
                    
                    st.progress(high_margin_count / total_students if total_students > 0 else 0)
                    st.write(f"**마진 개념 이해**: {high_margin_count}/{total_students}명 (50% 이상 마진 달성)")
                    
                    # 가격 전략 다양성
                    avg_prices = []
                    for name, data in st.session_state.students.items():
                        total_qty = sum(data['rounds'][r].get('quantity_sold', 0) for r in data['rounds'])
                        if total_qty > 0:
                            avg_price = data['total_revenue'] / total_qty
                            avg_prices.append(avg_price)
                    
                    if len(avg_prices) > 1:
                        price_variance = pd.Series(avg_prices).std()
                        st.write(f"**가격 전략 다양성**: {price_variance:,.0f}원 (표준편차)")
                        
                        if price_variance > 50000:
                            st.success("✅ 학생들이 다양한 가격 전략을 시도했습니다!")
                        else:
                            st.info("💡 학생들의 가격이 비슷합니다. 더 창의적인 전략을 유도해보세요.")
                    
                    # 3. 유형별 분석
                    st.markdown("## 🏪 유형별 분석")
                    
                    type_analysis = {}
                    for name, data in st.session_state.students.items():
                        btype = data['business_type']
                        if btype not in type_analysis:
                            type_analysis[btype] = {'count': 0, 'total_profit': 0, 'total_revenue': 0}
                        
                        type_analysis[btype]['count'] += 1
                        type_analysis[btype]['total_profit'] += data['total_profit']
                        type_analysis[btype]['total_revenue'] += data['total_revenue']
                    
                    type_df = pd.DataFrame([
                        {
                            '유형': btype,
                            '학생 수': info['count'],
                            '평균 매출': f"{info['total_revenue'] / info['count']:,.0f}원",
                            '평균 순이익': f"{info['total_profit'] / info['count']:,.0f}원",
                            '마진율': f"{(info['total_profit'] / info['total_revenue'] * 100) if info['total_revenue'] > 0 else 0:.1f}%"
                        }
                        for btype, info in type_analysis.items()
                    ])
                    
                    st.dataframe(type_df, use_container_width=True, hide_index=True)
                    
                    # 4. 우수 전략 사례
                    st.markdown("## 🌟 우수 전략 사례")
                    
                    # 순이익 1위
                    if st.session_state.students:
                        top_profit = max(st.session_state.students.items(), key=lambda x: x[1]['total_profit'])
                        st.success(f"""
                        **💰 최고 수익**: {top_profit[0]}  
                        순이익 {top_profit[1]['total_profit']:,}원 달성!  
                        전략: {top_profit[1]['business_type']}로 높은 마진율 유지
                        """)
                        
                        # 마진율 1위
                        top_margin = max(
                            st.session_state.students.items(),
                            key=lambda x: (x[1]['total_profit'] / x[1]['total_revenue']) if x[1]['total_revenue'] > 0 else 0
                        )
                        margin_rate = (top_margin[1]['total_profit'] / top_margin[1]['total_revenue'] * 100) if top_margin[1]['total_revenue'] > 0 else 0
                        
                        st.info(f"""
                        **📊 최고 마진율**: {top_margin[0]}  
                        마진율 {margin_rate:.1f}% 달성!  
                        전략: 적정 가격으로 효율적 판매
                        """)
                    
                    # 5. 학습 포인트
                    st.markdown("## 💡 핵심 학습 포인트")
                    
                    st.write("""
                    - **순이익 > 매출**: 매출이 높아도 순이익이 낮으면 의미 없음
                    - **가격 전략**: 너무 높으면 판매 안 되고, 너무 낮으면 마진 부족
                    - **재고 관리**: 남은 재고는 손실, 적정 재고 유지 필요
                    - **시장 분석**: 경쟁자와 구매자 특성 파악 중요
                    - **전략 수정**: 1라운드 경험을 바탕으로 2라운드 개선
                    """)
        
        else:  # 개별 학생 상세
            if st.button("📄 개별 리포트 생성", type="primary"):
                if not st.session_state.students:
                    st.warning("⚠️ 아직 등록된 학생이 없습니다. '창업 컨설팅' 탭에서 먼저 학생을 등록하세요.")
                else:
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
            for business_name, business_data in st.session_state.business_types.items():
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
                        st.session_state.business_types[business_name]['cost'] = new_cost
                        st.session_state.business_types[business_name]['recommended_price'] = new_price
                        st.session_state.business_types[business_name]['margin_rate'] = (new_price - new_cost) / new_price
                        if business_data['max_sales_per_10min'] is not None:
                            st.session_state.business_types[business_name]['max_sales_per_10min'] = new_limit
                        
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

# ==================== TAB 5: 실시간 경쟁 현황 ====================
with tab5:
    st.header("🏆 실시간 경쟁 현황")
    
    if not st.session_state.is_admin:
        st.warning("⚠️ 관리자 로그인이 필요합니다.")
    else:
        if not st.session_state.students:
            st.info("등록된 학생이 없습니다.")
        else:
            st.markdown("### 📊 경쟁 상황 한눈에 보기")
            
            # 자동 새로고침 옵션
            auto_refresh = st.checkbox("⚡ 5초마다 자동 새로고침", value=False)
            if auto_refresh:
                import time
                time.sleep(5)
                st.rerun()
            
            # 전체 통계
            total_students = len(st.session_state.students)
            total_revenue = sum([s.get('total_revenue', 0) for s in st.session_state.students.values()])
            total_profit = sum([s.get('total_profit', 0) for s in st.session_state.students.values()])
            avg_price = sum([s.get('recommended_price', 0) for s in st.session_state.students.values()]) / total_students if total_students > 0 else 0
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("👥 참가자 수", f"{total_students}명")
            with metric_col2:
                st.metric("💰 총 매출", f"{total_revenue:,}원")
            with metric_col3:
                st.metric("💎 총 순이익", f"{total_profit:,}원")
            with metric_col4:
                st.metric("💵 평균 판매가", f"{avg_price:,.0f}원")
            
            st.markdown("---")
            
            # 실시간 리더보드
            leaderboard_tab1, leaderboard_tab2, leaderboard_tab3 = st.tabs([
                "💰 매출 순위", 
                "💎 순이익 순위", 
                "📈 효율성 순위"
            ])
            
            with leaderboard_tab1:
                st.markdown("#### 💰 매출 순위")
                revenue_sorted = sorted(
                    st.session_state.students.items(), 
                    key=lambda x: x[1].get('total_revenue', 0), 
                    reverse=True
                )
                
                for rank, (name, data) in enumerate(revenue_sorted, 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"
                    
                    with st.expander(f"{medal} {name} - {data.get('total_revenue', 0):,}원", expanded=(rank <= 3)):
                        info_col1, info_col2, info_col3 = st.columns(3)
                        with info_col1:
                            st.metric("💰 매출", f"{data.get('total_revenue', 0):,}원")
                        with info_col2:
                            st.metric("💵 판매가", f"{data.get('recommended_price', 0):,}원")
                        with info_col3:
                            sold_1 = data.get('rounds', {}).get(1, {}).get('quantity_sold', 0)
                            sold_2 = data.get('rounds', {}).get(2, {}).get('quantity_sold', 0)
                            st.metric("📦 판매량", f"{sold_1 + sold_2}개")
                        
                        st.caption(f"🏪 사업: {data.get('business_type', '-')}")
                        st.caption(f"💰 원가: {data.get('cost', 0):,}원 | 💳 현재 자본: {data.get('final_capital', 0):,}원")
            
            with leaderboard_tab2:
                st.markdown("#### 💎 순이익 순위")
                profit_sorted = sorted(
                    st.session_state.students.items(), 
                    key=lambda x: x[1].get('total_profit', 0), 
                    reverse=True
                )
                
                for rank, (name, data) in enumerate(profit_sorted, 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"
                    profit = data.get('total_profit', 0)
                    profit_color = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
                    
                    with st.expander(f"{medal} {name} - {profit_color} {profit:,}원", expanded=(rank <= 3)):
                        info_col1, info_col2, info_col3 = st.columns(3)
                        with info_col1:
                            st.metric("💎 순이익", f"{profit:,}원")
                        with info_col2:
                            margin = (profit / data.get('total_revenue', 1)) * 100 if data.get('total_revenue', 0) > 0 else 0
                            st.metric("📊 이익률", f"{margin:.1f}%")
                        with info_col3:
                            roi = (profit / data.get('initial_capital', 1)) * 100 if data.get('initial_capital', 0) > 0 else 0
                            st.metric("📈 ROI", f"{roi:.1f}%")
                        
                        st.caption(f"🏪 사업: {data.get('business_type', '-')}")
                        st.caption(f"💰 총 원가: {data.get('total_cost', 0):,}원 | 💵 총 매출: {data.get('total_revenue', 0):,}원")
            
            with leaderboard_tab3:
                st.markdown("#### 📈 효율성 순위 (ROI)")
                roi_sorted = sorted(
                    st.session_state.students.items(), 
                    key=lambda x: (x[1].get('total_profit', 0) / x[1].get('initial_capital', 1)) if x[1].get('initial_capital', 0) > 0 else 0, 
                    reverse=True
                )
                
                for rank, (name, data) in enumerate(roi_sorted, 1):
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"
                    roi = (data.get('total_profit', 0) / data.get('initial_capital', 1)) * 100 if data.get('initial_capital', 0) > 0 else 0
                    
                    with st.expander(f"{medal} {name} - ROI {roi:.1f}%", expanded=(rank <= 3)):
                        info_col1, info_col2, info_col3 = st.columns(3)
                        with info_col1:
                            st.metric("📈 ROI", f"{roi:.1f}%")
                        with info_col2:
                            st.metric("💵 초기자본", f"{data.get('initial_capital', 0):,}원")
                        with info_col3:
                            st.metric("💎 순이익", f"{data.get('total_profit', 0):,}원")
                        
                        # 자본 회전율
                        turnover = data.get('total_revenue', 0) / data.get('initial_capital', 1) if data.get('initial_capital', 0) > 0 else 0
                        st.caption(f"🔄 자본 회전율: {turnover:.2f}회")
                        st.caption(f"🏪 사업: {data.get('business_type', '-')}")
            
            st.markdown("---")
            
            # 가격 전쟁 분석
            st.markdown("### 💰 가격 경쟁 분석")
            
            # 사업 유형별 그룹화
            business_groups = {}
            for name, data in st.session_state.students.items():
                biz_type = data.get('business_type', '기타')
                if biz_type not in business_groups:
                    business_groups[biz_type] = []
                business_groups[biz_type].append({
                    'name': name,
                    'price': data.get('recommended_price', 0),
                    'cost': data.get('cost', 0),
                    'revenue': data.get('total_revenue', 0),
                    'profit': data.get('total_profit', 0)
                })
            
            for biz_type, students in business_groups.items():
                with st.expander(f"🏪 {biz_type} - {len(students)}명", expanded=len(business_groups) == 1):
                    if len(students) > 1:
                        st.info(f"⚔️ 같은 업종에 {len(students)}명이 경쟁 중입니다!")
                    
                    # 가격대별 정렬
                    students_sorted = sorted(students, key=lambda x: x['price'])
                    
                    for student in students_sorted:
                        price_col1, price_col2, price_col3, price_col4 = st.columns([2, 2, 2, 2])
                        
                        with price_col1:
                            st.caption(f"**{student['name']}**")
                        with price_col2:
                            margin = ((student['price'] - student['cost']) / student['price'] * 100) if student['price'] > 0 else 0
                            st.caption(f"💵 {student['price']:,}원 (마진 {margin:.0f}%)")
                        with price_col3:
                            st.caption(f"💰 매출: {student['revenue']:,}원")
                        with price_col4:
                            profit_icon = "🟢" if student['profit'] > 0 else "🔴" if student['profit'] < 0 else "⚪"
                            st.caption(f"{profit_icon} 순이익: {student['profit']:,}원")

st.markdown("---")
st.caption("🏪 장사의 신 게임 관리 시스템 V2 - 실전 창업 시뮬레이션")
