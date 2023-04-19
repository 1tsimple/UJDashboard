document.addEventListener("click", (event) => {
  if (event.target.classList.contains("clickable-close-button-dummy")) {
    let graph_container = event.target.parentElement.parentElement.parentElement.parentElement;
    var container = graph_container.parentElement;
    graph_container.remove();
  }
  if (event.target.type === "button" && event.target.classList.contains("filter-button")) {
    let collapsible = event.target.parentElement.parentElement.getElementsByClassName("filter-collapse")[0];
    collapsible.classList.toggle("show");
  }
  console.log(event.target)
  /* TODO: apply button basılınca collapsible'ı kapat */
});
