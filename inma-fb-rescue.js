/*!
 * INMA in-app browser rescue
 * - Detects Facebook, Instagram, TikTok, LinkedIn, X, WeChat, Snapchat, LINE, KakaoTalk
 * - Injects warning banner at top of page
 * - Provides escape helpers (Android intent://, iOS copy-link modal)
 * - Provides print/share/contact fallbacks that work in any browser
 *
 * Public API on window.INMA:
 *   .isInApp, .isIOS, .isAndroid       (booleans)
 *   .escape()                          (try to bounce to real browser)
 *   .print({selector, filename})       (window.print in real browsers; client-side PDF in webviews)
 *   .share({title, text, url})         (Web Share API or copy-link)
 */
(function () {
  'use strict';

  var ua = navigator.userAgent || '';
  var INAPP_RE = /FBAN|FBAV|FB_IAB|Instagram|LinkedInApp|Twitter|musical_ly|BytedanceWebview|TikTok|MicroMessenger|Snapchat|Line\/|KAKAOTALK/i;
  var isInApp = INAPP_RE.test(ua);
  var isIOS = /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
  var isAndroid = /Android/.test(ua);

  var INMA = window.INMA = window.INMA || {};
  INMA.isInApp = isInApp;
  INMA.isIOS = isIOS;
  INMA.isAndroid = isAndroid;

  // ============ BANNER ============
  function injectBanner() {
    if (!isInApp) return;
    if (document.getElementById('inmaInAppBanner')) return;

    var bar = document.createElement('div');
    bar.id = 'inmaInAppBanner';
    bar.setAttribute('role', 'alert');
    bar.style.cssText = [
      'position:sticky','top:0','z-index:99999',
      'background:#FCD34D','color:#1C1A17',
      'padding:14px 16px',
      "font-family:Inter,Outfit,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",
      'font-size:14px','line-height:1.4',
      'box-shadow:0 2px 10px rgba(0,0,0,.18)'
    ].join(';');

    bar.innerHTML =
      '<div style="display:flex;align-items:flex-start;gap:10px;max-width:780px;margin:0 auto">' +
        '<div style="flex:1;min-width:0">' +
          '<strong style="display:block;font-weight:700;margin-bottom:2px">Open in your browser for full features</strong>' +
          'PDF, share, and contacts don’t work in this in-app browser.' +
        '</div>' +
        '<button type="button" id="inmaOpenSafariBtn" style="background:#1C1A17;color:#FCD34D;border:0;border-radius:8px;padding:10px 14px;font-weight:700;font-family:inherit;font-size:13px;cursor:pointer;white-space:nowrap;flex-shrink:0">Open ↗</button>' +
        '<button type="button" aria-label="Dismiss" id="inmaDismissBtn" style="background:transparent;border:0;color:#1C1A17;font-size:24px;line-height:1;cursor:pointer;padding:0 4px;opacity:.5">×</button>' +
      '</div>';

    document.body.insertBefore(bar, document.body.firstChild);

    document.getElementById('inmaOpenSafariBtn').addEventListener('click', INMA.escape);
    document.getElementById('inmaDismissBtn').addEventListener('click', function () { bar.remove(); });
  }

  // ============ ESCAPE TO REAL BROWSER ============
  INMA.escape = function () {
    var url = window.location.href;

    if (isAndroid) {
      // intent:// trick forces Chrome (or default browser) to open the URL
      var noProto = url.replace(/^https?:\/\//, '');
      window.location.href = 'intent://' + noProto + '#Intent;scheme=https;package=com.android.chrome;end';
      // Fallback after a tick — if intent failed, show modal
      setTimeout(function () { showCopyModal(url); }, 800);
      return;
    }
    // iOS + everything else: copy-link modal
    showCopyModal(url);
  };

  function showCopyModal(url) {
    if (document.getElementById('inmaEscapeModal')) return;

    var m = document.createElement('div');
    m.id = 'inmaEscapeModal';
    m.style.cssText = [
      'position:fixed','inset:0','z-index:999999',
      'background:rgba(0,0,0,.7)',
      'display:flex','align-items:center','justify-content:center',
      'padding:24px',
      "font-family:Inter,Outfit,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
    ].join(';');

    var iosTip = isIOS
      ? '<p style="margin:14px 0 0;font-size:12px;color:#666;line-height:1.5"><strong>Or:</strong> Tap <strong>⋯</strong> at the bottom of this screen → <strong>“Open in Safari”</strong>.</p>'
      : '<p style="margin:14px 0 0;font-size:12px;color:#666;line-height:1.5"><strong>Or:</strong> Tap the menu (⋮ or ⋯) → <strong>“Open in Browser”</strong>.</p>';

    m.innerHTML =
      '<div style="background:#fff;color:#1C1A17;border-radius:16px;padding:24px;max-width:380px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.4)">' +
        '<h3 style="margin:0 0 10px;font-size:18px;font-weight:700">Open in Safari</h3>' +
        '<p style="margin:0 0 14px;font-size:14px;line-height:1.5;color:#444">Your in-app browser doesn’t allow full features. Copy the link and paste into Safari.</p>' +
        '<div style="background:#F4F4F5;border-radius:8px;padding:10px 12px;margin-bottom:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;color:#1C1A17;word-break:break-all">' + escapeHtml(url) + '</div>' +
        '<button type="button" id="inmaCopyBtn" style="background:#1C1A17;color:#fff;border:0;border-radius:10px;padding:13px;width:100%;font-weight:700;font-size:15px;font-family:inherit;cursor:pointer">Copy Link</button>' +
        iosTip +
        '<button type="button" id="inmaCloseModal" style="background:transparent;border:0;color:#666;padding:10px;width:100%;font-size:13px;cursor:pointer;font-family:inherit;margin-top:6px">Close</button>' +
      '</div>';

    document.body.appendChild(m);

    document.getElementById('inmaCopyBtn').addEventListener('click', function () {
      copyToClipboard(url);
      this.textContent = '✓ Copied — now open Safari';
      this.style.background = '#16A34A';
    });
    document.getElementById('inmaCloseModal').addEventListener('click', function () { m.remove(); });
    m.addEventListener('click', function (e) { if (e.target === m) m.remove(); });
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(function () { fallbackCopy(text); });
    } else {
      fallbackCopy(text);
    }
  }
  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try { document.execCommand('copy'); } catch (e) { /* ignore */ }
    ta.remove();
  }
  function escapeHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ============ PRINT / PDF ============
  INMA.print = function (opts) {
    opts = opts || {};
    if (!isInApp) {
      // Real browser — system print dialog gives the user PDF/AirPrint
      window.print();
      return;
    }
    // In-app browser: generate PDF client-side
    loadHtml2Pdf(function (ok) {
      if (!ok) {
        alert('PDF generator failed to load. Tap "Open ↗" at the top to switch to Safari, then try again.');
        return;
      }
      var element = document.body;
      if (opts.selector) {
        var el = document.querySelector(opts.selector);
        if (el) element = el;
      }
      var pdfOpts = {
        margin: 10,
        filename: opts.filename || ('inma-' + Date.now() + '.pdf'),
        image: { type: 'jpeg', quality: 0.95 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
        jsPDF: { unit: 'mm', format: 'letter', orientation: 'portrait' }
      };
      window.html2pdf().set(pdfOpts).from(element).save();
    });
  };

  var pdfLoading = false;
  var pdfCallbacks = [];
  function loadHtml2Pdf(cb) {
    if (window.html2pdf) { cb(true); return; }
    pdfCallbacks.push(cb);
    if (pdfLoading) return;
    pdfLoading = true;
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/html2pdf.js@0.10.1/dist/html2pdf.bundle.min.js';
    s.onload = function () { pdfCallbacks.forEach(function (c) { c(true); }); pdfCallbacks = []; };
    s.onerror = function () { pdfCallbacks.forEach(function (c) { c(false); }); pdfCallbacks = []; pdfLoading = false; };
    document.head.appendChild(s);
  }

  // ============ SHARE ============
  INMA.share = function (data) {
    data = data || {};
    if (!data.url) data.url = window.location.href;
    if (navigator.share) {
      navigator.share(data).catch(function () { /* user cancelled */ });
      return;
    }
    copyToClipboard(data.url);
    alert('Link copied to clipboard.');
  };

  // ============ AUTO INIT ============
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectBanner);
  } else {
    injectBanner();
  }
})();
