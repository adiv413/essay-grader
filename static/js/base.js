// Disables the button for 1000 milli seconds
function interval(){
    setTimeout(disableButton, 1);
    setTimeout(undisableButton, 1000)
}

// Disables Button
function disableButton(){
    document.getElementById("btn").disabled = true;
    console.log(document.getElementById("btn").disabled)
}

// Enables Button
function undisableButton(){
    document.getElementById("btn").disabled = false;
    console.log(document.getElementById("btn").disabled)
}
(function () {

    if (document.getElementById('info').getAttribute("dark_mode") == "True") {
        document.getElementById("gear").classList.add("invert");
    } else {
        document.getElementById("gear").classList.remove("invert");
    }
    console.log
})();