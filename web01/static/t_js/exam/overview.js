/**
 * Created by meisa on 2018/5/9.
 */

var cn_exam_type = {"xlcp1": "专业测评", "xlcp2": "兴趣测评"};

function init_info(data){
    if(data == null){
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if(data.length > 0) {
        var t = $("#t_exams");
        for(var i=0;i<data.length;i++){
            var add_tr = $("<tr></tr>");

            var td_t = new_td(data[i]["exam_type"], cn_exam_type);
            add_tr.append(td_t);

            var td_name = new_td("exam_name", data[i]);
            add_tr.append(td_name);

            var td_no = new_td("exam_no", data[i], null, null, timestamp_2_datetime);
            add_tr.append(td_no);

            var td_status = new_td("status", data[i]);
            add_tr.append(td_status);

            var td_op = $("<td></td>");
            var question_url = AddUrlArg(location.pathname, "exam_no", data[i]["exam_no"]);
            question_url = AddUrlArg(question_url, "exam_type", data[i]["exam_type"]);
            td_op.append(new_link("管理试题", question_url));
            add_tr.append(td_op);
            t.append(add_tr);
        }
    }
}

$(function() {
    init_info(null);
});