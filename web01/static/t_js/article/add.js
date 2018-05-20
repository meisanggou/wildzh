/**
 * Created by msg on 3/21/17.
 */

function handler(data) {
    if ("article_no" in data) {
        $("#article_no").val(data.article_no);
        set_look_link();
    }
    if ("content" in data && "title" in data) {
        $("#article_type").val(data.article_type);
        $("#article_type").attr("disabled", "disabled");
        $("#author").val(data.author);
        $("#article_title").val(data.title);
        $("#article_desc").val(data.article_desc);
        $("#pic_url").attr("src", data.pic_url);
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
        var article_type = UrlArgsValue(location.href, "article_type");
        console.info(article_type);
        var article_no = $("#article_no").val();
        if (article_no.length == 32 && article_type != null) {
            var r_url = $("#url_info").val();
            my_async_request2(r_url, "GET", {"article_type": article_type, "article_no": article_no}, handler);
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
        var article_desc = $("#article_desc").val();
        var author = $("#author").val();
        var pic_url = $("#pic_url").attr("src");
        var article_no = $("#article_no").val();
        var article_type = $("#article_type").val();
        var method = "POST";
        var r_data = {"content": content, "abstract": abstract, "title": title, "article_desc": article_desc,
            "pic_url": pic_url, "author": author, "article_type": article_type};
        if (article_no.length == 32) {
            r_data["article_no"] = article_no;
            method = "PUT";
        }
        var r_url = location.href;
        my_async_request2(r_url, method, r_data, handler);
        $("#auto").val("1");
    });
    set_look_link();
    $("#upload_article_pic").change(function(){
        var upload_url= $("#upload_url").val();
        if($("#upload_article_pic")[0].files.length <= 0){
            return 1;
        }
        var data = {"pic": $("#upload_article_pic")[0].files[0]};
        upload_request(upload_url, "POST", data, function(data){
            $("#pic_url").attr("src", data["pic"]);
        });
    });
});