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


  // Project carousel
  $$('[data-carousel]').forEach(function (car) {
    var track = $('.car-track', car), slides = $$('.car-slide', car), thumbs = $$('.car-thumb', car);
    var countEl = $('.car-count b', car), bar = $('.car-progress i', car), play = $('.car-play', car);
    var n = slides.length, cur = 0, timer = null, start = 0, DUR = 5000;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var paused = reduce, hover = false;
    function pad(i) { return (i < 9 ? '0' : '') + (i + 1); }
    function mark(i) {
      cur = i; countEl.textContent = pad(i);
      thumbs.forEach(function (t, k) { t.setAttribute('aria-current', k === i); });
      var t = thumbs[i];
      if (t) { var row = t.parentNode; row.scrollTo({ left: t.offsetLeft - row.clientWidth / 2 + t.clientWidth / 2 }); }
    }
    function go(i) { i = (i + n) % n; track.scrollTo({ left: slides[i].offsetLeft }); mark(i); restart(); }
    function restart() { start = performance.now(); }
    function tick(now) {
      if (!paused && !hover && n > 1 && !document.hidden) {
        var p = Math.min(1, (now - start) / DUR);
        bar.style.width = (p * 100) + '%';
        if (p >= 1) go(cur + 1);
      } else { start = now - (parseFloat(bar.style.width) || 0) / 100 * DUR; }
      requestAnimationFrame(tick);
    }
    $('.car-prev', car).addEventListener('click', function () { go(cur - 1); });
    $('.car-next', car).addEventListener('click', function () { go(cur + 1); });
    thumbs.forEach(function (t) { t.addEventListener('click', function () { go(+t.dataset.i); }); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
    });
    var st; track.addEventListener('scroll', function () {
      clearTimeout(st); st = setTimeout(function () {
        var i = Math.round(track.scrollLeft / track.clientWidth);
        if (i !== cur && i >= 0 && i < n) { mark(i); restart(); }
      }, 90);
    }, { passive: true });
    car.addEventListener('mouseenter', function () { hover = true; });
    car.addEventListener('mouseleave', function () { hover = false; });
    function setPaused(p) { paused = p; play.setAttribute('aria-pressed', p); play.setAttribute('aria-label', p ? 'Play slideshow' : 'Pause slideshow'); if (p) bar.style.width = '0'; restart(); }
    play.addEventListener('click', function () { setPaused(!paused); });
    setPaused(paused); mark(0); restart(); requestAnimationFrame(tick);
    // open current slide large
    track.addEventListener('click', function (e) {
      var img = e.target.closest('.car-slide img'); if (!img) return;
      openLightbox(img.currentSrc || img.src, img.alt);
    });
  });

  function openLightbox(src, alt) {
    var lb = document.createElement('div'); lb.className = 'lightbox';
    lb.innerHTML = '<button type="button" aria-label="Close">&times;</button><img alt="">';
    $('img', lb).src = src; $('img', lb).alt = alt || '';
    lb.addEventListener('click', function () { lb.remove(); });
    document.addEventListener('keydown', function esc(e) { if (e.key === 'Escape') { lb.remove(); document.removeEventListener('keydown', esc); } });
    document.body.appendChild(lb);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('.photo-grid a'); if (!a) return;
    e.preventDefault(); openLightbox(a.dataset.full, $('img', a).alt);
  });


  // Team directory: filter, search, bio dialog
  var tg = $('#team-grid');
  if (tg) {
    var dept = '', tq = '';
    var people = $$('.sp-person', tg);
    var applyTeam = function () {
      var shown = 0;
      people.forEach(function (p) {
        var ok = (!dept || p.dataset.dept === dept) && (!tq || p.dataset.search.indexOf(tq) > -1);
        p.hidden = !ok; if (ok) shown++;
      });
      $('#team-empty').hidden = shown > 0;
    };
    $$('#team-chips button').forEach(function (b) {
      b.addEventListener('click', function () {
        dept = b.dataset.dept;
        $$('#team-chips button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
        applyTeam();
      });
    });
    var tqi = $('#team-q'); if (tqi) tqi.addEventListener('input', function () { tq = tqi.value.trim().toLowerCase(); applyTeam(); });
  }
  var dlg = $('#bio-dialog');
  if (dlg) {
    document.addEventListener('click', function (e) {
      var b = e.target.closest('[data-bio]'); if (!b) return;
      var tpl = document.getElementById('bio-' + b.dataset.bio); if (!tpl) return;
      var body = $('.sp-dialog-body', dlg); body.innerHTML = ''; body.appendChild(tpl.content.cloneNode(true));
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
      body.scrollTop = 0;
    });
    $('.sp-dialog-close', dlg).addEventListener('click', function () { dlg.close ? dlg.close() : dlg.removeAttribute('open'); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  }

  // Tabs
  $$('[data-tabs]').forEach(function (box) {
    var tabs = $$('[role="tab"]', box);
    var select = function (t) {
      tabs.forEach(function (x) {
        var on = x === t; x.setAttribute('aria-selected', on); x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute('aria-controls')).hidden = !on;
      });
    };
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowDown' || e.key === 'ArrowRight' ? 1 : e.key === 'ArrowUp' || e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return; e.preventDefault();
        var n = tabs[(i + d + tabs.length) % tabs.length]; select(n); n.focus();
      });
    });
  });

  // Town finder
  var townQ = $('#town-q');
  if (townQ) townQ.addEventListener('input', function () {
    var q = townQ.value.trim().toLowerCase(), shown = 0;
    $$('#town-grid .sp-town').forEach(function (a) { var ok = !q || a.dataset.search.indexOf(q) > -1; a.hidden = !ok; if (ok) shown++; });
    $('#town-empty').hidden = shown > 0;
  });

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
  $$('form.estimate, #sellForm').forEach(function (form) {
    if (form.dataset.bound) return; form.dataset.bound = 1;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      form.innerHTML = '<div class="form-ok">Thanks! This is a staging site, so this form isn’t connected yet. Please call (316) 927-2233 and we’ll take it from there.</div>';
    });
  });

  // Customer reviews: topic filter, search, load more, expand
  var rvGrid = $('#rv-grid');
  if (rvGrid) {
    var cards = $$('.rv-card', rvGrid), topic = '', rq = '', shown = 24, STEP = 24;
    var loadBtn = $('#rv-load'), empty = $('#rv-empty');
    var applyRv = function () {
      var match = cards.filter(function (c) {
        var okT = !topic || c.dataset.topics.split('|').indexOf(topic) > -1;
        return okT && (!rq || c.dataset.search.indexOf(rq) > -1);
      });
      cards.forEach(function (c) { c.hidden = true; });
      match.forEach(function (c, i) { c.hidden = i >= shown; });
      empty.hidden = match.length > 0;
      loadBtn.parentNode.hidden = match.length <= shown;
    };
    $$('#rv-chips button').forEach(function (b) {
      b.addEventListener('click', function () {
        topic = b.dataset.topic; shown = STEP;
        $$('#rv-chips button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
        applyRv();
      });
    });
    var rqi = $('#rv-q'); if (rqi) rqi.addEventListener('input', function () { rq = rqi.value.trim().toLowerCase(); shown = STEP; applyRv(); });
    loadBtn.addEventListener('click', function () { shown += STEP; applyRv(); });
    rvGrid.addEventListener('click', function (e) {
      var b = e.target.closest('.rv-more'); if (!b) return;
      var t = b.previousElementSibling, open = b.getAttribute('aria-expanded') !== 'true';
      t.classList.toggle('clamp', !open); b.setAttribute('aria-expanded', open);
      b.textContent = open ? 'Show less' : 'Read full review';
    });
    applyRv();
  }
})();
