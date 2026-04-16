(function () {
  // --- Language Toggle ---
  var STORAGE_KEY = "fixitbrampton-lang";
  var langToggle = document.getElementById("langToggle");
  var langLabel = document.getElementById("langLabel");

  function setLang(lang) {
    var els = document.querySelectorAll("[data-en]");
    for (var i = 0; i < els.length; i++) {
      var text = els[i].getAttribute("data-" + lang);
      if (text) els[i].textContent = text;
    }
    langLabel.textContent = lang === "en" ? "ਪੰਜਾਬੀ" : "English";
    document.documentElement.lang = lang === "pa" ? "pa" : "en";
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {}
  }

  langToggle.addEventListener("click", function () {
    var current = localStorage.getItem(STORAGE_KEY) || "en";
    setLang(current === "en" ? "pa" : "en");
  });

  // Restore saved language
  var saved = null;
  try {
    saved = localStorage.getItem(STORAGE_KEY);
  } catch (e) {}
  if (saved === "pa") setLang("pa");

  // --- Contact Form ---
  var form = document.getElementById("contactForm");
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

    if (!data.name || !data.phone || !data.message) {
      status.textContent = "Please fill in all fields.";
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
          var lang = localStorage.getItem(STORAGE_KEY) || "en";
          status.textContent =
            lang === "pa"
              ? "ਸੁਨੇਹਾ ਭੇਜ ਦਿੱਤਾ ਗਿਆ! ਅਸੀਂ ਜਲਦੀ ਸੰਪਰਕ ਕਰਾਂਗੇ।"
              : "Message sent! We'll get back to you soon.";
          status.className = "form-status success";
          form.reset();
        } else {
          throw new Error(result.body.error || "Send failed");
        }
      })
      .catch(function () {
        var lang = localStorage.getItem(STORAGE_KEY) || "en";
        status.textContent =
          lang === "pa"
            ? "ਭੇਜਣ ਵਿੱਚ ਅਸਫ਼ਲ। ਕਿਰਪਾ ਕਰਕੇ ਕਾਲ ਕਰੋ।"
            : "Failed to send. Please call us instead.";
        status.className = "form-status error";
      })
      .finally(function () {
        btn.disabled = false;
      });
  });
})();
