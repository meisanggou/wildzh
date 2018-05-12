/**
 * Created by meisa on 2018/5/9.
 */

function init_info(data){
    if(data == null){
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if(data.length > 0) {
        var music_item = data[0];
        $("#music_name").val(music_item["music_name"]);
        $("#music_no").val(music_item["music_no"]);
        select_option("music_type", music_item["music_type"]);
        $("#eval_type").val(music_item["eval_type"]);
        $("#music_desc").val(music_item["music_desc"]);
        $("#music_extend_pic_url").attr("src", music_item["pic_url"]);
        $("#music_url").attr("href", music_item["music_url"]);
    }
}

$(function () {
    init_info(null);
});