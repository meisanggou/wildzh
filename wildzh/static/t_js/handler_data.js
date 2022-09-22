/**
 * Created by msg on 10/27/16.
 */

function bit_and(role1, role2) {
    var v = role1 & role2;
    if (v < role1 && v < role2)
        return false;
    else
        return true;
}

function escape(s) {
    return s.replace(/[<>&"]/g, function (c) {
        return {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}[c];
    });
}

function rTrim(str, c) {
    var s_len = str.length;
    for (var i = s_len - 1; i >= 0; i--) {
        if (str[i] != c) {
            return str.substr(0, i + 1);
        }
    }
    return "";
}
function lTrim(str, c) {
    var s_len = str.length;
    for (var i = 0; i < s_len; i++) {
        if (str[i] != c) {
            return str.substr(i, s_len - i);
        }
    }
    return "";
}

function format_json_str(s) {
    try {
        var obj = JSON.parse(s);
    }
    catch (e) {
        return s;
    }
    return JSON.stringify(obj, null, 4);
}

function format_num(s) {
    return s.replace(/[^\d]/g, "");
}


function replace_url(content) {
    var reg = /https?:\/\/(\w|=|\?|\.|\/|\&|-)+/ig;
    content = content.replace(reg, function ($url) {
        return "<a href='" + $url + "' target='_blank'> " + $url + " </a>";
    });
    return content;
}

function isSuitableNaN(num, min_allow, max_allow){
    var i_num = parseFloat(num);
    if(isNaN(i_num)){
        return false;
    }
    if(min_allow != null){
        if(i_num < min_allow){
            return false;
        }
    }
    if(max_allow != null){
        if(i_num > max_allow){
            return false;
        }
    }
    return true;
}


function split(s, sep, num){
    var arr = s.split(sep);
    if(num == null || num <=0){
        return arr;
    }
    if(num >= arr.length - 1){
        return  arr;
    }
    var n_arr = new Array();
    var i=0;
    for(;i<num;i++){
        n_arr.push(arr[i]);
    }
    var _w = "";
    for(;i<arr.length - 1;i++){
        _w += arr[i] + sep;
    }
    _w += arr[i];
    n_arr.push(_w);
    return n_arr;
}


$(function() {
   $("input[type=tel]").change(function(){
       var v = $(this).val();
       $(this).val(format_num(v).substr(0, 11));
   });
    $("input[type=number]").change(function(){
       var v = $(this).val();
       $(this).val(format_num(v));
   });
});