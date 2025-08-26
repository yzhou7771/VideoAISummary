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

  setStatus('🔄 正在请求后端生成结论…（可能需要数十秒）');
  setConclusions([]); 
  $("summary").textContent = ''; 
  $("transcript").textContent = '';

  const requestUrl = `${apiBase}/api/summarize?video_id=${encodeURIComponent(currentMeta.videoId)}&lang=${encodeURIComponent(lang)}`;
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
    setStatus('❌ 出错：' + err.message);
    
    // 提供更详细的错误信息
    if (err.message.includes('Failed to fetch')) {
      setStatus('❌ 无法连接到后端服务 - 请确认服务器正在运行在 ' + apiBase);
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
function escapeHtml(str) { return str?.replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[s])) || ''; }

// 获取当前活动 tab 的最新元信息（兼容 popup 打开时）
(async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return;
  chrome.tabs.sendMessage(tab.id, { type: 'PING' }, () => {});
})();