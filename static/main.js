
document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  const toggle = document.getElementById("theme-toggle");

  const setTheme = (theme) => {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  };


  const saved = localStorage.getItem("theme");
  if (saved) {
    setTheme(saved);
  } else {

    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDark ? "dark" : "light");
  }

  toggle.addEventListener("click", () => {
    const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    setTheme(next);
   
    toggle.animate([{ transform: "scale(0.95)" }, { transform: "scale(1)" }], {duration:120});
  });
});
