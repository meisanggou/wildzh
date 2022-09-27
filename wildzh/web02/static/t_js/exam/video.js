/**
 * Created by meisa on 2018/5/6.
 */

var q_vm = null;


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
function entry_success(r_d){
    var action = r_d.action;
    var msg = "更新成功";
    if(action == "POST") {
        msg = "录入成功，可继续录入";
        init_info(null);
    }
    $.toast().reset('all');
    $("body").removeAttr('class');
    $.toast({
        heading: '操作成功',
        text: msg,
        position: 'top-right',
        loaderBg:'#FFBD4A',
        icon: 'success',
        hideAfter: 3500,
        stack: 6
      });
}

function add_video()
{
    var btn = $(this);
    var r_data = new Object();
    var msg = "";
    var video_title = q_vm.video_title;
    if(video_title.length <= 0){
        popup_waring("数据格式有误", "请输入 视频标题");
        return 1;
    }
    r_data['video_title'] = video_title;
    r_data['video_desc'] = q_vm.video_desc;
    if(q_vm.upload_lab.length == 0){
        popup_waring("未选择视频", "请选择一个要上传的视频");
        return 1;
    }
    if(q_vm.video_url.length <= 0){
        popup_waring("视频上传中", "请等待视频上传完成");
        return 1;
    }
    r_data['video_url'] = q_vm.video_url;
    r_data['video_state'] = q_vm.video_state;
    console.info(r_data);
    var obj_url = $("#obj_url").val();
    my_async_request2(obj_url, 'POST', r_data, entry_success);
}

function init_info(data){
    if(data == null){
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if(data.length > 0) {
        for(var index in data){
            q_vm.all_exams.push(data[index]);
            if(data[index].exam_no == q_vm.current_exam.exam_no){
                q_vm.current_exam_index = index;
                if(q_vm.current_question_no > 0) {
                    q_vm.select_exam(q_vm.current_question_no);
                }
                else{
                    q_vm.select_exam();
                }
            }
        }
    }
}

function receive_questions(data){
    var current_question = data[0];
    q_vm.current_question_no = current_question.question_no;
    q_vm.select_mode = current_question.select_mode;
    q_vm.question_source = current_question.question_source;
    q_vm.question_state = current_question.state;
    q_vm.question_subject = current_question.question_subject;
    q_vm.question_desc = current_question.question_desc;
    if(current_question.question_desc_url == null){
        q_vm.question_desc_url = "";
    }
    else{
        q_vm.question_desc_url = current_question.question_desc_url;
    }
    q_vm.answer = current_question.answer;
    q_vm.action = "update";
    var el = current_question.options.length;
    if(el < 5){
        el = 5;
    }
    var options = get_options(el);
    for(var i= 0,l=current_question.options.length;i<l;i++){
        options[i].desc = current_question.options[i].desc;
        options[i].value = current_question.options[i].score;
    }
    q_vm.options = options;

}

$(function() {
    var video_uuid = UrlArgsValue(location.href, "video_uuid");

    var upload_url= $("#upload_url").val();
    q_vm = new Vue({
        el: "#myTabContent",
        data:{
            video_states: [{'name': '正常'}, {'name': '停用'}],
            video_title: "",
            video_desc: "",
            upload_lab: "",
            video_url: "",
            video_state: 0
        },
        methods: {
            upload_video: function(){
                var u_files = this.$refs.filElem.files;
                if(u_files.length <= 0){
                    this.upload_lab = '';
                    this.video_url = '';
                    return 1;
                }
                var name = split(u_files[0].name, '.', 1)[0];
                if(this.video_title.length <= 0){
                    this.video_title = name;
                }
                var data = {"video": u_files[0]};
                this.upload_lab = '视频上传中...';
                upload_request(upload_url, "POST", data, function(data){
                    q_vm.video_url = data["video"];
                    q_vm.upload_lab = '视频上传完成';
                });
            },
            new_video: function(){
                add_video();
            }
        }
    });
    //init_info(null);
});