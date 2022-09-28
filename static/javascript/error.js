// get error
// create request
if (window.XMLHttpRequest) {
    var req = new XMLHttpRequest();
}
else {
    var req = new ActiveXObject("Microsoft.XMLHTTP");
}

req.open("POST", "/get_error", true);
req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
req.onreadystatechange = function () {
    // when information is returned, put it into a datalist
    if (this.readyState == 4 && this.status == 200) {
        var response = this.responseText;
        var errorText = document.getElementById("error text");
        if (response == ""){
            errorText.parentElement.setAttribute("style","display: none;")
            return;
        }

        // display errors
        errorText.textContent = response;
        errorText.parentElement.setAttribute("style", 'padding: 5px;');
        errorText.style.height = 0;
        errorText.style.height = errorText.scrollHeight+"px";
    }
}
req.send();