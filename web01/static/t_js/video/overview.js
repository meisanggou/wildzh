/**
 * Created by meisa on 2018/5/9.
 */

var cn_video_type = {"dongman": "动漫", "yingshi": "影视"};

function delete_video() {
    var current_td = $(this).parent();
    var current_tr = current_td.parent();
    var tr_id = current_tr.attr("id");
    var video_type = current_tr.find("td:eq(0)").text();
    var video_name = current_tr.find("td:eq(1)").text();
    var msg = "确定要删除【" + video_type + "】【" + video_name + "】";
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
                var ks = tr_id.split("|");
                var r_d = {"video_no": ks[1], "video_type": ks[0]};
                my_async_request2($("#info_url").val(), "DELETE", r_d, function (data) {
                    location.reload();
                });
            }
        }
    );
}

function explain_status(s) {
    if ((s & 128) != 0) {
        return "已下线"
    }
    if ((s & 2) == 0) {
        return "缺少视频";
    }
    if ((s & 4) == 0) {
        return "缺少结果解释";
    }
    if ((s & 64) != 0) {
        return "已上线"
    }
    return "待上线"
}

function init_info(data) {
    if (data == null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        var t = $("#t_videos");
        for (var i = 0; i < data.length; i++) {
            var add_tr = $("<tr></tr>");
            add_tr.attr("id", data[i]["video_type"] + "|" + data[i]["video_no"]);
            var td_t = new_td(data[i]["video_type"], cn_video_type);
            add_tr.append(td_t);

            var td_name = new_td("video_name", data[i]);
            add_tr.append(td_name);

            var td_no = new_td("insert_time", data[i], null, null, timestamp_2_datetime);
            add_tr.append(td_no);

            var td_upload = $("<td></td>");
            td_upload.text(data[i]["upload_num"] + "/" + data[i]["episode_num"]);
            add_tr.append(td_upload);

            var td_status = new_td("status", data[i], null, null, explain_status);
            add_tr.append(td_status);

            var td_op = $("<td></td>");
            var del_link = $("<a href='javascript:void(0)'>删除</a>");
            del_link.click(delete_video);
            td_op.append(del_link);
            if ((data[i]["status"] & 64) == 0) {
                td_op.append(" | ");
                var basic_url = AddUrlArg(location.pathname, "video_no", data[i]["video_no"]);
                basic_url = AddUrlArg(basic_url, "video_type", data[i]["video_type"]);
                var question_url = AddUrlArg(basic_url, "action", "question");
                td_op.append(new_link("管理视频", question_url));

                td_op.append(" | ");
                var update_url = AddUrlArg(basic_url, "action", "video");
                td_op.append(new_link("更新信息", update_url));
            }
            if (data[i]["status"] == 7) {
                var data_item = data[i];
                td_op.append(" | ");
                var online_link = $("<a href='javascript:void(0)'>上线</a>");
                var msg = "确定上线【" + data[i]["video_name"] + "】\n上线后将不可更改测试内容！";
                online_link.click(function () {
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
                                my_async_request2($("#online_url").val(), "POST", data_item, function (data) {
                                    location.reload();
                                });
                            }
                        }
                    );
                });
                td_op.append(online_link);
            }
            add_tr.append(td_op);

            t.append(add_tr);
        }
    }
}

$(function () {
    init_info(null);
});