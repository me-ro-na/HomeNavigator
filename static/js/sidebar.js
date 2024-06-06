document.addEventListener("DOMContentLoaded", function() {
    const sidebar = document.querySelector('.sidebar');
    const toggleButton = document.querySelector('.sidebar-toggle');
    const content = document.querySelector('.content');

    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('closed');
        content.classList.toggle('closed');

        if (sidebar.classList.contains('closed')) {
            toggleButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        } else {
            toggleButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
        }
    });
});
