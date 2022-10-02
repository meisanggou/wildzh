/**
 * Created by meisa on 2018/5/9.
 */

var e_vm = null;
var video_states = [{'name': '正常'}, {'name': '停用'}];
var exam_id_dict = {};

function popup_waring(head, text){
    $.toast().reset('all');
    $("body").removeAttr('class');
    $.toast({
        heading: head,
        text: text,
        position: 'top-right',
        loaderBg:'#FFBD4A',
        icon: 'error',
        hideAfter: 5500
    });
}

function init_videos(data) {
    if (data == null) {
        var obj_url = $("#obj_url").val();
        my_async_request2(obj_url, "GET", null, init_videos);
        return 0;
    }
    if (data.length > 0) {
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
    var l = data.length;
    var not_s = {'name': '--不选择--'};
    for(var i=0;i<l;i++){
        var exam = data[i];
        if(!('subjects' in exam)){
            exam['subjects'] = [];
        }
        var sl = exam['subjects'].length;
        for(var j=0;j<sl;j++){
            if(!('chapters' in exam['subjects'][j])){
                exam['subjects'][j]['chapters'] = [];
            }
            exam['subjects'][j]['chapters'].push(not_s);
        }
        exam_id_dict[exam.exam_no] = exam;
        exam['subjects'].push(not_s);
        e_vm.all_exams.push(exam);
    }
}


var no_exam = {'name': '--请选择题库--'};
var no_subject = {'name': '--请选择科目--'};


function set_map_result(data){
    $.toast().reset('all');
    $("body").removeAttr('class');
    $.toast({
        heading: '',
        text: '操作成功',
        position: 'top-right',
        loaderBg:'#FFBD4A',
        icon: 'success',
        hideAfter: 3500,
        stack: 6
      });
    e_vm.select_video();
}

function get_maps_result(data){
    if(e_vm.video_index < 0 || e_vm.video_index >= e_vm.all_videos.length)
    {
        return false;
    }
    var video_uuid = e_vm.all_videos[e_vm.video_index].video_uuid;
    var dl = data.length;
    var maps = [];
    for(var i=0;i<dl;i++){
        var map = data[i];
        if(map.video_uuid != video_uuid){
            var msg = str_format('User select video uuid is %s, now is %s, skipped', [video_uuid, map.video_uuid]);
            console.warn(msg);
            continue;
        }
        if(!(map.exam_no in exam_id_dict)){
            var msg = str_format('Not found exam_no %s', map.exam_no);
            console.warn(msg);
            continue;
        }
        var exam = exam_id_dict[map.exam_no];
        var s_map = exam.exam_name;
        if(map.video_subject != null){
            s_map += ' - ';
            if(map.video_subject < 0|| map.video_subject>=exam.subjects.length){
                s_map += map.video_subject + ' [未识别！！]'
            }
            else{
                s_map+= exam.subjects[map.video_subject].name;
            }
        }
        if(map.video_chapter != null){
            s_map += ' - ' + map.video_chapter;
        }
        map['updating'] = false;
        map['desc'] = s_map;
        maps.push(map);
    }
    e_vm.maps = maps;
    e_vm.detect_updating();
}


$(function () {
    var map_url = $("#map_url").val();
    e_vm =new Vue({
        el: "#div_content",
        data: {
            all_videos: [],
            maps: [],
            all_exams: [],
            subjects: [no_exam],
            chapters: [no_subject],
            video_index: -1,
            exam_index: -1,
            subject_index: -1,
            chapter_index: -1,
            action: 'new',
            video_states: video_states
        },
        methods: {
            select_video: function(){
                this.maps = [];
                if(this.video_index < 0 || this.video_index >= this.all_videos.length){
                    return false;
                }
                var video_uuid = this.all_videos[this.video_index].video_uuid;
                my_async_request2(map_url, 'GET', {'video_uuid': video_uuid}, get_maps_result);
            },
            select_exam: function(){
                var exam = this.all_exams[this.exam_index];
                var subjects = exam['subjects'];
                this.subject_index = -1;
                this.subjects = subjects;
                this.chapter_index = -1;
                this.chapters = [no_subject];
                this.detect_updating();
            },
            select_subject: function(){
                if(this.subject_index <0 || this.subject_index >= this.subjects.length-1){
                    this.chapters = [no_subject];
                    this.chapter_index = -1;
                    return;
                }
                this.chapters = this.subjects[this.subject_index]['chapters'];
            },
            prepare_update: function(map){
                console.info(map);
                var exam_index = -1;
                for(var i=0;i<this.all_exams.length;i++){
                    if(this.all_exams[i].exam_no == map.exam_no){
                        exam_index = i;
                        break
                    }
                }
                if(exam_index == -1){
                    return false;
                }
                var exam = this.all_exams[exam_index];
                var subject_index = -1;
                if(map.video_subject != null && map.video_subject>=0 && map.video_subject<exam['subjects'].length){
                    subject_index = map.video_subject
                }
                var chapter_index = -1;
                if(subject_index != -1 && map.video_chapter != null){
                    var subject = exam['subjects'][subject_index];
                    for(var j=0;j<subject.chapters.length;j++){
                        if(subject.chapters[j].name == map.video_chapter){
                            chapter_index = j;
                            break;
                        }
                    }
                }
                this.exam_index = exam_index;
                this.select_exam();
                this.subject_index = subject_index;
                this.select_subject();
                this.chapter_index = chapter_index;

            },
            detect_updating: function(){
                if(this.maps.length <= 0){
                    return false;
                }
                if(this.exam_index < 0){
                    return false;
                }
                var exam = this.all_exams[this.exam_index];

                var ml = this.maps.length;
                this.action = 'new';
                for(var i=0;i<ml;i++){
                    if(this.maps[i].exam_no == exam.exam_no){
                        this.maps[i].updating = true;
                        this.action = 'update';
                    }
                    else{
                        this.maps[i].updating = false;
                    }
                }
            },
            set_map: function(){
                if(this.video_index < 0|| this.video_index >= this.all_videos.length){
                    popup_waring("未选择视频", "请选择一个视频");
                    return false;
                }
                if(this.exam_index < 0|| this.exam_index >= this.all_exams.length){
                    popup_waring("未选择题库", "请选择一个题库");
                    return false;
                }
                var data = {'video_uuid': this.all_videos[this.video_index].video_uuid,
                             'exam_no': this.all_exams[this.exam_index].exam_no,
                             'video_subject': null,
                             'video_chapter': null};
                if(this.subject_index >=0 && this.subject_index < this.subjects.length-1){
                    // subjects最后一个元素是 不选择， 也要排除掉
                    data['video_subject'] = this.subject_index;
                }
                if(this.chapter_index >= 0 && this.chapter_index < this.chapters.length-1){
                    // chapters最后一个元素是 不选择， 也要排除掉
                    data['video_chapter'] = this.chapters[this.chapter_index].name;
                }
                var method = 'POST';
                if(this.action != 'new'){
                    method = 'PUT';
                }
                my_async_request2(map_url, method, data, set_map_result);
            },
            delete_map: function(map){
                var v_name = this.all_videos[this.video_index].video_title;
                var msg = str_format('确定移除视频【%s】和题库【%s】关联关系？', [v_name, map.desc]);
                swal({
                        title: "删除关联",
                        text: msg,
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: '#DD6B55',
                        confirmButtonText: '确定解除',
                        cancelButtonText: "取消",
                        closeOnConfirm: true,
                        closeOnCancel: true
                    },
                    function (isConfirm) {
                        if (isConfirm) {
                            var r_d = {"exam_no": map.exam_no, "video_uuid": map.video_uuid};
                            my_async_request2(map_url, "DELETE", r_d, set_map_result);
                        }
                    }
                );
            }
        }
    });
    init_videos(null);
    init_exams(null);
});
