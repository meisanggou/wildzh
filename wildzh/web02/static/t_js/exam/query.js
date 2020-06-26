/**
 * Created by zhouhenglc on 2020/5/28.
 */
var exam_name_mapping = {};
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
                    that.questions_items.splice(0, that.questions_items.length);
                    for(var i=0;i<data.length;i++){
                        var item = data[i];
                        if(item.exam_no in exam_name_mapping){
                            item['exam_name'] = exam_name_mapping[item.exam_no];
                        }
                        else{
                            item['exam_name'] = item.exam_no;
                        }
                        that.questions_items.push(item);
                    }
                });
            },
            to_question: function(index){
                var q_item = this.questions_items[index];
                var page_question_url = $("#page_question_url").val();
                console.info(page_question_url);
                var url = page_question_url + "?exam_no=" + q_item['exam_no'] + '&question_no=' + q_item['question_no']
                location.href = url;
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