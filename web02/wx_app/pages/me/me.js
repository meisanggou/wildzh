var app = getApp();
var that;
Page({

    data: {
        examIndex: -1,
        allExams: [],
        examName: "未选择"
    },
    onLoad: function(options) {
        this.setData({
            examName: app.globalData.defaultExamName
        })
        this.getExams();
    },

    getExams: function() {
        that = this;
        wx.request2({
            url: '/exam/info/',
            method: 'GET',
            success: res => {
                var allExams = [];
                for (var index in res.data.data) {
                    if (res.data.data[index]["question_num"] > 0) {
                        allExams.push(res.data.data[index]);
                    }
                }
                that.setData({
                    allExams: allExams
                });
                wx.hideLoading();
            }
        })
    },
    examChange: function(e) {
        this.setData({
            examIndex: e.detail.value
        })
        var currentExam = this.data.allExams[this.data.examIndex];
        app.setDefaultExam(currentExam);
    }
})