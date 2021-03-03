/**
 * Created by meisa on 2018/5/6.
 */
var ad_vm = null;

function init_info(data) {
    if (data == null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        ad_vm.all_exams = [];
        for (var index in data) {
            ad_vm.all_exams.push(data[index]);
        }
    }
}

$(function () {
    var data_url = $("#data_url").val();
    ad_vm = new Vue({
        el: "#myTabContent",
        data: {
            all_exams: [],
            current_exam_index: -1,
            ad_desc: "",
            ignore_interval: 0,
            enabled: 0
        },
        methods: {
            select_exam: function () {
                var exam = this.all_exams[this.current_exam_index];
                var args = {'exam_no': exam.exam_no};
                my_async_request2(data_url, 'GET', args, function (data) {
                    console.info(data);
                    ad_vm.ad_desc = data.ad_desc;
                    ad_vm.ignore_interval = data.ignore_interval;
                    if (data.enabled) {
                        ad_vm.enabled = 1
                    }
                    else {
                        ad_vm.enabled = 0;
                    }
                })
            },
            update: function () {
                if (this.current_exam_index < 0) {
                    popup_show('请先选择一个题库！');
                    return false;
                }
                var exam = this.all_exams[this.current_exam_index];
                var body = {'exam_no': exam.exam_no, 'ad_desc': this.ad_desc,
                    'ignore_interval': this.ignore_interval, 'enabled': this.enabled};
                my_async_request2(data_url, 'PUT', body, function (data) {
                    popup_show('更新成功！');
                });
            }
        }
    });
    init_info();
});