var app = getApp();

Page({

    data: {
        training_modes: ['分科练习', '综合练习'],
        subjects_array: ['微观经济学', '宏观经济学', '政治经济学'],
        select_modes: ['选择题', '名词解释', '简答题', '计算题', '论述题'],
        index: 1,
        subjectIndex: 0,
        modeIndex: 0,
        isAccordingToType: true,
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
                that.setData({
                    errorMsg: errorMsg
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
            url += "&select_mode=" + (this.data.modeIndex + 1);
        }
        if (this.data.index == 0) {
            url += "&question_subject=" + (this.data.subjectIndex + 1);
        }
        wx.navigateTo({
            url: url
        })
    }
})