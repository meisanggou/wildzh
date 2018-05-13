/**
 * Created by msg on 2/22/17.
 */

function login_success(data) {
    console.info(data);
    var current_user = data.user_name;
    var storage_key = "jingyun_username";
    var rem_user_names = localStorage.getItem(storage_key);
    var rem_v2 = "";
    if ($("input[name='remember']").is(':checked')) {
        rem_v2 += current_user + ",";
        if (rem_user_names != null) {
            var user_names = rem_user_names.split(",");
            for (var i = 0; i < user_names.length; i++) {
                if (user_names[i] != current_user && user_names[i] != "") {
                    rem_v2 += user_names[i] + ",";
                }
            }
        }
        if (rem_v2.length > 0) {
            localStorage.setItem(storage_key, rem_v2.substr(0, rem_v2.length - 1));
        }
    }
    else {
        console.info("un checked");
        localStorage.removeItem(storage_key);
    }


    location.href = data.location;
}

function login() {
    var user_name = $("input[name='user_name']").val();
    var password = $("input[name='password']").val();
    var next = $("input[name='next']").val();
    var request_data = {"user_name": user_name, "password": password, "next": next};
    var request_url = "/login/";
    my_async_request2(request_url, "POST", request_data, login_success);
}

$(document).ready(function () {
    console.info("welcome to dms, please login first!");
    // 自动填充记录的账户名
    var storage_key = "jingyun_username";
    var rem_user_names = localStorage.getItem(storage_key);
    if (rem_user_names != null) {
        var user_names = rem_user_names.split(",");
        console.info(user_names);
        $("input[name='user_name']").val(user_names[0]);
    }
    $("#btn_login").click(login);
    if ($("#btn_domain_login").length > 0) {
        $("#btn_login").text("自动登录中...");
        var request_url = "/login/";
        var request_data = {"domain_user": true};
        my_async_request2(request_url, "POST", request_data, login_success);
    }
    $(function(){
        document.onkeydown = function(e){
            var ev = document.all ? window.event : e;
            if(ev.keyCode==13) {
                $("#btn_login").click();
             }
        }
    });

});