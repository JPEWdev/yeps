// Wrap the tables in YEP bodies in a div, to allow for responsive scrolling

"use strict";

const yepContentId = "yep-content";


// Wrap passed table element in wrapper divs
function wrapTable (table) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("table-wrapper");
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
}


// Wrap all tables in the YEP content in wrapper divs
function wrapYepContentTables () {
    const yepContent = document.getElementById(yepContentId);
    const bodyTables = yepContent.getElementsByTagName("table");
    Array.from(bodyTables).forEach(wrapTable);
}


// Wrap the tables as soon as the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById(yepContentId)) {
        wrapYepContentTables();
    }
})
