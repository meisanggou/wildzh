/**
 * Created by meisa on 2018/5/6.
 */

var ascii = ["A", "B", "C", "D", "E", "F"];

function new_exam(){
    var r_data = new Object();
    var keys = ["exam_type", "exam_name", "exam_desc", "eval_type"];
    for(var i=0;i<keys.length;i++){
        var item = $("#" + keys[i]);
        var v = item.val().trim();
        if(v.length <= 0){
            var msg = item.attr("msg");
            console.info(msg);
            popup_show(msg);
            return 1;
        }
        r_data[keys[i]] = v;
    }
    r_data["result_explain"] = new Array();
    var exist_explains = $("#result_explain").find("li[name='li_explain']:visible");
    console.info(exist_explains);
    for(var i=0;i<exist_explains.length;i++){
        var explain_item = $(exist_explains[i]);
        var c = explain_item.find("input:eq(0)").val();
        var t = explain_item.find("input:eq(1)").val().trim();
        if(t.length <=0){
            popup_show("请输入【" + c + "】结果对应的解释");
            return 2;
        }
        console.info(t);
        r_data["result_explain"][i] = t;
    }
    var add_url = $("#add_url").val();
    my_async_request2(add_url, "POST", r_data);
}

$(function() {
    $("#exam_type").change(function(){
        var select_m = $("#exam_type option:selected").val();
        var about = parseInt($("#exam_type option:selected").attr("about"));
        var exist_explain = $("#result_explain").find("li[name='li_explain']");
        var demo_li = $(exist_explain[0]);
        var demo_parent = demo_li.parent();
        var exist_len = exist_explain.length;
        for(var i=exist_len;i<about + 1 && i<= 7;i++)
        {
            var clone_li = demo_li.clone();
            clone_li.show();
            $(clone_li.find("input")[0]).val(ascii[i - 1]);
            demo_parent.append(clone_li);
        }
        for(var i=about+ 1; i<exist_len;i++){
            $(exist_explain[i]).remove();
        }
    });
    $("#exam_type").change();
    $("#btn_new").click(new_exam);
});