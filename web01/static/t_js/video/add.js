/**
 * Created by meisa on 2018/5/6.
 */

var ascii = ["A", "B", "C", "D", "E", "F"];
var p_vm = null;

function init_info(data) {
    if (data == null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        var video_item = data[0];
        p_vm.media_item = video_item;
        $("#btn_new").text("更新");
        $("#li_add").show();
        var link_update = $("#li_update a");
        link_update.text(link_update.text().replace("添加", "更新"));
    }
}

function request_video(method, r_data) {
    var msg = "新建成功";
    if(method == "PUT"){
        msg = "更新成功";
    }
    var info_url = $("#info_url").val();
    my_async_request2(info_url, method, r_data, function (data) {
        if(method == "PUT"){
            popup_show(msg);
            if("upload_num" in data){
                $("#lab_upload_num").text(data["upload_num"]);
            }
        }
        else {
            p_vm.media_item = data;
            p_vm.action_new = false;
            if(data["link_people"] != null) {
                var resource_data = {"people_no": data["link_people"]};
                resource_data["resource_id"] = "005" + data["video_no"];
                var url_resource = $("#url_people_resource").val();
                my_async_request2(url_resource, "POST", resource_data, function (data) {
                    console.info(data)
                });
            }
            swal({
                    title: "选择下一步",
                    text: msg,
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: '#DD6B55',
                    confirmButtonText: '上传分集视频',
                    cancelButtonText: "留在此页",
                    closeOnConfirm: true,
                    closeOnCancel: true
                },
                function (isConfirm) {
                    if (isConfirm) {
                        var j_url = AddUrlArg(location.pathname, "video_no", data["video_no"]);
                        j_url = AddUrlArg(j_url, "video_type", data["video_type"]);
                        location.href = j_url;
                    }
                    else {
                        $("#video_type").attr("disabled", "disabled");
                        $("#video_no").val(data["video_no"]);
                        $("#btn_new").text("更新");
                    }
                }
            );
        }
    });
}
function new_or_update_video() {
    var r_data = new Object();
    var keys = ["video_type", "video_name", "video_desc", "video_pic"];
    for (var i = 0; i < keys.length; i++) {
        if (p_vm.media_item[keys[i]].length <= 0) {
            return 1;
        }
        r_data[keys[i]] = p_vm.media_item[keys[i]];
    }
    var episode_num = p_vm.media_item.episode_num;
    if (isSuitableNaN(episode_num, 0, 10000) == false) {
        return 2;
    }
    r_data["episode_num"] = episode_num;
    r_data['accept_formats'] = p_vm.type_info[p_vm.media_item.video_type].format;
    if(p_vm.media_item.link_people!=null&&p_vm.media_item.link_people.length == 32&&p_vm.can_link_people){
        r_data["link_people"] = p_vm.media_item.link_people;
    }

    var video_no = p_vm.media_item.video_no;
    var method = "POST";
    if (video_no.length == 32) {
        method = "PUT";
        r_data["video_no"] = video_no;
    }
    if (p_vm.media_item.upload_num.length > 0) {
        var upload_num = p_vm.media_item.upload_num;
        if (r_data["episode_num"] < upload_num) {
            r_data["upload_num"] = r_data["episode_num"];
            var msg = "更新后总集数【" + r_data["episode_num"] + "】小于已上传集数【" + upload_num + "】，多上传的将会删除！";
            swal({
                    title: "更新确认",
                    text: msg,
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: '#DD6B55',
                    confirmButtonText: '确定更新',
                    cancelButtonText: "再看看",
                    closeOnConfirm: true,
                    closeOnCancel: true
                },
                function (isConfirm) {
                    if (isConfirm) {
                        request_video(method, r_data);
                    }
                }
            );
            return 4;
        }
    }
    request_video(method, r_data);
}

$(function () {
    $("#li_add").hide();
    var media_item = {"link_people": "0", "episode_num": "", "action_new": true, "video_name": "",
        "video_type": "", "video_desc": "", "video_pic": "", "video_no": "", "upload_num": ""};
    if (UrlArgsValue(location.href, "video_no") != null) {
        init_info(null);
    }
    p_vm = new Vue({
        el:"#myTabContent",
        data:{
            people: [],
            all_people: {},
            can_link_people: false,
            given_type: false,  //是否指定了煤体类型 指定后不可更改
            video_type: "",
            media_item: media_item,
            submit_count: 0,
            type_info: {}
        },
        methods:{
            start_upload: function(){
                var upload_url = $("#upload_url").val();
                if ($("#video_extend_pic")[0].files.length <= 0) {
                    return 1;
                }
                var data = {"pic": $("#video_extend_pic")[0].files[0]};
                upload_request(upload_url, "POST", data, function (data) {
                    p_vm.media_item.video_pic = data["pic"];
                });
            },
            new_media: function () {
                this.submit_count += 1;
                console.info(this.submit_count);
                new_or_update_video();
            }
        },
        watch: {
            video_type: function (value, old_value) {
                this.media_item.video_type = value;
                if(value.length <= 0){
                    this.can_link_people = false;
                    return;
                }
                if(!value in this.type_info){
                    this.can_link_people = false;
                    return;
                }
                if(this.type_info[value].p_group.length <= 0){
                    this.can_link_people = false;
                    return;
                }
                else{
                    this.can_link_people = true;
                }
                var p_group = this.type_info[value].p_group;
                if(p_group in this.all_people){
                    this.people = this.all_people[p_group];
                    console.info("use exist")
                }
                else{

                    console.info("request new");
                    my_async_request2($("#url_people").val(), "GET", {"group_id": p_group}, function(data){
                            p_vm.people = data;
                            p_vm.all_people[p_group] = data;
                    });
                    console.info(p_group);
                }
            }
        }
    });
    my_async_request2("/video/type/info/", "GET", null, function(data){
        var video_type = UrlArgsValue(location.search, "video_type");
        if(video_type in data) {
            p_vm.given_type = true;
            p_vm.video_type = video_type;
            p_vm.type_info = data;
        }
    });
});