(function addGraphsButtonsInteractions() {
  document.addEventListener("click", (e) => {
    switch (true) {
      case e.target.matches("div.clickable-close-button-dummy"): // if close button is pressed, remove the graph
        e.target.closest("div.graph-container-outer").remove();
        break;
      case e.target.matches("button.filter-button"): // if filter button is pressed, toggle the collapsible
        e.target.closest("div.filter").querySelector("div.filter-collapse").classList.toggle("show");
        break;
      case e.target.matches("button.filter-apply-button") || e.target.parentElement.matches("button.filter-apply-button"): // if filter apply button is pressed and collapsible is open, close the collapsible
        const collapsible = e.target.closest("div.filter").querySelector("div.filter-collapse");
        if (collapsible.classList.contains("show")) {
          collapsible.classList.remove("show");
        }
        break;
      default:
        break;
    }
  });
})();
