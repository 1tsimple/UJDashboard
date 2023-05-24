(function changeCardBorderColorOnCloseButtonHover() {
  document.addEventListener("mouseover", (e) => {
    const hovered_element = e.target;
    if (hovered_element.classList.contains("erank-keyword-data-card-close-button")) {
      hovered_element.parentElement.style.borderColor = "var(--bg-red)";
    }
  });
  document.addEventListener("mouseout", (e) => {
    const hovered_element = e.target;
    if (hovered_element.classList.contains("erank-keyword-data-card-close-button")) {
      hovered_element.parentElement.style.removeProperty("border-color");
    }
  });
})();
