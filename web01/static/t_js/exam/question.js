/**
 * Created by meisa on 2018/5/6.
 */

function add_question()
{
    var r_data = new Object();
    var msg = "";
    var question_desc = $("#question_desc").val().trim();
    if(question_desc.length <= 0){
        popup_show("请录入题目描述");
        return 1;
    }
    msg += "题目描述：";
    msg += question_desc + "\n";
    var select_mode = $("#select_mode").val();
    r_data["question_desc"] = question_desc;
    r_data["select_mode"] = select_mode;
    r_data["options"] = new Array();
    var options = $("#options li[name='li_option']");
    var i = 0;
    var c = "";
    var t= "";
    msg += "选项：\n";
    for(;i<options.length;i++){
        var option_item = $(options[i]);
        c = option_item.find("input:eq(0)").val();
        t = option_item.find("input:eq(1)").val().trim();
        if(t.length <= 0){
            break
        }
        r_data["options"][i] = t;
        msg += c + ":" + t + "\n";
    }
    for(;i<options.length;i++){
        var option_item = $(options[i]);
        t = option_item.find("input:eq(1)").val().trim();
        if(t.length != 0){
            popup_show("请录入【" + c +"】选项");
            return 2;
        }
    }
    if(r_data["options"].length < 2){
        popup_show("请至少录入两个选项！");
            return 2;
    }
    swal({
                title: "是否录入",
                text: msg,
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: '#DD6B55',
                confirmButtonText: '录入',
                cancelButtonText: "取消",
                closeOnConfirm: true,
                closeOnCancel: true
            },
            function(isConfirm){
                if (isConfirm){
                    console.info("录入")
                }
            }
        );
}

function init_info(data){
    if(data == null){
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    console.info(data);
}

$(function() {
    $("#btn_new_question").click(add_question);
    init_info(null);
});