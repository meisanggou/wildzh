/**
 * Created by meisa on 2018/5/15.
 */

function update_doctor(){
    var r_data = new Object();
    var keys = ["people_name", "degree", "company", "department", "domain", "labels", "star_level"];
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
    var people_photo = $("#people_photo").attr("src");
    if(people_photo.length <= 0){
        popup_show("请上传医生图片");
        return 2;
    }
    r_data["people_photo"] = people_photo;

    var info_url = $("#info_url").val();
    my_async_request2(info_url, "PUT", r_data, function(data){
        swal({
                title: "选择下一步",
                text: msg,
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: '#DD6B55',
                confirmButtonText: '录入详细信息',
                cancelButtonText: "留在此页",
                closeOnConfirm: true,
                closeOnCancel: true
            },
            function(isConfirm){
                if (isConfirm){
                    var j_url = location.pathname + "?people_no=" + data["people_no"] + "&action=detail";
                    j_url += "&people_name=" + data["people_name"];
                    location.href = j_url;
                }
            }
        );
    });
}

function init_info(data){
    if(data == null){
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if(data.length > 0) {
        var doctor_item = data[0];
        var keys = ["people_name", "degree", "company", "department", "domain", "labels", "star_level"];
        for(var i=0;i<keys.length;i++) {
            $("#" + keys[i]).val(doctor_item[keys[i]]);
        }

        $("#people_photo").attr("src", doctor_item["people_photo"]);
        var detail_href = location.pathname + "?action=detail&people_no=" + doctor_item["people_no"];
        detail_href += "&people_name=" + doctor_item["people_name"];
        $("#link_detail").attr("href", detail_href);
        if((doctor_item["status"] & 2) == 2){
            $("#link_detail").text("更新详细");
        }
        $("#link_detail").show();
    }
}

$(function() {
    $("#people_extend_pic").change(function(){
        var upload_url= $("#upload_url").val();
        console.info(upload_url);
        if($("#people_extend_pic")[0].files.length <= 0){
            return 1;
        }
        var data = {"pic": $("#people_extend_pic")[0].files[0]};
        upload_request(upload_url, "POST", data, function(data){
            $("#people_photo").attr("src", data["pic"]);
        });
    });
    $("#btn_update").click(update_doctor);
    init_info(null);
});