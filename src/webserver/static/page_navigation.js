function change_page() {
    window.location.href = this.getAttribute('data-url') + '&page=' + this.value;
}