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
    popup_show('操作成功！');
}


function add_video()
{
    var r_data = new Object();
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
    var obj_url = $("#obj_url").val();
    my_async_request2(obj_url, 'POST', r_data, function(){
        popup_show('操作成功！');
        window.location.reload();
    });
}

function update_video()
{
    var r_data = new Object();
    var video_title = q_vm.video_title;
    if(video_title.length <= 0){
        popup_waring("数据格式有误", "请输入 视频标题");
        return 1;
    }
    r_data['video_title'] = video_title;
    r_data['video_desc'] = q_vm.video_desc;
    r_data['video_state'] = q_vm.video_state;
    var obj_url = $("#obj_url").val() + '/' + q_vm.video_uuid;
    my_async_request2(obj_url, 'PUT', r_data, function(){
        popup_show('操作成功！');
        window.location.reload();
    });
}


function init_info(data){
    if(data == null){
        var info_url = $("#obj_url").val() + '/' + q_vm.video_uuid;
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    var info = data['info'];
    q_vm.video_title_old = info.video_title;
    q_vm.video_title = info.video_title;
    q_vm.video_desc = info.video_desc;
    q_vm.video_state = info.video_state;
    q_vm.video_url = info.video_location;
}


$(function() {
    var video_uuid = UrlArgsValue(location.href, "video_uuid");
    var upload_url= $("#upload_url").val();
    q_vm = new Vue({
        el: "#myTabContent",
        data:{
            video_uuid: video_uuid,
            video_states: [{'name': '正常'}, {'name': '停用'}],
            video_title_old: "",
            video_title: "",
            video_desc: "",
            upload_lab: "",
            video_url: "",
            video_state: 0
        },
        methods: {
            replace_video: function(){
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
            },
            update_video: function(){
                update_video();
            }
        }
    });
    if(video_uuid != null) {
        init_info(null);
    }
});
