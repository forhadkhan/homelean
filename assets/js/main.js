(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var yearEl = $('#year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- mobile menu ---------- */
  var header = $('.site-header');
  var menuBtn = $('#menuBtn');
  var nav = $('#nav');

  function setMenu(open) {
    header.classList.toggle('nav-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  menuBtn.addEventListener('click', function () {
    setMenu(!header.classList.contains('nav-open'));
  });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && header.classList.contains('nav-open')) {
      setMenu(false);
      menuBtn.focus();
    }
  });
  document.addEventListener('click', function (e) {
    if (header.classList.contains('nav-open') && !header.contains(e.target)) setMenu(false);
  });
  window.matchMedia('(min-width: 900px)').addEventListener('change', function (m) {
    if (m.matches) setMenu(false);
  });

  /* ---------- booking dialog ---------- */
  var dlg = $('#book');
  var bookForm = $('#bookForm');
  var bookDone = $('#bookDone');
  var bookErr = $('#bookErr');
  var bookSvc = $('#b-svc');
  var bookDate = $('#b-date');

  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function todayISO() {
    var d = new Date();
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }
  function decode(s) {
    var t = document.createElement('textarea');
    t.innerHTML = s;
    return t.value;
  }

  function openBook(service) {
    bookForm.hidden = false;
    bookDone.hidden = true;
    bookErr.textContent = '';
    $$('.field.bad', bookForm).forEach(function (f) { f.classList.remove('bad'); });
    bookDate.min = todayISO();
    if (service) {
      var name = decode(service);
      var opt = $$('option', bookSvc).filter(function (o) { return o.textContent === name; })[0];
      if (opt) bookSvc.value = opt.value || opt.textContent;
    }
    if (typeof dlg.showModal === 'function') {
      dlg.showModal();
      document.body.classList.add('lock');
    }
  }
  function closeBook() { if (dlg.open) dlg.close(); document.body.classList.remove('lock'); }

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-book]');
    if (trigger) {
      setMenu(false);
      openBook(trigger.getAttribute('data-book'));
      return;
    }
    if (e.target.closest('[data-close]')) closeBook();
  });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) closeBook(); });
  dlg.addEventListener('close', function () {
    document.body.classList.remove('lock');
    bookForm.reset();
  });

  /* one rule set for every form: returns an error message, or '' when the value is fine */
  var EMAIL = /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/;
  function phoneError(v) {
    v = v.trim();
    if (!v) return 'Enter your phone number.';
    if (/[^\d\s+\-().]/.test(v) || v.lastIndexOf('+') > 0) return 'Use digits only. A leading + is fine.';
    var d = v.replace(/\D/g, '');
    if (d.length < 7) return 'That looks too short. Include the area code.';
    if (d.length > 15) return 'That looks too long. Phone numbers have at most 15 digits.';
    if (/^(\d)\1+$/.test(d)) return 'Enter a real phone number.';
    return '';
  }
  function fieldError(el) {
    var v = el.value.trim();
    if (el.required && !v) {
      return el.type === 'tel' ? phoneError('') : el.type === 'email' ? 'Enter your email address.' : el.id === 'c-name' ? 'Enter your name.' : el.id === 'c-msg' ? 'Write a few words about what you need.' : 'This field is required.';
    }
    if (!v) return '';
    if (el.type === 'tel') return phoneError(v);
    if (el.type === 'email') return EMAIL.test(v) ? '' : 'Enter a valid email, like name@example.com.';
    if (el.id === 'c-name' && v.length < 2) return 'Enter your full name.';
    if (el.id === 'c-msg' && v.length < 10) return 'Add a little more detail (at least 10 characters).';
    return '';
  }
  function showError(el, msg) {
    var f = el.closest('.field');
    if (!f) return;
    f.classList.toggle('bad', !!msg);
    f.classList.toggle('ok', !msg && el.value.trim() !== '');
    el.setAttribute('aria-invalid', msg ? 'true' : 'false');
    var m = $('.msg', f);
    if (m) m.textContent = msg;
  }
  function validate(form) {
    var first = null;
    $$('[required]', form).forEach(function (el) {
      var msg = fieldError(el);
      showError(el, msg);
      if (msg && !first) first = el;
    });
    return first;
  }
  /* keep phone fields to phone characters while typing */
  $$('input[type=tel]').forEach(function (el) {
    el.addEventListener('input', function () {
      var v = el.value.replace(/[^\d\s+\-().]/g, '');
      v = v.charAt(0) + v.slice(1).replace(/\+/g, '');
      if (v !== el.value) el.value = v;
    });
  });
  $$('.field input, .field select, .field textarea').forEach(function (el) {
    el.addEventListener('input', function () {
      var f = el.closest('.field');
      if (!f) return;
      if (f.classList.contains('bad')) showError(el, fieldError(el));
      else f.classList.remove('ok');
    });
    el.addEventListener('blur', function () {
      if (el.value.trim() !== '' || isBad(el)) showError(el, fieldError(el));
    });
  });
  function isBad(el) { var f = el.closest('.field'); return !!f && f.classList.contains('bad'); }

  bookForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var bad = validate(bookForm);
    if (bad) {
      bookErr.textContent = 'Please complete the highlighted fields.';
      bad.focus();
      return;
    }
    bookErr.textContent = '';
    var d = new Date(bookDate.value + 'T00:00:00');
    var when = isNaN(d) ? bookDate.value : d.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
    $('#bookSummary').textContent = bookSvc.value + ' on ' + when + ', ' + $('#b-time').value.toLowerCase() +
      '. This is a demo site, so nothing was sent. Connect the form to your booking backend to receive requests.';
    bookForm.hidden = true;
    bookDone.hidden = false;
    var h = $('h2', bookDone);
    h.setAttribute('tabindex', '-1');
    h.focus();
  });

  /* ---------- contact form ---------- */
  var cForm = $('#contactForm');
  var cDone = $('#contactDone');
  var cMsg = $('#c-msg');
  var cCount = $('#c-count');
  function updateCount() {
    var n = cMsg.value.length;
    cCount.textContent = n + '/' + cMsg.maxLength;
    cCount.classList.toggle('near', n > cMsg.maxLength - 50);
  }
  cMsg.addEventListener('input', updateCount);
  cForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var bad = validate(cForm);
    if (bad) { bad.focus(); return; }
    var first = $('#c-name').value.trim().split(/\s+/)[0];
    var topic = $('input[name=topic]:checked', cForm);
    $('#contactSummary').textContent = 'Thanks, ' + first + '. ' + (topic ? 'Topic: ' + topic.value.toLowerCase() + '. ' : '') +
      'This is a demo site, so nothing was sent. Connect the form to a mail service to receive messages.';
    cForm.hidden = true;
    cDone.hidden = false;
    $('#contactDoneTitle').focus();
  });
  $('#contactAgain').addEventListener('click', function () {
    cForm.reset();
    $$('.field', cForm).forEach(function (f) { f.classList.remove('bad', 'ok'); var m = $('.msg', f); if (m) m.textContent = ''; });
    updateCount();
    cDone.hidden = true;
    cForm.hidden = false;
    $('#c-name').focus();
  });
  updateCount();

  /* ---------- service search ---------- */
  var sForm = $('#searchForm');
  var sInput = $('#q');
  var sMsg = $('#searchMsg');
  var cards = $$('.svc');
  var sList = $('#suggList');
  var services = cards.map(function (c) {
    var btn = $('[data-book]', c);
    var price = $('.from strong', c);
    return {
      name: decode(btn.getAttribute('data-book')),
      price: price ? price.textContent : '',
      icon: $('.ico', c).innerHTML,
      tint: ($('.ico', c).className.match(/tint-\w+/) || [''])[0],
      keys: (c.getAttribute('data-keys') + ' ' + c.querySelector('h3').textContent).toLowerCase()
    };
  });
  var sActive = -1;

  function suggest() {
    var tokens = sInput.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    var list = services.filter(function (s) {
      return tokens.every(function (t) { return s.keys.indexOf(t) !== -1; });
    });
    sList.innerHTML = '';
    sActive = -1;
    if (!list.length) {
      sList.innerHTML = '<li class="none" role="presentation">No service called that yet. Press Find to look anyway.</li>';
    }
    list.forEach(function (s, i) {
      var li = document.createElement('li');
      li.id = 'sg' + i;
      li.setAttribute('role', 'option');
      li.dataset.name = s.name;
      li.innerHTML = '<span class="ico ' + s.tint + '">' + s.icon + '</span><span class="nm"></span>' +
        '<span class="pr">' + (s.price ? 'From ' + s.price : '') + '</span>' +
        '<svg class="i go" aria-hidden="true"><use href="assets/icons.svg#chevron-right"/></svg>';
      $('.nm', li).textContent = s.name;
      sList.appendChild(li);
    });
    openSugg(true);
  }
  function openSugg(on) {
    sList.hidden = !on;
    sInput.setAttribute('aria-expanded', on ? 'true' : 'false');
    if (!on) sInput.removeAttribute('aria-activedescendant');
  }
  function setActive(i) {
    var items = $$('li[role=option]', sList);
    if (!items.length) return;
    sActive = (i + items.length) % items.length;
    items.forEach(function (li, n) { li.classList.toggle('on', n === sActive); li.setAttribute('aria-selected', n === sActive); });
    sInput.setAttribute('aria-activedescendant', items[sActive].id);
  }
  function chooseService(li) {
    sInput.value = li.dataset.name;
    openSugg(false);
    clearSearch();
    openBook(li.dataset.name);
  }
  sInput.addEventListener('click', suggest);
  sInput.addEventListener('input', suggest);
  sInput.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (sList.hidden) suggest();
      setActive(sActive + (e.key === 'ArrowDown' ? 1 : -1));
    } else if (e.key === 'Enter' && sActive > -1 && !sList.hidden) {
      e.preventDefault();
      chooseService($$('li[role=option]', sList)[sActive]);
    } else if (e.key === 'Escape' && !sList.hidden) {
      openSugg(false);
    }
  });
  sList.addEventListener('mousedown', function (e) {
    var li = e.target.closest('li[role=option]');
    if (li) { e.preventDefault(); chooseService(li); }
  });
  document.addEventListener('click', function (e) {
    if (!sForm.contains(e.target)) openSugg(false);
  });
  sForm.addEventListener('focusout', function () {
    setTimeout(function () { if (!sForm.contains(document.activeElement)) openSugg(false); }, 0);
  });

  function clearSearch() {
    cards.forEach(function (c) { c.classList.remove('is-hit', 'is-dim'); });
    sMsg.textContent = '';
  }
  sInput.addEventListener('input', function () { if (!sInput.value.trim()) clearSearch(); });
  sForm.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = sInput.value.trim().toLowerCase();
    openSugg(false);
    if (!q) { clearSearch(); return; }
    var tokens = q.split(/\s+/).filter(function (t) { return t.length > 1; });
    var hits = 0;
    cards.forEach(function (c) {
      var hay = (c.getAttribute('data-keys') + ' ' + c.textContent).toLowerCase();
      var words = hay.split(/[^a-z]+/).filter(function (w) { return w.length > 3; });
      var match = tokens.some(function (t) {
        return hay.indexOf(t) !== -1 || words.some(function (w) { return t.indexOf(w) === 0; });
      });
      c.classList.toggle('is-hit', match);
      c.classList.toggle('is-dim', !match);
      if (match) hits++;
    });
    if (!hits) {
      sMsg.textContent = 'No match for "' + sInput.value.trim() + '". Try cleaning, plumbing or painting.';
      cards.forEach(function (c) { c.classList.remove('is-dim'); });
      return;
    }
    sMsg.textContent = hits === 1 ? '1 service matches. Scroll down to see it.' : hits + ' services match. Scroll down to see them.';
    $('#services').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  });

  /* ---------- carousel ---------- */
  var track = $('#carTrack');
  var dotsEl = $('#dots');
  var slides = $$('.slide', track);
  var current = 0;
  var pausedUntil = 0;
  var hovering = false;
  function hold(ms) { pausedUntil = Date.now() + ms; }

  slides.forEach(function () { dotsEl.appendChild(document.createElement('span')); });
  var dots = $$('span', dotsEl);

  function slideStep() {
    var s = slides[0];
    return s.getBoundingClientRect().width + (parseFloat(getComputedStyle(track).columnGap) || 0);
  }
  function mark() {
    current = Math.max(0, Math.min(slides.length - 1, Math.round(track.scrollLeft / slideStep())));
    dots.forEach(function (d, i) { d.classList.toggle('on', i === current); });
  }
  function go(i) {
    var n = (i + slides.length) % slides.length;
    var wraps = (i < 0 || i >= slides.length);
    track.scrollTo({ left: n * slideStep(), behavior: (reduce || wraps) ? 'auto' : 'smooth' });
  }
  track.addEventListener('scroll', mark, { passive: true });
  $('.car-btn.prev').addEventListener('click', function () { hold(10000); go(current - 1); });
  $('.car-btn.next').addEventListener('click', function () { hold(10000); go(current + 1); });
  ['pointerdown', 'touchstart', 'focusin', 'wheel'].forEach(function (ev) {
    track.addEventListener(ev, function () { hold(10000); }, { passive: true });
  });
  var car = $('#carousel');
  car.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hovering = true; });
  car.addEventListener('pointerleave', function () { hovering = false; hold(2500); });
  mark();

  /* auto-advance runs even with reduced motion (the swap is instant then) */
  if ('IntersectionObserver' in window) {
    var visible = false;
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }, { threshold: 0.5 }).observe(track);
    setInterval(function () {
      if (visible && !hovering && Date.now() > pausedUntil && !document.hidden) go(current + 1);
    }, 4500);
  }

  /* ---------- trust photo cards: photos swap on their own ---------- */
  /* each card changes photo every 1-1.8s (own random timing), only while on screen, tab visible and not hovered.
     Every swap plays a random transition (never the same twice in a row). The new photo is revealed on top of the
     old one with the Web Animations API. With reduced motion only the "calm" reveals (clip-path, nothing slides or
     scales) are used. */
  var pick = function (list) { return list[Math.floor(Math.random() * list.length)]; };
  var FX = [
    { calm: true, make: function () {   /* wipe in from a random side */
      return { inc: [{ clipPath: pick(['inset(0 100% 0 0)', 'inset(0 0 0 100%)', 'inset(100% 0 0 0)', 'inset(0 0 100% 0)']) }, { clipPath: 'inset(0 0 0 0)' }] };
    } },
    { calm: true, make: function () {   /* circle grows from the centre or a corner */
      var o = pick(['50% 50%', '0% 0%', '100% 0%', '0% 100%', '100% 100%']);
      return { inc: [{ clipPath: 'circle(0% at ' + o + ')' }, { clipPath: 'circle(150% at ' + o + ')' }] };
    } },
    { calm: true, make: function () {   /* slanted slice sweeps across */
      var flip = Math.random() < 0.5;
      return { inc: flip
        ? [{ clipPath: 'polygon(100% 0, 100% 0, 140% 100%, 100% 100%)' }, { clipPath: 'polygon(100% 0, -40% 0, 0% 100%, 100% 100%)' }]
        : [{ clipPath: 'polygon(0 0, 0 0, -40% 100%, 0 100%)' }, { clipPath: 'polygon(0 0, 140% 0, 100% 100%, 0 100%)' }] };
    } },
    { calm: true, make: function () {   /* curtains open from the middle */
      return { inc: [{ clipPath: pick(['inset(0 50% 0 50%)', 'inset(50% 0 50% 0)']) }, { clipPath: 'inset(0 0 0 0)' }] };
    } },
    { calm: true, make: function () {   /* rounded box grows from the centre */
      return { inc: [{ clipPath: 'inset(50% round 44px)' }, { clipPath: 'inset(0% round 0px)' }] };
    } },
    { calm: false, make: function () {  /* settles in from a soft, zoomed blur */
      return { inc: [{ opacity: 0, transform: 'scale(1.22)', filter: 'blur(10px)' }, { opacity: 1, transform: 'scale(1)', filter: 'blur(0px)' }] };
    } },
    { calm: false, make: function () {  /* new photo pushes the old one aside */
      var d = Math.random() < 0.5 ? 1 : -1;
      return { inc: [{ transform: 'translateX(' + (100 * d) + '%)' }, { transform: 'translateX(0%)' }],
               out: [{ transform: 'translateX(0%)' }, { transform: 'translateX(' + (-28 * d) + '%)' }] };
    } },
    { calm: false, make: function () {  /* rises from below while the old one sinks back */
      return { inc: [{ transform: 'translateY(100%)' }, { transform: 'translateY(0%)' }],
               out: [{ transform: 'scale(1)', filter: 'brightness(1)' }, { transform: 'scale(.9)', filter: 'brightness(.6)' }] };
    } }
  ];
  var usable = FX.filter(function (f) { return f.calm || !reduce; });

  $$('[data-rotate]').forEach(function (card, n) {
    var pics = $$('img', card);
    if (pics.length < 2) return;
    var at = 0, onScreen = false, over = false, busy = false, last = -1;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { onScreen = en[0].isIntersecting; }, { threshold: 0.25 }).observe(card);
    } else { onScreen = true; }
    card.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') over = true; });
    card.addEventListener('pointerleave', function () { over = false; });

    var swap = function () {
      var from = pics[at], to = pics[(at + 1) % pics.length];
      var i; do { i = Math.floor(Math.random() * usable.length); } while (usable.length > 1 && i === last);
      last = i;
      var fx = usable[i], spec = fx.make();
      var finish = function () {
        from.classList.remove('on'); to.classList.remove('in'); to.classList.add('on'); busy = false;
      };
      at = (at + 1) % pics.length;
      if (!to.animate) { to.classList.add('on'); from.classList.remove('on'); return; }
      busy = true;
      to.classList.add('in');
      var opts = { duration: 680 + Math.random() * 180, easing: 'cubic-bezier(.77,0,.18,1)' };
      if (!spec.out && fx.calm && !reduce) spec.out = [{ transform: 'scale(1)' }, { transform: 'scale(1.07)' }];
      if (spec.out) from.animate(spec.out, opts);
      to.animate(spec.inc, opts).onfinish = finish;
    };

    var next = function () {
      if (onScreen && !over && !busy && !document.hidden) swap();
      setTimeout(next, 1000 + Math.random() * 800);
    };
    setTimeout(next, 900 + n * 450);
  });

  /* ---------- reviews: each card swaps to its next review every 5-7.5s ---------- */
  /* Every review of a card sits in one grid cell (see .rv), so the height never changes. A random effect plays per swap,
     like the photo cards. With reduced motion only the calm ones (fades and clip reveals) are used. */
  var voiceCards = $$('[data-reviews]');
  if (voiceCards.length && Element.prototype.animate) {
    var VE = 'cubic-bezier(.22,.8,.2,1)';
    var parts = function (rv) { return [$('blockquote', rv), $('figcaption', rv)]; };
    var wordsOf = function (p) {
      if (p._w) return p._w;
      var bits = p.textContent.split(' ');
      p.textContent = '';
      p._w = bits.map(function (w, i) {
        var sp = document.createElement('span');
        sp.className = 'w';
        sp.textContent = w;
        p.appendChild(sp);
        if (i < bits.length - 1) p.appendChild(document.createTextNode(' '));
        return sp;
      });
      return p._w;
    };
    var animate = function (list, el, kf, o) { list.push(el.animate(kf, o)); };
    var blur = function (px) { return 'blur(' + px + 'px)'; };
    var VFX = [
      { calm: false, run: function (a, b, A) {                 /* rise: old lifts away, new floats up */
        parts(a).forEach(function (el, i) { animate(A, el, [{ opacity: 1, transform: 'none', filter: 'none' }, { opacity: 0, transform: 'translateY(-18px)', filter: blur(6) }], { duration: 300, delay: i * 40, easing: 'ease-in', fill: 'both' }); });
        parts(b).forEach(function (el, i) { animate(A, el, [{ opacity: 0, transform: 'translateY(28px)', filter: blur(8) }, { opacity: 1, transform: 'none', filter: 'none' }], { duration: 720, delay: 130 + i * 90, easing: VE, fill: 'both' }); });
      } },
      { calm: false, run: function (a, b, A) {                 /* slide: old exits left, new enters from the right */
        parts(a).forEach(function (el, i) { animate(A, el, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateX(-46px)' }], { duration: 320, delay: i * 50, easing: 'ease-in', fill: 'both' }); });
        parts(b).forEach(function (el, i) { animate(A, el, [{ opacity: 0, transform: 'translateX(54px)' }, { opacity: 1, transform: 'none' }], { duration: 700, delay: 140 + i * 90, easing: VE, fill: 'both' }); });
      } },
      { calm: false, run: function (a, b, A) {                 /* words: the new quote lands word by word */
        parts(a).forEach(function (el) { animate(A, el, [{ opacity: 1, filter: 'none' }, { opacity: 0, filter: blur(5) }], { duration: 260, easing: 'ease-in', fill: 'both' }); });
        var ws = wordsOf($('p', b));
        var step = Math.min(30, 900 / ws.length);
        ws.forEach(function (w, i) { animate(A, w, [{ opacity: 0, transform: 'translateY(.65em) rotate(4deg)' }, { opacity: 1, transform: 'none' }], { duration: 520, delay: 130 + i * step, easing: VE, fill: 'both' }); });
        animate(A, parts(b)[1], [{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }], { duration: 600, delay: 130 + ws.length * step * 0.6, easing: VE, fill: 'both' });
      } },
      { calm: false, run: function (a, b, A) {                 /* flip: the card turns over on its top edge */
        animate(A, a, [{ opacity: 1, transform: 'perspective(900px) rotateX(0)' }, { opacity: 0, transform: 'perspective(900px) rotateX(-75deg) translateY(-10px)' }], { duration: 340, easing: 'ease-in', fill: 'both' });
        animate(A, b, [{ opacity: 0, transform: 'perspective(900px) rotateX(75deg) translateY(10px)' }, { opacity: 1, transform: 'perspective(900px) rotateX(0)' }], { duration: 640, delay: 200, easing: VE, fill: 'both' });
      } },
      { calm: false, run: function (a, b, A) {                 /* zoom: old recedes, new settles from slightly large */
        animate(A, a, [{ opacity: 1, transform: 'none', filter: 'none' }, { opacity: 0, transform: 'scale(.93)', filter: blur(5) }], { duration: 300, easing: 'ease-in', fill: 'both' });
        animate(A, b, [{ opacity: 0, transform: 'scale(1.07)', filter: blur(7) }, { opacity: 1, transform: 'none', filter: 'none' }], { duration: 760, delay: 130, easing: VE, fill: 'both' });
      } },
      { calm: true, run: function (a, b, A) {                  /* wipe: new text is revealed left to right */
        animate(A, a, [{ opacity: 1 }, { opacity: 0 }], { duration: 280, easing: 'ease-in', fill: 'both' });
        animate(A, b, [{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }, { clipPath: 'inset(0 0 0 0)', opacity: 1 }], { duration: 900, delay: 60, easing: 'cubic-bezier(.77,0,.18,1)', fill: 'both' });
      } },
      { calm: true, run: function (a, b, A) {                  /* curtains: new text opens from the middle */
        animate(A, a, [{ opacity: 1 }, { opacity: 0 }], { duration: 280, easing: 'ease-in', fill: 'both' });
        animate(A, b, [{ clipPath: 'inset(0 50% 0 50%)', opacity: 0 }, { clipPath: 'inset(0 0 0 0)', opacity: 1 }], { duration: 880, delay: 60, easing: 'cubic-bezier(.77,0,.18,1)', fill: 'both' });
      } },
      { calm: true, run: function (a, b, A) {                  /* fade */
        animate(A, a, [{ opacity: 1 }, { opacity: 0 }], { duration: 320, easing: 'ease-in', fill: 'both' });
        animate(A, b, [{ opacity: 0 }, { opacity: 1 }], { duration: 700, delay: 60, easing: 'ease-out', fill: 'both' });
      } }
    ];
    var vUsable = VFX.filter(function (f) { return f.calm || !reduce; });

    voiceCards.forEach(function (card, n) {
      var revs = $$('.rv', card);
      if (revs.length < 2) return;
      var at = 0, busy = false, over = false, onScreen = true, lastFx = -1;
      card.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') over = true; });
      card.addEventListener('pointerleave', function () { over = false; });
      card.addEventListener('focusin', function () { over = true; });
      card.addEventListener('focusout', function () { over = false; });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (en) { onScreen = en[0].isIntersecting; }, { threshold: 0.3 }).observe(card);
      }
      var swap = function () {
        var from = revs[at], to = revs[(at + 1) % revs.length];
        var k;
        do { k = Math.floor(Math.random() * vUsable.length); } while (vUsable.length > 1 && k === lastFx);
        lastFx = k;
        busy = true;
        to.classList.add('in');
        var A = [];
        vUsable[k].run(from, to, A);
        /* the card takes the colour of the incoming review: a Web Animation, so it also runs with reduced motion */
        var tint = to.getAttribute('data-tint');
        if (tint && tint !== card.getAttribute('data-tint')) {
          var was = getComputedStyle(card).backgroundColor;
          card.setAttribute('data-tint', tint);
          animate(A, card, [{ backgroundColor: was }, { backgroundColor: getComputedStyle(card).backgroundColor }], { duration: 1100, delay: 100, easing: 'ease-in-out', fill: 'backwards' });
        }
        /* every incoming card also pops its avatar and ticks its stars on, one by one */
        var av = $('figcaption > img, figcaption > .av', to);
        var stars = $$('.stars-row .i', to);
        if (av) animate(A, av, reduce ? [{ opacity: 0 }, { opacity: 1 }] : [{ opacity: 0, transform: 'scale(.4) rotate(-30deg)' }, { opacity: 1, transform: 'none' }], { duration: 640, delay: 560, easing: 'cubic-bezier(.34,1.56,.64,1)', fill: 'both' });
        stars.forEach(function (st, i) { animate(A, st, reduce ? [{ opacity: 0 }, { opacity: 1 }] : [{ opacity: 0, transform: 'scale(0) rotate(-40deg)' }, { opacity: 1, transform: 'none' }], { duration: 480, delay: 760 + i * 90, easing: 'cubic-bezier(.34,1.56,.64,1)', fill: 'both' }); });
        Promise.all(A.map(function (a) { return a.finished; })).then(function () {
          from.classList.remove('on');
          to.classList.remove('in');
          to.classList.add('on');
          at = (at + 1) % revs.length;
          /* release the animations a moment later, once the class change has been painted: cancelling in the same frame let the
             old review flash back at full opacity for a frame (a blink) */
          setTimeout(function () { A.forEach(function (a) { a.cancel(); }); busy = false; }, 120);
        }, function () { A.forEach(function (a) { a.cancel(); }); busy = false; });
      };
      var tick = function () {
        if (onScreen && !over && !busy && !document.hidden) { swap(); setTimeout(tick, 5000 + Math.random() * 2500); }
        else setTimeout(tick, 700);
      };
      setTimeout(tick, 2600 + n * 1900);
    });
  }

  /* ---------- marquee light sweep ---------- */
  /* a wide, soft glint drifts across the strip against the scroll direction. A new one starts every 1.5-4s at random,
     so two can overlap. Runs with reduced motion too: it is a faint fade, no content moves. */
  var strip = $('.marquee');
  if (strip && strip.animate) {
    var stripVisible = false;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { stripVisible = en[0].isIntersecting; }, { threshold: 0.1 }).observe(strip);
    }
    var sweep = function () {
      if (stripVisible && !document.hidden) {
        var glint = document.createElement('span');
        glint.className = 'sheen';
        strip.appendChild(glint);
        var peak = 0.6 + Math.random() * 0.4;
        var skew = ' skewX(-18deg)';
        var run = glint.animate([
          { transform: 'translateX(-460px)' + skew, opacity: 0 },
          { opacity: peak, offset: 0.25 },
          { opacity: peak, offset: 0.75 },
          { transform: 'translateX(' + strip.offsetWidth + 'px)' + skew, opacity: 0 }
        ], { duration: 4200 + Math.random() * 2300, easing: 'cubic-bezier(.35,0,.35,1)' });
        run.onfinish = function () { glint.remove(); };
      }
      setTimeout(sweep, 1500 + Math.random() * 2500);
    };
    setTimeout(sweep, 1000);
  }

  /* ---------- motion ---------- */
  if (reduce || !window.gsap) return;
  var gsap = window.gsap;
  if (window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);

  // hero: one orchestrated entrance
  var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  var hl = $('.house-line path');
  if (hl && hl.getTotalLength) {
    var len = hl.getTotalLength();
    gsap.set(hl, { strokeDasharray: len, strokeDashoffset: len });
    tl.to(hl, { strokeDashoffset: 0, duration: 2.2, ease: 'power2.inOut' }, 0);
  }
  tl.from('.hero h1 .ln > span', { yPercent: 115, duration: 0.95, stagger: 0.12 }, 0.05)
    .from('.hero .lead, .hero .search, .hero .rated', { y: 18, opacity: 0, duration: 0.7, stagger: 0.1 }, 0.55)
    .from('.arch', { y: 110, opacity: 0, duration: 1, stagger: 0.14 }, 0.15)
    .from('.arch img', { scale: 1.25, duration: 1.4, stagger: 0.14 }, 0.15)
    .from('.hero .spark', { scale: 0, rotate: -90, duration: 0.8, stagger: 0.12, ease: 'back.out(2)' }, 0.9)
    .from('.chip', { scale: 0.6, opacity: 0, duration: 0.7, stagger: 0.15, ease: 'back.out(1.8)' }, 1.0)
    .from('.eta-bar i', { width: '0%', duration: 1.6, ease: 'power2.inOut' }, 1.3);

  // gentle idle float on the chips
  $$('[data-float]').forEach(function (el, i) {
    gsap.to(el, { y: i % 2 ? -8 : 8, duration: 2.4 + i * 0.5, ease: 'sine.inOut', yoyo: true, repeat: -1, delay: 1.8 });
  });
  gsap.to('.hero .spark', { rotate: 45, duration: 4, ease: 'sine.inOut', yoyo: true, repeat: -1, stagger: 0.4, delay: 2 });

  if (!window.ScrollTrigger) return;
  var ST = window.ScrollTrigger;

  // hero blobs drift as you scroll
  gsap.to('.hero .b1', { yPercent: 40, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });
  gsap.to('.hero .b2', { yPercent: -50, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true } });

  // stat counters
  $$('[data-count]').forEach(function (el) {
    var end = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-decimals') || '0', 10);
    var suf = el.getAttribute('data-suffix') || '';
    var o = { v: 0 };
    el.textContent = (0).toFixed(dec) + suf;
    ST.create({
      trigger: el, start: 'top 90%', once: true,
      onEnter: function () {
        gsap.to(o, {
          v: end, duration: 1.8, ease: 'power2.out',
          onUpdate: function () { el.textContent = o.v.toFixed(dec) + suf; },
          onComplete: function () { el.textContent = end.toFixed(dec) + suf; }
        });
      }
    });
  });

  // stat bento pops in once
  gsap.from('.bento .tile', {
    scale: 0.92, opacity: 0, duration: 0.8, stagger: 0.09, ease: 'back.out(1.4)',
    scrollTrigger: { trigger: '.bento', start: 'top 85%', once: true }
  });

  // steps: dotted path sweeps across, icons pop
  var line = $('.steps-line');
  if (line && getComputedStyle(line).display !== 'none') {
    gsap.from(line, { clipPath: 'inset(0 100% 0 0)', duration: 1.4, ease: 'power2.inOut', scrollTrigger: { trigger: '.steps', start: 'top 80%', once: true } });
  }
  gsap.from('.step-ico', {
    scale: 0, rotate: -40, duration: 0.7, stagger: 0.18, ease: 'back.out(2)',
    scrollTrigger: { trigger: '.steps', start: 'top 80%', once: true }
  });

  // CTA photo moves slower than the page
  gsap.fromTo('.cta-img', { yPercent: -8, scale: 1.12 }, {
    yPercent: 8, ease: 'none',
    scrollTrigger: { trigger: '.cta', start: 'top bottom', end: 'bottom top', scrub: true }
  });

  window.addEventListener('load', function () { ST.refresh(); });
})();
