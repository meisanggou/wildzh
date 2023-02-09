var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
var STATE_WRONG = 'wrong';
var STATE_RIGHT = 'right'
var STATE_SKIP = 'skip'
// 计时相关
var TIMER_USE = null;
var basicSecond = 0;
var startTime = 0;
var dt = require("../common/datetime_tools.js");

var app = getApp();
Page({
    data: {
        remote_host: app.globalData.remote_host,
        optionChar: app.globalData.optionChar,
        examNo: null,
        examName: "",
        answerTime: "00:00:00",
        question_subject: null,
        questionItems: [],
        nowQuestion: null,
        nowQuestionIndex: 0,
        showAnswer: false,
        totalQuestionNumber: 0,
        score: 0,
        showSurvey: false, // 显示测试情况
        mode: 'answer',
        rightNum: 0,
        skipNum: 0,
    },

    onLoad: function (options) {
        var question_subject = null;
        if ("question_subject" in options) {
            question_subject = options["question_subject"];
        }
        this.setData({
            examNo: app.globalData.defaultExamNo,
            examName: app.globalData.defaultExamName,
            question_subject: question_subject
        });
        that = this;
        this.initTimePro();
        if (that.data.examNo == null) {
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
        } else {
            wx.showLoading({
                title: '加载中',
            })
            if ("strategy_id" in options) {
                this.getStrategy(this.data.examNo, options["strategy_id"]);
            } else {
                var strategy_items = [{
                    'num': 20,
                    'value': -1
                }];
                if ("select_mode" in options) {
                    strategy_items[0]['value'] = options["select_mode"];
                }
                this.getQuestionbyStrategy(strategy_items);
            }
            return true;
        }


    },
    initTimePro() {
        var that = this;
        startTime = dt.get_timestamp();
        this.runTimer();
    },
    runTimer: function () {
        var that = this;
        TIMER_USE = setInterval(function () {
            var useTime = (dt.get_timestamp() - startTime) / 1000;
            var s = dt.duration_str(parseInt(useTime + basicSecond));
            that.setData({
                answerTime: s
            })
        }, 1000);
    },
    getStrategy(examNo, strategy_id) {
        var that = this;
        wx.request2({
            url: '/exam/strategy/' + examNo,
            method: 'GET',
            success: res => {
                wx.hideLoading();
                var resData = res.data.data;
                var strategies = resData['strategies'];
                for (var i = 0; i < strategies.length; i++) {
                    if (strategies[i].strategy_id == strategy_id) {
                        var strategy_items = strategies[i]["strategy_items"];
                        var totalQuestionNumber = 0
                        for (var j = 0; j < strategy_items.length; j++) {
                            totalQuestionNumber += strategy_items[j]['num'];
                        }
                        that.setData({
                            totalQuestionNumber: totalQuestionNumber
                        })
                        that.getQuestionbyStrategy(strategy_items);
                        wx.showLoading({
                            title: '组卷中...',
                        })
                        return;
                    }
                }
                wx.showModal({
                    title: '组卷策略不存在',
                    content: "请返回重试！",
                    showCancel: false,
                    success(res) {
                        wx.navigateBack({
                            delta: 1
                        })
                    }
                })
                return;
            },
            fail: res => {
                wx.showModal({
                    title: '访问失败',
                    content: "请稍后重试！",
                    showCancel: false,
                    success(res) {
                        wx.navigateBack({
                            delta: 1
                        })
                    }
                })
                return;
            }
        })
    },
    getQuestionbyStrategy(strategy_items) {
        var that = this;
        for (var i = 0; i < strategy_items.length; i++) {
            var item = strategy_items[i];
            if ('loaded' in item) {
                continue;
            } else {
                var exclude_nos = "";
                var existItems = that.data.questionItems;
                for (var k = 0; k < existItems.length; k++) {
                    var _item = existItems[k];
                    if (_item['select_mode'] == item['value']) {
                        exclude_nos += "," + _item['question_no'];
                    }
                }
                var url = '/exam/questions/?fmt_version=2&exam_no=' + that.data.examNo + "&num=" + item["num"];
                if (exclude_nos != "") {
                    url += "&exclude_nos=" + exclude_nos;
                }
                url += "&select_mode=" + item["value"];
                if (this.data.question_subject != null) {
                    url += "&question_subject=" + this.data.question_subject;
                }
                wx.request2({
                    url: url,
                    method: 'GET',
                    success: res => {
                        if (res.data.status == false) {
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
                            return;
                        }
                        var questionItems = res.data.data;
                        var oldItems = that.data.questionItems;
                        questionItems = oldItems.concat(res.data.data)
                        var data = {
                            "questionItems": questionItems
                        };
                        if (that.data.nowQuestion == null && questionItems.length > 0) {
                            data['nowQuestion'] = questionItems[0];
                            data['nowQuestion']['displayed'] = true;
                            wx.hideLoading();
                        }
                        that.setData(data);
                        item['loaded'] = true;
                        that.getQuestionbyStrategy(strategy_items);
                    },
                    fail: res => {
                        setTimeout(function () {
                            that.getQuestionbyStrategy(strategy_items);
                        }, 10000);

                    }
                })
                return;
            }
        }
        var questionItems = this.data.questionItems;
        if (questionItems.length <= 0) {
            wx.hideLoading();
            wx.showModal({
                title: '无试题',
                content: "暂无相关试题，请重新选择试题类型或者更换试题库",
                showCancel: false,
                success(res) {
                    wx.navigateBack({
                        delta: 1
                    })
                }
            })
            return;
        }
        if (questionItems.length != this.data.totalQuestionNumber) {
            this.setData({
                totalQuestionNumber: questionItems.length
            })
        }
    },
    changeNowQuestion: function (index) {
        var nowQuestion = this.data.questionItems[index];
        wx.pageScrollTo({
            scrollTop: 0,
            duration: 0,
        })
        // if ("options" in nowQuestion) {
        //     //已经获取内容
        // } else {
        //     // 没有获取内容
        //     wx.showLoading({
        //         title: '加载中...',
        //         mask: true
        //     })
        //     that.reqQuestion(index, true);
        //     return;
        // }
        this.setData({
            nowQuestion: nowQuestion,
            nowQuestionIndex: index,
        })
    },
    choseOption: function (e) {
        var choseRight = e.detail.choseRight;
        var selectedOpts = e.detail.selectedOpts;

        var questionItems = that.data.questionItems;
        var nowQuestionIndex = that.data.nowQuestionIndex;

        questionItems[nowQuestionIndex]["right"] = choseRight;
        questionItems[nowQuestionIndex]["selectedOpts"] = selectedOpts;

        var nextQuestionNumber = nowQuestionIndex + 1;
        if (nextQuestionNumber == that.data.questionItems.length) {
            that.submit();
        } else {
            var interval = setInterval(function () {
                clearInterval(interval)
                questionItems[nextQuestionNumber]['displayed'] = true;
                that.setData({
                    nowQuestionIndex: nextQuestionNumber,
                    nowQuestion: questionItems[nextQuestionNumber]
                })
            }, 1000)

        }
        this.setData({
            ['questionItems[' + nowQuestionIndex + ']']: questionItems[nowQuestionIndex]
        })
    },
    submit: function () {
        if (this.data.mode != 'answer') {
            wx.showToast({
                title: '已是最后一题',
            })
            return false;
        }
        var msg = '确定要交卷吗？';
        if (this.data.questionItems.length != this.data.totalQuestionNumber) {
            msg = '题目信息都没加载完，确定要交卷吗？';
        }
        wx.showModal({
            title: '交卷',
            content: msg,
            success(res) {
                if (res.confirm) {
                    var timestamp = (new Date()).valueOf()
                    var test_id = app.globalData.testIdPrefix + that.data.examNo + "_" + timestamp;
                    wx.setStorageSync(test_id, that.data.questionItems);
                    var allTestIds = wx.getStorageSync(app.globalData.allTestIdKey)
                    if (allTestIds) {
                        allTestIds = allTestIds + "," + test_id;
                    } else {
                        allTestIds = test_id;
                    }
                    wx.setStorage({
                        key: app.globalData.allTestIdKey,
                        data: allTestIds,
                    })
                    that.setResult();
                }
            }
        })

    },
    setResult: function () {
        clearInterval(TIMER_USE);
        var questionItems = this.data.questionItems;
        var questionNum = questionItems.length;
        var score = 0;
        var skipNum = 0;
        var showNums = [];
        // var wrong_question = [];
        var questions = [];
        for (var i = 0; i < questionNum;) {
            var lineNums = [];
            for (var j = 0; j < 5 && i < questionNum; i++, j++) {
                lineNums.push(i);
                if (!('displayed' in questionItems[i])) {
                    skipNum += 1;
                    continue;
                }
                if (!('right' in questionItems[i])) {
                    questions.push({
                        'no': questionItems[i].question_no,
                        'state': STATE_SKIP
                    })
                    skipNum += 1;
                    continue;
                }
                if (questionItems[i]["right"] == true) {
                    score = score + 1;
                    questions.push({
                        'no': questionItems[i].question_no,
                        'state': STATE_RIGHT
                    })
                } else if (questionItems[i]["right"] == false) {
                    questions.push({
                        'no': questionItems[i].question_no,
                        'state': STATE_WRONG
                    })
                    // wrong_question.push(res.data[i]["question_no"]);
                }

            }
            showNums.push(lineNums);
        }
        that.setData({
            allQuestionIndexs: showNums,
            score: score,
            totalScore: questionNum,
            mode: 'answer-show',
            showAnswer: true,
            showSurvey: true,
            rightNum: score,
            skipNum: skipNum
        })
        that.saveBrushNum(questions);
    },
    showDeatil: function (e) {
        var index = e.currentTarget.dataset.index;
        this.setData({
            showSurvey: false
        })
        this.changeNowQuestion(index);
    },
    returnSurvey: function (e) {
        this.setData({
            showSurvey: true
        })
    },
    after1: function () {
        wx.pageScrollTo({
            scrollTop: 0,
            duration: 0,
        })
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var totalQuestionNumber = that.data.totalQuestionNumber;
        var questionItems = that.data.questionItems;
        if (nowQuestionIndex + 1 < totalQuestionNumber) {
            nowQuestionIndex++;
            if (nowQuestionIndex >= questionItems.length) {
                wx.showModal({
                    title: '试题未加载',
                    content: "试题尚未加载出来，请检查网络，或稍等片刻！",
                    showCancel: false,
                    success(res) {}
                })
                return false;
            }
            questionItems[nowQuestionIndex]['displayed'] = true;
            that.setData({
                nowQuestion: questionItems[nowQuestionIndex],
                nowQuestionIndex: nowQuestionIndex
            })
        } else {
            if (this.data.mode == 'answer') {
                this.submit();
            } else {
                wx.showToast({
                    title: '已是最后一题',
                })
            }
        }
    },

    before1: function () {
        wx.pageScrollTo({
            scrollTop: 0,
            duration: 0,
        })
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var questionItems = that.data.questionItems;
        if (nowQuestionIndex > 0) {
            nowQuestionIndex--;
            questionItems[nowQuestionIndex]['displayed'] = true;
            that.setData({
                nowQuestion: questionItems[nowQuestionIndex],
                nowQuestionIndex: nowQuestionIndex
            })
        }
    },
    
    saveBrushNum: function (questions) {
        if (questions.length <= 0) {
            return false;
        }
        var examNo = this.data.examNo;
        var data = {
            'exam_no': examNo,
            'num': questions.length,
            'questions': questions
        }
        wx.request2({
            url: '/exam/usage?exam_no=' + examNo,
            method: 'POST',
            data: data,
            success: res => {},
            fail: function () {}
        })
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