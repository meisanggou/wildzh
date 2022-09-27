/**
 * Created by meisa on 2018/5/9.
 */

var e_vm = null;
var video_states = [{'name': '正常'}, {'name': '停用'}];


function init_videos(data) {
    if (data == null) {
        var obj_url = $("#obj_url").val();
        my_async_request2(obj_url, "GET", null, init_videos);
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


function init_exams(data){
    if (data == null) {
        var obj_url = $("#exam_info_url").val();
        my_async_request2(obj_url, "GET", null, init_exams);
        return 0;
    }
    e_vm.all_exams = data;
}


$(function () {
    e_vm =new Vue({
        el: "#div_content",
        data: {
            all_videos: [],
            all_exams: [],
            subjects: [],
            chapters: [],
            video_index: -1,
            exam_index: -1,
            project_index: -1,
            chapter_index: -1,
            video_states: video_states
        },
        methods: {
            select_video: function(index){},
            select_exam: function(index){},
            set_map: function(){},
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
            }
        }
    });
    init_videos(null);
    init_exams(null);
});
