/**
 * Created by meisa on 2018/5/6.
 */

var ascii = ["A", "B", "C", "D", "E", "F"];

function new_video(){
    var r_data = new Object();
    var keys = ["video_type", "video_name", "video_desc", "episode_num"];
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
    var video_pic = $("#video_pic").attr("src");
    if(video_pic.length <= 0){
        popup_show("请上传视频图片");
        return 2;
    }
    r_data["video_pic"] = video_pic;

    var add_url = $("#add_url").val();
    my_async_request2(add_url, "POST", r_data, function(data){
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
            function(isConfirm){
                if (isConfirm){
                    var j_url = AddUrlArg(location.pathname, "video_no", data["video_no"]);
                    j_url = AddUrlArg(j_url, "video_type", data["video_type"]);
                    location.href = j_url;
                }
            }
        );
    });
}

$(function() {
    $("#video_extend_pic").change(function(){
        var upload_url= $("#upload_url").val();
        if($("#video_extend_pic")[0].files.length <= 0){
            return 1;
        }
        var data = {"pic": $("#video_extend_pic")[0].files[0]};
        upload_request(upload_url, "POST", data, function(data){
            $("#video_pic").attr("src", data["pic"]);
        });
    });
    $("#video_type").change();
    $("#btn_new").click(new_video);
});