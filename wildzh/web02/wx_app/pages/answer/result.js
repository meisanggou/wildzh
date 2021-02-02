var that;
var app = getApp();
var STATE_WRONG = 'wrong';
var STATE_RIGHT = 'right'
var STATE_SKIP = 'skip'
Page({
    data: {
        score: 0,
        totalScore: 0,
        examNo: 0,
        timestamp: 0,
        allQuestionIndexs: [],
        questionItems: []
    },


    onLoad: function (options) {
        that = this;
        wx.showLoading({
            title: '加载中',
        })
        if ("exam_no" in options) {
            var examNo = options["exam_no"];
            var timestamp = options["timestamp"];
            that.setData({
                examNo: examNo,
                timestamp: timestamp
            });
            var test_id = app.globalData.testIdPrefix + examNo + "_" + timestamp;
            wx.getStorage({
                key: test_id,
                success: function (res) {
                    wx.hideLoading();
                    var questionNum = res.data.length;
                    var score = 0;
                    var showNums = [];
                    // var wrong_question = [];
                    var questions = [];
                    for (var i = 0; i < questionNum;) {
                        var lineNums = [];
                        for (var j = 0; j < 5 && i < questionNum; i++ , j++) {
                            lineNums.push(i);
                            if(!('displayed' in res.data[i])){
                                continue;
                            }
                            if(!('right' in res.data[i])){
                                questions.push({'no': res.data[i].question_no, 'state': STATE_SKIP})
                                continue;
                            }
                            if (res.data[i]["right"] == true) {
                                score = score + 1;
                                questions.push({'no': res.data[i].question_no, 'state': STATE_RIGHT})
                            }
                            else if (res.data[i]["right"] == false) {
                                questions.push({'no': res.data[i].question_no, 'state': STATE_WRONG})
                                // wrong_question.push(res.data[i]["question_no"]);
                            }
                            
                        }
                        showNums.push(lineNums);
                    }
                    that.setData({
                        allQuestionIndexs: showNums,
                        questionItems: res.data,
                        score: score,
                        totalScore: questionNum
                    })
                    that.saveBrushNum(questions);
                    // wx.request2({
                    //     url: '/exam/wrong/',
                    //     method: "POST",
                    //     data: { "question_no": wrong_question, "exam_no": examNo }
                    // })
                },
            })
        }

    },

    showDeatil: function (e) {
        var index = e.currentTarget.dataset.index;
        console.info(index);
        var args = "exam_no=" + that.data.examNo + "&timestamp=" + that.data.timestamp;
        wx.navigateTo({
            url: '../showDetail/showDetail?index=' + index + "&" + args
        })
    },

    saveBrushNum: function (questions) {
        console.info(questions);
        if(questions.length <= 0){
            return false;
        }
        var examNo = this.data.examNo;
        var data = { 'exam_no': examNo, 'num': questions.length, 'questions': questions }
        wx.request2({
            url: '/exam/usage?exam_no=' + examNo,
            method: 'POST',
            data: data,
            success: res => {
            },
            fail: function () {
            }
        })
    },
    onUnload: function () {

        getApp().globalData.nowAnswerResultList = [];
        getApp().globalData.wrongAnswerList = [];
        getApp().globalData.score = 0;
        getApp().globalData.choseQB = '';
    },


})