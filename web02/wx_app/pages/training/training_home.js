Page({

    data: {
        training_modes: ['分科练习', '综合练习'],
        subjects_array: ['微观经济学', '宏观经济学', '政治经济学'],
        select_modes: ['选择题', '名词解释', '简答题', '计算题', '论述题'],
        index: 1,
        subject_index: 0,
        mode_index: 0,
        to: "training"
    },
    onLoad: function(options) {
        console.info(options);
        if("to" in options){
            this.setData({
                to: options["to"]
            })
        }
    },
    bindPickerChange(e) {
        this.setData({
            index: parseInt(e.detail.value)
        })
    },
    subjectChange(e) {
        this.setData({
            subject_index: parseInt(e.detail.value)
        })
    },
    selectModeChange(e) {
        this.setData({
            mode_index: parseInt(e.detail.value)
        })
    },
    startTraining() {
        var url = "";
        if(this.data.to == "answer"){
            url += "../answer/answer"
        }
        else{
            url += "training"
        }
        url += "?select_mode=" + (this.data.mode_index + 1);
        if (this.data.index == 0) {
            url += "&question_subject=" + (this.data.subject_index + 1);
        }
        wx.navigateTo({
            url: url
        })
    }
})