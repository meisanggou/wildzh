var app = getApp();
Page({

    data: {
        training_modes: ['分科练习', '综合练习'],
        subjects_array: ['微观经济学', '宏观经济学', '政治经济学'],
        select_modes: ['选择题', '名词解释', '简答题', '计算题', '论述题'],
        index: 1,
        subjectIndex: 0,
        modeIndex: 0,
        to: "training",
        cacheSelectedKey: "selectedTrainingOptions",
        canUpdate: false
    },
    onLoad: function(options) {
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

        if("to" in options){
            this.setData({
                to: options["to"]
            })
        }
        var selectedOptions = app.getOrSetCacheData(this.data.cacheSelectedKey);
        if (selectedOptions != null) {
            this.setData(selectedOptions);
        }
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
    selectModeChange(e) {
        this.setData({
            modeIndex: parseInt(e.detail.value)
        })
    },
    startTraining() {
        app.getOrSetCacheData(this.data.cacheSelectedKey, this.data);
        var url = "";
        if(this.data.to == "answer"){
            url += "../answer/answer"
        }
        else{
            url += "training"
        }
        url += "?select_mode=" + (this.data.modeIndex + 1);
        if (this.data.index == 0) {
            url += "&question_subject=" + (this.data.subjectIndex + 1);
        }
        wx.navigateTo({
            url: url
        })
    },
    startUpdateQuestion: function(){
        app.getOrSetCacheData(this.data.cacheSelectedKey, this.data);
        var url = "../questions/question?select_mode=" + (this.data.modeIndex + 1);
        if (this.data.index == 0) {
            url += "&question_subject=" + (this.data.subjectIndex + 1);
        }
        wx.navigateTo({
            url: url
        })
    }
})