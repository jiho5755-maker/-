/*
 * =============================================
 * 모바일 유튜브 자동화 스크립트 (Google Apps Script 방식)
 * =============================================
 * 
 * 모바일 버전: 최신 영상 3개만 표시
 * Google Apps Script를 프록시로 사용하는 방식입니다.
 * 메이크샵 모바일에서 100% 작동합니다.
 * 
 * 설정 방법:
 * 1. youtube-proxy.gs를 Google Apps Script에 배포
 * 2. 배포 URL을 아래 GOOGLE_SCRIPT_URL에 입력
 * =============================================
 */

const Myswiper = new Swiper('.banner_section .swiper', {
    slidesPerView: "auto",
    centeredSlides: true,
    spaceBetween: 25,
});

$(function(){
    // 카테고리 탭 클릭 이벤트
    $("ul.category_name>li>a").click(function(e){
        e.preventDefault();
        console.log("click!!!")
        $("ul.category_name>li>a").removeClass("on");
        $(this).addClass("on");
        let n=$(this).parent("li").index();
        $("ul.tap_cont>li").hide();
        $("ul.tap_cont>li").eq(n).show()
    });
    
    // 슬라이드 정지/재생 버튼
    $(".btn_stop").click(function(){
        swiper.autoplay.stop();
        if( $(this).hasClass("btn_stop") ){
            $(this).removeClass("btn_stop").addClass("btn_play"); 
        }
        else{
            $(this).removeClass("btn_play").addClass("btn_stop");
            swiper.autoplay.start();
        }
    });
    
    // YouTube 영상 자동 로드
    loadMobileYouTubeVideos();
});


/*
 * =============================================
 * Google Apps Script URL 설정
 * =============================================
 * 
 * 아래 URL을 본인의 Google Apps Script 배포 URL로 교체하세요!
 * 데스크톱과 동일한 URL을 사용합니다.
 * =============================================
 */
var GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxNQxgd8Ew0oClPSIoSA3vbtbf4LoOyHL6j7J1cXSyI1gmaL3ya6teTwmu883js4zSkwg/exec';


/*
 * 모바일용 YouTube 영상 자동 로드 (3개만 + 캐싱)
 * 하루에 한 번만 새로고침하고 나머지는 캐시 사용
 */
function loadMobileYouTubeVideos() {
    var container = document.getElementById('youtube-container');
    if (!container) {
        console.log('[YouTube Mobile] youtube-container를 찾을 수 없습니다.');
        return;
    }
    
    // 캐시 확인 (24시간 = 86400000ms)
    var CACHE_KEY = 'youtube_mobile_videos_cache';
    var CACHE_TIME_KEY = 'youtube_mobile_cache_time';
    var CACHE_DURATION = 24 * 60 * 60 * 1000; // 24시간
    
    try {
        var cachedData = localStorage.getItem(CACHE_KEY);
        var cacheTime = localStorage.getItem(CACHE_TIME_KEY);
        var now = Date.now();
        
        // 캐시가 있고 24시간이 지나지 않았으면 캐시 사용
        if (cachedData && cacheTime && (now - parseInt(cacheTime)) < CACHE_DURATION) {
            console.log('[YouTube Mobile] 캐시된 영상 사용 (마지막 업데이트: ' + 
                        new Date(parseInt(cacheTime)).toLocaleString('ko-KR') + ')');
            var videos = JSON.parse(cachedData);
            displayMobileYouTubeVideos(videos);
            return;
        }
    } catch (e) {
        console.log('[YouTube Mobile] 캐시 확인 실패, 새로 로드합니다:', e);
    }
    
    // 캐시가 없거나 만료되었으면 API 호출
    console.log('[YouTube Mobile] 영상 로드 시작... (3개)');
    
    var MAX_RESULTS = 3;  // 모바일은 3개만 표시
    var apiUrl = GOOGLE_SCRIPT_URL + '?count=' + MAX_RESULTS + '&t=' + Date.now();
    
    // 로딩 메시지 표시
    container.innerHTML = '<div class="loading-message"><div class="spinner"></div><p>최신 영상을 불러오는 중...</p></div>';
    
    // jQuery AJAX로 데이터 가져오기
    jQuery.ajax({
        url: apiUrl,
        dataType: 'json',
        cache: false,
        timeout: 10000,
        success: function(data) {
            if (data.status === 'success' && data.items && data.items.length > 0) {
                console.log('[YouTube Mobile] ' + data.items.length + '개 영상 로드 성공');
                
                // 캐시에 저장
                try {
                    localStorage.setItem(CACHE_KEY, JSON.stringify(data.items));
                    localStorage.setItem(CACHE_TIME_KEY, Date.now().toString());
                    console.log('[YouTube Mobile] 캐시 저장 완료 (다음 업데이트: 24시간 후)');
                } catch (e) {
                    console.log('[YouTube Mobile] 캐시 저장 실패:', e);
                }
                
                displayMobileYouTubeVideos(data.items);
            } else {
                console.error('[YouTube Mobile] 데이터 없음:', data);
                showMobileErrorMessage();
            }
        },
        error: function(xhr, status, error) {
            console.error('[YouTube Mobile] API 호출 실패:', error);
            showMobileErrorMessage();
        }
    });
}

/*
 * 모바일 영상 목록 표시
 */
function displayMobileYouTubeVideos(videos) {
    var container = document.getElementById('youtube-container');
    container.innerHTML = '';
    container.className = 'mobile-youtube-grid';
    
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
        
        // 제목 길이 제한 (모바일은 조금 더 짧게)
        var title = video.title;
        if (title && title.length > 45) {
            title = title.substring(0, 45) + '...';
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
        
        // 로드 완료 시 애니메이션
        (function(item) {
            var iframe = item.querySelector('iframe');
            iframe.onload = function() {
                item.classList.add('loaded');
            };
        })(videoItem);
    }
    
    console.log('[YouTube Mobile] 모든 영상 표시 완료');
}

/*
 * 모바일 에러 메시지 표시
 */
function showMobileErrorMessage() {
    var container = document.getElementById('youtube-container');
    container.innerHTML = '<div class="error-message">' +
        '<p style="font-size: 16px; color: #555; margin-bottom: 12px;">' +
            '최신 영상을 불러오는 중입니다' +
        '</p>' +
        '<p style="font-size: 13px; color: #999;">' +
            '잠시 후 다시 시도하거나<br>' +
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


// 메이크샵 기본 상품 리스트 함수들
function get_main_list(_t_name, _page, _element, _page_html, _row) {
    if ($(_element).length > 0) {
        $.ajax({
            url: '/m/product_list.action.html?r=' + Math.random(),
            type: 'GET',
            dataType: 'json',
            data: {
                action_mode: 'GET_MAIN_PRODUCT_LIST',
                tag_name: _t_name,
                page_id : get_page_id(),
                page: _page
            },  
            success: function(res) {
                var dom = $('<div>').html(res.html);
                if ($('ul.items:only-child', $(_element)).length == 0) {
                    $(_element).append($('<ul class="items"></ul>'));
                }
                $('ul.items', _element).append($('ul.items', dom).html());

                if (res.is_page_end == true) {
                    $('.' + _page_html).hide();
                } else {
                    _page++;
                    $('.' + _page_html + ' > a').prop('href', "javascript:get_main_list('"+_t_name+"', " + _page + ", '" + _element + "', '" + _page_html + "', '" + _row + "');");
                }   
                dom = null;    
            }
        }); 
    }
}

$(function() {
    get_main_list('block_special_product', 1, '.MK_block_special_product', 'btn-special_product', '1');
    get_main_list('block_recmd_product', 1, '.MK_block_recmd_product', 'btn-recmd_product', '1');
    get_main_list('block_new_product', 1, '.MK_block_new_product', 'btn-new_product', '1');
    get_main_list('block_add1_product', 1, '.MK_block_add1_product', 'btn-add1_product', '1');
    get_main_list('block_add2_product', 1, '.MK_block_add2_product', 'btn-add2_product', '1');
    get_main_list('block_add3_product', 1, '.MK_block_add3_product', 'btn-add3_product', '1');
    get_main_list('block_add4_product', 1, '.MK_block_add4_product', 'btn-add4_product', '1');
    get_main_list('block_add5_product', 1, '.MK_block_add5_product', 'btn-add5_product', '1');
});

