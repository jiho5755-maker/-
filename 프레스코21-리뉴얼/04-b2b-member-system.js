/**
 * =====================================================
 * 프레스코21 B2B 회원 등급별 UI 시스템
 * =====================================================
 * 강사/협회 회원에게 특별 가격과 전용 UI를 제공하는 스크립트
 * 메이크샵 API 연동 준비 완료
 */

// ========== 회원 등급 정의 ==========
const MEMBER_GRADES = {
  NORMAL: 'normal',           // 일반 회원
  INSTRUCTOR: 'instructor',   // 강사 회원
  ASSOCIATION: 'association', // 협회 회원
  VIP: 'vip'                 // VIP 회원
};

const DISCOUNT_RATES = {
  [MEMBER_GRADES.NORMAL]: 0,
  [MEMBER_GRADES.INSTRUCTOR]: 0.25,      // 25% 할인
  [MEMBER_GRADES.ASSOCIATION]: 0.30,     // 30% 할인
  [MEMBER_GRADES.VIP]: 0.35              // 35% 할인
};

const GRADE_LABELS = {
  [MEMBER_GRADES.NORMAL]: '일반 회원',
  [MEMBER_GRADES.INSTRUCTOR]: '강사 회원',
  [MEMBER_GRADES.ASSOCIATION]: '협회 회원',
  [MEMBER_GRADES.VIP]: 'VIP 회원'
};

const GRADE_BADGES = {
  [MEMBER_GRADES.NORMAL]: '',
  [MEMBER_GRADES.INSTRUCTOR]: '⭐ 공인 강사',
  [MEMBER_GRADES.ASSOCIATION]: '🏆 제휴 협회',
  [MEMBER_GRADES.VIP]: '👑 VIP'
};

// ========== 회원 정보 가져오기 ==========
class MemberService {
  constructor() {
    this.currentMember = null;
  }
  
  /**
   * 메이크샵에서 현재 로그인한 회원 정보 가져오기
   * 실제 구현 시 메이크샵 API 또는 쿠키/세션에서 가져와야 함
   */
  async getCurrentMember() {
    // 방법 1: 메이크샵 JavaScript 변수 사용 (메이크샵이 제공하는 경우)
    if (typeof MakeshopMemberInfo !== 'undefined') {
      return {
        isLoggedIn: MakeshopMemberInfo.isLogin,
        memberId: MakeshopMemberInfo.memberId,
        memberName: MakeshopMemberInfo.memberName,
        grade: this.mapMakeshopGrade(MakeshopMemberInfo.grade)
      };
    }
    
    // 방법 2: 쿠키에서 읽기
    const memberGrade = this.getCookie('member_grade');
    const memberId = this.getCookie('member_id');
    
    if (memberId) {
      return {
        isLoggedIn: true,
        memberId: memberId,
        memberName: this.getCookie('member_name') || '',
        grade: memberGrade || MEMBER_GRADES.NORMAL
      };
    }
    
    // 방법 3: 로컬스토리지 (개발/테스트용)
    const storedMember = localStorage.getItem('presco21_member');
    if (storedMember) {
      return JSON.parse(storedMember);
    }
    
    // 로그인하지 않은 경우
    return {
      isLoggedIn: false,
      memberId: null,
      memberName: null,
      grade: MEMBER_GRADES.NORMAL
    };
  }
  
  /**
   * 메이크샵의 등급명을 우리 시스템 등급으로 매핑
   */
  mapMakeshopGrade(makeshopGrade) {
    const gradeMap = {
      '강사': MEMBER_GRADES.INSTRUCTOR,
      'instructor': MEMBER_GRADES.INSTRUCTOR,
      '협회': MEMBER_GRADES.ASSOCIATION,
      'association': MEMBER_GRADES.ASSOCIATION,
      'vip': MEMBER_GRADES.VIP,
      'VIP': MEMBER_GRADES.VIP
    };
    
    return gradeMap[makeshopGrade] || MEMBER_GRADES.NORMAL;
  }
  
  /**
   * 쿠키 읽기 유틸리티
   */
  getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }
  
  /**
   * 회원 등급에 따른 할인율 반환
   */
  getDiscountRate(grade) {
    return DISCOUNT_RATES[grade] || 0;
  }
  
  /**
   * 할인 적용된 가격 계산
   */
  calculateDiscountedPrice(originalPrice, grade) {
    const discountRate = this.getDiscountRate(grade);
    const discountAmount = Math.floor(originalPrice * discountRate);
    return originalPrice - discountAmount;
  }
}

// ========== UI 업데이트 클래스 ==========
class B2BUIManager {
  constructor(memberService) {
    this.memberService = memberService;
    this.currentMember = null;
  }
  
  /**
   * 초기화 및 UI 업데이트
   */
  async init() {
    this.currentMember = await this.memberService.getCurrentMember();
    
    if (this.currentMember.isLoggedIn && this.currentMember.grade !== MEMBER_GRADES.NORMAL) {
      this.showB2BUI();
      this.updateProductPrices();
      this.addPartnerBadge();
      this.enableBulkOrderUI();
    }
  }
  
  /**
   * B2B 전용 UI 표시
   */
  showB2BUI() {
    // 상세 페이지의 B2B 안내 박스 표시
    const b2bNotice = document.getElementById('b2b-notice');
    if (b2bNotice) {
      b2bNotice.classList.add('visible');
    }
    
    // 전체 페이지에 B2B 바 추가
    this.addB2BTopBar();
  }
  
  /**
   * 상단 B2B 회원 알림 바 추가
   */
  addB2BTopBar() {
    const existingBar = document.getElementById('b2b-top-bar');
    if (existingBar) return;
    
    const bar = document.createElement('div');
    bar.id = 'b2b-top-bar';
    bar.style.cssText = `
      background: linear-gradient(135deg, #B5A48B 0%, #968870 100%);
      color: white;
      padding: 12px 20px;
      text-align: center;
      font-size: 14px;
      font-weight: 500;
      position: sticky;
      top: 0;
      z-index: 9999;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    `;
    
    const badge = GRADE_BADGES[this.currentMember.grade];
    const label = GRADE_LABELS[this.currentMember.grade];
    const discount = Math.floor(DISCOUNT_RATES[this.currentMember.grade] * 100);
    
    bar.innerHTML = `
      ${badge} ${this.currentMember.memberName || ''}님 환영합니다! 
      | ${label} 특별가 ${discount}% 할인 적용 중 
      | <a href="/mypage" style="color: white; text-decoration: underline; margin-left: 8px;">마이페이지</a>
    `;
    
    document.body.insertBefore(bar, document.body.firstChild);
  }
  
  /**
   * 상품 목록/상세 페이지의 가격 업데이트
   */
  updateProductPrices() {
    const grade = this.currentMember.grade;
    const discountRate = this.memberService.getDiscountRate(grade);
    
    // 상품 목록 페이지
    document.querySelectorAll('.product-item, .card').forEach(item => {
      const priceElement = item.querySelector('.product-price, .price');
      if (!priceElement) return;
      
      const originalPriceText = priceElement.textContent;
      const originalPrice = parseInt(originalPriceText.replace(/[^0-9]/g, ''));
      
      if (isNaN(originalPrice)) return;
      
      const discountedPrice = this.memberService.calculateDiscountedPrice(originalPrice, grade);
      
      // 가격 표시 업데이트
      priceElement.innerHTML = `
        <span style="text-decoration: line-through; color: #999; font-size: 0.9em; margin-right: 8px;">
          ${originalPrice.toLocaleString()}원
        </span>
        <span style="color: #7B8E7E; font-weight: bold;">
          ${discountedPrice.toLocaleString()}원
        </span>
        <span style="display: inline-block; background: #C17B7B; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin-left: 6px;">
          ${Math.floor(discountRate * 100)}%
        </span>
      `;
    });
    
    // 상세 페이지 재료 가격
    document.querySelectorAll('.material-price').forEach(priceElement => {
      const originalPriceText = priceElement.textContent;
      const originalPrice = parseInt(originalPriceText.replace(/[^0-9]/g, ''));
      
      if (isNaN(originalPrice)) return;
      
      const discountedPrice = this.memberService.calculateDiscountedPrice(originalPrice, grade);
      
      priceElement.innerHTML = `
        <span style="text-decoration: line-through; color: #999; font-size: 0.85em; display: block;">
          ${originalPrice.toLocaleString()}원
        </span>
        <span style="color: #7B8E7E; font-weight: bold;">
          ${discountedPrice.toLocaleString()}원
        </span>
      `;
    });
  }
  
  /**
   * 공식 파트너 인증 배지 추가
   */
  addPartnerBadge() {
    // 마이페이지나 주요 위치에 배지 추가
    const badge = document.createElement('div');
    badge.className = 'partner-certification-badge';
    badge.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: linear-gradient(135deg, #7B8E7E, #5A6B5D);
      color: white;
      padding: 16px 20px;
      border-radius: 12px;
      box-shadow: 0 4px 16px rgba(123, 142, 126, 0.3);
      font-size: 14px;
      font-weight: 600;
      z-index: 9998;
      cursor: pointer;
      transition: transform 0.3s ease;
    `;
    
    badge.innerHTML = `
      <div style="text-align: center;">
        ${GRADE_BADGES[this.currentMember.grade]}<br>
        <small style="font-size: 12px; opacity: 0.9;">이진선 장인의 공식 파트너</small>
      </div>
    `;
    
    badge.addEventListener('mouseenter', () => {
      badge.style.transform = 'scale(1.05)';
    });
    
    badge.addEventListener('mouseleave', () => {
      badge.style.transform = 'scale(1)';
    });
    
    badge.addEventListener('click', () => {
      alert(`${GRADE_LABELS[this.currentMember.grade]} 혜택을 이용 중입니다.\n\n- 모든 상품 ${Math.floor(DISCOUNT_RATES[this.currentMember.grade] * 100)}% 할인\n- 도매 발주 기능 이용 가능\n- 우선 배송 서비스\n- 전용 고객센터`);
    });
    
    document.body.appendChild(badge);
  }
  
  /**
   * 도매 발주용 퀵 리스트 UI 추가
   */
  enableBulkOrderUI() {
    // 상품 상세 페이지에만 추가
    const materialsArea = document.querySelector('.materials-area');
    if (!materialsArea) return;
    
    const bulkOrderBtn = document.createElement('button');
    bulkOrderBtn.className = 'btn btn-secondary';
    bulkOrderBtn.style.cssText = `
      width: 100%;
      margin-top: 12px;
    `;
    bulkOrderBtn.innerHTML = '📋 도매 발주 리스트로 담기';
    
    bulkOrderBtn.addEventListener('click', () => {
      this.openBulkOrderModal();
    });
    
    const cartActions = materialsArea.querySelector('.cart-actions');
    if (cartActions) {
      cartActions.insertAdjacentElement('beforebegin', bulkOrderBtn);
    }
  }
  
  /**
   * 도매 발주 모달 열기
   */
  openBulkOrderModal() {
    // 모달 배경
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    
    // 모달 내용
    const modal = document.createElement('div');
    modal.style.cssText = `
      background: white;
      border-radius: 16px;
      padding: 32px;
      max-width: 800px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
    `;
    
    modal.innerHTML = `
      <h2 style="font-size: 24px; margin-bottom: 16px; font-family: 'Noto Serif KR', serif;">
        📋 도매 발주 리스트
      </h2>
      <p style="color: #666; margin-bottom: 24px;">
        여러 옵션을 한 번에 대량으로 주문할 수 있습니다.
      </p>
      
      <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
        <thead>
          <tr style="background: #F9F8F5; border-bottom: 2px solid #7B8E7E;">
            <th style="padding: 12px; text-align: left;">상품명</th>
            <th style="padding: 12px; text-align: center; width: 120px;">수량</th>
            <th style="padding: 12px; text-align: right; width: 120px;">단가</th>
            <th style="padding: 12px; text-align: right; width: 120px;">합계</th>
          </tr>
        </thead>
        <tbody id="bulk-order-table-body">
          <tr>
            <td style="padding: 12px;">압화 입문 키트</td>
            <td style="padding: 12px; text-align: center;">
              <input type="number" value="10" min="1" style="width: 60px; text-align: center; padding: 4px; border: 1px solid #E5E3DC; border-radius: 4px;">
            </td>
            <td style="padding: 12px; text-align: right;">26,250원</td>
            <td style="padding: 12px; text-align: right; font-weight: bold; color: #7B8E7E;">262,500원</td>
          </tr>
          <tr>
            <td style="padding: 12px;">프레싱 툴 세트</td>
            <td style="padding: 12px; text-align: center;">
              <input type="number" value="5" min="1" style="width: 60px; text-align: center; padding: 4px; border: 1px solid #E5E3DC; border-radius: 4px;">
            </td>
            <td style="padding: 12px; text-align: right;">11,250원</td>
            <td style="padding: 12px; text-align: right; font-weight: bold; color: #7B8E7E;">56,250원</td>
          </tr>
        </tbody>
        <tfoot>
          <tr style="border-top: 2px solid #7B8E7E;">
            <td colspan="3" style="padding: 16px; text-align: right; font-weight: bold; font-size: 18px;">
              총 발주 금액
            </td>
            <td style="padding: 16px; text-align: right; font-weight: bold; font-size: 20px; color: #7B8E7E;">
              318,750원
            </td>
          </tr>
        </tfoot>
      </table>
      
      <div style="display: flex; gap: 12px;">
        <button class="btn-cancel" style="flex: 1; padding: 16px; background: #E5E3DC; border: none; border-radius: 8px; cursor: pointer; font-size: 16px;">
          취소
        </button>
        <button class="btn-confirm" style="flex: 2; padding: 16px; background: #7B8E7E; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600;">
          발주 리스트에 추가
        </button>
      </div>
    `;
    
    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);
    
    // 버튼 이벤트
    modal.querySelector('.btn-cancel').addEventListener('click', () => {
      backdrop.remove();
    });
    
    modal.querySelector('.btn-confirm').addEventListener('click', () => {
      alert('✅ 발주 리스트에 추가되었습니다!');
      backdrop.remove();
    });
    
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.remove();
      }
    });
  }
}

// ========== 개발/테스트 모드 ==========
class DevModeHelper {
  /**
   * 테스트용 회원 정보 설정
   */
  static setTestMember(grade = MEMBER_GRADES.INSTRUCTOR) {
    const testMember = {
      isLoggedIn: true,
      memberId: 'test_member_001',
      memberName: '홍길동',
      grade: grade
    };
    
    localStorage.setItem('presco21_member', JSON.stringify(testMember));
    console.log('✅ 테스트 회원 정보 설정됨:', testMember);
  }
  
  /**
   * 회원 로그아웃 (테스트용)
   */
  static clearTestMember() {
    localStorage.removeItem('presco21_member');
    console.log('✅ 테스트 회원 정보 삭제됨');
  }
  
  /**
   * 현재 회원 정보 확인
   */
  static checkCurrentMember() {
    const member = localStorage.getItem('presco21_member');
    if (member) {
      console.log('현재 회원 정보:', JSON.parse(member));
    } else {
      console.log('로그인하지 않음');
    }
  }
}

// ========== 자동 초기화 ==========
document.addEventListener('DOMContentLoaded', async () => {
  const memberService = new MemberService();
  const b2bUI = new B2BUIManager(memberService);
  
  await b2bUI.init();
  
  // 개발 모드에서 콘솔에 헬퍼 노출
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.DevMode = DevModeHelper;
    console.log(`
===========================================
🛠️  프레스코21 B2B 개발 모드
===========================================
테스트 명령어:

// 강사 회원으로 로그인
DevMode.setTestMember('instructor');

// 협회 회원으로 로그인
DevMode.setTestMember('association');

// 로그아웃
DevMode.clearTestMember();

// 현재 회원 정보 확인
DevMode.checkCurrentMember();

// 페이지 새로고침
location.reload();
===========================================
    `);
  }
});

// ========== 전역 노출 (다른 스크립트에서 사용 가능) ==========
window.Presco21 = {
  MemberService,
  B2BUIManager,
  MEMBER_GRADES,
  DISCOUNT_RATES
};
