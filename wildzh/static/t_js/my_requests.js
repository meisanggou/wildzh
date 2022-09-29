/**
 * Created by msg on 5/21/16.
 */

function request_error(xhr){
    var res = "状态码：" + xhr.status + "\n";
    res += "返回值：" + xhr.statusText + "";
    console.info(res);
    console.info(xhr);
    if(xhr.status === 301 || xhr.status === 302){
        swal({
                title: xhr.responseText,
                text: "是否重新登录",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: '#DD6B55',
                confirmButtonText: '重新登录',
                cancelButtonText: "取消",
                closeOnConfirm: true,
                closeOnCancel: true
            },
            function(isConfirm){
                if (isConfirm){
                    location.reload(true);
                }
            }
        );
    }
    else{
        sweetAlert(xhr.statusText);
    }
}

function my_request(request_url, request_method, body_param, request_success){
    if(request_method != "GET"){
        body_param = JSON.stringify(body_param)
    }
    $.ajax({
        url: request_url,
        method: request_method,
        contentType: "application/json",
        dataType: "json",
        data: body_param,
        async:false,
        success:function(data){
            console.info(data);
            if(data.status == false){
                sweetAlert(data.data);
            }
            else if("location" in data){
                location.href = data.location;
            }
            else if(request_success == null){
                sweetAlert(data.data);
            }
            else{
                request_success(data);
            }
        },
        error:request_error
    });
}

function my_async_request(request_url, request_method, body_param, request_success){
    if(request_method != "GET"){
        body_param = JSON.stringify(body_param)
    }
    $.ajax({
        url: request_url,
        method: request_method,
        contentType: "application/json",
        dataType: "json",
        data: body_param,
        success:function(data){
            if(data.status == false){
                sweetAlert(data.data);
            }
            else if("location" in data){
                location.href = data.location;
            }
            else if(request_success == null){
                sweetAlert(data.data);
            }
            else{
                request_success(data);
            }
        },
        error:request_error
    });
}

function my_async_request2(request_url, request_method, body_param, request_success, exec_obj){
    // 异步请求
    if (request_url.indexOf("/?") > 0) {
        request_url += "&rf=async";
    }
    else {
        request_url += "?rf=async";
    }
    if(request_method != "GET"){
        body_param = JSON.stringify(body_param)
    }
    $.ajax({
        url: request_url,
        method: request_method,
        contentType: "application/json",
        dataType: "json",
        data: body_param,
        headers: {"rf": "async"},
        success:function(data){
            if(exec_obj != null) {
                if ("exec_r" in exec_obj) {
                    exec_obj.exec_r = true;
                }
                if ("exec_completed" in exec_obj) {
                    exec_obj.exec_completed = true;
                }
                if ("exec_ing" in exec_obj) {
                    exec_obj.exec_ing = false;
                }
            }
            if(data.status == false){
                sweetAlert(data.data);
            }
            else if("location" in data){
                location.href = data.location;
            }
            else if(request_success == null){
                sweetAlert(data.data);
            }
            else if("data" in data){
                request_success(data.data);
            }
            else{
                request_success(data);
            }
        },
        error:function(xhr){
            if(exec_obj != null) {
                if ("exec_r" in exec_obj) {
                    exec_obj.exec_r = false;
                }
                if ("exec_completed" in exec_obj) {
                    exec_obj.exec_completed = true;
                }
                if ("exec_ing" in exec_obj) {
                    exec_obj.exec_ing = false;
                }
            }
            request_error(xhr);
        }
    });
}

function upload_request(request_url, request_method, body_param, request_success, exec_obj)
{
    if (request_url.indexOf("/?") > 0) {
        request_url += "&rf=async";
    }
    else {
        request_url += "?rf=async";
    }
    var fd = new FormData();
    for(var key in body_param){
        fd.append(key, body_param[key]);
    }
    $.ajax({
        url: request_url,
        method: request_method,
        contentType: false,
        processData: false,
        dataType: "json",
        data: fd,
        success:function(data){
            if(exec_obj != null) {
                if ("exec_r" in exec_obj) {
                    exec_obj.exec_r = true;
                }
                if ("exec_completed" in exec_obj) {
                    exec_obj.exec_completed = true;
                }
                if ("exec_ing" in exec_obj) {
                    exec_obj.exec_ing = false;
                }
            }
            if(data.status == false){
                sweetAlert(data.data);
            }
            else if("location" in data){
                location.href = data.location;
            }
            else if(request_success == null){
                sweetAlert(data.data);
            }
            else{
                request_success(data.data);
            }
        },
        error:function(xhr){
            if(exec_obj != null) {
                if ("exec_r" in exec_obj) {
                    exec_obj.exec_r = false;
                }
                if ("exec_completed" in exec_obj) {
                    exec_obj.exec_completed = true;
                }
                if ("exec_ing" in exec_obj) {
                    exec_obj.exec_ing = false;
                }
            }
            request_error(xhr);
        }
    });
}