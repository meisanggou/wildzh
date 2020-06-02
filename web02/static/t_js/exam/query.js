/**
 * Created by zhouhenglc on 2020/5/28.
 */
$(function () {
    var query_url = $("#query_url").val();
    var vm = new Vue({
        el: "#div_content",
        data: {
            all_exams: [],
            current_exam_index: 0,
            exam_no: null,
            questions_items: [],
            query_str: ""
        },
        methods: {
            query: function () {
                var that = this;
                var exam_no = this.all_exams[this.current_exam_index].exam_no;
                var data = {'query_str': this.query_str, 'exam_no': exam_no};
                my_async_request2(query_url, 'POST', data, function(data){
                    console.info(data);
                    that.questions_items = data;
                });
            }
        }
    });
    var info_url = $("#info_url").val();
    my_async_request2(info_url, "GET", null, function(data){
        for(var index in data){
            vm.all_exams.push(data[index]);
            //if(data[index].exam_no == q_vm.current_exam.exam_no){
            //    q_vm.current_exam_index = index;
            //    q_vm.select_exam();
            //}
        }
    });
});