// ANIMACION DE ESCRITURA
var text = "Busca el dominio de una empresa";
var i = 0;
var typingText = document.querySelector(".typing-text");

function typeWriter() {
  if (i < text.length) {
    typingText.innerHTML += text.charAt(i);
    i++;
    setTimeout(typeWriter, 90);
  }
}

typeWriter();

//ANIMACION DE ESPERA
document.addEventListener("DOMContentLoaded", function () {
  // DESENFOQUE EN PANTALLA
  const form = document.querySelector("form");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const mainContent = document.getElementById("mainContent");

  // MENSAJE ESPERA
  form.addEventListener("submit", function (e) {
    loadingOverlay.style.display = "flex";
    mainContent.classList.add("content-blur");
  });
});
