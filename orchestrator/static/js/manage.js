
function update_action_info(action) {
    var widget = document.getElementById('action-info');
    widget.style.display = "block";
    widget.innerHTML = "Making the action '"+action+"', please wait...";
    $.getJSON('http://127.0.0.1:8080/api/'+action,
        function(data_list) {
            widget.innerHTML = data_list.action + ": " + data_list.number + "";
            widget.innerHTML += "<div class='right'><a href='#' onclick='close_action_info()' class='button'>Close</a></div>"
            if (message in data_list) {
                $( "#message" ).dialog({ width: 700, height: 500 });
                $( "#message").innerHTML = data_list.message;
            }
        });
}

function close_action_info(action) {
    var widget = document.getElementById('action-info');
    widget.style.display = "none";
}