/**
 * Created by msg on 3/21/17.
 */


$(document).ready(function () {
    ue = UE.getEditor('container');
    $("#btn_save_all_html").click(function () {
        DownloadFile("demo_all_html.txt", ue.getAllHtml());
    });
    $("#btn_save_content").click(function () {
        DownloadFile("demo_content_html.txt", ue.getContent());
    });
    $("#btn_save_content_text").click(function () {
        DownloadFile("demo_content_text.txt", ue.getContentTxt());
    });
    $("#btn_save_plain_text").click(function () {
        DownloadFile("demo_plain_text.txt", ue.getPlainTxt());
    });
});