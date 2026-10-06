(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Header: add a compact state once the page scrolls past the fold.
  var header = document.getElementById("app-header");
  if (header) {
    var onScroll = function () {
      if (window.scrollY > 8) {
        header.classList.add("is-scrolled");
      } else {
        header.classList.remove("is-scrolled");
      }
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Mobile nav toggle.
  var navToggle = document.getElementById("nav-toggle");
  var topNav = document.getElementById("top-nav");
  if (navToggle && topNav) {
    navToggle.addEventListener("click", function () {
      var open = topNav.classList.toggle("is-open");
      navToggle.classList.toggle("is-open", open);
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("nav-open", open);
    });

    topNav.querySelectorAll("a, button[type='submit']").forEach(function (el) {
      el.addEventListener("click", function () {
        topNav.classList.remove("is-open");
        navToggle.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        document.body.classList.remove("nav-open");
      });
    });
  }

  // Toast messages: stagger entrance, offer manual close, auto-dismiss success only.
  var toasts = document.querySelectorAll(".toast");
  toasts.forEach(function (toast, index) {
    toast.style.setProperty("--toast-delay", index * 90 + "ms");

    var closeToast = function () {
      toast.classList.add("is-leaving");
      window.setTimeout(function () {
        toast.remove();
      }, reduceMotion ? 0 : 220);
    };

    var closeBtn = toast.querySelector(".toast-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", closeToast);
    }

    if (toast.classList.contains("toast-success") && !reduceMotion) {
      window.setTimeout(closeToast, 5200 + index * 200);
    }
  });

  // Scroll-reveal for cards and sections.
  var revealTargets = document.querySelectorAll(
    ".hotel-card, .management-card, .auth-feature-item, .empty-state, .section-heading"
  );

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealTargets.forEach(function (el) {
      el.classList.add("is-visible");
    });
  } else {
    revealTargets.forEach(function (el, index) {
      el.classList.add("reveal");
      el.style.setProperty("--reveal-delay", Math.min(index % 6, 5) * 60 + "ms");
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    revealTargets.forEach(function (el) {
      observer.observe(el);
    });
  }

  // Buttons: a short-lived ripple anchored at the pointer position.
  if (!reduceMotion) {
    document.addEventListener("click", function (event) {
      var button = event.target.closest(".button");
      if (!button) return;

      var rect = button.getBoundingClientRect();
      var ripple = document.createElement("span");
      ripple.className = "button-ripple";
      ripple.style.left = event.clientX - rect.left + "px";
      ripple.style.top = event.clientY - rect.top + "px";
      button.appendChild(ripple);
      window.setTimeout(function () {
        ripple.remove();
      }, 650);
    });
  }

  // Date range coordination and validation (Check-in / Check-out)
  function showAppToast(text, type) {
    var stack = document.getElementById("toast-stack");
    if (!stack) {
      alert(text);
      return;
    }
    var toast = document.createElement("div");
    toast.className = "toast toast-" + (type || "error");
    toast.setAttribute("role", "status");
    toast.innerHTML =
      '<span class="toast-icon" aria-hidden="true">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16.01"/></svg>' +
      "</span>" +
      '<span class="toast-text">' +
      text +
      "</span>" +
      '<button class="toast-close" type="button" aria-label="Cerrar mensaje">&times;</button>';

    var closeBtn = toast.querySelector(".toast-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        toast.classList.add("is-leaving");
        setTimeout(function () {
          toast.remove();
        }, 220);
      });
    }
    stack.appendChild(toast);
    setTimeout(function () {
      toast.classList.add("is-leaving");
      setTimeout(function () {
        toast.remove();
      }, 220);
    }, 5500);
  }

  function addDays(dateStr, days) {
    if (!dateStr) return "";
    var parts = dateStr.split("-");
    if (parts.length !== 3) return "";
    var d = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
    d.setDate(d.getDate() + days);
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + day;
  }

  function setupDateRangePicker(desdeInput, hastaInput, form, options) {
    if (!desdeInput || !hastaInput) return;
    options = options || {};

    var minDate = desdeInput.getAttribute("min");
    var maxDate = desdeInput.getAttribute("max");

    function syncLimits() {
      var dVal = desdeInput.value;
      var hVal = hastaInput.value;

      if (dVal) {
        var minCheckout = addDays(dVal, 1);
        hastaInput.min = minCheckout;
        if (hVal && hVal <= dVal) {
          hastaInput.value = maxDate && minCheckout > maxDate ? maxDate : minCheckout;
        }
      } else if (minDate) {
        hastaInput.min = addDays(minDate, 1);
      }

      if (hVal) {
        var maxCheckin = addDays(hVal, -1);
        if (maxDate && maxCheckin > maxDate) {
          desdeInput.max = maxDate;
        } else {
          desdeInput.max = maxCheckin;
        }
        if (dVal && dVal >= hVal) {
          desdeInput.value = minDate && maxCheckin < minDate ? minDate : maxCheckin;
        }
      } else if (maxDate) {
        desdeInput.max = maxDate;
      }
    }

    syncLimits();

    desdeInput.addEventListener("change", syncLimits);
    hastaInput.addEventListener("change", syncLimits);
    desdeInput.addEventListener("input", syncLimits);
    hastaInput.addEventListener("input", syncLimits);

    if (form) {
      form.addEventListener("submit", function (e) {
        var dVal = desdeInput.value;
        var hVal = hastaInput.value;

        if (options.requireBoth && (!dVal || !hVal)) {
          e.preventDefault();
          showAppToast("Ingresá tanto la fecha de ingreso como la de salida para consultar disponibilidad.", "warning");
          if (!dVal) desdeInput.focus();
          else hastaInput.focus();
          return false;
        }

        if (!options.requireBoth && ((dVal && !hVal) || (!dVal && hVal))) {
          e.preventDefault();
          showAppToast("Para buscar disponibilidad ingresá tanto la fecha de ingreso como la de salida, o dejá ambas vacías para buscar solo por destino.", "warning");
          if (!dVal) desdeInput.focus();
          else hastaInput.focus();
          return false;
        }

        if (dVal && hVal) {
          if (minDate && dVal < minDate) {
            e.preventDefault();
            showAppToast("La fecha de ingreso no puede ser anterior a hoy.", "error");
            desdeInput.focus();
            return false;
          }
          if (maxDate && (dVal > maxDate || hVal > maxDate)) {
            e.preventDefault();
            showAppToast("Las fechas de búsqueda y reserva no pueden superar 1 año en adelante.", "error");
            return false;
          }
          if (dVal >= hVal) {
            e.preventDefault();
            showAppToast("La fecha de salida debe ser posterior a la fecha de ingreso.", "error");
            hastaInput.focus();
            return false;
          }
        }
      });
    }
  }

  window.setupDateRangePicker = setupDateRangePicker;

  var homeDesde = document.getElementById("campo-desde");
  var homeHasta = document.getElementById("campo-hasta");
  if (homeDesde && homeHasta) {
    setupDateRangePicker(homeDesde, homeHasta, homeDesde.closest("form"), { requireBoth: false });
  }

  var detalleDesde = document.getElementById("detalle-desde");
  var detalleHasta = document.getElementById("detalle-hasta");
  if (detalleDesde && detalleHasta) {
    setupDateRangePicker(detalleDesde, detalleHasta, detalleDesde.closest("form"), { requireBoth: true });
  }
})();

