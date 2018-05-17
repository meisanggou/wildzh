/**
 * Created by meisa on 2018/5/9.
 */

var cn_doctor_type = {"diantai": "电台", "fangsong": "放松"};

function delete_doctor() {
    var current_td = $(this).parent();
    var current_tr = current_td.parent();
    var tr_id = current_tr.attr("id");
    var doctor_type = current_tr.find("td:eq(0)").text();
    var doctor_name = current_tr.find("td:eq(1)").text();
    var msg = "确定要删除【" + doctor_type + "】【" + doctor_name + "】";
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
                var r_d = {"doctor_no": ks[1], "doctor_type": ks[0]};
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
    if ((s & 64) != 0) {
        return "已上线"
    }
    if ((s & 2) == 0) {
        return "缺详细信息"
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
        var keys = ["doctor_name", "degree", "company", "department"];
        var t = $("#t_doctors");
        for (var i = 0; i < data.length; i++) {
            var add_tr = $("<tr></tr>");
            add_tr.attr("id", data[i]["doctor_no"]);

            for(var j=0;j<keys.length;j++){
                var td_t = new_td(keys[j], data[i]);
                add_tr.append(td_t);
            }

            var td_status = new_td("status", data[i], null, null, explain_status);
            add_tr.append(td_status);

            var td_op = $("<td></td>");
            var basic_url = AddUrlArg(location.pathname, "doctor_no", data[i]["doctor_no"]);
            var detail_url = AddUrlArg(basic_url, "action", "update");
            td_op.append(new_link("查看", detail_url));

            td_op.append(" | ");
            var del_link = $("<a href='javascript:void(0)'>删除</a>");
            del_link.click(delete_doctor);
            td_op.append(del_link);

            if (data[i]["status"] == 3) {
                var data_item = data[i];
                td_op.append(" | ");
                var online_link = $("<a href='javascript:void(0)'>上线</a>");
                var msg = "确定上线医生【" + data[i]["doctor_name"] + "】\n上线后将不可更改信息！";
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