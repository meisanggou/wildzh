/**
 * Created by msg on 5/26/16.
 */

function add_option(select_id, value, text, title){
    if(title == null){
        title = text;
    }
    var select_elem = null;
    if(typeof select_id == "string") {
        if (select_id.indexOf("#") != 0) {
            select_id = "#" + select_id;
        }
        select_elem = $(select_id);
    }
    else{
        select_elem = select_id;
    }
    var option = "<option value='{value}' title='{title}'>{text}</option>";
    var option_item = option.replace("{value}", value).replace("{text}", text).replace("{title}", title);
    if(select_elem != null) {
        select_elem.append(option_item);
    }
}

function query_option(select_id, v, query_t){
    if(query_t == null){
        query_t = "value";
    }
    if (query_t != "text") {
        var o = $("#" + select_id).find("[" + query_t + "='" + v + "']");
    } else {
        var each_option = $("#" + select_id).find("option");
        var o = [];
        var c = 0;
        for (var i = 0; i < each_option.length; i++) {
            var current_option = $(each_option[i]);
            if (current_option.text() == v) {
                o[c] = current_option;
                c++;
            }
        }
    }
    return o;
}

function select_option(select_id, v, query_t) {
    if (query_t == null) {
        query_t = "value";
    }
    if (query_t != "text") {
        var o = $("#" + select_id).find("[" + query_t + "='" + v + "']");
        o.attr("selected", true);
        return true;
    } else {
        var each_option = $("#" + select_id).find("option");
        var c = 0;
        for (var i = 0; i < each_option.length; i++) {
            var current_option = $(each_option[i]);
            if (current_option.text() == v) {
                current_option.attr("selected", true);
                $("#" + select_id).val(current_option.val());
                return true;
            }
        }
    }
    return false;
}

function new_td(key, obj, max_len, editable, convert_value) {
    var td = $("<td></td>");
    if(key in obj){
        if(convert_value != null){
            var td_text = convert_value(obj[key]) + "";
        }
        else {
            var td_text = obj[key] + "";
        }
        if(max_len != null){
            if(td_text.length > max_len){
                td.attr("title", td_text);
                td_text = td_text.substr(0, max_len - 2) + ".."
            }
        }
        td.attr("name", "td_" + key);
        if (editable != null && editable == true) {
            var e = $("<input />");
            e.css("border", 0);
            e.css("background-color", "transparent");
            e.val(td_text);
            td.append(e);
        }
        else {
            td.append(td_text);
        }
    }
    return td;
}

function new_link(t, href)
{
    var link = $("<a></a>");
    link.attr("href", href);
    link.text(t);
    return link
}

function clear_table(table_id){
    if(table_id[0] != "#"){
        table_id = "#" + table_id;
    }
    $(table_id + " tr").not(":first").remove();
}

function add_row_td(t_id, content, col_len)
{
    if(t_id[0] != "#"){
        t_id = "#" + t_id;
    }
    var t = $(t_id);
    var add_tr = $("<tr></tr>");
    var add_td = $("<td></td>");
    add_td.text(content);
    if(col_len == null){
        var th_len = t.find("th").length;
        if(th_len > 0)
            col_len = th_len;
        else
            col_len = 1;
    }
    add_td.css({"text-align": "center"});
    add_td.attr("colSpan", col_len);
    add_tr.append(add_td);
    t.append(add_tr);
    return add_td;
}


function msg_include(s, s2) {
    var len_include = s2.length;
    var len_str = s.length;
    var i = 0, j = 0;
    while (true) {
        if (i >= len_include) {
            return true;
        }
        if (j >= len_str) {
            return false;
        }
        if (s[j] == s2[i]) {
            i++;
            j++;
        }
        else {
            j++;
        }
    }
}

function query_table(t_id, key){
    var trs = $("#" + t_id + " tr").not(":first");
    var tr_len = trs.length;
    for(var i=0;i<tr_len;i++){
        var tr_item = $(trs[i]);
        var tr_tds = tr_item.find("td");
        var td_len = tr_tds.length;
        var is_show = false;
        for(var j=0;j<td_len;j++){
            var td_item = $(tr_tds[j]);
            if (msg_include(td_item.text(), key) == true) {
                is_show = true;
                break;
            }
        }
        if(is_show == true){
            tr_item.show();
        }
        else{
            tr_item.hide();
        }
    }
}

function package_input(parent_el) {
    var data = new Object();
    var tags = ["input", "textarea", "select"];
    var tag_len = tags.length;
    for (var i = 0; i < tag_len; i++) {
        var all_input = parent_el.find(tags[i]);
        var input_len = all_input.length;
        for (var j = 0; j < input_len; j++) {
            var item = $(all_input[j]);
            var key = item.attr("name");
            if (key == undefined) {
                key = item.attr("id");
                if (key == undefined) {
                    continue;
                }
            }
            data[key] = item.val();
        }
    }

    return data;
}

function alert1(msg) {
    $("div[role='alert']").hide();
    var dialog_div = $('<div class="alert alert-success" role="alert" style="z-index:999"></div>');
    dialog_div.text(msg);
    $("body").append(dialog_div);
    register_reset_bottom(dialog_div);
    setTimeout(function () {
        dialog_div.remove();
    }, 2000);
}