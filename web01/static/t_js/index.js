/**
 * Created by msg on 10/20/16.
 */


$(function(){
    var current_user_role = parseInt($("#current_user_role").val());
    if(current_user_role > 0) {
    }
    $("#div_main_menu").append('<a href="' + '/exam/">' + '测试管理' + '</a>');
    $("#div_main_menu").append('<a href="' + '/music/">' + '音乐管理' + '</a>');
    $("#div_main_menu").append('<a href="' + '/article/">' + '文章管理' + '</a>');
    $("#div_main_menu").append('<a href="' + '/user/password' + '/">' + '修改密码' + '</a>');
    $("#div_main_menu").append('<a href="' + '/user/login' + '/">' + '退出' + '</a>');
});