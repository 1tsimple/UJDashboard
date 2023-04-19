document.addEventListener("click", (event) => {
  if (event.target.classList.contains("clickable-close-button-dummy")) {
    let graph_container = event.target.parentElement.parentElement.parentElement.parentElement;
    graph_container.remove();
  } else if (event.target.type === "button" && event.target.classList.contains("filter-button")) {
    let collapsible = event.target.parentElement.parentElement.getElementsByClassName("filter-collapse")[0];
    collapsible.classList.toggle("show");
  } else if ((event.target.type === "submit" && event.target.classList.contains("filter-apply-button")) || (event.target.parentElement.type === "submit" && event.target.parentElement.classList.contains("filter-apply-button"))) {
    let target
    if (event.target.type === "submit" && event.target.classList.contains("filter-apply-button")) {
      target = event.target.parentElement.parentElement;
    } else {
      target = event.target.parentElement.parentElement.parentElement;
    }
    let collapsible = event.target.parentElement.parentElement.getElementsByClassName("filter-collapse")[0];
    if (collapsible.classList.contains("show")) {
      collapsible.classList.remove("show")
    }
  }
});
