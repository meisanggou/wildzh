/**
 * Created by meisa on 2018/5/6.
 */

var exists_questions = [];
var question_no = 1;
var current_question = 0;

function load_question(index)
{
    if(index < 0){
        return 1;
    }
    if(index < exists_questions.length){
        var item = exists_questions[index];
        $("#question_desc").val(item["question_desc"]);
        $("#select_mode").val(item["select_mode"]);
        var options = $("#options li[name='li_option']");
        var i = 0;
        for(i=0;i<options.length&&i<item["options"].length;i++){
            var option_item = $(options[i]);
            option_item.find("input:eq(1)").val(item["options"][i]);
        }
        for(;i<options.length;i++){
            option_item.find("input:eq(1)").val("");
        }
    }
    else{
        $("#question_desc").val("");
        $("#options li[name='li_option']").find("input:eq(1)").val("");
    }
    return 0;
}

function execute_action(action)
{
    if(action == "pre"){
        if(current_question <= 0){
            return 1
        }
        current_question -= 1;
    }
    else if(action == "next"){
        if(current_question >= exists_questions.length){
            return 2
        }
        current_question += 1;
    }
    else if(action == "current"){
        if(current_question > exists_questions.length || current_question < 0){
            return 3
        }
    }
    else{
        return 4;
    }
    $("#link_pre").hide();
    $("#btn_update").hide();
    $("#btn_new_question").hide();
    $("#link_next").hide();
    if(current_question > 0){
        $("#link_pre").show();
    }
    if(current_question == exists_questions.length){
        $("#btn_new_question").show();
    }
    if(current_question < exists_questions.length){
        $("#link_next").show();
        $("#btn_update").show();
    }
    load_question(current_question);
}

function entry_success(r_d){
    var data= r_d.data;
    var action = data.action;
    if(action == "POST") {
        exists_questions[exists_questions.length] = data;
        if(question_no <= data.question_no){
            question_no = data.question_no + 1;
        }
        popup_show("录入成功，可继续录入");
        current_question = exists_questions.length;
        load_question(current_question);
        $("#questions_num").val(exists_questions.length);
    }
    else{
        popup_show("更新成功");
    }
}

function add_question()
{
    var r_data = new Object();
    r_data["question_no"] = exists_questions.length + 1;
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
                var questions_url = $("#questions_url").val();
                my_async_request2(questions_url, "POST", r_data, entry_success);
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
    if(data.length > 0) {
        var exam_item = data[0];
        $("#s_exam_name").val(exam_item["exam_name"]);
        $("#s_exam_type").val(exam_item["exam_type"]);
    }
}

function receive_questions(data){
    if(data == null){
        var questions_url = $("#questions_url").val();
        my_async_request2(questions_url, "GET", null, receive_questions);
        return 0;
    }
    exists_questions = data;
    for(var i;i<exists_questions.length;i++){
        if(question_no <= exists_questions[i].question_no){
            question_no = exists_questions[i].question_no + 1;
        }
    }
    $("#questions_num").val(exists_questions.length);
    $("#btn_new_question").removeAttr("disabled");
    current_question = exists_questions.length;
    execute_action("current");
}

$(function() {
    if(UrlArgsValue(location.href, "exam_no") != null) {
        $("#btn_new_question").click(add_question);
        init_info(null);
        receive_questions(null);
        $("#link_pre").click(function(){
           execute_action("pre");
        });
        $("#link_next").click(function(){
           execute_action("next");
        });
    }
});