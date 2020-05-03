var app = getApp();

Page({

    data: {
        select_modes: [],  // 对应综合练习菜单 题型
        subjects_array: [[], []],  // 对应分科练习菜单 科目-题型
        chapters_array: [[], [], []], // 对应章节练习菜单 科目-章节-题型
        sources_array: [],  // 对应真题练习 题目来源
        errorMsg: "题库信息加载中...",
        cacheSelectedKey: "selectedTrainingOptions",
        canUpdate: false
    },
    onLoad: function(options) {
        var selectedOptions = app.getOrSetCacheData(this.data.cacheSelectedKey);
        if (selectedOptions != null) {
            if ('subjects_array' in selectedOptions){
                delete selectedOptions['subjects_array'];
            }
            this.setData(selectedOptions);
        }
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
    onShow: function() {
        var examNo = app.globalData.defaultExamNo;
        if (examNo) {
            this.getExam(examNo);
        } else {
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
        }
    },
    getExam: function(examNo) {
        var that = this;
        wx.request2({
            url: '/exam/info/?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                var allExams = [];
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
                if (examItem['exam_role'] > 10) {
                    errorMsg = '无权限进行操作，请先升级成会员！';
                }
                var select_modes = [{'name': '全部题型', 'value': -1}];
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

                var subjects_array = [[], []];
                var subjects = [];
                if ('subjects' in examItem) {
                    var _subjects = examItem['subjects'];
                    for (var i = 0; i < _subjects.length; i++) {
                        var _item = _subjects[i];
                        if (_item.enable == true) {
                            _item['value'] = i;
                            if(!'chapters' in _item){
                                _item['chapters'] = [];
                            }
                            _item['chapters'].unshift({'name': '全部章节', 'enable': true});
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
    comprehensiveExerciseChange(e){
      console.info(e.detail.value);
    },
    subjectExerciseChange(e){

    },
    subjectExerciseColumnChange: function(e){

    },
    chapterExerciseChange: function(e){

    },
    chapterExerciseColumnChange: function(e){
      var column = e.detail.column;
        var value = e.detail.value;
        var subjects = this.data.chapters_array[0];
        var sub_items = [];
        if(column == 0){
            var subject_item = subjects[value];
            if('chapters' in subject_item){
                var chapters = subject_item['chapters'];
                for(var i=0;i<chapters.length;i++){
                    if(chapters[i].enable){
                        sub_items.push(chapters[i]);
                    }
                }
            }
            this.setData({
                "chapters_array[1]": sub_items
            })
        }
    },
    sourceChange: function(e){

    },
    bindPickerChange(e) {
        this.setData({
            index: parseInt(e.detail.value)
        })
    },
    subjectChange(e) {
        this.setData({
            subjectIndexs: e.detail.value
        })
        console.info(this.data.subjects_array);
    },
    bindSubjectColumnChange: function(e){
        var column = e.detail.column;
        var value = e.detail.value;
        var subjects = this.data.subjects_array[0];
        var sub_items = []
        if(column == 0){
            var subject_item = subjects[value];
            if('chapters' in subject_item){
                var chapters = subject_item['chapters'];
                for(var i=0;i<chapters.length;i++){
                    if(chapters[i].enable){
                        sub_items.push(chapters[i]);
                    }
                }
            }
            this.setData({
                "subjects_array[1]": sub_items,
                "subjectIndex[0]": value
            })
        }

    },
    selectModeChange(e) {
        this.setData({
            modeIndex: parseInt(e.detail.value)
        })
    },
    startTraining() {
        app.getOrSetCacheData(this.data.cacheSelectedKey, this.data);
        var url = "";
        if (this.data.to == "answer") {
            url += "../answer/answer"
        } else {
            url += "training"
        }
        var sm_index = -1;
        if (this.data.modeIndex < this.data.select_modes.length) {
            sm_index = this.data.select_modes[this.data.modeIndex].value;
        }
        url += "?select_mode=" + sm_index;
        var subjects = this.data.subjects_array[0];
        if (this.data.index == 1) {
            var current_sj = subjects[this.data.subjectIndexs[0]];
            url += "&question_subject=" + current_sj.value;
            var ch_index = this.data.subjectIndexs[1];
            console.info(ch_index);
            if(ch_index > 0){
                var question_chapter = this.data.subjects_array[1][ch_index];
                console.info(question_chapter);
                url += "&question_chapter=" + question_chapter.name;
            }
        }
        wx.navigateTo({
            url: url
        })
    },
    startUpdateQuestion: function() {
        app.getOrSetCacheData(this.data.cacheSelectedKey, this.data);
        var modeIndex = parseInt(this.data.modeIndex)
        var sm_index = -1;
        if (this.data.modeIndex < this.data.select_modes.length) {
            sm_index = this.data.select_modes[this.data.modeIndex].value;
        }
        var url = "../questions/question?select_mode=" + sm_index;
        if (this.data.index == 1) {
            var current_sj = this.data.subjects_array[0][this.data.subjectIndex];
            url += "&question_subject=" + current_sj.value;
        }
        wx.navigateTo({
            url: url
        })
    }
})