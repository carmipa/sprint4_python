document.addEventListener('DOMContentLoaded', function () {
    const menuLinks = document.querySelectorAll('.menu-container ul li a');
    const popup = document.querySelector('.popup');
    const overlay = document.querySelector('.overlay');
    const closePopup = document.querySelector('.popup-close');
    const popupContent = document.querySelector('.popup-content');

    // Adiciona eventos de clique aos links do menu
    menuLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');

            // Exibe o popup apenas se o link não tiver um destino válido (por exemplo, href="#")
            if (href === '#') {
                e.preventDefault();  // Evita o redirecionamento somente nesses casos
                const itemName = this.textContent;  // Captura o texto do link
                popupContent.textContent = `Você clicou em: ${itemName}`;
                popup.style.display = 'block';
                overlay.style.display = 'block';
            }
        });
    });

    // Fechar popup ao clicar no "X"
    closePopup.addEventListener('click', function () {
        popup.style.display = 'none';
        overlay.style.display = 'none';
    });

    // Fechar popup ao clicar fora do popup (no overlay)
    overlay.addEventListener('click', function () {
        popup.style.display = 'none';
        overlay.style.display = 'none';
    });
});
