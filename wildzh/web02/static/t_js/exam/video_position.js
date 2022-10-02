/**
 * Created by meisa on 2022/10/1.
 */

var e_vm = null;
var video_states = [{'name': '正常'}, {'name': '停用'}];


function init_exams(data){
    if (data == null) {
        var obj_url = $("#exam_info_url").val();
        my_async_request2(obj_url, "GET", null, init_exams);
        return 0;
    }
    var l = data.length;
    for(var i=0;i<l;i++){
        var exam = data[i];
        e_vm.all_exams.push(exam);
    }
}


function get_maps_result(data) {
    var exam = e_vm.all_exams[e_vm.exam_index];
    var all_videos = [];
    for(var i=0;i<data.length;i++){
        var map = data[i];
        if(map.exam_no != exam.exam_no){
            return false;
        }
        var s_map = " - " ;
        if(map.video_subject != null){
            if(map.video_subject < 0 || !('subjects' in exam)|| map.video_subject>=exam.subjects.length){
                s_map += map.video_subject + ' [未识别！！]'
            }
            else{
                s_map+= exam.subjects[map.video_subject].name;
            }
        }
        if(map.video_chapter != null){
            s_map += ' - ' + map.video_chapter;
        }
        map['map_desc'] = s_map;
        all_videos.push(map);
    }
    e_vm.all_videos = all_videos;
}


$(function () {
    var map_url = $("#map_url").val();
    e_vm =new Vue({
        el: "#div_content",
        data: {
            all_exams: [],
            exam_index: -1,
            all_videos: [],
            video_states: video_states
        },
        methods: {
            select_exam: function(){
                if(this.exam_index < 0|| this.exam_index >= this.all_exams.length){
                    return false;
                }
                var exam_no = this.all_exams[this.exam_index].exam_no;
                my_async_request2(map_url, 'GET', {'exam_no': exam_no}, get_maps_result);
            },
            change_position: function(org_index, new_index){
                if(new_index < 0){
                    console.info('已是最顶部');
                    return false;
                }
                if(new_index >= this.all_videos.length){
                    console.info('已是最低部');
                    return false;
                }
                var v1 = this.all_videos[org_index];
                var v2 = this.all_videos[new_index];
                if(new_index > org_index){
                    // 下移
                    this.all_videos.splice(org_index, 2, v2, v1);
                }
                else{
                    // 上移
                    this.all_videos.splice(new_index, 2, v1, v2);
                }

            },
            get_changed: function(){
                var ml = this.all_videos.length;
                var items = [];
                for(var i=0;i<ml;i++){
                    var v = this.all_videos[i];
                    if(v.position != i){
                        items.push({'video_uuid': v.video_uuid, 'exam_no': v.exam_no, 'position': i})
                    }
                }
                console.info(items);
                return items;
            },
            set_position: function(){
                var items = this.get_changed();
                if(items.length <= 0){
                    popup_show('无需调整！');
                    return false;
                }
                for(var j=0;j<items.length;j++){
                    my_async_request2(map_url, 'PUT', items[j], function(data){});
                }
                popup_show('已发送更新请求');
            }
        }
    });
    init_exams(null);
});