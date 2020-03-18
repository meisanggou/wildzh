/**
 * Created by meisa on 2018/5/6.
 */

$(function () {
    var select_modes = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题"];
    var default_subject = {'name': '', 'select_modes': [], 'chapters': [], 'enable': true};
    for(var i=0;i<select_modes.length;i++){
        default_subject.select_modes.push({'name': select_modes[i], 'enable': true})
    }
    console.info(default_subject);
    var vm = new Vue({
        el: "#myTabContent",
        data: {
            exam_no: null,
            exam_name: "",
            exam_desc: "",
            openness_level: "private",
            open_mode: 1,
            open_no_start: '',
            open_no_end: '',
            exam_subjects: [],
            new_chapter: '',
            error_tips: {"exam_name": "请输入测试名称", "exam_desc": "请输入测试介绍"}
        },
        methods: {
            add_subject: function(){
                this.exam_subjects.push(default_subject);
            },
            add_chapter: function(index){
                this.exam_subjects[index]['chapters'].push(this.new_chapter);
                this.new_chapter = '';
            },
            add: function () {
                var r_data = new Object();
                var keys = ["exam_name", "exam_desc"];
                for (var i = 0; i < keys.length; i++) {
                    var item = this[keys[i]];
                    var v = item.trim();
                    if (v.length <= 0) {
                        var msg = this.error_tips[keys[i]];
                        popup_show(msg);
                        return 1;
                    }
                    r_data[keys[i]] = v;
                }
                var add_url = $("#add_url").val();
                my_async_request2(add_url, "POST", r_data, function (data) {
                    swal({
                            title: "选择下一步",
                            text: msg,
                            type: "warning",
                            showCancelButton: true,
                            confirmButtonColor: '#DD6B55',
                            confirmButtonText: '录入试题',
                            cancelButtonText: "留在此页",
                            closeOnConfirm: true,
                            closeOnCancel: true
                        },
                        function (isConfirm) {
                            if (isConfirm) {
                                var j_url = AddUrlArg(location.pathname, "exam_no", data["exam_no"]);
                                j_url = AddUrlArg(j_url, "exam_type", data["exam_type"]);
                                location.href = j_url;
                            }
                        }
                    );
                });
            },
            update: function(){
                var r_data = new Object();
                var keys = ["exam_no", "exam_name", "exam_desc", 'openness_level', 'open_mode', 'open_no_start',  'open_no_end'];
                for (var i = 0; i < keys.length; i++) {
                    r_data[keys[i]] = this[keys[i]];
                }
                var exam_subjects = [];
                for(var j=0;j<this.exam_subjects.length;j++){
                    var s_item = this.exam_subjects[j];
                    if(s_item.name.length == 0){
                        popup_show('每个科目都需要设置名称');
                        return false;
                    }
                }
                var info_url = $("#info_url").val();
                my_async_request2(info_url, "PUT", r_data, function (data){
                    popup_show("更新成功");
                });
            }
        }
    });
    var exam_no = UrlArgsValue(location.href, 'exam_no');
    if(exam_no != null){
        var info_url = $("#info_url").val();
        my_async_request2(info_url, 'GET', null, function(data){
            if(data.length == 1){
                var exam_item = data[0];
                vm.exam_no = exam_item.exam_no;
                vm.exam_name = exam_item.exam_name;
                vm.exam_desc = exam_item.exam_desc;
                var keys = ['openness_level', 'open_mode', 'open_no_start',  'open_no_end'];
                for (var i = 0; i < keys.length; i++) {
                    if(keys[i] in exam_item) {
                        vm[keys[i]] = exam_item[keys[i]];
                    }
                }
            }
        })

    }
});