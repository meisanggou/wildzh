/**
 * Created by msg on 3/21/17.
 */

function handler(data) {
    if ("article_no" in data) {
        $("#article_no").val(data.article_no);
        set_look_link();
    }
    if ("content" in data && "title" in data) {
        $("#article_title").val(data.title);
        ue.setContent(data.content);
    }
    else {
        alert1("保存成功");
    }
}

function save_article() {
    var auto = $("#auto").val();
    if (auto != 1) {
        return;
    }
    var title = $("#article_title").val();
    var content = ue.getContent();
    var abstract = ue.getContentTxt().substr(0, 400);
    var article_no = $("#article_no").val();
    var method = "POST";
    var r_data = {"content": content, "abstract": abstract, "title": title, "auto": true};
    if (article_no.length == 32) {
        r_data["article_no"] = article_no;
        method = "PUT";
        var r_url = location.href;
        my_async_request2(r_url, method, r_data, handler);
    }
}

function set_look_link()
{
    var article_no = $("#article_no").val();
    if (article_no.length == 32) {
        $("#link_look").show();
        var look_url = location.origin + location.pathname + "?&action=look&article_no=" + article_no;
        $("#link_look").attr("href", look_url);
    }
    else{
        $("#link_look").hide();
    }
}

$(document).ready(function () {
    ue = UE.getEditor('container');
    ue.ready(function () {
        var article_no = $("#article_no").val();
        if (article_no.length == 32) {
            var r_url = location.href;
            my_async_request2(r_url, "GET", null, handler);
        }
    });
    window.setInterval(save_article, 60000);
    $("#btn_save").click(function () {
        var title = $("#article_title").val();
        if (title.length < 3) {
            alert1("标题不可少于3个字符");
            return;
        }
        var content = ue.getContent();
        var abstract = ue.getContentTxt().substr(0, 400);
        var article_no = $("#article_no").val();
        var method = "POST";
        var r_data = {"content": content, "abstract": abstract, "title": title};
        if (article_no.length == 32) {
            r_data["article_no"] = article_no;
            method = "PUT";
        }
        var r_url = location.href;
        my_async_request2(r_url, method, r_data, handler);
        $("#auto").val("1");
    });
    set_look_link();
});