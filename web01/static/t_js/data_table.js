/**
 * Created by msg on 10/29/15.
 */
// $('#search_table').bind('input propertychange', function() {alert("success")});

function msg_include(str, include_str){
    var len_include = include_str.length;
    var len_str = str.length;
    var i= 0, j=0;
    while(true){
        if(i >= len_include){
            return true;
        }
        if(j >= len_str){
            return false;
        }
        if(str[j] == include_str[i]){
            i++;
            j++;
        }
        else{
            j++;
        }
    }
}

function search_table(){
    var v = $("#search_table").val();
    var a_el = $("a[class='data_title']");
    var len_a = a_el.length;
    for(var i=0;i<len_a;i++){
        if (a_el[i].id == "main_menu"){
            continue;
        }
        var a_href = a_el[i].attributes["title"].value + "&query=" + v;
        a_el[i].href = a_href;
        a_el[i].hidden = true;
        if(v.length == 0){
            a_el[i].hidden = false;
        }
        else if(msg_include(a_el[i].text, v)){
            a_el[i].hidden = false;
        }
        else{
            a_el[i].hidden = true;
        }
    }
}


function produce_alter_sql()
{
    var table_name_origin = $("#table_name_origin").val();
    var table_name = $("#table_name").val();
    var comment = $("#comment").val();
    if(comment.length<=0){
        $("#out_sql").val("注释不能为空");
        return;
    }

    var sign = $("#sign").val();
    if(sign == "0") {
        var sql = "ALTER TABLE " + table_name_origin + " COMMENT '" + comment + "';";
        $("#out_sql").val(sql);
    }
    else if(sign == "1" || sign == "2")
    {
        var col_name_origin = $("#col_name_origin").val();
        var col_name = $("#col_name").val();
        var col_type = $("#col_type").val();
        var default_value = $("#default_value").val().toLowerCase();
        var allow_null = $("#allow_null").val();
        if(col_name.length <= 0){
            $("#out_sql").val("列名不能为空");
            return;
        }
        if(col_type.length<=0){
            $("#out_sql").val("类型不能为空");
            return;
        }

        var sql = "ALTER TABLE " + table_name_origin;
        if(sign == 1)
            sql += " CHANGE";
        else
            sql += " ADD";
        sql += " COLUMN " + col_name_origin + " " + col_name;
        sql += " " + col_type;
        if(default_value != "none" && default_value != "null" && default_value != ""){
            sql += " DEFAULT " + default_value;
        }
        if(allow_null != "YES"){
            sql += " NOT NULL"
        }
        sql += " COMMENT '" + comment + "';";
        $("#out_sql").val(sql);
    }
}

function change_table_comment()
{
    var table_name = $("#p_table_name").text();
    var table_comment = $("#p_table_comment").text();
    $("input[id^='table_name']").val(table_name.substr(3));
    $("#comment").val(table_comment.substr(3));
    $("tr[name='col_info']").hide();
    $("#out_sql").val("");
    $("#sign").val("0");
}

function table_add_col()
{
    var table_name = $("#p_table_name").text();
    $("input[id^='table_name']").val(table_name.substr(3));
    $("#out_sql").val("");
    $("input[id^='col_name']").val("");
    $("#col_type").val("");
    $("#default_value").val("");
    $("#allow_null").val("NO");
    $("#comment").val("");
    $("tr[name='col_info']").show();
    $("input[name='update_value']").removeAttr("readonly");
    $("select").removeAttr("disabled");
    $("a[name='remove_readonly']").hide();
    $("#sign").val("2");
}

function backup_table(){
    var table_name = $("#p_table_name").text().substr(3);
    console.info(table_name);
    my_async_request("/dev/data/table/backup/", "POST", {"t_name": table_name});
}

$(function() {
    $("#btn_produce_sql").click(produce_alter_sql);
    $("a[name='a_change_struct']").click(function(){
        var table_name = $("#p_table_name").text();
        $("input[id^='table_name']").val(table_name.substr(3));
        $("#out_sql").val("");
        var tr_col = this.parentNode.parentNode;
        var children_td = tr_col.children;
        $("input[id^='col_name']").val(children_td[0].innerHTML);
        $("#col_type").val(children_td[1].innerHTML);
        $("#default_value").val(children_td[3].innerHTML);
        $("#allow_null").val(children_td[4].innerHTML);
        $("#comment").val(children_td[6].innerHTML);
        $("tr[name='col_info']").show();
        $("input[name='update_value']").attr("readonly", "readonly");
        $("select").attr("disabled", "disabled");
        $("a[name='remove_readonly']").show();
        $("#sign").val("1");
      }
    );
    $("a[name='remove_readonly']").click(function(){
        console.info(this);
        var input = $(this.parentNode).prev().children(":input");
        input.removeAttr("readonly");
        input.removeAttr("disabled");
    });
    search_table();
    $("a[name='delete_column']").click(function () {
        var table_name_origin = $("#table_name_origin").val();
        var col_name_origin = $("#col_name_origin").val();
        var sql = "ALTER TABLE ";
        sql += table_name_origin;
        sql += " DROP COLUMN ";
        sql += col_name_origin;
        sql += ";";
        $("#out_sql").val(sql);
    });
});