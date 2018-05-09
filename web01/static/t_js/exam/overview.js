/**
 * Created by meisa on 2018/5/9.
 */

var cn_exam_type = {"xlcp1": "专业测评", "xlcp2": "兴趣测评"};

function explain_status(s) {
    if ((s & 128) != 0) {
        return "已下线"
    }
    if ((s & 2) == 0) {
        return "缺少试题";
    }
    if ((s & 4) == 0) {
        return "缺少结果解释";
    }
    if ((s & 8) != 0) {
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
        var t = $("#t_exams");
        for (var i = 0; i < data.length; i++) {
            var add_tr = $("<tr></tr>");

            var td_t = new_td(data[i]["exam_type"], cn_exam_type);
            add_tr.append(td_t);

            var td_name = new_td("exam_name", data[i]);
            add_tr.append(td_name);

            var td_no = new_td("exam_no", data[i], null, null, timestamp_2_datetime);
            add_tr.append(td_no);

            var td_status = new_td("status", data[i], null, null, explain_status);
            add_tr.append(td_status);

            var td_op = $("<td></td>");
            td_op.append(new_link("删除", "#"));
            if ((data[i]["status"] & 8) == 0) {
                td_op.append(" | ");
                var question_url = AddUrlArg(location.pathname, "exam_no", data[i]["exam_no"]);
                question_url = AddUrlArg(question_url, "exam_type", data[i]["exam_type"]);
                question_url = AddUrlArg(question_url, "action", "question");
                td_op.append(new_link("管理试题", question_url));
            }
            if (data[i]["status"] == 7) {
                var data_item = data[i];
                td_op.append(" | ");
                var online_link = $("<a href='javascript:void(0)'>上线</a>");
                var msg = "确定上线【" + data[i]["exam_name"] + "】\n上线后将不可更改测试内容！";
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
                                my_async_request2($("#online_url").val(), "POST", data_item, function(data){
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