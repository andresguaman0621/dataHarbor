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
