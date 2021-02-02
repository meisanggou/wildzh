var app = getApp();
var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
var questionItems = [];
var brushList = new Array();
var brushDetail = new Array();
var STATE_WRONG = 'wrong';
var STATE_RIGHT = 'right'
var STATE_SKIP = 'skip'
var firstEnter = true;
Page({
    data: {
        remote_host: app.globalData.remote_host,
        optionChar: app.globalData.optionChar,
        examNo: null,
        examName: "",
        questionNum: -1,
        nowQuestionIndex: 0,
        questionAnswer: "",
        nowQuestion: null,
        showAnswer: false,
        showRemove: false,
        isReq: false
    },

    onLoad: function(options) {},
    onShow: function() {
        brushList = [];
        var initR = this.initExam();
        if (initR != false) {
            this.reqWrongAnswer();
        }
    },
    initExam: function() {
        that = this;
        var examNo = app.globalData.defaultExamNo;
        var examName = app.globalData.defaultExamNo;
        if (this.data.examNo != null && this.data.examNo != examNo) {
            // 切换题库后 又再次进入
            this.setData({
                questionNum: 0,
                nowQuestionIndex: 0,
                questionAnswer: "",
                nowQuestion: null,
                showAnswer: false,
                showRemove: false,
            })
            questionItems = [];
            firstEnter = true;
        }
        that.setData({
            examNo: examNo,
            examName: examName
        })
        if (examNo == null) {
            wx.showModal({
                title: '未选择题库',
                content: "未选择题库,确定进入【我的】选择题库",
                showCancel: false,
                success(res) {
                    wx.switchTab({
                        url: "/pages/me/me"
                    })
                }
            })
            return false;
        }
        return true;
    },
    reqWrongAnswer: function() {
        that = this
        var examNo = this.data.examNo;
        if (examNo == null) {
            return false;
        }
        var questionLen = questionItems.length;
        var minWrongTime = 0;
        if (questionLen <= 0) {
            wx.showLoading({
                title: '加载中...',
            })
        } else {
            minWrongTime = questionItems[questionLen - 1].wrong_time;
        }
        wx.request2({
            url: '/exam/wrong/?exam_no=' + examNo + "&min_wrong_time=" + minWrongTime,
            methods: "GET",
            success: function(res) {
                if (res.data.status != true) {
                    wx.hideLoading();
                    wx.showModal({
                        title: '无法访问题库',
                        content: "题库已删除，或无权访问。确定进入【我的】更换题库",
                        showCancel: false,
                        success(res) {
                            wx.switchTab({
                                url: "/pages/me/me"
                            })
                        }
                    })
                    return false;
                }
                var addQuestionItems = res.data.data;
                // 如果有新的错题，显示第一个，没有保持原来的显示
                var showIndex = that.data.nowQuestionIndex;
                var latestQuestionItems = questionItems;
                if (addQuestionItems.length > 0) {
                    // 按照错误时间排序 最新错题排到前面
                    addQuestionItems.sort(function(a, b) {
                        return a.wrong_time - b.wrong_time;
                    })
                    latestQuestionItems = addQuestionItems.concat(questionItems);
                    showIndex = 0;
                }
                // 判定最新的试题是否在
                questionItems = latestQuestionItems;
                wx.hideLoading();
                if (questionItems.length <= 0 && firstEnter) {
                    wx.showModal({
                        title: '无错题',
                        content: "没有发现错题",
                        showCancel: false,
                        success(res) {
                            // wx.navigateBack({
                            //     delta: 1
                            // })
                        }
                    })
                    firstEnter = false;
                    return false;
                }
                if (addQuestionItems.length > 0) {
                    // 请求questionItems
                    that.reqQuestion(examNo, 0, 0);
                }
            },
            fail: function({
                errMsg
            }) {
                wx.hideLoading();
                wx.showModal({
                    title: '页面请求失败',
                    content: "无法连接远程主机获取错题信息，确定返回首页",
                    showCancel: false,
                    success(res) {
                        wx.navigateBack({
                            delta: 1
                        })
                    }
                })
            }
        })
    },
    reqQuestion: function(exam_no, startIndex, showIndex) {
        if (exam_no == null) {
            console.info("Can not req, examNo is null");
            return false;
        }
        var isReq = that.data.isReq;
        if (isReq == true) {
            return false;
        } else {
            that.setData({
                isReq: true
            })
        }
        var nos = "";
        var endIndex = startIndex + 13;
        if (endIndex > questionItems.length) {
            endIndex = questionItems.length;
        }

        wx.showLoading({
            title: '加载题目中...',
        })
        for (var i = startIndex; i < endIndex; i++) {
            if ("options" in questionItems[i]){
                continue;
            }
            nos += "," + questionItems[i].question_no;
        }
        wx.request2({
            url: '/exam/questions/?exam_no=' + exam_no + "&nos=" + nos,
            method: 'GET',
            success: res => {
                wx.hideLoading();
                if (res.data.status == false) {
                    return;
                }
                var newItems = res.data.data;
                for (var i = endIndex - 1; i >= startIndex; i--) {
                    for (var j = 0; j < newItems.length; j++) {
                        if (questionItems[i].question_no == newItems[j].question_no) {
                            // questionItems[i]["question_desc"] = newItems[j]["question_desc"];
                            questionItems[i]["question_desc_rich"] = newItems[j]["question_desc_rich"]
                            // questionItems[i]["question_desc_url"] = newItems[j]["question_desc_url"];
                            questionItems[i]["options"] = newItems[j]["options"];
                            // questionItems[i]["answer"] = newItems[j]["answer"];
                            questionItems[i]["answer_rich"] = newItems[j]["answer_rich"]
                            break;
                        }
                    }
                }
                // 判断 是否questionItems有题
                if (questionItems.length <= 0) {
                    // 没有错题 有问题
                }
                if (showIndex != null) {
                    that.setData({
                        nowQuestion: questionItems[showIndex],
                        nowQuestionIndex: showIndex,
                        questionNum: questionItems.length
                    });
                }
                that.setData({
                    isReq: false
                })
            },
            fail: function({
                errMsg
            }) {
                wx.hideLoading();
                console.log('request fail', errMsg)
                that.setData({
                    isReq: false
                })
            }
        })
    },
    remove: function() {
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var questionLen = questionItems.length;
        wx.request2({
            url: '/exam/wrong/?exam_no=' + that.data.examNo,
            method: "DELETE",
            data: {
                "question_no": nowQuestion.question_no
            },
            success: function(res) {
                console.info(res.data);
            }
        })
        questionItems.splice(nowQuestionIndex, 1);
        questionLen = questionItems.length;
        if (questionLen <= 0) {
            questionItems = [];
            wx.showModal({
                title: '无错题',
                content: "已经没有错题",
                showCancel: false,
                success(res) {
                    wx.navigateBack({
                        delta: 1
                    })
                }
            })
            return true;
        }
        
        if (nowQuestionIndex >= questionLen) {
            nowQuestionIndex = questionLen - 1;
        }
        that.setData({
            nowQuestion: questionItems[nowQuestionIndex],
            nowQuestionIndex: nowQuestionIndex,
            questionNum: questionItems.length,
            showAnswer: false,
            showRemove: false
        })

    },
    after: function(afterNum) {
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var questionLen = questionItems.length;
        var nextIndex = nowQuestionIndex + afterNum;
        if (nowQuestionIndex >= questionItems.length - 1) {
            // 判断是否当前是否是最后一题
            wx.showToast({
                title: "已是最后一题",
                icon: "none",
                duration: 2000
            });
            return true;
        }
        if (nextIndex >= questionItems.length) {
            nextIndex = questionItems.length - 1;
        }
        if ("options" in questionItems[nextIndex]) {
            //错题 已经获取内容
            var nowQuestion = questionItems[nextIndex];
            that.setData({
                nowQuestion: nowQuestion,
                nowQuestionIndex: nextIndex,
                showAnswer: false,
                showRemove: false
            })
            // 判断紧接着10条是否都已预获取数据
            for (var i = 1; i < 11 && nextIndex + i < questionLen; i++) {
                if (!("options" in questionItems[nextIndex + i])) {
                    that.reqQuestion(that.data.examNo, nextIndex + i, null);
                    break;
                }
            }
        } else {
            // 错题没有获取内容
            wx.showLoading({
                title: '加载中...',
                mask: true
            })
            that.reqQuestion(that.data.examNo, nextIndex, nextIndex)
        }
    },
    after1: function() {
        that.after(1);
    },

    after10: function() {
        that.after(10);
    },
    before: function(preNum) {
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var preIndex = nowQuestionIndex - preNum;
        if (nowQuestionIndex <= 0) {
            // 判断是否当前是否是第一题
            wx.showToast({
                title: "已是第一题",
                icon: "none",
                duration: 1000
            });
            return true;
        }
        if (preIndex <= 0) {
            preIndex = 0;
        }
        var nowQuestion = questionItems[preIndex];
        that.setData({
            nowQuestion: nowQuestion,
            nowQuestionIndex: preIndex,
            showAnswer: false,
            showRemove: false
        })

    },
    before1: function() {
        that.before(1);
    },

    before10: function() {
        that.before(10);
    },
    choseItem: function(e) {
        var choseIndex = parseInt(e.currentTarget.dataset.choseitem);
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var showRemove = false;
        for (var index in questionItems[nowQuestionIndex]["options"]) {
            nowQuestion["options"][index]["class"] = "noChose";
        }
        if (parseInt(nowQuestion["options"][choseIndex]["score"]) > 0) {
            nowQuestion["options"][choseIndex]["class"] = "chose";
            this.addBrushNum(nowQuestion.question_no, STATE_RIGHT);
            showRemove = true;
        } else {
            this.addBrushNum(nowQuestion.question_no, STATE_WRONG);
            nowQuestion["options"][choseIndex]["class"] = "errorChose";
        }

        that.setData({
            nowQuestion: nowQuestion,
            showRemove: showRemove
        })
        // 显示答案
        that.showAnswer();
    },
    showAnswer: function(e) {
        var nowQuestion = that.data.nowQuestion;
        if(nowQuestion == null){
            return false;
        }
        this.addBrushNum(nowQuestion.question_no, STATE_SKIP);
        var questionAnswer = new Array();
        for (var index in nowQuestion.options) {
            if (parseInt(nowQuestion.options[index]["score"]) > 0) {
                var tmp_answer = new Array(app.globalData.optionChar[index], "、");
                questionAnswer = questionAnswer.concat(tmp_answer);
                questionAnswer = questionAnswer.concat(nowQuestion.options[index]["desc_rich"]);
            }
        }
        if (questionAnswer.length == 0) {
            questionAnswer[0] = "没有答案"
        }
        that.setData({
            showAnswer: true,
            questionAnswer: questionAnswer
        })
    },
    addBrushNum: function (q_no, state) {
        if (brushList.indexOf(q_no) >= 0) {
            return false;
        }
        brushList.push(q_no);
        brushDetail.push({'no': q_no, 'state': state});
        this.saveBrushNum();
    },
    saveBrushNum: function () {
        if (brushDetail.length <= 0) {
            return false;
        }
        var _num = brushDetail.length;
        var questions = new Array();
        while(brushDetail.length > 0){
            questions.push(brushDetail.pop());
        }
        var examNo = this.data.examNo;
        brushDetail = new Array();
        var data = {
            'exam_no': examNo,
            'num': _num,
            'questions': questions
        }
        wx.request2({
            url: '/exam/usage?exam_no=' + examNo,
            method: 'POST',
            data: data,
            success: res => {},
            fail: function () {
                brushDetail.concat(questions);
            }
        })
    },
    // 触摸开始事件
    touchStart: function(e) {
        touchStartX = e.touches[0].pageX; // 获取触摸时的原点
        touchStartY = e.touches[0].pageY;
        // 使用js计时器记录时间    
        touchInterval = setInterval(function() {
            touchTime++;
        }, 100);
    },
    // 触摸结束事件
    touchEnd: function(e) {
        var touchEndX = e.changedTouches[0].pageX;
        var touchEndY = e.changedTouches[0].pageY;
        var touchMoveX = touchEndX - touchStartX;
        var touchMoveY = touchEndY - touchStartY;
        if (Math.abs(touchMoveY) < 0.618 * Math.abs(touchMoveX)) {
            // 向左滑动   
            if (touchMoveX <= -93 && touchTime < 10) {
                //执行切换页面的方法
                that.after1();
            }
            // 向右滑动   
            if (touchMoveX >= 93 && touchTime < 10) {
                that.before1();
            }
        }

        clearInterval(touchInterval); // 清除setInterval
        touchTime = 0;
    }


})