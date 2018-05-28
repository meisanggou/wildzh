/**
 * Created by meisa on 2018/5/15.
 */

function add_or_update_detail(){
    var r_data = new Object();
    var keys = ["doctor_profile", "work_experience", "study_experience", "honor", "unit_price"];
    for(var i=0;i<keys.length;i++){
        var item = $("#" + keys[i]);
        var v = item.val().trim();
        if(v.length <= 0){
            var msg = item.attr("msg");
            popup_show(msg);
            return 1;
        }
        r_data[keys[i]] = v;
    }

    var detail_url = $("#detail_url").val();
    var method = "POST";
    if($("#btn_new").text() == "更新"){
        method = "PUT";
    }
    my_async_request2(detail_url, method, r_data, function(data){
        swal({
                title: "选择下一步",
                text: msg,
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: '#DD6B55',
                confirmButtonText: '进入列表',
                cancelButtonText: "留在此页",
                closeOnConfirm: true,
                closeOnCancel: true
            },
            function(isConfirm){
                if (isConfirm){
                    var j_url = location.pathname;
                    location.href = j_url;
                }
            }
        );
    });
}

function init_detail(data){
    if(data == null){
        var detail_url = $("#detail_url").val();
        my_async_request2(detail_url, "GET", null, init_detail);
        return 0;
    }
    if(typeof(data) == Array && data.length > 0) {
        var item = data[0];
        if(item == null){
            return 0;
        }
        var keys = ["doctor_profile", "work_experience", "study_experience", "honor", "unit_price"];
        for(var i=0;i<keys.length;i++) {
            $("#" + keys[i]).val(item[keys[i]]);
        }
        $("#btn_new").text("更新");
    }
}

$(function() {
    $("#btn_new").click(add_or_update_detail);
    init_detail(null);
    $("#doctor_name").val(decodeURI(UrlArgsValue(location.href, "doctor_name")));
});