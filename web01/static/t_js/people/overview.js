/**
 * Created by meisa on 2018/5/9.
 */

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

$(function () {
    g_p_vm = new Vue({
        el: "#div_overview",
        data: {
            group_id: "",
            p_items: []
        },
        methods: {
            look_p: function(index){

            },
            delete_p: function(index){
                var p_item = this.p_items[index];
                var name = p_item.people_name;
                var degree = p_item.degree;
                var msg = "确定要删除【" + degree + "】【" + name + "】";
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
                            var r_d = {"people_no": p_item.people_no};
                            my_async_request2($("#info_url").val(), "DELETE", r_d, function (data) {
                                location.reload();
                            });
                        }
                    }
                );
            },
            online_p: function(index){
                var p_item = this.p_items[index];
                var name = p_item.people_name;
                var msg = "确定上线【" + name + "】\n上线后将不可更改信息！";
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
                            var r_d = {"people_no": p_item.people_no};
                            my_async_request2($("#online_url").val(), "POST", r_d, function (data) {
                                location.reload();
                            });
                        }
                    }
                );
            }
        }
    });
    var info_url = $("#info_url").val();
    my_async_request2(info_url, "GET", null, function(data){

        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            item.cn_status = explain_status(item.status);
            var basic_url = AddUrlArg(location.pathname, "people_no", data[i]["people_no"]);
            var detail_url = AddUrlArg(basic_url, "action", "update");
            item.detail_url = detail_url;
            g_p_vm.p_items.push(item);
        }
    });
    //init_info(null);
});