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
        isReq: false,
        progressStorageKey: "",
        answerIndex: null,
        subjectsArray: ['无', '微观经济学', '宏观经济学', '政治经济学'],
    },

    onLoad: function (options) {
        var currentUser = app.getOrSetCurrentUserData();
        if (currentUser != null) {
            if ("role" in currentUser) {
                if ((currentUser.role & 2) == 2) {
                }
            }
        }
        this.setData({
            examNo: app.globalData.defaultExamNo,
            examName: app.globalData.defaultExamName
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
                progressStorageKey += "_" + options["question_subject"];
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
    reqQuestion: function (startIndex, updateShow = false, stepNum = 13) {
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

        if (_end > questionItems.length) {
            _end = questionItems.length;
        }
        if (_start < 0) {
            _start = 0
        }
        for (var i = _start; i < _end; i++) {
            if (("options" in questionItems[i]) && questionItems[i].forceUpdate != true) {
                continue;
            }
            nos += "," + questionItems[i].question_no;
        }
        wx.request2({
            url: '/exam/questions/?no_rich=true&exam_no=' + exam_no + "&nos=" + nos,
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
                            questionItems[i]["options"] = newItems[j]["options"];
                            questionItems[i]["answer"] = newItems[j]["answer"];
                            questionItems[i]["question_subject"] = newItems[j]["question_subject"];
                            questionItems[i]["inside_mark"] = newItems[j]["inside_mark"];
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
                        questionNum: questionItems.length
                    });
                    that.changeNowQuestion(startIndex);
                }
                else if (startIndex == that.data.nowQuestionIndex) {
                    // 如果当前请求的内容正好是当前显示的，需要重新更新一下答案显示。答案显示是拼出来的没和变量关联
                }
                that.setData({
                    isReq: false
                })
            },
            fail: function ({
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
    after: function (afterNum) {
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
    after1: function () {
        that.after(1);
    },

    after10: function () {
        that.after(10);
    },
    before: function (preNum) {
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
    before1: function () {
        that.before(1)

    },

    before10: function () {
        that.before(10)
    },
    changeNowQuestion: function (index) {
        var nowQuestion = this.data.questionItems[index];
        if (nowQuestion.question_subject == null) {
            nowQuestion.question_subject = 0;
        }
        var answerIndex = null;
        for (var i in nowQuestion.options) {
            if (parseInt(nowQuestion.options[i]["score"]) > 0) {
                answerIndex = i;
                break;
            }
        }

        this.setData({
            nowQuestion: nowQuestion,
            nowQuestionIndex: index,
            answerIndex: answerIndex
        })
    },
    changeSubject: function (event) {
        var selected = event.detail.value;
        var nowQuestion = this.data.nowQuestion;
        nowQuestion.question_subject = selected;
        this.setData({
            nowQuestion: nowQuestion
        })
    },
    updateAnswerOption: function (event) {
        var selected = event.detail.value;
        var nowQuestion = this.data.nowQuestion;
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
        this.setData({
            answerIndex: selected
        })
    },
    updateAnswer: function () {
    },

    updateQuestion: function (e) {
        var nowQuestion = this.data.nowQuestion;
        var uData = new Object();
        var pData = e.detail.value;
        uData.question_no = nowQuestion.question_no;
        if (pData.question_desc != nowQuestion.question_desc) {
            uData.question_desc = pData.question_desc;
        }
        if (pData.answer != nowQuestion.answer) {
            uData.answer = pData.answer;
        }
        uData.options = nowQuestion.options;
        for (var i = 0; i < uData.options.length; i++) {
            uData.options[i].desc = pData["option_" + i]
        }
        uData.question_subject = nowQuestion.question_subject;
        nowQuestion.forceUpdate = true;

        var index = this.data.nowQuestionIndex;
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

    onUnload: function () {

        if (that.data.examNo == null || that.data.nowQuestion == null) {
            return false;
        }
        if (this.data.progressStorageKey == "" || this.data.nowQuestionIndex <= 0) {
            return false;
        }
        app.getOrSetExamCacheData(this.data.progressStorageKey, this.data.nowQuestionIndex);

    },
    // 触摸开始事件
    touchStart: function (e) {
        touchStartX = e.touches[0].pageX; // 获取触摸时的原点
        touchStartY = e.touches[0].pageY;
        // 使用js计时器记录时间    
        touchInterval = setInterval(function () {
            touchTime++;
        }, 100);
    },
    // 触摸结束事件
    touchEnd: function (e) {
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