(function () {
  document.documentElement.classList.add('js');
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // Mobile navigation
  var nav = $('#nav'), mb = $('.menu-btn');
  function setNav(o) { if (!nav) return; nav.classList.toggle('open', o); if (mb) mb.setAttribute('aria-expanded', o); }
  if (mb) mb.addEventListener('click', function () { setNav(true); });
  var nc = $('.nav-close'); if (nc) nc.addEventListener('click', function () { setNav(false); });
  if (nav) nav.addEventListener('click', function (e) { if (e.target.closest('a')) setNav(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setNav(false); });

  // YouTube facade
  document.addEventListener('click', function (e) {
    var v = e.target.closest('[data-yt]'); if (!v || v.dataset.on) return;
    v.dataset.on = '1';
    v.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + v.dataset.yt + '?autoplay=1&rel=0" title="Video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
  });

  // Glossary term tooltips
  var tip;
  function showTip(a) {
    var t = a.getAttribute('data-tip'); if (!t) return;
    tip = tip || document.body.appendChild(document.createElement('div'));
    tip.className = 'tip'; tip.hidden = false;
    tip.innerHTML = '<b>Glossary</b>';
    tip.appendChild(document.createTextNode(t));
    var r = a.getBoundingClientRect();
    var left = Math.min(Math.max(12, r.left + window.scrollX), window.scrollX + document.documentElement.clientWidth - 332);
    tip.style.left = left + 'px';
    tip.style.top = (r.bottom + window.scrollY + 10) + 'px';
  }
  function hideTip() { if (tip) tip.hidden = true; }
  $$('a.term[data-tip]').forEach(function (a) {
    a.addEventListener('mouseenter', function () { showTip(a); });
    a.addEventListener('mouseleave', hideTip);
    a.addEventListener('focus', function () { showTip(a); });
    a.addEventListener('blur', hideTip);
  });

  // Glossary search
  var gq = $('input[data-filter=".gl-item"]');
  if (gq) gq.addEventListener('input', function () {
    var q = gq.value.trim().toLowerCase(), shown = 0;
    $$('.gl-group').forEach(function (g) {
      var any = 0;
      $$('.gl-item', g).forEach(function (it) { var m = !q || it.textContent.toLowerCase().indexOf(q) > -1; it.hidden = !m; if (m) any++; });
      g.hidden = !any; shown += any;
    });
    $('#noResults').hidden = !!shown;
  });

  // Learning center: render, filter, search, load more
  var grid = $('#postGrid');
  if (grid && window.POSTS) {
    var PAGE = 12, limit = PAGE, cat = '', q = '';
    var esc = function (s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    function list() {
      return window.POSTS.filter(function (p) {
        if (cat && (p.cats || []).indexOf(cat) < 0) return false;
        if (q && (p.title + ' ' + p.excerpt + ' ' + p.cat).toLowerCase().indexOf(q) < 0) return false;
        return true;
      });
    }
    function render() {
      var all = list(), items = all.slice(0, limit);
      grid.innerHTML = items.map(function (c) {
        return '<a class="pcard" href="' + esc(c.href) + '"><div class="ph">' + (c.img ? '<img loading="lazy" src="' + esc(c.img) + '" alt="">' : '') +
          '</div><div class="bd">' + ((c.cat || c.date) ? '<span class="meta">' + esc(c.cat) + (c.cat && c.date ? ' · ' : '') + esc(c.date) + '</span>' : '') +
          '<h3>' + esc(c.title) + '</h3>' + (c.excerpt ? '<p>' + esc(c.excerpt.length > 150 ? c.excerpt.slice(0, 147) + '…' : c.excerpt) + '</p>' : '') +
          '<span class="more">Read more →</span></div></a>';
      }).join('');
      $('#count').textContent = all.length + (all.length === 1 ? ' article' : ' articles');
      $('#noResults').hidden = all.length > 0;
      $('#moreBtn').parentNode.hidden = all.length <= limit;
    }
    $('#moreBtn').addEventListener('click', function () { limit += PAGE; render(); });
    var sq = $('#q');
    if (sq) sq.addEventListener('input', function () { q = sq.value.trim().toLowerCase(); limit = PAGE; render(); });
    $$('#catChips button[data-cat]').forEach(function (b) {
      b.addEventListener('click', function () {
        cat = b.dataset.cat; limit = PAGE;
        $$('#catChips button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
        render();
      });
    });
    render();
  }

  // Gallery lightbox
  document.addEventListener('click', function (e) {
    var a = e.target.closest('.gal a, .gal img'); if (!a) return;
    var img = a.tagName === 'IMG' ? a : $('img', a); if (!img) return;
    e.preventDefault();
    var lb = document.createElement('div'); lb.className = 'lightbox';
    lb.innerHTML = '<button type="button" aria-label="Close">&times;</button><img alt="">';
    $('img', lb).src = img.currentSrc || img.src; $('img', lb).alt = img.alt;
    lb.addEventListener('click', function () { lb.remove(); });
    document.body.appendChild(lb);
  });

  // Estimate forms (staging: no backend)
  $$('form.estimate').forEach(function (form) {
    if (form.dataset.bound) return; form.dataset.bound = 1;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.innerHTML = '<div class="form-ok">Thanks! This is a staging site, so the form isn’t connected yet. Please call (316) 927-2233 to schedule your free estimate.</div>';
    });
  });
})();
