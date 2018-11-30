/**
 * Created by meisa on 2018/5/6.
 */

$(function () {
    var vm = new Vue({
        el: "#myTabContent",
        data: {
            exam_no: null,
            exam_name: "",
            exam_desc: "",
            error_tips: {"exam_name": "请输入测试名称", "exam_desc": "请输入测试介绍"}
        },
        methods: {
            add: function () {
                var r_data = new Object();
                r_data["exam_type"] = "tiku";
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
            }
        }
    });

});