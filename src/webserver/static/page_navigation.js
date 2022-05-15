const MIN_PAGE = 0;

function change_page() {
    window.location.href = this.getAttribute('data-url') + '&page=' + this.value;
}

function populate_page_select(element) {
    let last_page = element.getElementsByClassName('last-page')[0].textContent;
    last_page = parseInt(last_page.slice(0, -3));

    let current_page = element.getElementsByClassName('page-selection')[0];
    current_page = current_page.getElementsByTagName('option')[0].value;
    current_page = parseInt(current_page);

    if (current_page > MIN_PAGE) {
        for (var i = current_page - 1; i >= 0; i--) {
            let option = document.createElement('option');
            option.value = i;
            option.text = i;
            element.insertBefore(option, element.firstChild);
        }
    }
    
    if (current_page < last_page) {
        for (var i = current_page + 1; i <= last_page; i++) {
            let option = document.createElement('option');
            option.value = i;
            option.text = i;
            element.appendChild(option);
        }
    }
}

function load_navigation() {
    let navigation_elements = document.getElementsByClassName('page-navigation');
    for (var nav_span of navigation_elements) {
        if (nav_span.tagName == "SPAN") {
            populate_page_select(nav_span);
        }
    }
}