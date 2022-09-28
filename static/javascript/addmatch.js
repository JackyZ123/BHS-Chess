var white = undefined;
var black = undefined;

// if click out of input for first player select the first
document.getElementById('white').addEventListener('keyup', function (e) {
    if (e.which == 13) {
        pickFirst("white");
        select = "no id";
        this.blur();
    }
});

// if click out of input for second player select the first
document.getElementById('black').addEventListener('keyup', function (e) {
    if (e.which == 13) {
        pickFirst("black");
        select = "no id";
        this.blur();
    }
});

// take the most similar player to name given
function pickFirst(caller) {
    var input = document.getElementById(caller);
    var datalist = document.getElementById(caller + " drop");

    console.log(datalist);

    // check if they typed anything in
    if (input.value == "")
        return;
    // console.log(document.getElementById(caller + " drop").childElementCount);
    if (datalist.childElementCount > 0) {
        if (input.value.length != datalist.firstChild.value.length){
            if (caller == 'white')
                white = undefined;
            else
                black = undefined;
        }
        else{
            input.value = datalist.firstChild.value;
            if (caller == 'white')
                white = datalist.firstChild.id;
            else
                black = datalist.firstChild.id;
        }
    }
}

// get similar names from input
function autofill_matches(caller) {
    var val = document.getElementById(caller).value;
    var datalist = document.getElementById(caller + " drop");

    // create request
    if (window.XMLHttpRequest) {
        var req = new XMLHttpRequest();
    }
    else {
        var req = new ActiveXObject("Microsoft.XMLHTTP");
    }

    req.open("POST", "/autofill_matches", true);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.onreadystatechange = function () {
        // when information is returned, put it into a datalist
        if (this.readyState == 4 && this.status == 200) {
            var response = this.responseText;
            response = response.split("|");
            // remove current options
            while (datalist.childElementCount > 0) {
                datalist.removeChild(datalist.firstChild);
            }
            // create new options
            for (var i = 0; i < response.length; i++) {
                if (response[i] == "")
                    continue;

                response[i] = response[i].substr(1, response[i].length - 3);
                var this_option = response[i].split(", '");
                var option = new Option("", this_option[1]);
                option.id = this_option[0];
                datalist.appendChild(option);
            }
        }
    };

    // console.log(val);

    req.send("data=" + val);

    // console.log("sent")
}

// first iteration so it functions as intended (get it on start)
autofill_matches('white');
autofill_matches('black');

var select = "no id";

// check if they select something other than an input and pick first from datalist
document.onselectionchange = function () {
    try {
        if ((select.substr(0, 5) == "white" || select.substring(0,5) == 'black') && document.getSelection().focusNode.firstChild.id != select) {
            pickFirst(select.substr(6, select.length));
        }

        else if (select.substr(0, 5) == "white" || select.substring(0,5) == 'black')
            select = document.getSelection().focusNode.firstChild.id;
        else
            select = "no id";
    }
    catch {
        select = "no id";
    }
};

// submit the new match
function submit() {
    if (window.XMLHttpRequest) {
        var req = new XMLHttpRequest();
    }
    else {
        var req = new ActiveXObject("Microsoft.XMLHTTP");
    }

    // check inputs again
    pickFirst("white");
    pickFirst("black");

    // send details
    req.open("POST", "/new_match", true);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            location.reload(true);
        }
    };

    var winner = document.getElementById("winner").value;

    // console.log(white,black);

    req.send("white=" + white + "&black=" + black + "&winner=" + winner);
}