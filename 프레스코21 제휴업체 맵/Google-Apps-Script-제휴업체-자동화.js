// ========================================
// 제휴업체 신청 데이터 자동화 스크립트
// ========================================
// 
// 기능:
// 1. onEdit: P열(심사상태)이 '승인'으로 변경되면 F열(도로명 주소)를 Geocoding하여 Q열(위도), R열(경도) 자동 입력
// 2. doGet: P열이 '승인'이고 위도/경도가 있는 데이터만 JSON으로 반환
//
// 열 구조:
// A: 타임스탬프, B: 업체명, C: 카테고리, D: 대표자성함, E: 사업자번호
// F: 도로명 주소, G: 상세 주소, H: 전화번호, I: 이메일, J: 운영시간
// K: 링크, L: 소개, M: 이미지
// N: 관리자메모 (관리자 입력), O: 협회 (폼 질문 13번)
// P: 심사상태 (관리자 입력 - '승인' 시 자동화 트리거)
// Q: 위도 (자동생성), R: 경도 (자동생성)
//
// 사용 방법:
// 1. Google 스프레드시트에서 확장 프로그램 > Apps Script 메뉴 클릭
// 2. 이 코드를 붙여넣기
// 3. 파일 > 저장
// 4. 배포 > 새 배포 > 유형: 웹 앱 > 실행 사용자: 나 > 액세스 권한: 모든 사용자 > 배포
// 5. 생성된 웹 앱 URL을 복사하여 HTML 파일의 GOOGLE_SHEET_API_URL에 입력
//
// ========================================

/**
 * 시트 편집 이벤트 트리거
 * P열(심사상태)이 '승인'으로 변경되면 주소를 Geocoding하여 위도/경도 자동 입력
 * 
 * ⚠️ 주의: 이 함수는 시트를 편집할 때 자동으로 실행됩니다.
 * 직접 실행하면 오류가 발생합니다. 테스트는 testGeocodeRow 함수를 사용하세요.
 */
function onEdit(e) {
  try {
    // e 매개변수 검증 (직접 실행 방지)
    if (!e || !e.source || !e.range) {
      Logger.log('onEdit: 직접 실행할 수 없습니다. 시트를 편집해야 자동으로 실행됩니다.');
      return;
    }
    
    var sheet = e.source.getActiveSheet();
    var range = e.range;
    var row = range.getRow();
    var col = range.getColumn();
    
    // P열(16번째 열)이 편집되었는지 확인 (심사상태)
    if (col !== 16) {
      return; // P열이 아니면 종료
    }
    
    // 심사상태 값 확인 (P열, 16번째 열)
    var statusCell = sheet.getRange(row, 16); // P열 = 16번째 열
    var statusValue = String(statusCell.getValue()).trim();
    
    // '승인'이 아니면 종료
    if (statusValue !== '승인') {
      return;
    }
    
    // 이미 위도/경도가 있으면 종료 (중복 실행 방지)
    var latCell = sheet.getRange(row, 17); // Q열 = 17번째 열 (위도)
    var lngCell = sheet.getRange(row, 18); // R열 = 18번째 열 (경도)
    var existingLat = latCell.getValue();
    var existingLng = lngCell.getValue();
    
    if (existingLat && existingLng && existingLat !== '' && existingLng !== '') {
      Logger.log('이미 좌표가 존재함: 행 ' + row);
      return;
    }
    
    // F열(도로명 주소) 읽기 (6번째 열)
    var addressCell = sheet.getRange(row, 6); // F열 = 6번째 열
    var address = String(addressCell.getValue()).trim();
    
    if (!address || address === '') {
      Logger.log('주소가 없음: 행 ' + row);
      return;
    }
    
    Logger.log('주소 Geocoding 시작: ' + address);
    
    // Geocoding 수행
    var geocodeResult = geocodeAddress(address);
    
    if (geocodeResult && geocodeResult.lat && geocodeResult.lng) {
      // Q열(위도), R열(경도)에 값 입력
      latCell.setValue(geocodeResult.lat);
      lngCell.setValue(geocodeResult.lng);
      
      Logger.log('✅ 좌표 입력 완료: 행 ' + row + ', 위도: ' + geocodeResult.lat + ', 경도: ' + geocodeResult.lng);
    } else {
      Logger.log('❌ Geocoding 실패: ' + address);
      // 실패한 경우 사용자에게 알림 (선택사항)
      // SpreadsheetApp.getUi().alert('주소를 좌표로 변환할 수 없습니다: ' + address);
    }
    
  } catch (error) {
    Logger.log('onEdit 오류: ' + error.toString());
  }
}

/**
 * 주소를 위도/경도로 변환 (Geocoding)
 * Google Maps Geocoding API 사용
 */
function geocodeAddress(address) {
  try {
    // Google Maps Geocoding API 사용
    var geocoder = Maps.newGeocoder();
    var response = geocoder.geocode(address);
    
    if (response.status === 'OK' && response.results.length > 0) {
      var location = response.results[0].geometry.location;
      return {
        lat: location.lat,
        lng: location.lng
      };
    } else {
      Logger.log('Geocoding 응답 오류: ' + response.status);
      return null;
    }
    
  } catch (error) {
    Logger.log('Geocoding 오류: ' + error.toString());
    return null;
  }
}

/**
 * 웹 앱으로 호출할 API 엔드포인트
 * P열이 '승인'이고 위도/경도가 있는 데이터만 JSON으로 반환
 */
function doGet() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // ========================================
    // 🔧 시트 이름 설정 (필요시 수정)
    // ========================================
    // 방법 1: 현재 활성 시트 사용 (기본)
    var sheet = ss.getActiveSheet();
    
    // 방법 2: 특정 시트 이름 지정 (활성화하려면 위 줄을 주석 처리하고 아래 줄 주석 해제)
    // var sheet = ss.getSheetByName('제휴업체'); // 시트 이름을 여기에 입력하세요
    // ========================================
    
    // 데이터 범위 읽기
    var lastRow = sheet.getLastRow();
    var lastCol = sheet.getLastColumn();
    
    if (lastRow < 2) {
      return createErrorResponse('데이터가 없습니다.');
    }
    
    // 헤더 행 읽기 (1행)
    var headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
    
    // 데이터 행 읽기 (2행부터)
    var dataRange = sheet.getRange(2, 1, lastRow - 1, lastCol);
    var dataValues = dataRange.getValues();
    
    var approvedPartners = [];
    
    // 각 행 처리
    for (var i = 0; i < dataValues.length; i++) {
      var row = dataValues[i];
      var rowNum = i + 2; // 실제 행 번호 (헤더 제외)
      
      // P열(16번째 열, 인덱스 15) = 심사상태
      var status = String(row[15] || '').trim();
      
      // '승인'이 아니면 건너뛰기
      if (status !== '승인') {
        continue;
      }
      
      // Q열(17번째 열, 인덱스 16) = 위도, R열(18번째 열, 인덱스 17) = 경도
      var lat = parseFloat(row[16]) || 0;
      var lng = parseFloat(row[17]) || 0;
      
      // 위도/경도가 없으면 건너뛰기
      if (!lat || !lng || lat === 0 || lng === 0) {
        continue;
      }
      
      // 데이터 객체 생성 (필요한 필드만 포함)
      var partner = {
        name: String(row[1] || '').trim(),           // B열: 업체명
        category: String(row[2] || '').trim(),       // C열: 카테고리
        address: String(row[5] || '').trim(),        // F열: 도로명 주소
        detailAddress: String(row[6] || '').trim(),  // G열: 상세 주소
        phone: String(row[7] || '').trim(),          // H열: 대표 전화번호
        hours: String(row[9] || '').trim(),          // J열: 운영 시간
        link: String(row[10] || '').trim(),          // K열: 홈페이지/블로그/인스타 링크
        description: String(row[11] || '').trim(),   // L열: 업체 한 줄 소개
        imageUrl: String(row[12] || '').trim(),      // M열: 업체 대표 이미지 URL
        association: String(row[14] || '').trim(),   // O열: 협회 (인덱스 14)
        lat: lat,                                    // Q열: 위도
        lng: lng                                     // R열: 경도
      };
      
      // 업체명이 있는 경우에만 추가
      if (partner.name) {
        approvedPartners.push(partner);
      }
    }
    
    // JSON 응답 생성
    var result = {
      success: true,
      partners: approvedPartners,
      count: approvedPartners.length,
      timestamp: new Date().toISOString()
    };
    
    return createSuccessResponse(result);
    
  } catch (error) {
    Logger.log('doGet 오류: ' + error.toString());
    return createErrorResponse('데이터를 불러오는 중 오류가 발생했습니다: ' + error.toString());
  }
}

/**
 * 성공 응답 생성
 */
function createSuccessResponse(data) {
  var output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  
  // CORS 헤더 추가 (필요한 경우)
  // output.setHeaders({'Access-Control-Allow-Origin': '*'});
  
  return output;
}

/**
 * 에러 응답 생성
 */
function createErrorResponse(message) {
  var errorData = {
    success: false,
    error: true,
    message: message,
    timestamp: new Date().toISOString()
  };
  
  var output = ContentService.createTextOutput(JSON.stringify(errorData));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}

/**
 * 테스트 함수: doGet 함수 테스트
 */
function testDoGet() {
  var result = doGet();
  var content = result.getContent();
  Logger.log('=== API 응답 ===');
  Logger.log(content);
  
  try {
    var parsed = JSON.parse(content);
    Logger.log('성공: ' + parsed.success);
    Logger.log('제휴업체 수: ' + parsed.count);
    if (parsed.partners && parsed.partners.length > 0) {
      Logger.log('첫 번째 업체: ' + JSON.stringify(parsed.partners[0]));
    }
  } catch (e) {
    Logger.log('파싱 오류: ' + e.toString());
  }
}

/**
 * 테스트 함수: Geocoding 테스트
 */
function testGeocoding() {
  var testAddress = '서울특별시 강남구 테헤란로 123';
  Logger.log('테스트 주소: ' + testAddress);
  
  var result = geocodeAddress(testAddress);
  if (result) {
    Logger.log('위도: ' + result.lat);
    Logger.log('경도: ' + result.lng);
  } else {
    Logger.log('Geocoding 실패');
  }
}

/**
 * 테스트 함수: 특정 행의 주소를 Geocoding하여 위도/경도 입력
 * 사용법: 함수 드롭다운에서 선택 후 실행 (기본값: 2행 테스트)
 * 특정 행을 테스트하려면 아래 rowNumber 변수를 변경하세요
 */
function testGeocodeRow() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getActiveSheet();
    
    // ========================================
    // 🔧 여기서 테스트할 행 번호를 지정하세요
    // ========================================
    var rowNumber = 2; // 헤더 제외, 실제 데이터 행 번호 (2행 = 첫 번째 데이터)
    // ========================================
    
    if (!rowNumber || rowNumber < 2) {
      Logger.log('테스트할 행 번호를 지정하세요. (헤더 제외, 최소 2행)');
      Logger.log('코드에서 rowNumber 변수를 수정하세요.');
      return;
    }
    
    Logger.log('=== 행 ' + rowNumber + ' 테스트 시작 ===');
    
    // P열(심사상태) 확인
    var statusCell = sheet.getRange(rowNumber, 16); // P열 = 16번째 열
    var statusValue = String(statusCell.getValue()).trim();
    Logger.log('심사상태 (P열): ' + statusValue);
    
    if (statusValue !== '승인') {
      Logger.log('심사상태가 "승인"이 아닙니다. 현재 값: ' + statusValue);
      return;
    }
    
    // 이미 위도/경도가 있는지 확인
    var latCell = sheet.getRange(rowNumber, 17); // Q열 = 17번째 열 (위도)
    var lngCell = sheet.getRange(rowNumber, 18); // R열 = 18번째 열 (경도)
    var existingLat = latCell.getValue();
    var existingLng = lngCell.getValue();
    
    if (existingLat && existingLng && existingLat !== '' && existingLng !== '') {
      Logger.log('이미 좌표가 존재합니다. 위도: ' + existingLat + ', 경도: ' + existingLng);
      Logger.log('기존 좌표를 덮어쓰시겠습니까? (덮어쓰려면 수동으로 Q, R열을 비우고 다시 실행하세요)');
      return;
    }
    
    // F열(도로명 주소) 읽기
    var addressCell = sheet.getRange(rowNumber, 6);
    var address = String(addressCell.getValue()).trim();
    Logger.log('주소 (F열): ' + address);
    
    if (!address || address === '') {
      Logger.log('주소가 없습니다.');
      return;
    }
    
    // Geocoding 수행
    Logger.log('Geocoding 수행 중...');
    var geocodeResult = geocodeAddress(address);
    
    if (geocodeResult && geocodeResult.lat && geocodeResult.lng) {
      // Q열(위도), R열(경도)에 값 입력
      latCell.setValue(geocodeResult.lat);
      lngCell.setValue(geocodeResult.lng);
      
      Logger.log('✅ 좌표 입력 완료!');
      Logger.log('위도 (Q열): ' + geocodeResult.lat);
      Logger.log('경도 (R열): ' + geocodeResult.lng);
    } else {
      Logger.log('❌ Geocoding 실패: ' + address);
      Logger.log('주소를 다시 확인해주세요.');
    }
    
  } catch (error) {
    Logger.log('❌ 테스트 오류: ' + error.toString());
  }
}

