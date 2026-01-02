/*
 * =============================================
 * main-google-script.js (Google Apps Script 방식)
 * =============================================
 * 
 * Google Apps Script를 프록시로 사용하는 방식입니다.
 * 메이크샵에서 100% 작동합니다.
 * 
 * 사용 전 설정 필요:
 * 1. youtube-proxy.gs를 Google Apps Script에 배포
 * 2. 배포 URL을 아래 GOOGLE_SCRIPT_URL에 입력
 * =============================================
 */

jQuery(document).ready(function(){
    var _ = jQuery;
    
    // 메인 banner
    var _mainBanner = $('.main_banner').bxSlider({              
        mode:"fade",
        auto: true,
        autoHover:true,
        speed: 500,
        pause: 5000,
        controls: true,
        useCSS : false,
        pager : true,
        nextText: '<i class="xi-angle-right-thin"></i>',
        prevText: '<i class="xi-angle-left-thin"></i>',
        pagerType: 'short',
        onSlideBefore: function() {
            _mainBanner.stopAuto();
        },
        onSlideAfter: function() {
            _mainBanner.startAuto();
        }
    });  
    
    _(window).on('resize', function(){
        _mainBanner.reloadSlider();
        if (typeof newCateSlider !== 'undefined') {
            newCateSlider.reloadSlider();
        }
    });

    if(_('.bestPrdSlider').find('.items').last().children().length === 0) _('.bestPrdSlider').find('.items').last().remove();
    var bestPrdSlider = jQuery('.bestPrdSlider').bxSlider({
        auto : false,
        autoHover: true,
        pager : false,
        prevText : '<i class="xi-angle-left"></i>',
        nextText : '<i class="xi-angle-right"></i>',
        infiniteLoop : false,
        controls : true,
        onSliderLoad : function(){
            var pagerLink = _('.bestPrdArea').find('.bx-pager-link');
            
            pagerLink.on('hover', function(){
                 bestPrdSlider.stopAuto();     
            });
            pagerLink.on('mouseleave', function(){
                 bestPrdSlider.startAuto();        
            });
        }
    });
    
    jQuery(window).on('resize', function(){
        bestPrdSlider.reloadSlider();
    });
    
    fontChangeFunc = function(){
        bestPrdSlider.reloadSlider();
    }

    jQuery(".bestPrdSlider ul li").mouseenter(function(){
        jQuery(this).find(".shoppingInfo").fadeIn();
    }).mouseleave(function(){
        jQuery(this).find(".shoppingInfo").fadeOut();
    });

    // YouTube 영상 자동 로드
    loadYouTubeVideos();
});


/*
 * =============================================
 * Google Apps Script URL 설정
 * =============================================
 * 
 * 아래 URL을 본인의 Google Apps Script 배포 URL로 교체하세요!
 * 
 * 배포 URL 얻는 방법:
 * 1. https://script.google.com 접속
 * 2. youtube-proxy.gs 코드 붙여넣기
 * 3. 배포 > 새 배포 > 웹 앱 선택
 * 4. 실행 계정: 나, 액세스: 모든 사용자
 * 5. 배포 후 URL 복사
 * =============================================
 */
var GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxNQxgd8Ew0oClPSIoSA3vbtbf4LoOyHL6j7J1cXSyI1gmaL3ya6teTwmu883js4zSkwg/exec';


/*
 * YouTube 영상 자동 로드 (Google Apps Script 방식 + 캐싱)
 * 하루에 한 번만 새로고침하고 나머지는 캐시 사용
 */
function loadYouTubeVideos() {
    var container = document.getElementById('youtube-container');
    if (!container) {
        console.log('[YouTube] youtube-container를 찾을 수 없습니다.');
        return;
    }
    
    // 캐시 확인 (24시간 = 86400000ms)
    var CACHE_KEY = 'youtube_videos_cache';
    var CACHE_TIME_KEY = 'youtube_cache_time';
    var CACHE_DURATION = 24 * 60 * 60 * 1000; // 24시간
    
    try {
        var cachedData = localStorage.getItem(CACHE_KEY);
        var cacheTime = localStorage.getItem(CACHE_TIME_KEY);
        var now = Date.now();
        
        // 캐시가 있고 24시간이 지나지 않았으면 캐시 사용
        if (cachedData && cacheTime && (now - parseInt(cacheTime)) < CACHE_DURATION) {
            console.log('[YouTube] 캐시된 영상 사용 (마지막 업데이트: ' + 
                        new Date(parseInt(cacheTime)).toLocaleString('ko-KR') + ')');
            var videos = JSON.parse(cachedData);
            displayYouTubeVideos(videos);
            return;
        }
    } catch (e) {
        console.log('[YouTube] 캐시 확인 실패, 새로 로드합니다:', e);
    }
    
    // 캐시가 없거나 만료되었으면 API 호출
    console.log('[YouTube] Google Apps Script로 영상 로드 시작...');
    
    var MAX_RESULTS = 4;
    var apiUrl = GOOGLE_SCRIPT_URL + '?count=' + MAX_RESULTS + '&t=' + Date.now();
    
    // 로딩 메시지 표시 (스피너 추가)
    container.innerHTML = '<div class="loading-message"><div class="spinner"></div><p>최신 영상을 불러오는 중...</p></div>';
    
    // jQuery AJAX로 데이터 가져오기
    jQuery.ajax({
        url: apiUrl,
        dataType: 'json',
        cache: false,
        timeout: 10000,
        success: function(data) {
            if (data.status === 'success' && data.items && data.items.length > 0) {
                console.log('[YouTube] ' + data.items.length + '개 영상 로드 성공');
                
                // 캐시에 저장
                try {
                    localStorage.setItem(CACHE_KEY, JSON.stringify(data.items));
                    localStorage.setItem(CACHE_TIME_KEY, Date.now().toString());
                    console.log('[YouTube] 캐시 저장 완료 (다음 업데이트: 24시간 후)');
                } catch (e) {
                    console.log('[YouTube] 캐시 저장 실패:', e);
                }
                
                displayYouTubeVideos(data.items);
            } else {
                console.error('[YouTube] 데이터 없음:', data);
                showErrorMessage();
            }
        },
        error: function(xhr, status, error) {
            console.error('[YouTube] API 호출 실패:', error);
            showErrorMessage();
        }
    });
}

/*
 * 영상 목록 표시
 */
function displayYouTubeVideos(videos) {
    var container = document.getElementById('youtube-container');
    container.innerHTML = '';
    container.className = 'youtube-grid';
    
    for (var i = 0; i < videos.length; i++) {
        var video = videos[i];
        var videoId = video.id;
        
        if (!videoId) continue;
        
        // 날짜 포맷팅
        var publishDate = new Date(video.publishedAt);
        var formattedDate = formatDate(publishDate);
        
        // 영상 아이템 생성
        var videoItem = document.createElement('div');
        videoItem.className = 'youtube-video-item';
        
        // 제목 길이 제한
        var title = video.title;
        if (title && title.length > 50) {
            title = title.substring(0, 50) + '...';
        }
        
        videoItem.innerHTML = '<div class="video-wrapper">' +
            '<iframe ' +
                'width="560" ' +
                'height="315" ' +
                'src="https://www.youtube.com/embed/' + videoId + '?rel=0&modestbranding=1" ' +
                'title="' + escapeHtml(video.title) + '" ' +
                'frameborder="0" ' +
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" ' +
                'referrerpolicy="strict-origin-when-cross-origin" ' +
                'allowfullscreen ' +
                'loading="lazy">' +
            '</iframe>' +
        '</div>' +
        '<div class="video-info">' +
            '<h4 class="video-title">' + escapeHtml(title) + '</h4>' +
            '<p class="video-date">' + formattedDate + '</p>' +
        '</div>';
        
        container.appendChild(videoItem);
        
        // 클로저 문제 해결을 위한 즉시 실행 함수
        (function(item) {
            var iframe = item.querySelector('iframe');
            iframe.onload = function() {
                item.classList.add('loaded');
            };
        })(videoItem);
    }
    
    console.log('[YouTube] 모든 영상 표시 완료');
}

/*
 * 에러 메시지 표시
 */
function showErrorMessage() {
    var container = document.getElementById('youtube-container');
    container.innerHTML = '<div class="error-message">' +
        '<p style="font-size: 18px; color: #555; margin-bottom: 15px;">' +
            '최신 영상을 불러오는 중입니다' +
        '</p>' +
        '<p style="font-size: 14px; color: #999;">' +
            '잠시 후 다시 시도하거나 ' +
            '<a href="https://www.youtube.com/channel/UCOt_7gyvjqHBw304hU4-FUw" ' +
               'target="_blank" ' +
               'style="color: #e74c3c; text-decoration: underline;">' +
               'YouTube 채널에서 직접 보기' +
            '</a>' +
        '</p>' +
    '</div>';
}

/*
 * 날짜 포맷팅 (한국어)
 */
function formatDate(date) {
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    
    var today = new Date();
    var diffTime = today - date;
    var diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return '오늘';
    if (diffDays === 1) return '어제';
    if (diffDays < 7) return diffDays + '일 전';
    if (diffDays < 30) return Math.floor(diffDays / 7) + '주 전';
    
    return year + '년 ' + month + '월 ' + day + '일';
}

/*
 * HTML 이스케이프 (XSS 방지)
 */
function escapeHtml(text) {
    if (!text) return '';
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

