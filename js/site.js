/* MUFIME — shared site behaviour
   nav · reveals · showreel · forms · analytics events            */

(function () {
  'use strict';

  /* ---------------------------------------------------------
     Analytics — works with Plausible or GA4, silent if neither
     --------------------------------------------------------- */
  function track(event, props) {
    try {
      if (typeof window.plausible === 'function') {
        window.plausible(event, props ? { props: props } : undefined);
      }
      if (typeof window.gtag === 'function') {
        window.gtag('event', event.replace(/\s+/g, '_').toLowerCase(), props || {});
      }
    } catch (e) { /* never let analytics break the page */ }
  }
  window.mufimeTrack = track;

  /* ---------------------------------------------------------
     Navigation — the logo is the trigger
     --------------------------------------------------------- */
  var logoBtn = document.getElementById('logoBtn');
  var panel   = document.getElementById('navPanel');
  var scrim   = document.getElementById('navScrim');

  function setNav(open) {
    if (!panel || !scrim || !logoBtn) return;
    panel.classList.toggle('open', open);
    scrim.classList.toggle('open', open);
    logoBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    logoBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('nav-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) {
      var first = panel.querySelector('.nav-links a');
      if (first) first.focus({ preventScroll: true });
    }
  }

  if (logoBtn) {
    logoBtn.addEventListener('click', function (e) {
      e.preventDefault();
      setNav(logoBtn.getAttribute('aria-expanded') !== 'true');
    });
  }
  if (scrim) scrim.addEventListener('click', function () { setNav(false); });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    setNav(false);
    closeLightbox();
  });

  // Selecting a section: close the menu, then scroll.
  if (panel) {
    panel.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var href = a.getAttribute('href') || '';
        var hash = href.indexOf('#') === 0 ? href : null;
        setNav(false);
        if (hash) {
          e.preventDefault();
          var target = document.querySelector(hash);
          if (target) {
            setTimeout(function () {
              target.scrollIntoView({ behavior: 'smooth', block: 'start' });
              history.replaceState(null, '', hash);
            }, 260);
          }
        }
      });
    });
  }

  /* ---------------------------------------------------------
     Reveals — clip-path wipe
     --------------------------------------------------------- */
  var revealEls = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -50px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------------------------------------------------------
     Showreel + any click-to-play frame
     --------------------------------------------------------- */
  function ready(v) { return v && v.indexOf('REPLACE_WITH') !== 0; }

  // A frame carries either data-video-id (YouTube) or data-drive-id (Google
  // Drive). Drive files must be shared as "Anyone with the link - Viewer".
  function embedUrl(frame) {
    var drive = frame.getAttribute('data-drive-id');
    if (ready(drive)) return 'https://drive.google.com/file/d/' + drive + '/preview';
    var yt = frame.getAttribute('data-video-id');
    if (ready(yt)) {
      return 'https://www.youtube.com/embed/' + yt +
             '?autoplay=1&rel=0&modestbranding=1&playsinline=1';
    }
    return null;
  }

  // Drive ships no thumbnail with the embed, so pull its preview image in.
  // If that image fails to load we drop it and the designed placeholder stays.
  document.querySelectorAll('[data-drive-id]').forEach(function (frame) {
    var id = frame.getAttribute('data-drive-id');
    if (!ready(id) || frame.querySelector('img')) return;
    var img = document.createElement('img');
    img.alt = frame.getAttribute('data-title') || '';
    img.loading = 'lazy';
    img.onerror = function () { img.remove(); };
    img.src = 'https://drive.google.com/thumbnail?id=' + id + '&sz=w1280';
    frame.insertBefore(img, frame.firstChild);
  });

  document.querySelectorAll('[data-play]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var frame = btn.closest('[data-video-id], [data-drive-id]');
      if (!frame) return;
      var src = embedUrl(frame);
      if (!src) {
        // Placeholder slot — nothing to play yet, stay put rather than erroring.
        frame.classList.add('awaiting');
        return;
      }
      var label = (frame.getAttribute('data-title') || 'Showreel').replace(/"/g, '');
      frame.innerHTML =
        '<iframe src="' + src + '" title="' + label +
        '" frameborder="0" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
      frame.classList.add('playing');
      track('Showreel Played', { video: label });
    });
  });

  /* ---------------------------------------------------------
     Portfolio lightbox — a filled .slot opens the video at size
     rather than sending the visitor off to Drive or YouTube.
     Without JS the card stays an ordinary link, so it still works.
     --------------------------------------------------------- */
  var lb, lbBody, lbReturn;

  function closeLightbox() {
    if (!lb || !lb.classList.contains('open')) return;
    lb.classList.remove('open');
    lbBody.innerHTML = '';
    document.body.style.overflow = '';
    if (lbReturn) lbReturn.focus({ preventScroll: true });
  }

  function buildLightbox() {
    lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Project video');
    lb.innerHTML =
      '<button class="lb-close" type="button" aria-label="Close video">' +
      '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button>' +
      '<div class="lb-body"></div>';
    document.body.appendChild(lb);
    lbBody = lb.querySelector('.lb-body');
    lb.addEventListener('click', function (e) {
      if (e.target === lb) closeLightbox();
    });
    lb.querySelector('.lb-close').addEventListener('click', closeLightbox);
  }

  document.querySelectorAll('a.slot[data-drive-id], a.slot[data-video-id]').forEach(function (card) {
    var src = embedUrl(card);
    if (!src) return;                       // placeholder card, leave it alone
    card.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
      e.preventDefault();
      if (!lb) buildLightbox();
      lbReturn = card;
      var label = (card.getAttribute('data-title') || 'Project').replace(/"/g, '');
      lbBody.innerHTML =
        '<iframe src="' + src + '" title="' + label +
        '" frameborder="0" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
      lb.querySelector('.lb-close').focus({ preventScroll: true });
    });
  });

  /* ---------------------------------------------------------
     Scroll cue
     --------------------------------------------------------- */
  var cue = document.getElementById('scrollCue');
  if (cue) {
    cue.addEventListener('click', function () {
      var t = document.getElementById('showreel');
      if (t) t.scrollIntoView({ behavior: 'smooth' });
    });
  }

  /* ---------------------------------------------------------
     Floating dock — appears once the hero is behind you
     --------------------------------------------------------- */
  var dock = document.getElementById('dock');
  if (dock) {
    var onScroll = function () {
      dock.classList.toggle('show', window.scrollY > window.innerHeight * 0.75);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------------------------------------------------------
     Forms — Web3Forms. Replace ACCESS_KEY in each form's
     hidden access_key input. Submissions route to the address
     configured on the Web3Forms account (mufime.business@gmail.com).
     --------------------------------------------------------- */
  document.querySelectorAll('form[data-form]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    var submit = form.querySelector('button[type="submit"]');
    var name = form.getAttribute('data-form');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!status || !submit) return;

      var key = form.querySelector('input[name="access_key"]');
      if (key && key.value.indexOf('YOUR_WEB3FORMS') === 0) {
        status.className = 'form-status err';
        status.textContent = 'This form is not connected yet. Add your Web3Forms access key, or email mufime.business@gmail.com directly.';
        return;
      }

      var original = submit.textContent;
      submit.disabled = true;
      submit.textContent = 'Sending…';
      status.className = 'form-status';
      status.textContent = '';

      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form)))
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.success) {
            status.className = 'form-status ok';
            status.textContent = 'Got it. We\'ll come back to you at the email you gave us, usually within one working day.';
            form.reset();
            track(name === 'sample' ? 'Free Sample Requested' : 'Quote Form Submitted');
          } else {
            throw new Error(data.message || 'Submission failed');
          }
        })
        .catch(function () {
          status.className = 'form-status err';
          status.textContent = 'That didn\'t send. Please email mufime.business@gmail.com and we\'ll pick it up from there.';
        })
        .finally(function () {
          submit.disabled = false;
          submit.textContent = original;
        });
    });
  });

  /* ---------------------------------------------------------
     Tracked interactions
     --------------------------------------------------------- */
  document.querySelectorAll('[data-track]').forEach(function (el) {
    el.addEventListener('click', function () {
      track(el.getAttribute('data-track'));
    });
  });

  // Pricing viewed — fires once when the pricing block scrolls in
  var pricing = document.getElementById('pricing');
  if (pricing && 'IntersectionObserver' in window) {
    var pio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { track('Pricing Viewed'); pio.disconnect(); }
      });
    }, { threshold: 0.25 });
    pio.observe(pricing);
  }

  /* ---------------------------------------------------------
     Year stamp
     --------------------------------------------------------- */
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();
