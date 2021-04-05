var app = getApp();
var lastExamNo = null;
var lastUpdateSource = 0;
var dt = require("../common/datetime_tools.js");
Page({

    data: {
        select_modes: [], // 对应综合练习菜单 题型
        subjects_array: [
            [],
            []
        ], // 对应分科练习菜单 科目-题型
        chapters_array: [
            [],
            [],
            []
        ], // 对应章节练习菜单 科目-章节-题型
        chapter_indexs: [0, 0, 0],
        sources_array: [], // 对应真题练习 题目来源
        errorMsg: "题库信息加载中...",
        cacheSelectedKey: "selectedTrainingOptions",
        canUpdate: false
    },
    onLoad: function (options) {
        var canUpdate = false;
        var currentUser = app.getOrSetCurrentUserData();
        if (currentUser != null && typeof currentUser == "object") {
            if ("role" in currentUser) {
                if ((currentUser.role & 2) == 2) {
                    canUpdate = true;
                }
            }
        }
        this.setData({
            canUpdate: canUpdate
        })
        if ("to" in options) {
            this.setData({
                to: options["to"]
            })
        }

    },
    onShow: function () {
        var that = this;
        wx.user_ping(function(res){
            if(!('data' in res)){
                that.setData({
                    errorMsg: '网络连接异常，请检查网络！'
                })
                return;
            }
            if(res.data.status != true){
                that.setData({
                    errorMsg: res.data.data
                })
                return;
            }
            that.refreshExam(false);
        });
    },
    refreshExam(force) {
        var examNo = app.globalData.defaultExamNo;
        if (examNo) {} else {
            wx.showModal({
                title: '未选择题库',
                content: "未选择题库,确定进入【我的】选择题库",
                showCancel: false,
                success(res) {
                    wx.switchTab({
                        url: "/pages/me/me"
                    })
                }
            });
            this.setData({
                errorMsg: '请先选择一个题库'
            })
            return false;
        }
        var nowT = dt.get_timestamp2();
        var intervalT = nowT - lastUpdateSource;
        if (intervalT < 300 && lastExamNo == examNo && force == false) {
            return false;
        }
        this.getExam(examNo);
        this.getExamSources(examNo);
    },
    getExam: function (examNo) {
        var that = this;
        wx.request2({
            url: '/exam/info/?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                var resData = res.data.data;
                var errorMsg = '';
                if (res.data.status == false || resData.length <= 0) {
                    errorMsg = '未查询到题库详情，切换题库'
                    that.setData({
                        errorMsg: errorMsg
                    })
                    return false;
                }
                var examItem = resData[0];
                if (examItem['exam_role'] > 30) {
                    errorMsg = '无权限进行操作，请先升级成会员！';
                }
                else if(examItem['exam_role'] <= 3){
                    this.setData({
                        canUpdate: true
                    })
                }
                else{
                    this.setData({
                        canUpdate: false
                    })
                }
                // var select_modes = [{'name': '全部题型', 'value': -1}];
                var select_modes = [];
                if ('select_modes' in examItem) {
                    var _select_modes = examItem['select_modes'];
                    for (var i = 0; i < _select_modes.length; i++) {
                        var _item = _select_modes[i];
                        if (_item.enable == true) {
                            _item['value'] = i;
                            select_modes.push(_item);
                        }
                    }
                }
                if (select_modes.length <= 0) {
                    select_modes.push({
                        'name': '全部题型',
                        'value': -1
                    });
                }
                var subjects_array = [
                    [],
                    []
                ];
                var subjects = [];
                if ('subjects' in examItem) {
                    var _subjects = examItem['subjects'];
                    for (var i = 0; i < _subjects.length; i++) {
                        var _item = _subjects[i];
                        if (_item.enable == true) {
                            _item['value'] = i;
                            if (!'chapters' in _item) {
                                _item['chapters'] = [];
                            }
                            _item['chapters'].unshift({
                                'name': '全部章节',
                                'enable': true
                            });
                            subjects.push(_item);
                        }
                    }
                }
                subjects_array[0] = subjects;
                subjects_array[1] = select_modes;
                var chapters_array = [subjects, [], select_modes];
                if (subjects.length >= 1) {
                    chapters_array[1] = subjects[0]['chapters'];
                }
                that.setData({
                    errorMsg: errorMsg,
                    select_modes: select_modes,
                    subjects_array: subjects_array,
                    chapters_array: chapters_array
                });
                wx.hideLoading();
            },
            fail: res => {
                that.setData({
                    errorMsg: '未能成功加载题库信息，检查网络或重试！'
                });
            }
        })
    },
    getExamSources: function (examNo) {
        var that = this;
        wx.request2({
            url: '/exam/questions/sources?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                lastUpdateSource = dt.get_timestamp2();
                lastExamNo = examNo;
                var resData = res.data.data;
                var sources = resData['sources'];
                that.setData({
                    sources_array: sources
                });
                wx.hideLoading();
            },
            fail: res => {}
        })
    },
    comprehensiveExerciseChange(e) {
        var sm_index = e.detail.value;
        var sm_value = this.data.select_modes[sm_index].value;
        this.startTraining(sm_value, -1, null, null);
    },
    subjectExerciseChange(e) {
        var indexs = e.detail.value;
        var sj_value = this.data.subjects_array[0][indexs[0]].value;
        var sm_value = this.data.subjects_array[1][indexs[1]].value;
        this.startTraining(sm_value, sj_value, null, null);
    },
    chapterExerciseChange: function (e) {
        var indexs = e.detail.value;
        var sj_value = this.data.chapters_array[0][indexs[0]].value;
        var ch_value = null;
        if (indexs[1] > 0) {
            ch_value = this.data.chapters_array[1][indexs[1]].name;
        }
        var sm_value = this.data.chapters_array[2][indexs[2]].value;
        this.startTraining(sm_value, sj_value, ch_value, null);
    },
    chapterExerciseColumnChange (e) {
        var column = e.detail.column;
        var value = e.detail.value;
        var subjects = this.data.chapters_array[0];
        var chapter_indexs = this.data.chapter_indexs;
        var sub_items = [];
        if (column == 0) {
            var subject_item = subjects[value];
            if ('chapters' in subject_item) {
                var chapters = subject_item['chapters'];
                for (var i = 0; i < chapters.length; i++) {
                    if (chapters[i].enable) {
                        sub_items.push(chapters[i]);
                    }
                }
            }
            chapter_indexs[0] = value;
            chapter_indexs[1] = 0;
            this.setData({
                "chapters_array[1]": sub_items,
                "chapter_indexs[0]": value,
                "chapter_indexs[1]": 0
            })
        }
        else{
            var key1 = 'chapter_indexs[' + column + ']';
            var data = {};
            data[key1] = value;
            this.setData(data)
        }
    },
    sourceChange: function (e) {
        var source_index = e.detail.value;
        var s_value = this.data.sources_array[source_index].question_source;
        this.startTraining(-1, -1, null, s_value);
    },
    updateQuestionChange: function (e) {
        var index = e.detail.value;
        var sm_value = this.data.select_modes[index].value;
        this.startTraining(sm_value, -1, null, null, 'update');
    },
    startTraining(sm_value, sj_value, ch_value, source_value, action) {
        app.getOrSetCacheData(this.data.cacheSelectedKey, this.data);
        var url = "training?from=home";
        if (action == 'update') {
            url = "../questions/question?from=home";
        }
        if (sm_value >= -1) {
            url += "&select_mode=" + sm_value;
        }
        if (sj_value >= 0) {
            url += "&question_subject=" + sj_value;
        }
        if (ch_value != null) {
            url += "&question_chapter=" + ch_value;
        }
        if (source_value != null) {
            url += "&question_source=" + source_value;
        }
        wx.navigateTo({
            url: url
        })
    },
    onPullDownRefresh: function () {
        this.refreshExam(true);
        wx.stopPullDownRefresh({
            complete: (res) => {},
        })
    }
})