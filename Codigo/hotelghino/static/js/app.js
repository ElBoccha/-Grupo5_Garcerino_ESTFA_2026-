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
})();
