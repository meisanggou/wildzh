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
        skipNums: [1],
        skipIndex: 0,
        optionChar: app.globalData.optionChar,
        examNo: null,
        examName: "",
        questionNum: 0,
        nowQuestionIndex: 0,
        questionItems: [],
        questionAnswer: new Array(),
        nowQuestion: null,
        showAnswer: false,
        isShowSubject: false,
        isReq: false,
        progressStorageKey: ""
    },

    onLoad: function(options) {
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
            wx.showLoading({
                title: '试题加载中',
            });
            args_url += "exam_no=" + that.data.examNo;
            wx.request2({
                url: '/exam/questions/no/?' + args_url,
                method: 'GET',
                success: res => {
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
                        return
                    }
                    that.setData({
                        questionNum: res.data.data["questions"].length,
                        questionItems: res.data.data["questions"]
                    })
                    if (res.data.data["questions"].length <= 0) {
                        wx.hideLoading();
                        wx.showModal({
                            title: '无题目',
                            content: "无相关题目，确定返回",
                            showCancel: false,
                            success(res) {
                                wx.switchTab({
                                    url: "/pages/me/me"
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
                            // questionItems[i]["answer"] = newItems[j]["answer"];
                            questionItems[i]["answer_rich"] = newItems[j]["answer_rich"]
                            questionItems[i]["question_source"] = newItems[j]["question_source"]
                            // for (var qd_index in questionItems[i]["question_desc_rich"]) {
                            //     var qd_item = questionItems[i]["question_desc_rich"][qd_index];
                            //     if (typeof qd_item == "string") {
                            //         questionItems[i]["question_desc_rich"][qd_index] = qd_item.replace(/\\n/g, '\n')
                            //     }
                            // }
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
                } else if (startIndex == that.data.nowQuestionIndex) {
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
            wx.showModal({
                title: "已是最后一题",
                content: "是否从头开始练习？",
                showCancel: true,
                icon: "none",
                success: function(res) {
                    if (res.confirm) {
                        that.reqQuestion(0, true)
                    }
                }
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
    setSkipNums(num, end_num) {
        var max_times = 5;
        var skipIndex = 0;
        var _num = num;
        var interval = 10;
        var r = [];
        var times = 0;
        var p_num = 0
        while (num > 1) {
            p_num = num - interval;
            if (p_num > 1)
                r.push(p_num)
            else {
                r.push(1)
                break
            }
            times += 1
            if (times >= max_times){
                interval *= 10;
                times = 0;
            }
            
            num = p_num;
        }
        r.sort(function(a, b){return a-b;});
        r.push(_num);
        skipIndex = r.length - 1;
        num = _num;
        interval = 10;
        times = 0;
        while (num < end_num) {
            p_num = num + interval
            if (p_num >= end_num) {
                r.push(end_num);
                break
            } else {
                r.push(p_num);
            }
            times += 1;
            if (times >= max_times){
                interval *= 10;
                times = 0;
            }
            num = p_num;
        }
        this.setData({
            skipNums: r,
            skipIndex: skipIndex
        })
        return r;
        
    },
    skipAction: function(e){
        var index = e.detail.value;
        this.changeNowQuestion(this.data.skipNums[index] - 1);
    },
    changeNowQuestion: function(index) {
        var skipNums = [];
        var nowQuestion = this.data.questionItems[index];
        if ("options" in nowQuestion) {
            //已经获取内容
        } else {
            // 没有获取内容
            wx.showLoading({
                title: '加载中...',
                mask: true
            })
            that.reqQuestion(index, true);
            return;
        }
        this.setData({
            nowQuestion: nowQuestion,
            nowQuestionIndex: index,
            showAnswer: false
        })
        this.setSkipNums(index + 1, this.data.questionItems.length);
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
            if (this.data.showAnswer == false) {
                // 当前显示答案 不进入下一题
                var interval = setInterval(function() {
                    clearInterval(interval)
                    that.after1();
                }, 1000)
            }
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
    actionUpdateAnswer: function() {
        var nowQuestion = this.data.nowQuestion;
        var index = this.data.nowQuestionIndex;
        nowQuestion.forceUpdate = true;
        this.updateQuestion(nowQuestion.question_no, index, null, nowQuestion.answer);
    },
    previewImage: function(event) {
        var src = event.currentTarget.dataset.src; //获取data-src
        //图片预览
        console.info(src)
        // wx.previewImage({
        //     // current: src, // 当前显示图片的http链接
        //     urls: [src], // 需要预览的图片http链接列表
        //     fail: function(e){
        //         console.info("preview fail");
        //         console.info(e);
        //     },
        //     complete: function(e){
        //         console.info("preview complete");
        //         console.info(e);
        //     }
        // })

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

        var absMoveX = Math.abs(touchMoveX);
        var absMoveY = Math.abs(touchEndY);
        console.info(touchMoveX)
        console.info(touchMoveY)
        var wChange = true;
        if (absMoveY > 0.2 * absMoveX || absMoveY > 12){
            wChange = false;
        }
        if (wChange) {
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