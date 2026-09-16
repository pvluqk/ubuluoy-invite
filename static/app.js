(function () {
  const cover = document.getElementById("cover");
  const site = document.getElementById("site");
  const openBtn = document.getElementById("open-letter");

  function openLetter() {
    if (!cover || !site) return;
    cover.classList.add("is-gone");
    site.hidden = false;
    document.body.style.overflow = "";
    setTimeout(() => cover.remove(), 750);
  }

  if (sessionStorage.getItem("inviteOpened") === "1") {
    if (cover) cover.remove();
    if (site) site.hidden = false;
  } else {
    document.body.style.overflow = "hidden";
    openBtn?.addEventListener("click", () => {
      sessionStorage.setItem("inviteOpened", "1");
      openLetter();
    });
  }

  const block = document.getElementById("countdown-block");
  const deadline = block?.dataset.deadline;
  if (deadline && !Number.isNaN(Date.parse(deadline))) {
    const target = new Date(deadline).getTime();
    const els = {
      d: document.getElementById("cd-d"),
      h: document.getElementById("cd-h"),
      m: document.getElementById("cd-m"),
      s: document.getElementById("cd-s"),
    };

    function tick() {
      const diff = Math.max(0, target - Date.now());
      if (els.d) els.d.textContent = String(Math.floor(diff / 86400000));
      if (els.h) els.h.textContent = String(Math.floor((diff % 86400000) / 3600000)).padStart(2, "0");
      if (els.m) els.m.textContent = String(Math.floor((diff % 3600000) / 60000)).padStart(2, "0");
      if (els.s) els.s.textContent = String(Math.floor((diff % 60000) / 1000)).padStart(2, "0");
    }

    tick();
    setInterval(tick, 1000);
  }

  const form = document.getElementById("rsvp-form");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const errorEl = document.getElementById("form-error");
    const surname = (form.surname?.value || "").trim();
    const firstname = (form.firstname?.value || "").trim();
    const comingInput = form.querySelector('input[name="coming"]:checked');
    const name = [surname, firstname].filter(Boolean).join(" ");

    if (!firstname || !comingInput) {
      errorEl.hidden = false;
      errorEl.textContent = "Аатыҥ уонна эппиэтиҥ наада.";
      return;
    }

    errorEl.hidden = true;
    try {
      const res = await fetch("/api/rsvp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, coming: comingInput.value === "yes" }),
      });
      if (!res.ok) throw new Error("fail");
      const data = await res.json();
      const box = document.createElement("div");
      box.className = "thanks";
      box.setAttribute("role", "status");
      box.innerHTML =
        `<p class="thanks__title">Махтал, ${data.name}!</p>` +
        (data.coming
          ? "<p>Кэлэргин күүтэбит. Көрсүөххэ диэри!</p>"
          : "<p>Хомойуох иһин. Баҕа санааҕын истибиппит.</p>");
      form.replaceWith(box);
    } catch (err) {
      errorEl.hidden = false;
      errorEl.textContent = "Алҕас таҕыста. Өссө боруобалаан көр.";
    }
  });
})();
