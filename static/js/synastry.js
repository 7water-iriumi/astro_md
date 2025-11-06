const form = document.getElementById('synastry-form');
const resultContainer = document.getElementById('result-container');
const generateBtn = document.getElementById('generate-btn');
const loadingEl = document.getElementById('loading');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const errorBox = document.getElementById('error-box');
const hour1 = document.getElementById('hour');
const minute1 = document.getElementById('minute');
const hour2 = document.getElementById('hour2');
const minute2 = document.getElementById('minute2');
const timeUnknown1 = document.getElementById('time-unknown');
const timeUnknown2 = document.getElementById('time-unknown2');

function setDisabled(el, on) { if (el) el.disabled = !!on; }
function syncTimeUnknownUI() {
  setDisabled(hour1, timeUnknown1 && timeUnknown1.checked);
  setDisabled(minute1, timeUnknown1 && timeUnknown1.checked);
  setDisabled(hour2, timeUnknown2 && timeUnknown2.checked);
  setDisabled(minute2, timeUnknown2 && timeUnknown2.checked);
}
if (timeUnknown1) timeUnknown1.addEventListener('change', syncTimeUnknownUI);
if (timeUnknown2) timeUnknown2.addEventListener('change', syncTimeUnknownUI);
syncTimeUnknownUI();

function toggleLoading(loading) {
  if (!generateBtn || !loadingEl) return;
  generateBtn.disabled = loading;
  loadingEl.style.display = loading ? 'inline' : 'none';
  generateBtn.setAttribute('aria-busy', loading ? 'true' : 'false');
}

if (form) {
  form.addEventListener('submit', function(event) {
    event.preventDefault();
    if (errorBox) errorBox.textContent = '';

    const fd = new FormData(form);
    // Fallback for both charts
    const h1 = (fd.get('hour') || '').toString().trim();
    const m1 = (fd.get('minute') || '').toString().trim();
    if (h1 === '') fd.set('hour', '12');
    if (m1 === '') fd.set('minute', '0');
    if (timeUnknown1 && timeUnknown1.checked) fd.set('time_unknown', 'true');
    const h2 = (fd.get('hour2') || '').toString().trim();
    const m2 = (fd.get('minute2') || '').toString().trim();
    if (h2 === '') fd.set('hour2', '12');
    if (m2 === '') fd.set('minute2', '0');
    if (timeUnknown2 && timeUnknown2.checked) fd.set('time_unknown2', 'true');

    if (resultContainer) resultContainer.innerHTML = '<p>生成中...</p>';
    toggleLoading(true);

    fetch('/generate', { method: 'POST', body: fd })
      .then(async (response) => {
        if (!response.ok) {
          try {
            const err = await response.json();
            throw new Error(err.error || 'Network response was not ok');
          } catch (_) {
            throw new Error('ネットワークまたはサーバーエラーが発生しました');
          }
        }
        return response.json();
      })
      .then(data => {
        if (!resultContainer) return;
        if (data.markdown) {
          const pre = document.createElement('pre');
          pre.textContent = data.markdown;
          resultContainer.innerHTML = '';
          resultContainer.appendChild(pre);
          if (copyBtn) { copyBtn.hidden = false; copyBtn.dataset.content = data.markdown; }
          if (downloadBtn) { downloadBtn.hidden = false; downloadBtn.dataset.content = data.markdown; }
        } else if (data.error) {
          resultContainer.innerHTML = '';
          if (errorBox) errorBox.textContent = `エラー: ${data.error}`;
          if (copyBtn) copyBtn.hidden = true;
          if (downloadBtn) downloadBtn.hidden = true;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        if (resultContainer) resultContainer.innerHTML = '';
        if (errorBox) errorBox.textContent = `エラーが発生しました: ${error.message}`;
        if (copyBtn) copyBtn.hidden = true;
        if (downloadBtn) downloadBtn.hidden = true;
      })
      .finally(() => {
        toggleLoading(false);
      });
  });
}

if (copyBtn) {
  copyBtn.addEventListener('click', async () => {
    const text = copyBtn.dataset.content || '';
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta); ta.select();
        document.execCommand('copy'); document.body.removeChild(ta);
      }
      copyBtn.textContent = 'コピーしました';
      setTimeout(() => (copyBtn.textContent = 'コピー'), 1500);
    } catch (_) {
      copyBtn.textContent = 'コピー失敗';
      setTimeout(() => (copyBtn.textContent = 'コピー'), 1500);
    }
  });
}

if (downloadBtn) {
  downloadBtn.addEventListener('click', () => {
    const content = downloadBtn.dataset.content || '';
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'synastry.md';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
}
