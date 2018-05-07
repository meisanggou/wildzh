/**
 * Created by msg on 11/23/15.
 */

function bit_and(a, b) {
    var c = 1;
    var r = 0;
    while (a > 0 && b > 0) {
        if (a % 2 == 1 && b % 2 == 1) {
            r += c;
        }
        a = (a - a % 2) / 2;
        b = (b - b % 2) / 2;
        c = c * 2;
    }
    return r;
}

function user_select_change(){
    var role_value = JSON.parse($("#role_desc").text());
    var selected_user = $("#perm_user option:selected");
    var user_role = parseInt(selected_user.attr("role"));
    if(user_role == 0){
        $("#link_remove_user").show();
    }
    else{
        $("#link_remove_user").hide();
    }
    for(var role_module in role_value) {
        var role_list = role_value[role_module]["role_list"];
        for(var role in role_list) {
            var role_el = document.getElementById(role);
            if (role_el == null) {
                continue;
            }
            if (bit_and(role_list[role]["role_value"], user_role) == role_list[role]["role_value"]) {
                role_el.checked = true;
            }
            else {
                role_el.checked = false;
            }
        }
    }

}

function reload(data){
    location.reload();
}

function remove_user(){
    var selected_user = $("#perm_user option:selected").val();
    var r_url = $("#link_remove_user").attr("url");
    my_async_request2(r_url, "DELETE", {"user_name": selected_user}, reload);
}
$(function() {
    user_select_change();
    $("#link_remove_user").click(remove_user);
});