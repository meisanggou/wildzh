var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;

var app = getApp();
Page({

    data: {
        remote_host: app.globalData.remote_host,
        optionChar: app.globalData.optionChar,
        examNo: 0,
        examName: "测试",
        questionItems: [],
        nowQuestion: null,
        nowQuestionIndex: 0,
        totalQuestionNumber: 0,
        score: 0
    },

    onLoad: function(options) {
        this.setData({
            examNo: app.globalData.defaultExamNo,
            examName: app.globalData.defaultExamName
        });
        that = this;
        that = this;
        if (that.data.examNo == null) {
            wx.showModal({
                title: '页面加载失败',
                content: "页面缺少必要的参数，确定返回首页",
                showCancel: false,
                success(res) {
                    wx.navigateBack({
                        delta: 1
                    })
                }
            })
        } else {
            wx.showLoading({
                title: '加载中',
            })

            wx.request2({
                url: '/exam/questions/?exam_no=' + that.data.examNo + "&num=20",
                method: 'GET',
                success: res => {
                    if (res.data.status == false) {
                        wx.showModal({
                            title: '试题加载失败',
                            content: "加载试题失败，确定返回首页，重新选择试题",
                            showCancel: false,
                            success(res) {
                                wx.navigateBack({
                                    delta: 1
                                })
                            }
                        })
                        return;
                    }
                    var questionItems = res.data.data;
                    that.setData({
                        questionItems: questionItems,
                        nowQuestion: questionItems[0],
                        totalQuestionNumber: questionItems.length
                    });
                    wx.hideLoading();
                }
            })
        }


    },

    choseItem: function(e) {
        // that = this;
        var choseIndex = parseInt(e.currentTarget.dataset.choseitem);
        var questionItems = that.data.questionItems;
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        for (var index in questionItems[nowQuestionIndex]["options"]) {
            questionItems[nowQuestionIndex]["options"][index]["chosed"] = false;
            nowQuestion["options"][index]["chosed"] = false;
        }
        questionItems[nowQuestionIndex]["options"][choseIndex]["chosed"] = true;
        nowQuestion["options"][choseIndex]["chosed"] = true;
        if (parseInt(questionItems[nowQuestionIndex]["options"][choseIndex]["score"]) > 0) {
            questionItems[nowQuestionIndex]["right"] = true;
        } else {
            questionItems[nowQuestionIndex]["right"] = false;
        }
        that.setData({
            nowQuestion: nowQuestion
        })
        var nextQuestionNumber = nowQuestionIndex + 1;
        if (nextQuestionNumber == that.data.questionItems.length) {
            that.submit();
        } else {
            var interval = setInterval(function() {
                clearInterval(interval)
                that.setData({
                    nowQuestionIndex: nextQuestionNumber,
                    nowQuestion: questionItems[nextQuestionNumber]
                })
            }, 1000)

        }
    },

    submit: function() {
        wx.showModal({
            title: '交卷',
            content: "确定要交卷吗？",
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

                    wx.redirectTo({
                        url: '../result/result?exam_no=' + that.data.examNo + "&timestamp=" + timestamp
                    })
                }
            }
        })

    },
    after1: function() {
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var totalQuestionNumber = that.data.totalQuestionNumber;
        var questionItems = that.data.questionItems;
        if (nowQuestionIndex + 1 < totalQuestionNumber) {
            nowQuestionIndex++;
            that.setData({
                nowQuestion: questionItems[nowQuestionIndex],
                nowQuestionIndex: nowQuestionIndex
            })
        }
    },

    before1: function() {
        var nowQuestionIndex = that.data.nowQuestionIndex;
        var questionItems = that.data.questionItems;
        if (nowQuestionIndex > 0) {
            nowQuestionIndex--;
            that.setData({
                nowQuestion: questionItems[nowQuestionIndex],
                nowQuestionIndex: nowQuestionIndex
            })
        }
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