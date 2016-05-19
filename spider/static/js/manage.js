
function update_action_info(action) {
    var widget = document.getElementById('action-info');
    widget.style.display = "block";
    widget.innerHTML = "Making the action '"+action+"', please wait...";
    $.getJSON('/api/'+action,
        function(data_list) {
            widget.innerHTML = data_list.action + ": " + data_list.number + "";
            widget.innerHTML += "<div class='right'><a href='#' onclick='close_action_info()' class='button'>Close</a></div>"
            if (message in data_list) {
                $( "#message" ).dialog({ width: 700, height: 500 });
                $( "#message").innerHTML = data_list.message;
                console.log("update_action_info "+action+" "+data_list.message);
                $( "#message").show();
            }
        });
}

function close_action_info(action) {
    var widget = document.getElementById('action-info');
    widget.style.display = "none";
}