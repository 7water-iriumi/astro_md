const form = document.getElementById('horoscope-form');
const resultContainer = document.getElementById('result-container');
const generateBtn = document.getElementById('generate-btn');
const loadingEl = document.getElementById('loading');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const errorBox = document.getElementById('error-box');

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

    // Prepare form data with fallback for unknown time (12:00)
    const fd = new FormData(form);
    const hour = (fd.get('hour') || '').toString().trim();
    const minute = (fd.get('minute') || '').toString().trim();
    if (hour === '') fd.set('hour', '12');
    if (minute === '') fd.set('minute', '0');

    if (resultContainer) resultContainer.innerHTML = '<p>生成中...</p>';
    toggleLoading(true);

    fetch('/generate', {
      method: 'POST',
      body: fd
    })
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
      if (结果Container) resultContainer.innerHTML = '';
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
    a.download = 'horoscope.md';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });
}

