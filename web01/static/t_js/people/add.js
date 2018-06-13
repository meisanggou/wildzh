/**
 * Created by meisa on 2018/5/15.
 */

function new_people(){
    var r_data = new Object();
    var keys = ["people_name", "degree", "company", "department", "domain", "labels", "star_level", "people_photo"];
    for(var i=0;i<keys.length;i++){
        var v = g_n_vm.p_item[keys[i]];
        if(v.length <= 0){
            return 1;
        }
        r_data[keys[i]] = v;
    }

    var info_url = $("#info_url").val();
    if(g_n_vm.p_item.people_no.length != 32) {
        if(g_n_vm.group_id != ""){
            r_data["group_id"] = g_n_vm.group_id;
        }
        my_async_request2(info_url, "POST", r_data, function (data) {
            var msg = "成功添加" + data["people_name"];
            swal({
                    title: "选择下一步",
                    text: msg,
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: '#DD6B55',
                    confirmButtonText: '录入详细信息',
                    cancelButtonText: "留在此页",
                    closeOnConfirm: true,
                    closeOnCancel: true
                },
                function (isConfirm) {
                    if (isConfirm) {
                        var basic_url = location.pathname;
                        var j_url = AddUrlArg(basic_url, "people_no", data["people_no"]);
                        j_url = AddUrlArg(j_url, "action", "detail");
                        j_url = AddUrlArg(j_url, "people_name", data["people_name"]);
                        j_url = AddUrlArg(j_url, "group_id", g_n_vm.group_id);
                        location.href = j_url;
                    }
                    else {
                        g_n_vm.p_item = data;
                        g_n_vm.action_new = false;
                    }
                }
            );
        });
    }
    else{
        my_async_request2(info_url, "PUT", r_data, function (data){
            popup_show("更新成功");
        });
    }
}

$(function() {
    var group_id = UrlArgsValue(location.search, "group_id");
    if(group_id == null){
        group_id = "";
    }
    g_n_vm = new Vue({
        el: "#div_add",
        data: {
            group_id: group_id,
            p_item: {"people_name": "", "degree": "", "company": "", "department": "", "domain": "",
                "labels": "", "star_level": "", "people_no": "", "people_photo": ""},
            submit_count: 0,
            action_new: true
        },
        methods: {
            upload_photo: function(){
                var upload_url= $("#upload_url").val();
                if($("#people_extend_pic")[0].files.length <= 0){
                    return 1;
                }
                var data = {"pic": $("#people_extend_pic")[0].files[0]};
                upload_request(upload_url, "POST", data, function(data){
                    g_n_vm.p_item.people_photo =  data["pic"];
                });
            },
            action_submit: function(){
                this.submit_count += 1;
                new_people();
            },
            to_detail: function(){
                var detail_href = location.pathname + "?action=detail&people_no=" + this.p_item.people_no;
                detail_href += "&people_name=" + this.p_item.people_name + "&group_id=" + this.group_id;
                location.href = detail_href;
            }
        }

    });
    var people_no = UrlArgsValue(location.search, "people_no");
    if(people_no != null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, function(data){
            g_n_vm.p_item = data[0];
            g_n_vm.action_new = false;
            $("#li_add").show();
            var t = $("#li_update a").text();
            $("#li_update a").text(t.replace("添加", "更新"));

        });
    }
    else{
        $("#li_add").hide();
    }
});