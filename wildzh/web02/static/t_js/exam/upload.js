/**
 * Created by zhouhenglc on 2020/5/28.
 */
var exam_name_mapping = {};
$(function () {
    var query_url = $("#query_url").val();
    var file_url = $("#file_url").val();
    var vm = new Vue({
        el: "#div_content",
        data: {
            all_exams: [],
            current_exam_index: 0,
            exam_no: null,
            query_str: "",
            option_mapping: ["A", "B", "C", "D"],
            docx_file: null,
            answer_docx_file: null,
            has_answer: false,
            questions_items: [],
            error_question: [],
            error_msg: ''
        },
        methods: {
            file_change: function () {
                var u_files = this.$refs.fileElem.files;
                if(u_files.length <= 0){
                    return 1;
                }
                this.docx_file = u_files[0];
            },
            answer_file_change: function(){
                var u_files = this.$refs.answerFileElem.files;
                if(u_files.length <= 0){
                    return 1;
                }
                this.answer_docx_file = u_files[0];
            },
            upload: function(){
                if(this.docx_file == null){
                    popup_show('请先选择题目文件');
                    return false;
                }
                this.questions_items = [];
                var a_file = this.docx_file;
                var data = {"q_file": a_file};
                if(this.has_answer){
                    if(this.answer_docx_file == null){
                        popup_show('请选择答案文件');
                        return false;
                    }
                    data['answer_file'] = this.answer_docx_file;
                }
                var that = this;
                //swal.showLoading();
                upload_request(file_url, "POST", data, function(data){
                    that.questions_items = data.q_list;
                    that.error_question = data.error_question;
                    that.error_msg = data.error_msg;
                });
            }
        }
    });
    var info_url = $("#info_url").val();
    my_async_request2(info_url, "GET", null, function(data){
        for(var index in data){
            exam_name_mapping[data[index].exam_no] = data[index].exam_name;
            vm.all_exams.push(data[index]);
            //if(data[index].exam_no == q_vm.current_exam.exam_no){
            //    q_vm.current_exam_index = index;
            //    q_vm.select_exam();
            //}
        }
    });
});