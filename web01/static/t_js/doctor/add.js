/**
 * Created by meisa on 2018/5/6.
 */

var ascii = ["A", "B", "C", "D", "E", "F"];

function new_music(){
    var r_data = new Object();
    var keys = ["music_type", "music_name", "music_desc", "music_url"];
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
    var pic_url = $("#music_extend_pic_url").attr("src");
    if(pic_url.length <= 0){
        popup_show("请上传音乐图片");
        return 2;
    }
    r_data["pic_url"] = pic_url;

    var add_url = $("#add_url").val();
    my_async_request2(add_url, "POST", r_data, function(data){
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

$(function() {
    $("#music_type").change(function(){
        var select_m = $("#music_type option:selected").val();
        var about = parseInt($("#music_type option:selected").attr("about"));
        var exist_explain = $("#result_explain").find("li[name='li_explain']");
        var demo_li = $(exist_explain[0]);
        var demo_parent = demo_li.parent();
        var exist_len = exist_explain.length;
        for(var i=exist_len;i<about + 1 && i<= 7;i++)
        {
            var clone_li = demo_li.clone();
            clone_li.show();
            $(clone_li.find("input")[0]).val(ascii[i - 1]);
            demo_parent.append(clone_li);
        }
        for(var i=about+ 1; i<exist_len;i++){
            $(exist_explain[i]).remove();
        }
    });
    $("#music_extend_pic").change(function(){
        var upload_url= $("#upload_url").val();
        if($("#music_extend_pic")[0].files.length <= 0){
            return 1;
        }
        var data = {"pic": $("#music_extend_pic")[0].files[0]};
        upload_request(upload_url, "POST", data, function(data){
            $("#music_extend_pic_url").attr("src", data["pic"]);
        });
    });
    $("#upload_music").change(function () {
        if($("#upload_music")[0].files.length <= 0) {
            return 1;
        }
        $("#btn_upload").removeAttr("disabled");
        $("#btn_upload").text("上传");
    });
    $("#btn_upload").click(function(){
        if($("#upload_music")[0].files.length <= 0) {
            popup_show("请选择一首音乐");
            return 1;
        }
        $(this).attr("disabled", "disabled");
        $(this).text("上传中");
        $("#upload_music").attr("disabled", "disabled");

        var upload_url = $("#m_upload_url").val();
        var data = {"m": $("#upload_music")[0].files[0]};
        upload_request(upload_url, "POST", data, function(data){
            $("#btn_upload").text("已上传");
            $("#btn_new").removeAttr("disabled");
            $("#btn_new").click(new_music);
            $("#music_url").val(data["m"]);
        });

    });
    $("#music_type").change();
});