/**
 * Created by msg on 3/22/17.
 */

cn_article_type = {"meiwen": "美文", "xlts": "心理调适"};

function delete_article() {
    var current_td = $(this).parent();
    var current_tr = current_td.parent();
    var tr_id = current_tr.attr("id");
    var article_type_s = current_tr.find("td:eq(0)").text();
    var article_type = current_tr.find("td:eq(0)").attr("name").substr(3);
    var title = current_tr.find("td:eq(1)").text();
    var msg = "确定要删除【" + article_type_s + "】【" + title + "】";
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
                var r_d = {"article_no": tr_id, "article_type": article_type};
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
    return "待上线"
}

function fill_table(data) {
    var keys = ["title", "author"];
    var t = $("#t_article");
    if(data.length == 0){
        $("#tr_none").show();
    }
    for (var i = 0; i < data.length; i++) {
        var add_tr = $("<tr></tr>");
        add_tr.attr("id", data[i]["article_no"]);

        var td_type = new_td(data[i]["article_type"], cn_article_type);
        add_tr.append(td_type);

        for (var j = 0; j < keys.length; j++) {
            var td_t = new_td(keys[j], data[i]);
            add_tr.append(td_t);
        }
        var td_status = new_td("status", data[i], null, null, explain_status);
        add_tr.append(td_status);

        var td_op = $("<td></td>");
        var basic_url = AddUrlArg(location.pathname, "article_no", data[i]["article_no"]);

        var del_link = $("<a href='javascript:void(0)'>删除</a>");
        del_link.click(delete_article);
        td_op.append(del_link);

        if (data[i]["status"] == 1) {
            td_op.append(" | ");
            var detail_url = AddUrlArg(basic_url, "action", "article");
            detail_url = AddUrlArg(detail_url, "article_type", data[i]["article_type"]);
            td_op.append(new_link("更新", detail_url));

            td_op.append(" | ");
            var online_link = $("<a href='javascript:void(0)'>上线</a>");
            var data_item = data[i];
            online_link.click(function () {
                var current_td = $(this).parent();
                var current_tr = current_td.parent();
                var tr_id = current_tr.attr("id");
                var article_type_s = current_tr.find("td:eq(0)").text();
                var article_type = current_tr.find("td:eq(0)").attr("name").substr(3);
                var title = current_tr.find("td:eq(1)").text();
                var msg = "确定上线文章【" + article_type_s + "】【" + title + "】\n上线后将不可更改信息！";
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
                            var r_d = {"article_no": tr_id, "article_type": article_type};
                            my_async_request2($("#online_url").val(), "POST", r_d, function (data) {
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

function handler_query_article(data) {
    var article_count = data.length;
    //article_count = 0;
    if (article_count <= 0) {
        var no_article_div = $('<div class="paddingTop50 text-center">暂无文章显示 </div>');
        var add_link = $("<a>添加文章</a>");
        add_link.attr("href", $("#page_article").val());
        no_article_div.append(add_link);
        $("#article_container").append(no_article_div);
    }
    else {
        fill_table(data);
        var article_list = $('<div class="articleList"></>');
        var current_user_name = "";
        if ($("#current_user_name").length > 0) {
            current_user_name = $("#current_user_name").val();
        }
        for (var i = 0; i < article_count; i++) {
            var article_item = data[i];
            var article_li = $("<li></li>");
            var title_p = $('<p><a href="javascript:void(0)" target="_blank">' + article_item["title"] + '</a></p>');
            title_p.find("a").attr("href", location.pathname + "?action=look&article_no=" + article_item["article_no"]);
            article_li.append(title_p);
            var abstract_p = $('<p></p>');
            abstract_p.text(article_item["abstract"]);
            article_li.append(abstract_p);
            var time_p = $('<p></p>');
            var time_text = timestamp_2_datetime(article_item["update_time"]) + "&nbsp;&nbsp;&nbsp;&nbsp;[ 作者：" + article_item["adder"] + " ]";
            time_p.html(time_text);
            if (current_user_name == article_item["adder"]) {
                var update_a = $("<a>编辑</a>");
                update_a.attr("href", $("#page_article").val() + "&article_no=" + article_item["article_no"]);
                time_p.append($(update_a));
            }
            article_li.append(time_p);
            article_list.append(article_li);
        }
        $("#article_container").append(article_list);
    }
}

$(document).ready(function () {

    var r_url = $("#query_url").val();
    my_async_request2(r_url, "GET", null, fill_table);
    $("#btn_add_article").click(function () {
        window.open($("#page_article").val());
    });
    $("#btn_query").click(function () {
        console.info("query");
        var q_value = $("#query_str").val().trim(" ");
        var div_l = $(".articleList");
        var li_articles = div_l.find("li");
        var li_len = li_articles.length;
        for (var i = 0; i < li_len; i++) {
            var li_item = $(li_articles[i]);
            li_item.hide();
            if (q_value.length == 0) {
                li_item.show();
            }
            else {
                if (li_item.text().indexOf(q_value) >= 0) {
                    li_item.show();
                }
            }

        }
    });
    $(function () {
        document.onkeydown = function (e) {
            var ev = document.all ? window.event : e;
            if (ev.keyCode == 13) {
                $("#btn_query").click();
            }
        }
    });
});