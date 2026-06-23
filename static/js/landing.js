/**
 * Punto de entrada para CTAs conversacionales de la landing.
 * Hoy redirige al onboarding; mañana puede abrir un widget de ventas.
 */
function sendPrompt(message, options) {
  var opts = options || {};
  var text = (message || "").trim();

  try {
    sessionStorage.setItem("mantis_sales_prompt", text);
  } catch (e) {
    /* ignore */
  }

  window.dispatchEvent(
    new CustomEvent("mantis:sales-prompt", {
      detail: { message: text, source: opts.source || "landing" },
    })
  );

  if (opts.action === "contact") {
    var subject = encodeURIComponent("Contacto Mantis — Enterprise");
    var body = encodeURIComponent(text || "Hola, me interesa el plan Enterprise de Mantis.");
    window.location.href = "mailto:hola@mantis.app?subject=" + subject + "&body=" + body;
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
