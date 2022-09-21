/**
 * Created by meisa on 2018/5/6.
 */

var q_vm = null;


function popup_waring(head, text){
    $.toast().reset('all');
    $("body").removeAttr('class');
    $.toast({
        heading: head,
        text: text,
        position: 'top-right',
        loaderBg:'#FFBD4A',
        icon: 'error',
        hideAfter: 5500
    });
}
function entry_success(r_d){
    var action = r_d.action;
    var msg = "更新成功";
    if(action == "POST") {
        msg = "录入成功，可继续录入";
        init_info(null);
    }
    $.toast().reset('all');
    $("body").removeAttr('class');
    $.toast({
        heading: '操作成功',
        text: msg,
        position: 'top-right',
        loaderBg:'#FFBD4A',
        icon: 'success',
        hideAfter: 3500,
        stack: 6
      });
}

function add_question()
{
    var btn = $(this);
    var r_data = new Object();
    r_data["question_no"] = parseInt(q_vm.current_question_no);
    var msg = "";
    var question_desc = q_vm.question_desc;
    if(question_desc.length <= 0){
        popup_waring("数据格式有误", "请输入 题目描述");
        return 1;
    }
    msg += "题目描述：";
    msg += question_desc + "\n";
    r_data["select_mode"] = q_vm.select_mode;
    r_data["question_desc"] = question_desc;
    r_data["question_desc_url"] = q_vm.question_desc_url;
    r_data["question_subject"] = q_vm.question_subject;
    r_data["question_source"] = q_vm.question_source;
    r_data['state'] = q_vm.question_state;
    r_data["options"] = new Array();

    var options = q_vm.options;
    var i = 0;
    var c = "";
    var t= "";
    var answer = "";
    msg += "选项：\n";
    for(;i<options.length;i++){
        c = options[i].c;
        t = options[i].desc;
        var score = 0;
        if(options[i].value > 0){
            score = 1;
            answer += c;
        }
        if(t.length <= 0){
            break
        }
        r_data["options"][i] = {"desc": t, "score": score};
        msg += c + ":" + t + "\n";
    }
    for(;i<options.length;i++){
        t = options[i].desc;
        if(t.length != 0){
            popup_waring("缺少选项", "请录入【" + c +"】选项");
            return 2;
        }
    }
    if(r_data["options"].length < 2){
        popup_waring("缺少选项", "请至少录入两个选项！");
        return 2;
    }
    var answer_desc = q_vm.answer;
    r_data["answer"] = answer_desc;
    if(q_vm.select_modes[q_vm.select_mode].multi == true){
        if(answer.length < 2){
            popup_waring("信息不完整", "当前题型请至少选择2个选项作为答案！");
            return 3;
        }
    }
    else{
        if(answer.length != 1){
            popup_waring("信息不完整", "当前请选择且至多选择1个选项作为答案！");
            return 3;
        }
    }
    msg += "答案：" + answer;
    var action = "";
    if(q_vm.action == "new"){
        action = '添加'
    }
    else{
        action = '更新';
    }
    swal({
            title: "是否" + action,
            text: '',//msg,
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: '#DD6B55',
            confirmButtonText: action,
            cancelButtonText: "取消",
            closeOnConfirm: true,
            closeOnCancel: true
        },
        function(isConfirm){
            if (isConfirm){
                var questions_url = $("#questions_url").val() + "?exam_no=" + q_vm.current_exam.exam_no;
                if(q_vm.action == "new") {
                    my_async_request2(questions_url, "POST", r_data, entry_success);
                }
                else{
                    my_async_request2(questions_url, "PUT", r_data, entry_success);
                }
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
        for(var index in data){
            q_vm.all_exams.push(data[index]);
            if(data[index].exam_no == q_vm.current_exam.exam_no){
                q_vm.current_exam_index = index;
                if(q_vm.current_question_no > 0) {
                    q_vm.select_exam(q_vm.current_question_no);
                }
                else{
                    q_vm.select_exam();
                }
            }
        }
    }
}

function receive_questions(data){
    var current_question = data[0];
    q_vm.current_question_no = current_question.question_no;
    q_vm.select_mode = current_question.select_mode;
    q_vm.question_source = current_question.question_source;
    q_vm.question_state = current_question.state;
    q_vm.question_subject = current_question.question_subject;
    q_vm.question_desc = current_question.question_desc;
    if(current_question.question_desc_url == null){
        q_vm.question_desc_url = "";
    }
    else{
        q_vm.question_desc_url = current_question.question_desc_url;
    }
    q_vm.answer = current_question.answer;
    q_vm.action = "update";
    var el = current_question.options.length;
    if(el < 5){
        el = 5;
    }
    var options = get_options(el);
    for(var i= 0,l=current_question.options.length;i<l;i++){
        options[i].desc = current_question.options[i].desc;
        options[i].value = current_question.options[i].score;
    }
    q_vm.options = options;

}

$(function() {
    var video_uuid = UrlArgsValue(location.href, "video_uuid");

    var questions_url = $("#questions_url").val();
    var upload_url= $("#upload_url").val();
    q_vm = new Vue({
        el: "#myTabContent",
        data:{
            video_states: [{'name': '正常'}, {'name': '停用'}],
            video_title: "",
            video_desc: "",
            video_url: "",
            video_state: 0
        },
        methods: {
            change_mode: function(){
            },
            upload_video: function(){
                var u_files = this.$refs.filElem.files;
                if(u_files.length <= 0){
                    return 1;
                }
                console.info(u_files[0]);
                var name = u_files[0].name;
                if(this.video_title.length <= 0){
                    this.video_title = name;
                }
                var data = {"video": u_files[0]};
                //upload_request(upload_url, "POST", data, function(data){
                //    q_vm.video_url = data["video"];
                //});
            },
            remove_video: function(){
                q_vm.video_url = "";
            },
            update_question: function(){
                add_question();
            },
            new_video: function(){
                add_question();
            }
        }
    });
    //init_info(null);
});