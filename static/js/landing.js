/**
 * CTAs conversacionales de la landing pública Maintix (MKT-05).
 */
function sendPrompt(message, options) {
  var opts = options || {};
  var text = (message || "").trim();
  var contactEmail = "contacto@maintix.com";

  try {
    sessionStorage.setItem("maintix_sales_prompt", text);
  } catch (e) {
    /* ignore */
  }

  window.dispatchEvent(
    new CustomEvent("maintix:sales-prompt", {
      detail: { message: text, source: opts.source || "landing" },
    })
  );

  if (opts.action === "contact") {
    var subject = encodeURIComponent("Demostración Maintix");
    var body = encodeURIComponent(text || "Hola, me gustaría solicitar una demostración de Maintix.");
    window.location.href = "mailto:" + contactEmail + "?subject=" + subject + "&body=" + body;
    return;
  }

  var url = opts.url || "/onboarding";
  if (text) {
    url += (url.indexOf("?") >= 0 ? "&" : "?") + "prompt=" + encodeURIComponent(text);
  }
  window.location.href = url;
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-send-prompt]").forEach(function (el) {
    el.addEventListener("click", function (ev) {
      ev.preventDefault();
      sendPrompt(el.getAttribute("data-send-prompt") || "", {
        action: el.getAttribute("data-prompt-action") || "start",
        url: el.getAttribute("data-prompt-url") || "/onboarding",
        source: el.getAttribute("data-prompt-source") || "landing",
      });
    });
  });
});
