/**
 * Created by meisa on 2018/5/9.
 */

var e_vm = null;
var map_url = null;
var video_states = [{'name': '正常'}, {'name': '停用'}];


function get_maps(video_uuid){
    my_async_request2(map_url, 'GET', {'video_uuid': video_uuid}, function(data){
        e_vm.video_maps[video_uuid].maps = data.length;
    });
}

function init_info(data) {
    if (data == null) {
        var obj_url = $("#obj_url").val();
        my_async_request2(obj_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        for (var i = 0; i < data.length; i++) {
            var e_item = data[i];
            e_item["add_time"] = timestamp_2_datetime(e_item["add_time"]);
            e_item['maps'] = -1;
            e_vm.all_videos.push(e_item);
            e_vm.video_maps[e_item.video_uuid] = e_item;
            get_maps(e_item.video_uuid);
        }
    }

}


$(function () {
    map_url = $("#map_url").val();
    var map_page = $("#map_page").val();
    var upload_page = $("#upload_page").val();
    e_vm =new Vue({
        el: "#div_overview",
        data: {
            all_videos: [],
            video_maps: {},
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
            to_update: function(video_uuid){
                var action_url = AddUrlArg(upload_page, "video_uuid", video_uuid);
                location.href = action_url;
            },
            to_map: function(video_uuid){
                var url = map_page + '?video_uuid=' + video_uuid;
                location.href = url;
            }
        }
    });
    init_info(null);
});