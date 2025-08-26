const $ = (id) => document.getElementById(id);
let currentMeta = null;
let showAdvanced = false;

console.log('[YT Extension Popup] Starting popup initialization');

// 恢复用户设置并设置默认值
chrome.storage.sync.get(['apiBase', 'lang'], (cfg) => {
  $("apiBase").value = cfg.apiBase || 'http://localhost:8000';
  $("lang").value = cfg.lang || 'zh';
  console.log('[YT Extension Popup] Settings restored:', cfg);
});

// 双击视频状态区域显示/隐藏高级设置
$("videoMeta").addEventListener('dblclick', () => {
  showAdvanced = !showAdvanced;
  $("apiRow").style.display = showAdvanced ? 'flex' : 'none';
  $("langRow").style.display = showAdvanced ? 'flex' : 'none';
  console.log('[YT Extension Popup] Advanced settings:', showAdvanced ? 'shown' : 'hidden');
});

// 监听 content script 发送的元信息
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  console.log('[YT Extension Popup] Received message:', msg);
  if (msg?.type === 'YT_META') {
    currentMeta = msg.payload;
    console.log('[YT Extension Popup] Updated current meta:', currentMeta);
    renderMeta();
  }
});

function renderMeta() {
  const el = $("videoMeta");
  
  console.log('[YT Extension Popup] Rendering meta:', currentMeta);
  
  if (!currentMeta || !currentMeta.videoId) {
    el.innerHTML = `
      <div style="color: #666; text-align: center; padding: 10px;">
        ⚠️ No video detected<br/>
        <small>Please open a YouTube video page</small>
      </div>
    `;
    $("summarizeBtn").disabled = true;
    return;
  }
  
  $("summarizeBtn").disabled = false;
  el.innerHTML = `
    <div style="color: #333; text-align: center; padding: 8px;">
      <strong>✅ Video Ready</strong>
    </div>
  `;
}

$("summarizeBtn").addEventListener('click', async () => {
  console.log('[YT Extension Popup] Summarize button clicked');
  
  const apiBase = $("apiBase").value.trim() || 'http://localhost:8000';
  const lang = $("lang").value || 'zh';

  console.log('[YT Extension Popup] API Base:', apiBase, 'Language:', lang);
  console.log('[YT Extension Popup] Current Meta:', currentMeta);

  chrome.storage.sync.set({ apiBase, lang });

  if (!currentMeta?.videoId) {
    setStatus('❌ 未检测到视频ID - 请刷新YouTube页面重试');
    console.error('[YT Extension Popup] No video ID found');
    return;
  }

  // Check server status first
  setStatus('🔍 检查服务器状态...');
  const serverStatus = await checkServerStatus(apiBase);
  if (!serverStatus) {
    setStatus('❌ 无法连接到服务器');
    showDetailedError(`服务器连接失败：
• 请确认服务器运行在 ${apiBase}
• 检查网络连接
• 确认服务器地址正确`);
    return;
  }

  // Check if cookies are available and warn if not
  if (!serverStatus.cookies_available) {
    const shouldContinue = showCookiesReminder();
    if (!shouldContinue) {
      setStatus('⏸️ 已取消操作');
      return;
    }
  }

  setStatus('🔄 正在初始化处理流程...');
  setConclusions([]); 
  $("summary").textContent = ''; 
  $("transcript").textContent = '';
  clearErrorDetails(); // Clear any previous error messages

  const videoId = currentMeta.videoId;
  
  // Start progress monitoring
  startProgressMonitoring(apiBase, videoId);
  
  const requestUrl = `${apiBase}/api/summarize?video_id=${encodeURIComponent(videoId)}&lang=${encodeURIComponent(lang)}`;
  console.log('[YT Extension Popup] Making request to:', requestUrl);

  try {
    const res = await fetch(requestUrl);
    console.log('[YT Extension Popup] Response status:', res.status);
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status} - ${res.statusText}`);
    }
    
    const data = await res.json();
    console.log('[YT Extension Popup] Response data:', data);

    setConclusions(data?.conclusions || ['未获取到结论']);
    $("summary").textContent = data?.summary || '未获取到总结';
    $("transcript").textContent = data?.transcript_preview || '未获取到转录预览';
    setStatus('✅ 完成');
  } catch (err) {
    console.error('[YT Extension Popup] Request failed:', err);
    
    // 提供更友好的错误信息
    if (err.message.includes('Failed to fetch')) {
      setStatus('❌ 无法连接到后端服务');
      showDetailedError(`请确认以下事项：
• 后端服务正在运行在 ${apiBase}
• 网络连接正常
• 服务器地址设置正确`);
    } else if (err.message.includes('NetworkError')) {
      setStatus('❌ 网络连接问题');
      showDetailedError('请检查网络连接或稍后重试');
    } else if (err.message.includes('HTTP 401') || err.message.includes('Unauthorized')) {
      setStatus('❌ YouTube访问受限');
      showDetailedError(`可能的解决方案：
• YouTube cookies可能已过期
• 请尝试重新登录YouTube
• 检查服务器cookies.txt文件`);
    } else if (err.message.includes('HTTP 429')) {
      setStatus('❌ 请求过于频繁');
      showDetailedError('请稍等片刻后重试，或检查API限制设置');
    } else {
      setStatus('❌ 处理失败：' + err.message);
    }
  }
});

function setStatus(t) { $("status").textContent = t; }
function setConclusions(items) {
  const el = $("conclusions");
  el.innerHTML = '';
  items.forEach(t => {
    const li = document.createElement('li');
    li.textContent = t;
    el.appendChild(li);
  });
}

function showDetailedError(message) {
  // Create or update error details section
  let errorDetails = document.getElementById('errorDetails');
  if (!errorDetails) {
    errorDetails = document.createElement('div');
    errorDetails.id = 'errorDetails';
    errorDetails.style.cssText = `
      background: #ffebee;
      border: 1px solid #ffcdd2;
      border-radius: 4px;
      padding: 8px;
      margin: 8px 0;
      font-size: 11px;
      color: #c62828;
      white-space: pre-line;
      max-height: 100px;
      overflow-y: auto;
    `;
    $("status").parentNode.insertBefore(errorDetails, $("status").nextSibling);
  }
  errorDetails.textContent = message;
  errorDetails.style.display = 'block';
  
  // Auto-hide after 10 seconds
  setTimeout(() => {
    if (errorDetails && errorDetails.parentNode) {
      errorDetails.style.display = 'none';
    }
  }, 10000);
}

function clearErrorDetails() {
  const errorDetails = document.getElementById('errorDetails');
  if (errorDetails) {
    errorDetails.style.display = 'none';
  }
}

async function checkServerStatus(apiBase) {
  try {
    const response = await fetch(`${apiBase}/`);
    if (response.ok) {
      const data = await response.json();
      return data;
    }
  } catch (error) {
    console.log('[YT Extension Popup] Server status check failed:', error);
  }
  return null;
}

function showCookiesReminder() {
  const reminderMessage = `🔄 YouTube访问可能需要更新

建议操作：
• 访问 https://youtube.com 并登录
• 刷新页面以获取最新cookies
• 或联系管理员更新cookies.txt文件

点击"确定"继续尝试，或检查服务器状态`;

  if (confirm(reminderMessage)) {
    return true; // Continue with request
  }
  return false; // Cancel request
}

function startProgressMonitoring(apiBase, videoId) {
  console.log('[YT Extension Popup] Starting progress monitoring for:', videoId);
  
  let consecutiveErrors = 0;
  const maxConsecutiveErrors = 3;
  
  // Poll progress every 2 seconds
  const progressInterval = setInterval(async () => {
    try {
      const progressUrl = `${apiBase}/api/progress/${encodeURIComponent(videoId)}`;
      const response = await fetch(progressUrl);
      
      if (response.ok) {
        const progressData = await response.json();
        console.log('[YT Extension Popup] Progress update:', progressData);
        consecutiveErrors = 0; // Reset error counter
        
        // Update status with progress
        if (progressData.status === 'processing') {
          const progressBar = '█'.repeat(Math.floor(progressData.progress / 10)) + '░'.repeat(10 - Math.floor(progressData.progress / 10));
          const progressText = `🔄 ${progressData.current_step}\n${progressBar} ${progressData.progress}%`;
          setStatus(progressText);
        } else if (progressData.status === 'completed') {
          clearInterval(progressInterval);
          console.log('[YT Extension Popup] Progress monitoring completed');
        } else if (progressData.status === 'error') {
          clearInterval(progressInterval);
          setStatus(`❌ 处理出错: ${progressData.error}`);
          showDetailedError('处理过程中遇到错误，请检查视频链接或稍后重试');
        }
      } else if (response.status === 404) {
        // Progress not found - either completed very quickly or cleaned up
        consecutiveErrors++;
        if (consecutiveErrors >= maxConsecutiveErrors) {
          clearInterval(progressInterval);
          console.log('[YT Extension Popup] Progress monitoring stopped - not found');
        }
      }
    } catch (error) {
      console.log('[YT Extension Popup] Progress polling error:', error);
      consecutiveErrors++;
      if (consecutiveErrors >= maxConsecutiveErrors) {
        clearInterval(progressInterval);
        console.log('[YT Extension Popup] Progress monitoring stopped - too many errors');
      }
    }
  }, 1500); // Poll every 1.5 seconds for more responsive UI
  
  // Clean up after 5 minutes max
  setTimeout(() => {
    clearInterval(progressInterval);
    console.log('[YT Extension Popup] Progress monitoring timeout');
  }, 300000);
}

function escapeHtml(str) { return str?.replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])) || ''; }

// 获取当前活动 tab 的最新元信息（兼容 popup 打开时）
(async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return;
  chrome.tabs.sendMessage(tab.id, { type: 'PING' }, () => {});
})();