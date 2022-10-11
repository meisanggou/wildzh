/**
 * Created by meisa on 2018/5/6.
 */

$(function () {
    var mode_names = ["无", "选择题", "名词解释", "简答题", "计算题", "论述题", '多选题', '判断题'];
    var select_modes = [];
    var default_subject = {'name': '', 'select_modes': [], 'chapters': [], 'enable': true, 'custom_sm': false};
    for (var i = 0; i < mode_names.length; i++) {
        default_subject.select_modes.push({'name': mode_names[i], 'enable': true});
        select_modes.push({'name': mode_names[i], 'enable': true});
    }
    var default_subject_s = JSON.stringify(default_subject);
    var vm = new Vue({
        el: "#myTabContent",
        data: {
            exam_no: null,
            exam_name: "",
            exam_desc: "",
            openness_level: "private",
            open_mode: 1,
            open_no_start: '',
            open_no_end: '',
            allow_search: 0,
            enable_video: 0,
            search_tip: "",
            select_modes: select_modes,
            subjects: [],
            new_chapter: '',
            error_tips: {"exam_name": "请输入测试名称", "exam_desc": "请输入测试介绍"}
        },
        methods: {
            add_subject: function () {
                this.subjects.push(JSON.parse(default_subject_s));
            },
            add_chapter: function (index) {
                if (this.new_chapter.length <= 0) {
                    popup_show('请设置章节名称');
                    return false;
                }
                for (var i = 0; i < this.subjects[index]['chapters'].length; i++) {
                    if (this.subjects[index]['chapters'][i].name == this.new_chapter) {
                        popup_show('章节名称不能重复');
                        return false;
                    }
                }
                var ch_item = {'name': this.new_chapter, 'enable': true};
                this.subjects[index]['chapters'].push(ch_item);
                this.new_chapter = '';
            },
            handle_exam: function (is_update) {
                if (is_update == undefined) {
                    is_update = false;
                }
                var r_data = new Object();
                var keys = ["exam_name", "exam_desc", 'openness_level', 'open_mode', 'open_no_start', 'open_no_end', 'search_tip'];
                if (is_update == true) {
                    keys.push('exam_no')
                }
                r_data['allow_search'] = parseInt(this.allow_search);
                r_data['enable_video'] = parseInt(this.enable_video);
                r_data['select_modes'] = this.select_modes;
                for (var i = 0; i < keys.length; i++) {
                    r_data[keys[i]] = this[keys[i]];
                    if (keys[i] in this.error_tips) {
                        if (this[keys[i]].length <= 0) {
                            var msg = this.error_tips[keys[i]];
                            popup_show(msg);
                            return false;
                        }
                    }
                }
                var exam_subjects = [];
                for (var j = 0; j < this.subjects.length; j++) {
                    var s_item = this.subjects[j];
                    if (is_update == false && s_item.enable == false) {
                        continue
                    }
                    var exam_sj_item = {};

                    if (s_item.name.length == 0) {
                        popup_show('每个科目都需要设置名称');
                        return false;
                    }
                    exam_sj_item['enable'] = s_item.enable;
                    exam_sj_item['name'] = s_item.name;
                    exam_sj_item['select_modes'] = [];
                    //for (var k = 0; k < s_item.select_modes.length; k++) {
                    //    exam_sj_item['select_modes'].push(s_item.select_modes[k]);
                    //}
                    exam_sj_item['chapters'] = [];
                    for (var m = 0; m < s_item.chapters.length; m++) {
                        if (s_item.chapters[m].enable == false) {
                            continue
                        }
                        exam_sj_item['chapters'].push(s_item.chapters[m]);
                    }
                    exam_subjects.push(exam_sj_item);
                }
                r_data['subjects'] = exam_subjects;
                var info_url = $("#add_url").val();
                var success_msg = '创建成功';
                var req_med = 'POST';
                if (is_update) {
                    success_msg = '更新成功';
                    req_med = 'PUT';
                    info_url = $("#info_url").val();
                }
                my_async_request2(info_url, req_med, r_data, function (data) {
                    popup_show(success_msg);
                    if (is_update == false) {
                        swal({
                                title: "选择下一步",
                                text: msg,
                                type: "warning",
                                showCancelButton: true,
                                confirmButtonColor: '#DD6B55',
                                confirmButtonText: '录入试题',
                                cancelButtonText: "留在此页",
                                closeOnConfirm: true,
                                closeOnCancel: true
                            },
                            function (isConfirm) {
                                if (isConfirm) {
                                    var j_url = AddUrlArg(location.pathname, "exam_no", data["exam_no"]);
                                    j_url = AddUrlArg(j_url, "exam_type", data["exam_type"]);
                                    location.href = j_url;
                                }
                            }
                        );
                    }
                });
            },
            add: function () {
                this.handle_exam(false);
            },
            update: function () {
                this.handle_exam(true);
            }
        }
    });
    var exam_no = UrlArgsValue(location.href, 'exam_no');
    if (exam_no != null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, 'GET', null, function (data) {
            if (data.length == 1) {
                var exam_item = data[0];
                vm.exam_no = exam_item.exam_no;
                vm.exam_name = exam_item.exam_name;
                vm.exam_desc = exam_item.exam_desc;
                var keys = ['openness_level', 'open_mode', 'open_no_start', 'open_no_end',
                    'allow_search', 'search_tip', 'subjects', 'select_modes', 'enable_video'];
                for (var i = 0; i < keys.length; i++) {
                    if (keys[i] in exam_item) {
                        vm[keys[i]] = exam_item[keys[i]];
                    }
                }
            }
        })

    }
});