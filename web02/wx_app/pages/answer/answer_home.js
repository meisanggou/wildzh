var app = getApp();

Page({

    data: {
        training_modes: ['综合练习'],
        subjects_array: [],
        select_modes: [],
        index: 0,
        subjectIndex: 0,
        modeIndex: 0,
        isAccordingToType: false,
        to: "training",
        cacheSelectedKey: "selectedAnswerOptions",
        errorMsg: "题库信息加载中..."
    },
    onLoad: function(options) {
        if ("to" in options) {
            this.setData({
                to: options["to"]
            })
        }
        var selectedOptions = app.getOrSetCacheData(this.data.cacheSelectedKey);
        if(selectedOptions != null){
            this.setData(selectedOptions);
        }
        
    },
    onShow: function () {
        var examNo = app.globalData.defaultExamNo;
        if (examNo) {
            this.getExam(examNo);
        }
        else {
            this.setData({
                errorMsg: '请先选择一个题库'
            })
        }
    },
    getExam: function (examNo) {
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
                var subjects = []
                var training_modes = this.data.training_modes;
                if('select_modes' in examItem){
                    var _select_modes = examItem['select_modes'];
                    for (var i = 0; i < _select_modes.length;i++){
                        var _item = _select_modes[i];
                        if (_item.enable == true){
                            _item['value'] = i;
                            select_modes.push(_item);
                        }
                    }
                }
                if('subjects' in examItem){
                    var _subjects = examItem['subjects'];
                    for (var i = 0; i < _subjects.length; i++) {
                        var _item = _subjects[i];
                        if (_item.enable == true) {
                            _item['value'] = i;
                            subjects.push(_item);
                        }
                    }
                    console.info(subjects);
                    console.info(training_modes.indexOf('分科练习'))
                    if (subjects.length > 1 && training_modes.indexOf('分科练习') < 0){
                        training_modes.push('分科练习');
                    }
                }
                that.setData({
                    errorMsg: errorMsg,
                    select_modes: select_modes,
                    subjects_array: subjects,
                    training_modes: training_modes
                });
                wx.hideLoading();
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
            subjectIndex: parseInt(e.detail.value)
        })
    },
    switchModeChange(e) {
        this.setData({
            isAccordingToType: e.detail.value
        })
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
            url += "answer"
        }
        url += "?from=answer_home"
        if (this.data.isAccordingToType) {
            var modeIndex = parseInt(this.data.modeIndex)
            var select_mode = this.data.select_modes[modeIndex].value;
            url += "&select_mode=" + select_mode;
        }
        if (this.data.index == 1) {
            url += "&question_subject=" + (this.data.subjectIndex + 1);
        }
        wx.navigateTo({
            url: url
        })
    }
})