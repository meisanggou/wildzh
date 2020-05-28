/**
 * Created by zhouhenglc on 2020/5/28.
 */
$(function () {
    var query_url = $("#query_url").val();
    var vm = new Vue({
        el: "#div_content",
        data: {
            exam_no: null,
            questions_items: [],
            query_str: ""
        },
        methods: {
            query: function () {
                var that = this;
                var data = {'query_str': this.query_str};
                my_async_request2(query_url, 'POST', data, function(data){
                    console.info(data);
                    that.questions_items = data;
                });
            }
        }
    });
})