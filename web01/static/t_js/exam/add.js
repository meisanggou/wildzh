/**
 * Created by meisa on 2018/5/6.
 */

var ascii = ["A", "B", "C", "D", "E", "F"];

function new_exam(){
    var r_data = new Object();
    var keys = ["exam_type", "exam_name", "exam_desc", "eval_type"];
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
    var pic_url = $("#exam_extend_pic_url").attr("src");
    if(pic_url.length <= 0){
        popup_show("请上传测试图片");
        return 2;
    }
    r_data["pic_url"] = pic_url;
    r_data["result_explain"] = new Array();
    var exist_explains = $("#result_explain").find("li[name='li_explain']:visible");
    for(var i=0;i<exist_explains.length;i++){
        var explain_item = $(exist_explains[i]);
        var c = explain_item.find("input:eq(0)").val();
        var t = explain_item.find("input:eq(1)").val().trim();
        var score = explain_item.find("input:eq(2)").val().trim();
        if(t.length <=0){
            popup_show("请输入【" + c + "】结果对应的解释");
            return 2;
        }
        if(isSuitableNaN(score, 0, 100) == false){
            popup_show("请确保【" + c + "】结果对应的打分在0-100");
            return 2;
        }
        r_data["result_explain"][i] = {"desc": t, "score": score};
    }
    var add_url = $("#add_url").val();
    my_async_request2(add_url, "POST", r_data, function(data){
        swal({
                title: "选择下一步",
                text: msg,
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: '#DD6B55',
                confirmButtonText: '录入试题',
                cancelButtonText: "留在此页",
                closeOnConfirm: true,
                closeOnCancel: true
            },
            function(isConfirm){
                if (isConfirm){
                    var j_url = AddUrlArg(location.pathname, "exam_no", data["exam_no"]);
                    j_url = AddUrlArg(j_url, "exam_type", data["exam_type"]);
                    location.href = j_url;
                }
            }
        );
    });
}

$(function() {
    $("#exam_type").change(function(){
        var select_m = $("#exam_type option:selected").val();
        var about = parseInt($("#exam_type option:selected").attr("about"));
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
    $("#exam_extend_pic").change(function(){
        var upload_url= $("#upload_url").val();
        if($("#exam_extend_pic")[0].files.length <= 0){
            return 1;
        }
        var data = {"pic": $("#exam_extend_pic")[0].files[0]};
        upload_request(upload_url, "POST", data, function(data){
            $("#exam_extend_pic_url").attr("src", data["pic"]);
        });
    });
    $("#exam_type").change();
    $("#btn_new").click(new_exam);
});