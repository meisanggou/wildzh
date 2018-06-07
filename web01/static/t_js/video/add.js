/**
 * Created by meisa on 2018/5/6.
 */

var ascii = ["A", "B", "C", "D", "E", "F"];
var p_vm = null;

function init_info(data) {
    if (data == null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        var video_item = data[0];
        p_vm.media_item = video_item;
        $("#video_name").val(video_item["video_name"]);
        $("#video_no").val(video_item["video_no"]);
        select_option("video_type", video_item["video_type"]);
        $("#episode_num").val(video_item["episode_num"]);
        $("#video_desc").val(video_item["video_desc"]);
        $("#video_pic").attr("src", video_item["video_pic"]);
        $("#video_type").attr("disabled", "disabled");
        $("#lab_upload_num").text(video_item["upload_num"]);
        $("#btn_new").text("更新");
        $("#li_add").show();
        $("#div_upload_status").show();
        $("#li_update a").text("更新视频");
    }
}

function request_video(method, r_data) {
    var msg = "新建成功";
    if(method == "PUT"){
        msg = "更新成功";
    }
    var info_url = $("#info_url").val();
    my_async_request2(info_url, method, r_data, function (data) {
        if(method == "PUT"){
            popup_show(msg);
            if("upload_num" in data){
                $("#lab_upload_num").text(data["upload_num"]);
            }
        }
        else {
            swal({
                    title: "选择下一步",
                    text: msg,
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: '#DD6B55',
                    confirmButtonText: '上传分集视频',
                    cancelButtonText: "留在此页",
                    closeOnConfirm: true,
                    closeOnCancel: true
                },
                function (isConfirm) {
                    if (isConfirm) {
                        var j_url = AddUrlArg(location.pathname, "video_no", data["video_no"]);
                        j_url = AddUrlArg(j_url, "video_type", data["video_type"]);
                        location.href = j_url;
                    }
                    else {
                        $("#video_type").attr("disabled", "disabled");
                        $("#video_no").val(data["video_no"]);
                        $("#btn_new").text("更新");
                    }
                }
            );
        }
    });
}
function new_or_update_video() {
    var r_data = new Object();
    var keys = ["video_type", "accept_formats", "video_name", "video_desc"];
    for (var i = 0; i < keys.length; i++) {
        var item = $("#" + keys[i]);
        var v = item.val().trim();
        if (v.length <= 0) {
            var msg = item.attr("msg");
            popup_show(msg);
            return 1;
        }
        r_data[keys[i]] = v;
    }
    var episode_num = p_vm.media_item.episode_num;
    if (isSuitableNaN(episode_num, 0, 10000) == false) {
        popup_show("请在总集数出输入一个0-10000的数字");
        return 2;
    }
    r_data["episode_num"] = episode_num;
    var video_pic = $("#video_pic").attr("src");
    if (video_pic.length <= 0) {
        popup_show("请上传视频图片");
        return 3;
    }
    if(p_vm.media_item.link_people.length == 32){
        r_data["link_people"] = p_vm.media_item.link_people;
    }
    r_data["video_pic"] = video_pic;
    var video_no = $("#video_no").val();
    var method = "POST";
    if (video_no.length == 32) {
        method = "PUT";
        r_data["video_no"] = video_no;
    }
    if ($("#lab_upload_num").text().length > 0) {
        var upload_num = parseInt($("#lab_upload_num").text());
        if (r_data["episode_num"] < upload_num) {
            r_data["upload_num"] = r_data["episode_num"];
            var msg = "更新后总集数【" + r_data["episode_num"] + "】小于已上传集数【" + upload_num + "】，多上传的将会删除！";
            swal({
                    title: "更新确认",
                    text: msg,
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: '#DD6B55',
                    confirmButtonText: '确定更新',
                    cancelButtonText: "再看看",
                    closeOnConfirm: true,
                    closeOnCancel: true
                },
                function (isConfirm) {
                    if (isConfirm) {
                        request_video(method, r_data);
                    }
                }
            );
            return 4;
        }
    }
    request_video(method, r_data);
}

$(function () {
    $("#li_add").hide();
    var media_item = {"link_people": "0", "episode_num": ""};
    if (UrlArgsValue(location.href, "video_no") != null) {
        init_info(null);
    }
    $("#btn_new").click(new_or_update_video);
    p_vm = new Vue({
        el:"#myTabContent",
        data:{
            people: [],
            media_item: media_item
        },
        methods:{
            start_upload: function(){
                var upload_url = $("#upload_url").val();
                if ($("#video_extend_pic")[0].files.length <= 0) {
                    return 1;
                }
                var data = {"pic": $("#video_extend_pic")[0].files[0]};
                upload_request(upload_url, "POST", data, function (data) {
                    $("#video_pic").attr("src", data["pic"]);
                });
            },
            new_media: function () {
                new_or_update_video();
            }
        }
    });
    my_async_request2($("#url_people").val(), "GET", null, function(data){
        p_vm.people = data;
    })
});