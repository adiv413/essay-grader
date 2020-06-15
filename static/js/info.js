// function to toggle between light and dark theme
function toggleTheme() {
    var dark_mode = false;
    if (document.getElementById('slider').checked === false) {
        document.getElementById("global").className = 'theme-light';
        document.getElementById("gear").classList.remove("invert");
        dark_mode=false;
        document.documentElement.className = "theme-light";
        document.getElementById("info").getAttribute("dark_mode") == "True"
    } else {
        document.getElementById("global").className = 'theme-dark';
        document.getElementById("gear").classList.add("invert");
        dark_mode = true;
        document.documentElement.className = "theme-dark";
        document.getElementById("info").getAttribute("dark_mode") == "True"
    }
    var url = "/dark_mode/"
    $.ajax({
        url: url,
        data: {
            'dark':dark_mode,
            'email':document.getElementById("info").getAttribute("user")
        },
        success: function (data) {
            console.log("Should've Toggled");
        }
    });
    console.log(document.getElementById("info").getAttribute("dark_mode") == "True");
}

// Immediately invoked function to set the theme on initial load
(function () {
    var dark_theme = false;
    if (document.getElementById("info").getAttribute("dark_mode") === "True") {
        document.getElementById("global").className = 'theme-dark';
        document.getElementById('slider').checked = true;
        document.getElementById("gear").classList.add("invert");
        dark_theme = true;
        document.documentElement.className = "theme-dark";
    } else {
        document.getElementById("global").className = 'theme-light';
        document.getElementById('slider').checked = false;
        document.getElementById("gear").classList.remove("invert");
        dark_theme = false
        document.documentElement.className = "theme-light";
    }
})();