/**
 * Created by meisa on 2018/5/9.
 */

var e_vm = null;
var video_states = [{'name': '正常'}, {'name': '停用'}];


function init_info(data) {
    if (data == null) {
        var obj_url = $("#obj_url").val();
        my_async_request2(obj_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        console.info(data);
        for (var i = 0; i < data.length; i++) {
            var e_item = data[i];
            e_item["add_time"] = timestamp_2_datetime(e_item["add_time"]);
            e_vm.all_videos.push(e_item);
        }
    }

}


$(function () {
    e_vm =new Vue({
        el: "#div_overview",
        data: {
            all_videos: [],
            video_states: video_states
        },
        methods: {
            delete_exam: function(index){
                var e_item = this.all_exams[index];
                var exam_name = e_item.exam_name;
                var msg = "确定要删除【" + exam_name + "】";
                swal({
                        title: "删除警告",
                        text: msg,
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: '#DD6B55',
                        confirmButtonText: '删除',
                        cancelButtonText: "取消",
                        closeOnConfirm: true,
                        closeOnCancel: true
                    },
                    function (isConfirm) {
                        if (isConfirm) {
                            var r_d = {"exam_no": e_item.exam_no, "exam_type": e_item.exam_type};
                            my_async_request2($("#info_url").val(), "DELETE", r_d, function (data) {
                                location.reload();
                            });
                        }
                    }
                );
            },
            to_action: function(index, action){
                var e_item = this.all_exams[index];
                var basic_url = AddUrlArg(location.pathname, "exam_no", e_item.exam_no);
                //basic_url = AddUrlArg(basic_url, "exam_type", e_item.exam_type);
                var action_url = AddUrlArg(basic_url, "action", action);
                location.href = action_url;
            },
            online: function(index){
                var e_item = this.all_exams[index];
                var msg = "确定上线【" + e_item["exam_name"] + "】\n上线后将不可更改测试内容！";
                swal({
                        title: "上线提醒",
                        text: msg,
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: '#DD6B55',
                        confirmButtonText: '上线',
                        cancelButtonText: "取消",
                        closeOnConfirm: true,
                        closeOnCancel: true
                    },
                    function (isConfirm) {
                        if (isConfirm) {
                            my_async_request2($("#online_url").val(), "POST", e_item, function (data) {
                                location.reload();
                            });
                        }
                    }
                );
            },
            offline: function(index){
                var e_item = this.all_exams[index];
                var msg = "确定下线【" + e_item["exam_name"] + "】\n下线后用户将不可见！";
                swal({
                        title: "下线提醒",
                        text: msg,
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: '#DD6B55',
                        confirmButtonText: '下线',
                        cancelButtonText: "取消",
                        closeOnConfirm: true,
                        closeOnCancel: true
                    },
                    function (isConfirm) {
                        if (isConfirm) {
                            my_async_request2($("#online_url").val(), "DELETE", e_item, function (data) {
                                location.reload();
                            });
                        }
                    }
                );
            },
            sync_search_data: function(index){
                var e_item = this.all_exams[index];
                var msg = "确定同步【" + e_item["exam_name"] + "】\n！";
                swal({
                        title: "同步提醒",
                        text: msg,
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: '#DD6B55',
                        confirmButtonText: '同步',
                        cancelButtonText: "取消",
                        closeOnConfirm: true,
                        closeOnCancel: true
                    },
                    function (isConfirm) {
                        if (isConfirm) {
                            my_async_request2($("#sync_url").val(), "POST", e_item, function (data) {
                                location.reload();
                            });
                        }
                    }
                );
            }
        }
    });
    init_info(null);
});