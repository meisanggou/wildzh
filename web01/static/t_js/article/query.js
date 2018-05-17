/**
 * Created by msg on 3/22/17.
 */

function handler_query_article(data) {
    console.info(data);
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
    my_async_request2(r_url, "GET", null, handler_query_article);
    $("#btn_add_article").click(function () {
        window.open($("#page_article").val());
    });
    $("#btn_query").click(function(){
        console.info("query");
        var q_value = $("#query_str").val().trim(" ");
        var div_l = $(".articleList");
        var li_articles = div_l.find("li");
        var li_len = li_articles.length;
        for(var i=0;i<li_len;i++){
            var li_item = $(li_articles[i]);
            li_item.hide();
            if(q_value.length == 0){
                li_item.show();
            }
            else{
                if(li_item.text().indexOf(q_value) >= 0){
                    li_item.show();
                }
            }

        }
    });
    $(function(){
        document.onkeydown = function(e){
            var ev = document.all ? window.event : e;
            if(ev.keyCode==13) {
                $("#btn_query").click();
             }
        }
    });
});