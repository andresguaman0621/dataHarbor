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

// ANIMACION DE CARGA
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const loadingMessage = document.getElementById("loadingMessage");

  form.addEventListener("submit", function (e) {
    loadingMessage.style.display = "block";
  });
});
