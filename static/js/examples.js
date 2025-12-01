(() => {
  const container = document.getElementById('examples');
  const badge = document.getElementById('model-badge');

  function excerpt(text, maxLen = 160) {
    const t = (text || '').trim();
    if (t.length <= maxLen) return t;
    return t.slice(0, maxLen) + '…';
  }

  function renderExample(ex) {
    // Update badge with the first example's model
    if (badge && badge.textContent === 'Model: —' && ex.model) {
      badge.textContent = `Model: ${ex.model}`;
    }

    const wrap = document.createElement('div');
    wrap.className = 'example-card';

    const user = document.createElement('div');
    user.className = 'bubble user';
    user.textContent = ex.user_message || '（ユーザーの質問）';

    const ai = document.createElement('div');
    ai.className = 'bubble ai';

    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = excerpt(ex.ai_response || '');
    const body = document.createElement('div');
    body.style.marginTop = '6px';
    body.style.whiteSpace = 'pre-wrap';
    body.textContent = ex.ai_response || '';

    details.appendChild(summary);
    details.appendChild(body);
    ai.appendChild(details);

    wrap.appendChild(user);
    wrap.appendChild(ai);
    container.appendChild(wrap);
  }

  fetch(`${window.location.origin}${window.location.pathname.startsWith('/examples') ? '' : ''}/static/data/examples.json`, { cache: 'no-cache' })
    .then(r => r.json())
    .then(data => {
      const list = Array.isArray(data?.examples) ? data.examples : [];
      if (!list.length) {
        container.textContent = '実例がまだありません。準備中です。';
        return;
      }
      list.forEach(renderExample);
    })
    .catch(() => {
      container.textContent = '実例の読み込みに失敗しました。';
    });
})();

