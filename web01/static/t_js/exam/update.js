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
        var exam_item = data[0];
        $("#exam_name").val(exam_item["exam_name"]);
        $("#exam_type").val(exam_item["exam_type"]);
        $("#exam_desc").val(exam_item["exam_desc"]);
        $("#exam_extend_pic_url").attr("src", exam_item["pic_url"]);
    }
}

$(function () {
    init_info(null);
});