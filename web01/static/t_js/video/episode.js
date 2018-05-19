/**
 * Created by meisa on 2018/5/6.
 */

var exists_episodes = [];
var current_episode_index = 0;
var total_num = 0;


function load_episode(index) {
    if (index < 0) {
        return 1;
    }
    if (index < exists_episodes.length) {
        var item = exists_episodes[index];
        $("#title").val(item["title"]);
        $("#episode_pic").attr("src", item["episode_pic"]);
        $("#episode_url").attr("href", item["episode_url"]);
        $("#episode_url").show();
        $("#current_index").val(item["episode_index"]);

    }
    else {
        $("#current_index").val("上传第" + (exists_episodes.length + 1));
        $("#title").val("");
        $("#episode_pic").attr("src", "");
        $("#episode_url").attr("href", "");
        $("#episode_url").hide();
        $("#btn_upload").text("上传");
        $("#btn_upload").removeAttr("disabled");
        $("#upload_episode").removeAttr("disabled");
        $("#upload_episode").val("");
        $("#upload_episode_pic").val("");
    }
    return 0;
}

function execute_action(action) {
    if (action == "pre") {
        if (current_episode_index <= 0) {
            return 1
        }
        current_episode_index -= 1;
    }
    else if (action == "next") {
        if (current_episode_index >= exists_episodes.length) {
            return 2
        }
        current_episode_index += 1;
    }
    else if (action == "current") {
        if (current_episode_index > exists_episodes.length || current_episode_index < 0) {
            return 3
        }
    }
    else {
        return 4;
    }
    $("#link_pre").hide();
    $("#btn_update").hide();
    $("#btn_new_episode").hide();
    $("#link_next").hide();
    if (current_episode_index > 0) {
        $("#link_pre").show();
    }
    if (current_episode_index == exists_episodes.length) {
        $("#btn_new_episode").show();
    }
    if (current_episode_index < exists_episodes.length) {
        if (current_episode_index < total_num - 1) {
            $("#link_next").show();
        }
        $("#btn_update").show();
    }
    load_episode(current_episode_index);
}


function add_episode() {
    var btn = $(this);
    var btn_text = btn.text();
    var r_data = new Object();
    var title = $("#title").val();
    if (title.length <= 0) {
        popup_show("请输入分集标题");
        return 1;
    }
    r_data["title"] = title;
    var episode_pic = $("#episode_pic").attr("src");
    if (episode_pic.length <= 0) {
        popup_show("请上传分集封面图片");
        return 2;
    }
    r_data["episode_pic"] = episode_pic;
    var episode_url = $("#episode_url").attr("href");
    if (episode_url.length <= 0) {
        popup_show("请上传分集视频");
        return 3;
    }
    r_data["episode_url"] = episode_url;
    var method = "POST";
    if (current_episode_index < exists_episodes.length) {
        method = "PUT"
    }
    r_data["episode_index"] = current_episode_index + 1;
    var url_episode = $("#url_episode").val();
    my_async_request2(url_episode, method, r_data, function (r_d) {
        var data = r_d.data;
        var action = r_d.action;
        if (action == "POST") {
            exists_episodes[exists_episodes.length] = data;
            if (total_num == exists_episodes.length) {
                popup_show("本视频集已录入所有分集");
                current_episode_index = exists_episodes.length - 1;
            }
            else {
                current_episode_index = exists_episodes.length;
                popup_show("录入成功，可继续录入");
            }
            load_episode(current_episode_index);
        }
        else {
            exists_episodes[data.episode_index - 1] = data;
            popup_show("更新成功");
        }
    })
}

function init_info(data) {
    if (data == null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        var video_item = data[0];
        $("#s_video_name").val(video_item["video_name"]);
        $("#s_video_type").val(video_item["video_type"]);
        $("#episode_num").val(video_item["episode_num"]);
        total_num = video_item["episode_num"];
        receive_episodes(null);
    }
}


function receive_episodes(data) {
    if (data == null) {
        var url_episode = $("#url_episode").val();
        my_async_request2(url_episode, "GET", null, receive_episodes);
        return 0;
    }
    exists_episodes = data;

    $("#btn_new_episode").removeAttr("disabled");

    if (total_num == exists_episodes.length) {
        current_episode_index = exists_episodes.length - 1;
    }
    else {
        current_episode_index = exists_episodes.length;
    }
    execute_action("current");
}

$(function () {
    $("#btn_upload").click(function () {
        if ($("#upload_episode")[0].files.length <= 0) {
            popup_show("请选择分集视频");
            return 1;
        }
        $(this).attr("disabled", "disabled");
        $(this).text("上传中");
        $("#episode_url").attr("href", "");
        $("#upload_episode").attr("disabled", "disabled");

        var upload_url = $("#url_upload_e").val();
        var data = {"e": $("#upload_episode")[0].files[0]};
        upload_request(upload_url, "POST", data, function (data) {
            $("#btn_upload").text("已上传");
            $("#episode_url").attr("href", data["e"]);
            $("#episode_url").show();
        });

    });
    $("#upload_episode_pic").change(function () {
        var upload_url = $("#upload_url").val();
        if ($("#upload_episode_pic")[0].files.length <= 0) {
            return 1;
        }
        var data = {"pic": $("#upload_episode_pic")[0].files[0]};
        upload_request(upload_url, "POST", data, function (data) {
            $("#episode_pic").attr("src", data["pic"]);
        });
    });
    if (UrlArgsValue(location.href, "video_no") != null) {
        $("#btn_new_episode").click(add_episode);
        $("#btn_update").click(add_episode);
        init_info(null);
        $("#link_pre").click(function () {
            execute_action("pre");
        });
        $("#link_next").click(function () {
            execute_action("next");
        });
    }
});