document.addEventListener("click", (event) => {
  if (event.target.classList.contains("clickable-close-button-dummy")) {
    let graph_container = event.target.parentElement.parentElement.parentElement.parentElement
    var container = graph_container.parentElement
    graph_container.remove()
  }
});