function change_page() {
    window.location.href = this.getAttribute('data-url') + '&page=' + this.value;
}

function populate_page_select(element) {
    element.childNodes
}

function load_navigation() {
    let navigation_elements = document.getElementsByClassName('page-navigation');
    for (var nav_span of navigation_elements) {
        if (nav_span.tagName == "SPAN") {
            populate_page_select(nav_span)
            nav_span.childNodes
        }
    }
}