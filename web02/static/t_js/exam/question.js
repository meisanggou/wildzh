/**
 * Created by meisa on 2018/5/6.
 */

var q_vm = null;

function entry_success(r_d){
    var data= r_d.data;
    var action = r_d.action;
    if(action == "POST") {
        popup_show("录入成功，可继续录入");
        init_info(null);
    }
    else{
        popup_show("更新成功");
    }
}

function add_question()
{
    var btn = $(this);
    var btn_text = btn.text();
    var r_data = new Object();
    r_data["question_no"] = parseInt(q_vm.current_question_no);
    var msg = "";
    var question_desc = q_vm.question_desc;
    if(question_desc.length <= 0){
        $.toast().reset('all');
        $("body").removeAttr('class');
        $.toast({
           heading: '数据格式有误',
            text: '请输入 题目描述',
            position: 'top-right',
            loaderBg:'#FFBD4A',
            icon: 'warning',
            hideAfter: 3500,
            stack: 6
        });
        return 1;
    }
    msg += "题目描述：";
    msg += question_desc + "\n";
    r_data["question_desc"] = question_desc;
    r_data["options"] = new Array();
    var chars_o = ["A", "B", "C", "D"];
    var options = [q_vm.option_a, q_vm.option_b, q_vm.option_c, q_vm.option_d];
    var selected_option = q_vm.selected_option;
    var i = 0;
    var c = "";
    var t= "";
    var answer = "";
    msg += "选项：\n";
    for(;i<options.length;i++){
        c = chars_o[i];
        t = options[i];
        var score = 0;
        if(selected_option == i){
            score = 1;
            answer = c;
        }
        if(t.length <= 0){
            break
        }
        r_data["options"][i] = {"desc": t, "score": score};
        msg += c + ":" + t + "\n";
    }
    for(;i<options.length;i++){
        t = options[i];
        if(t.length != 0){
            popup_show("请录入【" + c +"】选项");
            return 2;
        }
    }
    if(r_data["options"].length < 2){
        popup_show("请至少录入两个选项！");
        return 2;
    }
    var answer_desc = q_vm.answer;
    r_data["answer"] = answer_desc;
    if(answer == ""){
        popup_show("请选择一个选项作为答案！");
        return 3;
    }
    msg += "答案：" + answer;
    swal({
            title: "是否" + btn_text,
            text: msg,
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: '#DD6B55',
            confirmButtonText: btn_text,
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
        q_vm.all_exams = [];
        for(var index in data){
            q_vm.all_exams.push(data[index]);
            if(data[index].exam_no == q_vm.current_exam.exam_no){
                q_vm.current_exam_index = index;
                q_vm.select_exam();
            }
        }
    }
}

function receive_questions(data){
    var current_question = data[0];
    q_vm.current_question_no = current_question.question_no;
    q_vm.question_desc = current_question.question_desc;
    q_vm.answer = current_question.answer;
    q_vm.action = "update";
    q_vm.option_a = current_question.options[0]["desc"];
    q_vm.option_b = current_question.options[1]["desc"];
    if(current_question.options.length >= 4){
        q_vm.option_c = current_question.options[2]["desc"];
        q_vm.option_d = current_question.options[3]["desc"];
    }
    else if(current_question.options.length >= 3){
        q_vm.option_c = current_question.options[2]["desc"];
    }
    for(var index in current_question.options){
        if(parseInt(current_question.options[index]["score"]) > 0){
            q_vm.selected_option = index;
            break;
        }
    }
}

$(function() {
    var exam_no = UrlArgsValue(location.href, "exam_no");
    if(exam_no != null) {
        exam_no = parseInt(exam_no);
    }
    var questions_url = $("#questions_url").val();
    q_vm = new Vue({
        el: "#myTabContent",
        data:{
            all_exams: [],
            current_exam_index: -1,
            current_exam: {question_num: 0, exam_no: exam_no},
            action: "new",
            current_question_no: 0,
            question_desc: "",
            answer: "",
            option_a: "",
            option_b: "",
            option_c: "",
            option_d: "",
            selected_option: -1
        },
        methods: {
            select_exam: function(){
                this.current_exam =this.all_exams[this.current_exam_index];
                this.current_question_no = this.current_exam.question_num;
                this.action_next();
            },
            action_pre: function(){
                var c_qno = this.current_question_no;
                if(c_qno <= 1){
                    return false;
                }
                var data = {"exam_no": this.current_exam.exam_no, "start_no": c_qno - 1, "num": 1, "desc": "true"};
                my_async_request2(questions_url, "GET", data, receive_questions);
            },
            action_next: function(){
                var c_qno = this.current_question_no;
                if(c_qno >= this.current_exam.question_num){
                    this.current_question_no = this.current_exam.question_num + 1;
                    this.question_desc = "";
                    this.answer = "";
                    this.action = "new";
                    this.option_a = this.option_b = this.option_c = this.option_d = "";
                    this.selected_option = -1;
                    return true;
                }
                var data = {"exam_no": this.current_exam.exam_no, "start_no": c_qno + 1, "num": 1};
                my_async_request2(questions_url, "GET", data, receive_questions);
            },
            update_question: function(){
                add_question();
            },
            new_question: function(){
                add_question();
            }
        }
    });
    init_info(null);
});