/**
 * Created by msg on 2/22/17.
 */

var storage_key = "wildzh_username";

function login_success(data) {
    var current_user = data.user_name;
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


$(document).ready(function () {
    var vm_l = new Vue({
        el: "#div_login",
        data: {
            user_name: "admin",
            password: ""
        },
        methods: {
            login: function () {
                var next = $("#next_url").val();
                var request_data = {"user_name": this.user_name, "password": this.password, "next": next};
                var request_url = $("#login_url").val();
                console.info(request_url);
                my_async_request2(request_url, "POST", request_data, login_success);
            }
        }
    });

});