/**
 * Created by meisa on 2020/5/4.
 */

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

$(function () {
    var exam_no = UrlArgsValue(location.href, "exam_no");
    if(exam_no != null) {
        exam_no = parseInt(exam_no);
    }
    q_vm = new Vue({
        el: "#div_content",
        data: {
            all_exams: [],
            current_exam_index: -1,
            current_exam: {question_num: 0, exam_no: exam_no},
            select_modes: [],
            strategy_pattern: []
        },
        methods: {
            select_exam: function () {
                this.current_exam = this.all_exams[this.current_exam_index];
                this.select_modes = this.current_exam["select_modes"];
            },
            add_mode: function () {
                this.strategy_pattern.push({'value': -1, 'num': ''});
            },
            remove_mode: function(index){
                this.strategy_pattern.splice(index, 1);
            },
            update: function(){
                console.info(this.strategy_pattern);
            }
        }
    });
    init_info(null);
});