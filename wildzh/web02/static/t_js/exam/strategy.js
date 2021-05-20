/**
 * Created by meisa on 2020/5/4.
 */

function init_info(data){
    if(data == null){
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if(data.length > 0) {
        q_vm.all_exams = [];
        for(var index in data){
            q_vm.all_exams.push(data[index]);
            if(data[index].exam_no == q_vm.current_exam.exam_no){
                q_vm.current_exam_index = index;
                q_vm.select_exam();
            }
        }
    }
}

$(function () {
    var exam_no = UrlArgsValue(location.href, "exam_no");
    var strategy_url = $("#strategy_url").val();
    var info_url = $("#info_url").val();
    if(exam_no != null) {
        exam_no = parseInt(exam_no);
    }
    q_vm = new Vue({
        el: "#div_content",
        data: {
            all_exams: [],
            current_exam_index: -1,
            current_exam: {question_num: 0, exam_no: exam_no},
            select_modes: [],
            subjects: [],
            strategies: [],
            current_strategy_index: -1,
            strategy_id: null,
            strategy_name: "",
            internal: 0,
            strategy_pattern: []
        },
        methods: {
            select_exam: function () {
                this.current_exam = this.all_exams[this.current_exam_index];
                this.select_modes = this.current_exam["select_modes"];
                this.subjects = this.current_exam["subjects"];
                if("strategies" in this.current_exam){
                    var strategies = this.current_exam['strategies'];
                    //if(strategies.length <= 0){
                    //    this.strategy_pattern = [];
                    //    this.strategy_id = null;
                    //}else{
                    //    this.strategy_pattern = strategies[0]["strategy_items"];
                    //    this.strategy_id = strategies[0]['strategy_id'];
                    //}
                    this.strategies = strategies;
                    this.current_strategy_index = -1;
                    this.select_strategy();
                }
                else{
                    var that = this;
                    var url = strategy_url + '/' + this.current_exam['exam_no'] + '?internal=';
                    my_request(url, 'GET', null, function(data){
                        that.current_exam['strategies'] =  data['data']['strategies'];
                        that.select_exam();
                    })
                }
            },
            select_strategy: function(){
                var index = this.current_strategy_index;
                if(index < 0){
                    this.strategy_pattern = [];
                    this.strategy_id = null;
                    this.strategy_name = "";
                    this.internal = 0;
                }
                else {
                    this.strategy_pattern = this.strategies[index]["strategy_items"];
                    this.strategy_id = this.strategies[index]['strategy_id'];
                    this.strategy_name = this.strategies[index]['strategy_name'];
                    this.internal = this.strategies[index]['internal'];
                }
            },
            add_mode: function (position) {
                if(this.current_exam_index < 0){
                    popup_show("请先选择题库");
                    return false;
                }
                if(this.strategy_pattern.length >= 8){
                    popup_show("最多添加8组题型");
                    return false;
                }
                if(position == -1){
                    position = this.strategy_pattern.length;
                }
                this.strategy_pattern.splice(position, 0, {'value': -1, 'num': '', 'qss': []});
            },
            remove_mode: function(index){
                this.strategy_pattern.splice(index, 1);
            },
            add_project: function(index){
                if(this.strategy_pattern[index].qss.length >= 5){
                    popup_show("最多添加5组 科目");
                    return false;
                }
                this.strategy_pattern[index].qss.push({'value': -1, 'min_num': '', 'max_num': ''});
            },
            remove_project: function(index, qs_index){
                this.strategy_pattern[index].qss.splice(qs_index, 1);
            },
            update: function(){
                if(this.strategy_pattern.length <= 0){
                    popup_show("请先增加题型");
                    return false;
                }
                var strategy_items = [];
                for(var i=0;i<this.strategy_pattern.length;i++){
                    var error_tip = "#" + (i + 1);
                    var sp_item = this.strategy_pattern[i];
                    if(sp_item.value < 0){
                        error_tip += " 未选择题型";
                        popup_show(error_tip);
                        return false;
                    }
                    var num = parseInt(sp_item.num);
                    if(isNaN(num) || num < 0 || num > 100){
                        error_tip += " 题目数需要大于0，小于等于100";
                        popup_show(error_tip);
                        return false;
                    }
                    var qss = sp_item.qss;
                    var sum_min = 0;
                    for(var j= 0,l=qss.length;j<l;j++){
                        var sub_error_tip = error_tip + " **" + (j + 1);
                        var qs_item = qss[j];
                        if(qs_item.value < 0){
                            sub_error_tip += " 未选择科目";
                            popup_show(sub_error_tip, 5000);
                            return false;
                        }
                        var qs_min_num = parseInt(qs_item.min_num);
                        if(isNaN(qs_min_num) || qs_min_num < 0 || qs_min_num > num){
                            sub_error_tip += " 题目数最小值 需要大于0，小于等于" + num;
                            popup_show(sub_error_tip, 5000);
                            return false;
                        }
                        var qs_max_num = parseInt(qs_item.max_num);
                        if(isNaN(qs_max_num) || qs_max_num < 0 || qs_max_num > num){
                            sub_error_tip += " 题目数最大值 需要大于0，小于等于" + num;
                            popup_show(sub_error_tip, 5000);
                            return false;
                        }
                        if(qs_min_num > qs_max_num){
                            sub_error_tip += " 最小值不能大于最大值";
                            popup_show(sub_error_tip, 5000);
                            return false;
                        }
                        sum_min += qs_min_num;
                    }
                    if(sum_min > num){
                        error_tip += " 所有科目的最小值的和 " + sum_min +  " 不能大于 该题型总题数" + num;
                        popup_show(error_tip, 5000);
                        return false;
                    }
                    strategy_items.push({'value': sp_item.value, 'num': num, 'qss': qss});
                }
                var data = {'strategy_items': strategy_items, 'exam_no': this.current_exam['exam_no']};
                if(this.strategy_id != null){
                    data['strategy_id'] = this.strategy_id;
                }
                data['strategy_name'] = this.strategy_name;
                data['internal'] = this.internal;
                var index = this.current_strategy_index;
                var that = this;
                my_async_request2(strategy_url, 'PUT', data, function(res_data){
                        popup_show("操作成功");
                        if(index == -1){
                            that.strategies.push(res_data);
                            that.current_strategy_index = that.strategies.length - 1;
                            that.select_strategy();
                        }
                        else {
                            that.strategies[index] = res_data;
                        }
                    }
               )
            },
            export_strategy: function (i_detail) {
                var answer = 'alone';
                if(i_detail){
                    answer = 'alone_detail';
                }
                var url = '/exam/export/word?file=true&exam_no=' + this.current_exam['exam_no'] +'&strategy_id=' + this.strategy_id;
                url += '&answer=' + answer;
                url += '&t=' + get_timestamp2() ;
                window.open(url);
            },
            remove_strategy: function(){
                var that = this;
                var delete_url = strategy_url + '/' + this.strategy_id;
                var del_data = {'exam_no': this.current_exam['exam_no']};
                my_async_request2(delete_url, 'DELETE', del_data, function(data){
                    popup_show("删除成功");
                    that.strategies.splice(that.current_strategy_index, 1);
                    that.current_strategy_index = -1;
                    that.select_strategy();
                });
            }
        }
    });
    init_info(null);
});