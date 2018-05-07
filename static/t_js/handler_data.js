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