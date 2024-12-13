document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('contact-modal');
    const contactLink = document.getElementById('contact-link');
    const closeButton = document.querySelector('.close-button');

    contactLink.addEventListener('click', (event) => {
        event.preventDefault();
        modal.style.display = 'block';
    });

    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
