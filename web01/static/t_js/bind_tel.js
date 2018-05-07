/**
 * Created by msg on 7/6/16.
 */

var allow_check = true;
var wait_time = 60;
var send_freq = 0;
var now_d = "0_1";
var send_tel = null;

function get_date_(){
    var now_date = new Date();
    return now_date.getMonth() + "_" + now_date.getDate();
}

function format_num(id){
    var v = $("#" + id).val();
    v = v.replace(/[^\d]/g, "");
    $("#" + id).val(v);
    return v;
}

function check_tel(){
    if(allow_check == false){
        return false;
    }
    var mobile = /^1(3|4|5|8|7)\d{9}$/;
    var tel = format_num("tel");
    if(mobile.test(tel)){
        $("#send_code").removeAttr("disabled");
        return true;
    }
    else{
        $("#send_code").attr("disabled","disabled");
        return false;
    }
}

function set_wait_time(){
    $("#send_code").text(wait_time + "s后重发");
    if(wait_time <= 0){
        $("#send_code").text("获取验证码");
        allow_check = true;
    }
    else{
        wait_time --;
        setTimeout(set_wait_time, 1000);
    }
}

function send_code_success(data){
    send_freq++;
    localStorage.setItem(now_d, "" + send_freq);
    allow_check = false;
    send_tel = data.data.tel;
}

function send_code(){
    if(send_freq >= 5){
        sweetAlert("您的发送频率过于频繁，请稍后重试");
        $("#send_code").attr("disabled","disabled");
        allow_check = false;
        return false;
    }
    wait_time = 60;
    set_wait_time();
    if(check_tel() == false){
        sweetAlert("请输入正确的手机号码");
        wait_time = 0;
        return false;
    }
    $("#send_code").attr("disabled","disabled");
    var request_data = new Object();
    request_data["bind_token"] = $("input[name='bind_token']").val();
    request_data["tel"] = $("#tel").val();
    var request_url = location.href;
    console.info(request_data);
    my_async_request(request_url, "PUT", request_data, send_code_success);
}

function bind_tel_success(data){
    location.href = "/";
}

function bind_tel(){
    if(send_tel != $("#tel").val()){
        sweetAlert("请先获取验证码");
        return false;
    }
    var code = $("#code").val();
    if(code.length != 6){
        sweetAlert("验证码应该是6的数字");
        return false;
    }
    var request_url = location.href;
    var request_data = new Object();
    request_data["bind_token"] = $("input[name='bind_token']").val();
    request_data["tel"] = $("#tel").val();
    request_data["code"] = code;
    my_async_request(request_url, "POST", request_data, bind_tel_success);
}

$(function() {
    setInterval(check_tel, 1000);
    $("#tel").keyup(check_tel);
    $("#send_code").click(send_code);
    $("button[name='btn_bind']").click(bind_tel);
    $("#code").keyup(function() {
        format_num(this.id);
    });
    now_d = get_date_();
    var local_freq = localStorage.getItem(now_d);
    if(local_freq != null){
        send_freq = parseInt(local_freq);
        if(send_freq == NaN){
            send_freq = 0;
        }
    }
    console.info(send_freq);
});