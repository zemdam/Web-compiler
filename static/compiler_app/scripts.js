let choose = [];
let current = 0;

async function changePage(url) {
    choose = [];
    current = 0;
    const respone = await fetch(url);
    document.querySelector("html").innerHTML = await respone.text();
    if (location.hash) {
        location.href = location.hash;
    }
}

async function sendPost(e, form) {
    choose = [];
    current = 0;
    e.preventDefault();
    const respone = await fetch(form.action, {method:'post', body: new FormData(form)});
    document.querySelector("html").innerHTML = await respone.text();
    if (location.hash) {
        location.href = location.hash;
    }
}

async function sendForm(form) {
    choose = [];
    current = 0;
    const respone = await fetch(form.action, {method:'post', body: new FormData(form)});
    document.querySelector("html").innerHTML = await respone.text();
    if (location.hash) {
        location.href = location.hash;
    }
}

async function hideHeader(header) {
    $(header).toggle();
}

async function hideSections() {
    $(".section__content").hide();
}

async function showSections() {
    $(".section__content").show();
}

async function highlightLine(line) {
    line = "#line-" + line;
    $(line).css("background-color","black");
    $(line).trigger("focus");
    $(line).blur(function(){
        $(this).css("background-color","");
    })
}

async function markLine(line_num) {
    $(".add-section").show()
    if (choose[current]) {
        $("#numed-" + choose[current]).css("background-color","");
    }

    $("#numed-" + line_num).css("background-color","red");
    choose[current] = line_num;

    current += 1;
    current %= 2;
}

async function addSection(section_type) {
    document.getElementById('id_section_start').value = Math.min(...choose) - 1;
    document.getElementById('id_section_end').value = Math.max(...choose) - 1;
    document.getElementById('id_section_type').value = section_type;
    form = document.getElementById('add-section-id');
    sendForm(form);
}