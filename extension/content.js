// 从 YouTube 页面提取 videoId、标题和频道名 - 增强版
(function() {
  console.log('[YT Extension] Content script loaded');
  
  const getVideoId = () => {
    console.log('[YT Extension] Current URL:', location.href);
    const url = new URL(location.href);
    if (url.hostname.includes('youtube.com')) {
      const videoId = url.searchParams.get('v');
      console.log('[YT Extension] URL params:', url.searchParams.toString());
      console.log('[YT Extension] Extracted video ID:', videoId);
      return videoId;
    }
    console.log('[YT Extension] Not a YouTube URL');
    return null;
  };

  const getTitle = () => {
    // 尝试多种方式获取标题
    let title = document.title.replace(/ - YouTube$/, '');
    
    // 如果标题为空或只是 "YouTube"，尝试从页面元素获取
    if (!title || title === 'YouTube') {
      const titleSelectors = [
        '#title h1.ytd-watch-metadata yt-formatted-string',
        'h1.title.style-scope.ytd-video-primary-info-renderer',
        '#container h1',
        'h1[class*="title"]',
        'ytd-watch-metadata h1',
        '.ytd-video-primary-info-renderer h1',
        '.watch-title'
      ];
      
      for (const selector of titleSelectors) {
        const titleElement = document.querySelector(selector);
        if (titleElement && titleElement.textContent.trim()) {
          title = titleElement.textContent.trim();
          break;
        }
      }
    }
    
    console.log('[YT Extension] Extracted title:', title);
    return title || 'Unknown Title';
  };

  const getChannel = () => {
    // 尝试多种方式获取频道名
    const selectors = [
      'ytd-video-owner-renderer a.yt-simple-endpoint',
      '#channel-name a',
      '#owner-text a', 
      '.ytd-channel-name a',
      'ytd-channel-name a',
      '.owner-text a',
      '.ytd-video-owner-renderer .ytd-channel-name',
      '[class*="channel"] a',
      '[class*="owner"] a'
    ];
    
    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el && el.textContent.trim()) {
        const channel = el.textContent.trim();
        console.log('[YT Extension] Extracted channel:', channel);
        return channel;
      }
    }
    
    console.log('[YT Extension] Channel not found');
    return 'Unknown Channel';
  };

  const sendMeta = () => {
    console.log('[YT Extension] sendMeta called');
    const meta = { 
      videoId: getVideoId(), 
      title: getTitle(), 
      channel: getChannel(), 
      url: location.href 
    };
    
    console.log('[YT Extension] Meta data collected:', meta);
    
    if (!meta.videoId) {
      console.warn('[YT Extension] No video ID found, meta may not be useful');
    }
    
    if (chrome.runtime?.sendMessage) {
      console.log('[YT Extension] Sending message to popup');
      chrome.runtime.sendMessage({ type: 'YT_META', payload: meta }, (response) => {
        if (chrome.runtime.lastError) {
          console.error('[YT Extension] Message send error:', chrome.runtime.lastError);
        } else {
          console.log('[YT Extension] Message sent successfully, response:', response);
        }
      });
    } else {
      console.error('[YT Extension] Chrome runtime not available');
    }
  };

  // 等待页面加载完成后再提取信息
  const waitAndSend = () => {
    // 等待一段时间让页面完全加载
    setTimeout(sendMeta, 1000);
    // 也立即发送一次
    sendMeta();
  };

  // 监听页面加载状态
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitAndSend);
  } else {
    waitAndSend();
  }

  // 监听URL变化 (YouTube是SPA)
  let lastUrl = location.href;
  const observer = new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      console.log('[YT Extension] URL changed:', lastUrl);
      // URL变化后等待新页面加载
      setTimeout(sendMeta, 2000);
    }
  });
  
  observer.observe(document, { childList: true, subtree: true });

  // 监听来自popup的消息
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'PING') {
      console.log('[YT Extension] Received PING, sending current meta');
      sendMeta();
      sendResponse({ received: true });
    }
  });

  console.log('[YT Extension] Content script initialization complete');
})();