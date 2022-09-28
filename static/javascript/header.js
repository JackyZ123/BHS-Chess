// create request
if (window.XMLHttpRequest) {
    var req = new XMLHttpRequest();
}
else {
    var req = new ActiveXObject("Microsoft.XMLHTTP");
}

req.open("POST", "/get_user", true);
req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
req.onreadystatechange = function () {
    // process user
    if (this.readyState == 4 && this.status == 200) {
        var response = this.responseText;
        var userText = document.getElementById("user");
        if (response == ""){
            // no user
            userText.textContent = "Not Signed In"
            document.getElementById("logout link").setAttribute("style","display: none;");
            return;
        }
        else{
            // yes user
            userText.textContent = "User: " + response;
            document.getElementById("login link").setAttribute("style","display: none;");
        }

    }
}
req.send();