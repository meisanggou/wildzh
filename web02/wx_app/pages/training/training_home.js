var app = getApp();

Page({

    data: {
        training_modes: ['综合练习'],
        subjects_array: [[], []],
        select_modes: [],
        index: 0,
        isAccordingToType: false,
        subjectIndexs: [0, 0],
        modeIndex: 0,
        to: "training",
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
                var select_modes = [];
                var training_modes = this.data.training_modes;
                var index = this.data.index;
                var isAccordingToType = this.data.isAccordingToType;
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
                    isAccordingToType = false;
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
                var index_0 = this.data.subjectIndexs[0];
                if(index_0 >= subjects.length){
                    index_0 = 0;
                }
                if (subjects.length > 1) {
                    if (training_modes.indexOf('分科练习') < 0) {
                        training_modes.push('分科练习');
                    }
                    subjects_array[1] = subjects[index_0]['chapters'];
                } else {
                    var f_i = training_modes.indexOf('分科练习')
                    if (f_i >= 0) {
                        training_modes.splice(f_i, 1);
                    }
                    index = 0;
                }
                that.setData({
                    errorMsg: errorMsg,
                    select_modes: select_modes,
                    subjects_array: subjects_array,
                    training_modes: training_modes,
                    index: index,
                    isAccordingToType: isAccordingToType
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
        if (this.data.index == 1) {
            var current_sj = subjects[this.data.subjectIndexs[0]];
            url += "&question_subject=" + current_sj.value;
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