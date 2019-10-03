var app = getApp();
var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
Page({
    data: {
        remote_host: app.globalData.remote_host,
        allExams: [],
        optionChar: app.globalData.optionChar,
        examNo: null,
        examName: "",
        questionNum: 0,
        nowQuestionIndex: 0,
        questionItems: [],
        questionAnswer: new Array(),
        nowQuestion: null,
        showAnswer: false,
        isShowSubject: true,
        isReq: false,
        progressStorageKey: "",
        canUpdate: false,
        isUpdateAnswer: false
    },

    onLoad: function(options) {
        var canUpdate = false;
        var currentUser = app.getOrSetCurrentUserData();
        if (currentUser != null) {
            if ("role" in currentUser) {
                if((currentUser.role & 2) == 2){
                    canUpdate = true;
                }
            }
        }
        this.setData({
            examNo: app.globalData.defaultExamNo,
            examName: app.globalData.defaultExamName,
            canUpdate: canUpdate
        });
        that = this;
        var args_url = "";
        var progressStorageKey = "training";
        if (that.data.examNo != null) {
            if ("select_mode" in options) {
                args_url += "select_mode=" + options["select_mode"] + "&";
                progressStorageKey += "_" + options["select_mode"];
            } else {
                progressStorageKey += "_" + 0;
            }
            if ("question_subject" in options) {
                args_url += "question_subject=" + options["question_subject"] + "&";
                progressStorageKey += "_" + options["question_subject"];
                that.setData({
                    isShowSubject: false
                })
            } else {
                progressStorageKey += "_" + 0;
            }
            this.setData({
                progressStorageKey: progressStorageKey
            });
            args_url += "exam_no=" + that.data.examNo;
            wx.request2({
                url: '/exam/questions/no/?' + args_url,
                method: 'GET',
                success: res => {
                    that.setData({
                        questionNum: res.data.data["questions"].length,
                        questionItems: res.data.data["questions"]
                    })
                    if (res.data.data["questions"].length <= 0) {
                        wx.showModal({
                            title: '无题目',
                            content: "无相关题目，确定返回",
                            showCancel: false,
                            success(res) {
                                wx.navigateBack({
                                    delta: 1
                                })
                            }
                        })
                    } else {
                        // 请求questionItems
                        var progressIndex = app.getOrSetExamCacheData(that.data.progressStorageKey);
                        if (progressIndex == null || typeof progressIndex != 'number' || progressIndex <= 0) {
                            progressIndex = 0;
                        }
                        that.reqQuestion(progressIndex, true);
                    }
                }
            })
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
            })
        }

    },
    reqQuestion: function(startIndex, updateShow = false, stepNum = 13) {
        that = this;
        var exam_no = that.data.examNo;
        if (that.data.examNo == null) {
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
        var questionItems = that.data.questionItems;
        var nos = "";
        var _start = -1;
        var _end = -1;
        if (stepNum < 0) {
            _start = startIndex + stepNum;
            _end = startIndex + 1
        } else {
            _start = startIndex;
            _end = startIndex + stepNum;
        }
        if(_end > questionItems.length){
            _end = questionItems.length;
        }
        if(_start < 0){
            _start = 0
        }
        for (var i = _start; i < _end; i++) {
            if (("options" in questionItems[i]) && questionItems[i].forceUpdate != true) {
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
                for (var i = _end - 1; i >= _start; i--) {
                    for (var j = 0; j < newItems.length; j++) {
                        if (questionItems[i].question_no == newItems[j].question_no) {
                            questionItems[i]["question_desc"] = newItems[j]["question_desc"];
                            questionItems[i]["question_desc_rich"] = newItems[j]["question_desc_rich"]
                            questionItems[i]["question_desc_url"] = newItems[j]["question_desc_url"];
                            questionItems[i]["options"] = newItems[j]["options"];
                            questionItems[i]["answer"] = newItems[j]["answer"];
                            questionItems[i]["answer_rich"] = newItems[j]["answer_rich"]
                            questionItems[i].forceUpdate = false;
                            break;
                        }
                    }
                }
                // 判断 是否questionItems有题
                if (questionItems.length <= 0) {
                    // 没有错题 有问题
                }
                if (updateShow) {
                    that.setData({
                        questionItems: questionItems,
                        nowQuestion: questionItems[startIndex],
                        nowQuestionIndex: startIndex,
                        questionNum: questionItems.length
                    });
                }
                else if(startIndex == that.data.nowQuestionIndex){
                    // 如果当前请求的内容正好是当前显示的，需要重新更新一下答案显示。答案显示是拼出来的没和变量关联
                    if (that.data.showAnswer) {
                        that.showAnswer();
                    }
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
    after: function(afterNum) {
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var questionItems = that.data.questionItems;
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
            //已经获取内容
            var nowQuestion = questionItems[nextIndex];
            that.changeNowQuestion(nextIndex);
            // 判断紧接着10条是否都已预获取数据
            for (var i = 1; i < 11 && nextIndex + i < questionLen; i++) {
                if (!("options" in questionItems[nextIndex + i])) {
                    that.reqQuestion(nextIndex + i);
                    break;
                }
            }
        } else {
            // 没有获取内容
            wx.showLoading({
                title: '加载中...',
                mask: true
            })
            that.reqQuestion(nextIndex, true)
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
        var questionItems = that.data.questionItems;
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
        if ("options" in questionItems[preIndex]) {
            //已经获取内容
            that.changeNowQuestion(preIndex);
        } else {
            // 没有获取内容
            wx.showLoading({
                title: '加载中...',
                mask: true
            })
            that.reqQuestion(preIndex, true, -13)
        }

    },
    before1: function() {
        that.before(1)

    },

    before10: function() {
        that.before(10)
    },
    changeNowQuestion: function(index){
        var nowQuestion = this.data.questionItems[index];
        this.setData({
            nowQuestion: nowQuestion,
            nowQuestionIndex: index,
            showAnswer: false,
            isUpdateAnswer: false
        })
    },
    showAnswer: function(e) {
        var nowQuestion = that.data.nowQuestion;
        if (nowQuestion == null) {
            return false;
        }
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
    choseItem: function(e) {
        var choseIndex = parseInt(e.currentTarget.dataset.choseitem);
        var questionItems = that.data.questionItems;
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        for (var index in questionItems[nowQuestionIndex]["options"]) {
            nowQuestion["options"][index]["class"] = "noChose";

        }
        if (parseInt(nowQuestion["options"][choseIndex]["score"]) > 0) {
            nowQuestion["options"][choseIndex]["class"] = "chose";
            // 自动进入下一题
            var interval = setInterval(function() {
                clearInterval(interval)
                that.after1();
            }, 1000)
        } else {
            nowQuestion["options"][choseIndex]["class"] = "errorChose";
            // 显示答案
            that.showAnswer();
            // 记录错题
            that.recordWrong(that.data.examNo, [nowQuestion.question_no]);
        }
        that.setData({
            nowQuestion: nowQuestion
        })
    },
    updateAnswerOption: function(event) {
        var selected = event.detail.value;
        var nowQuestion = this.data.nowQuestion;
        var index = this.data.nowQuestionIndex;
        var options = nowQuestion.options;
        var optLen = options.length;
        for (var i = 0; i < optLen; i++) {
            if (i == selected) {
                if (parseInt(options[i]["score"]) > 0) {
                    return false;
                }
                options[i]["score"] = 1;
            } else {
                options[i]["score"] = 0;
            }
        }
        nowQuestion.forceUpdate = true;
        this.updateQuestion(nowQuestion.question_no, index, options);
    },
    updateAnswer: function () {
        this.setData({
            isUpdateAnswer: true
        });
    },
    actionUpdateAnswer: function(){
        var nowQuestion = this.data.nowQuestion;
        var index = this.data.nowQuestionIndex;
        nowQuestion.forceUpdate = true;
        this.updateQuestion(nowQuestion.question_no, index, null, nowQuestion.answer);
    },
    updateQuestion: function(questionNo, index, options = null, answer = null) {
        var uData = new Object();
        uData["question_no"] = questionNo;
        if (options != null) {
            uData["options"] = options;
        }
        if (answer != null) {
            uData["answer"] = answer;
        }
        wx.request2({
            url: '/exam/questions/?exam_no=' + this.data.examNo,
            method: 'PUT',
            data: uData,
            success: res => {
                if (res.data.status == false) {
                    return;
                }
                wx.showToast({
                    title: "更新成功",
                    icon: "none",
                    duration: 1000
                });
                that.reqQuestion(index, false)
            }
        })
    },
    recordWrong: function(exam_no, wrong_question) {
        wx.request2({
            url: '/exam/wrong/',
            method: "POST",
            data: {
                "question_no": wrong_question,
                "exam_no": exam_no
            }
        })
    },
    onUnload: function() {
        console.info("un load")
        if (that.data.examNo == null || that.data.nowQuestion == null) {
            return false;
        }
        if (this.data.progressStorageKey == "" || this.data.nowQuestionIndex <= 0) {
            return false;
        }
        app.getOrSetExamCacheData(this.data.progressStorageKey, this.data.nowQuestionIndex);

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
            if (touchMoveX <= -30 && touchTime < 10) {
                //执行切换页面的方法
                that.after1();
            }
            // 向右滑动   
            if (touchMoveX >= 30 && touchTime < 10) {
                that.before1();
            }
        }

        clearInterval(touchInterval); // 清除setInterval
        touchTime = 0;
    }

})