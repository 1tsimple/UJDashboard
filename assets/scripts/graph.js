document.addEventListener("click", (event) => {
  if (event.target.classList.contains("clickable-close-button-dummy")) {
    event.target.parentElement.parentElement.parentElement.parentElement.remove()
  }
});