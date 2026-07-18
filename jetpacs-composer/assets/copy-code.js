// Adds a visible "Copy" button to every code block in page content.
// Loaded via layouts/_partials/docs/inject/body.html (hugo-book's override
// hook), so the vendored theme is untouched. Coexists with the theme's own
// copy-on-Ctrl+C clipboard.js.
(function () {
  "use strict";

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // Fallback for http:// / older browsers.
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy") ? resolve() : reject();
      } catch (e) {
        reject(e);
      } finally {
        document.body.removeChild(ta);
      }
    });
  }

  function addButton(pre) {
    // A relative wrapper keeps the button pinned while the <pre> scrolls.
    var wrap = document.createElement("div");
    wrap.className = "code-wrap";
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-code";
    btn.setAttribute("aria-label", "Copy code to clipboard");
    btn.textContent = "Copy";

    btn.addEventListener("click", function () {
      var code = pre.querySelector("code") || pre;
      var text = code.textContent.replace(/\n$/, "");
      copyText(text).then(
        function () { flash("Copied", true); },
        function () { flash("Error", false); }
      );
    });

    function flash(label, ok) {
      btn.textContent = label;
      btn.classList.add(ok ? "copied" : "failed");
      setTimeout(function () {
        btn.textContent = "Copy";
        btn.classList.remove("copied", "failed");
      }, 1600);
    }

    wrap.appendChild(btn);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var blocks = document.querySelectorAll(".book-page .markdown pre");
    Array.prototype.forEach.call(blocks, function (pre) {
      if (pre.querySelector("code") || pre.classList.contains("example")) {
        addButton(pre);
      }
    });
  });
})();
