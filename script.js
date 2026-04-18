(function () {
  // --- Language Toggle ---
  var STORAGE_KEY = "fixitbrampton-lang";
  var langToggle = document.getElementById("langToggle");
  var langLabel = document.getElementById("langLabel");

  function setLang(lang) {
    var els = document.querySelectorAll("[data-en]");
    for (var i = 0; i < els.length; i++) {
      var text = els[i].getAttribute("data-" + lang);
      if (text !== null && text !== undefined) els[i].textContent = text;
    }
    var htmlEls = document.querySelectorAll("[data-en-html]");
    for (var j = 0; j < htmlEls.length; j++) {
      var html = htmlEls[j].getAttribute("data-" + lang + "-html");
      if (html !== null && html !== undefined) htmlEls[j].innerHTML = html;
    }
    if (langLabel) langLabel.textContent = lang === "en" ? "ਪੰਜਾਬੀ" : "English";
    document.documentElement.lang = lang === "pa" ? "pa" : "en";
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {}
  }

  if (langToggle) {
    langToggle.addEventListener("click", function () {
      var current = localStorage.getItem(STORAGE_KEY) || "en";
      setLang(current === "en" ? "pa" : "en");
    });
  }

  // Restore saved language
  var saved = null;
  try {
    saved = localStorage.getItem(STORAGE_KEY);
  } catch (e) {}
  if (saved === "pa") setLang("pa");

  // --- Footer year ---
  var yearEl = document.getElementById("footerYear");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // --- Contact Form ---
  var form = document.getElementById("contactForm");
  if (!form) return;
  var status = document.getElementById("formStatus");

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    status.textContent = "";
    status.className = "form-status";

    var data = {
      name: form.name.value.trim(),
      phone: form.phone.value.trim(),
      message: form.message.value.trim(),
    };

    var lang = localStorage.getItem(STORAGE_KEY) || "en";

    if (!data.name || !data.phone || !data.message) {
      status.textContent = lang === "pa"
        ? "ਕਿਰਪਾ ਕਰਕੇ ਸਾਰੇ ਖੇਤਰ ਭਰੋ।"
        : "Please fill in all fields.";
      status.className = "form-status error";
      btn.disabled = false;
      return;
    }

    fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, body: body };
        });
      })
      .then(function (result) {
        if (result.ok) {
          status.textContent =
            lang === "pa"
              ? "ਸੁਨੇਹਾ ਭੇਜ ਦਿੱਤਾ ਗਿਆ! ਅਸੀਂ ਜਲਦੀ ਸੰਪਰਕ ਕਰਾਂਗੇ।"
              : "Message sent! We'll get back to you the same day.";
          status.className = "form-status success";
          form.reset();
        } else {
          throw new Error(result.body.error || "Send failed");
        }
      })
      .catch(function () {
        status.textContent =
          lang === "pa"
            ? "ਭੇਜਣ ਵਿੱਚ ਅਸਫ਼ਲ। ਕਿਰਪਾ ਕਰਕੇ ਟੈਕਸਟ ਕਰੋ (289) 275-3973।"
            : "Couldn't send — please text us instead at (289) 275-3973.";
        status.className = "form-status error";
      })
      .finally(function () {
        btn.disabled = false;
      });
  });
})();
