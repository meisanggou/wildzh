var app = getApp();
var that;
var questionItems;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
var brushList = new Array();
var brushDetail = new Array();
var STATE_WRONG = 'wrong';
var STATE_RIGHT = 'right'
var STATE_SKIP = 'skip'

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
        questionAnswer: new Array(),
        nowQuestion: null,
        showAnswer: false,
        isShowSubject: false,
        isReq: false,
        progressStorageKey: "",
        nosStorageKey: "",
        hiddenFeedback: true,
        fbTypes: ['题目错误', '答案错误', '解析错误', '其他'],
        fbTypeIndex: 1,
        feedbackDesc: ""
    },
    getQuestionNos: function (options) {
        that = this;
        var args_url = "";
        var progressStorageKey = "training";
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
            if ("question_chapter" in options) {
                args_url += "question_chapter=" + options["question_chapter"] + "&";
                progressStorageKey += "_" + options["question_chapter"];
            }
        } else {
            progressStorageKey += "_" + 0;
        }
        if ("question_source" in options) {
            args_url += "question_source=" + options["question_source"] + "&";
            progressStorageKey += "_" + options["question_source"];
        }
        var nosStorageKey = progressStorageKey + "_nos"
        this.setData({
            progressStorageKey: progressStorageKey,
            nosStorageKey: nosStorageKey
        });
        var cacheNos = app.getOrSetExamCacheData(nosStorageKey);
        // var cache_questions = that.extractQuestionNos(cacheNos);

        if (cacheNos == null || cacheNos == "" || true) {
            wx.showLoading({
                title: '试题加载中',
            });
        }
        args_url += "exam_no=" + that.data.examNo;
        args_url += "&compress=true"
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
                var _questions = that.extractQuestionNos(res.data.data['nos']);
                // for(var q_index=0;q_index<_questions.length;q_index++){
                //     cache_questions.push(_questions[q_index]);
                // }
                // app.getOrSetExamCacheData(nosStorageKey, cache_questions);
                questionItems = _questions
                that.setData({
                    questionNum: _questions.length
                })
                if (_questions.length <= 0) {
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
    },
    onLoad: function (options) {
        brushList = [];
        brushDetail = [];
        this.setData({
            examNo: app.globalData.defaultExamNo,
            examName: app.globalData.defaultExamName
        });
        that = this;

        if (that.data.examNo != null) {
            var questionNo = null;
            if ('question_no' in options) {
                questionNo = parseInt(options['question_no']);
                if (isNaN(questionNo)) {
                    questionNo = null;
                } else {
                    questionItems = [{
                        'question_no': questionNo
                    }];
                    that.setData({
                        questionNum: 1
                    })
                    this.reqQuestion(0, true);
                    return true;
                }
            }
            that.getQuestionNos(options);
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
    extractQuestionNos: function (nos_l) {
        if (typeof nos_l == "string" || nos_l == null) {
            return [];
        }
        var items = [];
        var ll = nos_l.length;
        for (var i = 0; i < ll; i++) {
            var ll_item = nos_l[i];
            for (var j = 0; j < ll_item[1]; j++) {
                var q_item = {
                    'question_no': ll_item[0] + j
                }
                items.push(q_item);
            }
        }
        return items
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

        var nos = "";
        var _start = -1;
        var _end = -1;
        // startIndex 可能超出最大题目长度
        if (startIndex >= questionItems.length) {
            startIndex = questionItems.length - 1;
        }
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
                if (res.data.status != true) {
                    return;
                }
                var canUpdate = false;
                if ('exam' in res.data) {
                    var exam_item = res.data.exam;

                    if (exam_item.exam_role <= 3) {
                        canUpdate = true;
                    }
                }
                var newItems = res.data.data;
                for (var i = _end - 1; i >= _start; i--) {
                    for (var j = 0; j < newItems.length; j++) {
                        if (questionItems[i].question_no == newItems[j].question_no) {
                            questionItems[i]["question_desc"] = newItems[j]["question_desc"];
                            questionItems[i]["question_desc_rich"] = newItems[j]["question_desc_rich"]
                            questionItems[i]["question_desc_url"] = newItems[j]["question_desc_url"];
                            questionItems[i]["options"] = newItems[j]["options"];
                            questionItems[i]["answer_rich"] = newItems[j]["answer_rich"]
                            questionItems[i]["question_source"] = newItems[j]["question_source"]
                            questionItems[i].forceUpdate = false;
                            questionItems[i].canUpdate = canUpdate
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
        var questionLen = questionItems.length;
        var nextIndex = nowQuestionIndex + afterNum;
        if (nowQuestionIndex >= questionItems.length - 1) {
            // 判断是否当前是否是最后一题
            wx.showModal({
                title: "已是最后一题",
                content: "是否从头开始练习？",
                showCancel: true,
                icon: "none",
                success: function (res) {
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
    after1: function () {
        that.after(1);
    },

    after10: function () {
        that.after(10);
    },
    before: function (preNum) {
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
            if (times >= max_times) {
                interval *= 10;
                times = 0;
            }

            num = p_num;
        }
        r.sort(function (a, b) {
            return a - b;
        });
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
            if (times >= max_times) {
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
    skipAction: function (e) {
        var index = e.detail.value;
        this.changeNowQuestion(this.data.skipNums[index] - 1);
    },
    changeNowQuestion: function (index) {
        var skipNums = [];
        var nowQuestion = questionItems[index];
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
        this.setSkipNums(index + 1, questionItems.length);
        this.saveTrainingProcess();
    },
    showAnswer: function (e) {
        var nowQuestion = that.data.nowQuestion;
        if (nowQuestion == null) {
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
    toUpdate: function (e) {
        var nowQuestion = that.data.nowQuestion;
        if (nowQuestion == null) {
            return false;
        }
        var question_no = nowQuestion.question_no;
        wx.navigateTo({
            url: "../questions/question?select_mode=-1&question_no=" + question_no
        })
    },
    choseItem: function (e) {
        var choseIndex = parseInt(e.currentTarget.dataset.choseitem);
        var nowQuestion = that.data.nowQuestion;
        var nowQuestionIndex = that.data.nowQuestionIndex;
        
        for (var index in questionItems[nowQuestionIndex]["options"]) {
            nowQuestion["options"][index]["class"] = "noChose";
        }
        if (parseInt(nowQuestion["options"][choseIndex]["score"]) > 0) {
            nowQuestion["options"][choseIndex]["class"] = "chose";
            this.addBrushNum(nowQuestion.question_no, STATE_RIGHT);
            // 自动进入下一题
            if (this.data.showAnswer == false) {
                // 当前显示答案 不进入下一题
                var interval = setInterval(function () {
                    clearInterval(interval)
                    that.after1();
                }, 1000)
            }
        } else {
            nowQuestion["options"][choseIndex]["class"] = "errorChose";
            // 记录错题
            this.addBrushNum(nowQuestion.question_no, STATE_WRONG);
            //that.recordWrong(that.data.examNo, [nowQuestion.question_no]);
            // 显示答案
            that.showAnswer();
        }
        that.setData({
            nowQuestion: nowQuestion
        })
    },
    updateAnswerOption: function (event) {
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
    actionUpdateAnswer: function () {
        var nowQuestion = this.data.nowQuestion;
        var index = this.data.nowQuestionIndex;
        nowQuestion.forceUpdate = true;
        this.updateQuestion(nowQuestion.question_no, index, null, nowQuestion.answer);
    },
    previewImage: function (event) {
        var src = event.currentTarget.dataset.src; //获取data-src
        //图片预览
        console.info(src);
        wx.previewImage({
            current: src, // 当前显示图片的http链接
            urls: [src], // 需要预览的图片http链接列表
            fail: function (e) {
                console.info("preview fail");
            },
            complete: function (e) {
                console.info("preview complete");
            }
        })

    },
    updateQuestion: function (questionNo, index, options = null, answer = null) {
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
    recordWrong: function (exam_no, wrong_question) {
        // 待废弃
        wx.request2({
            url: '/exam/wrong/',
            method: "POST",
            data: {
                "question_no": wrong_question,
                "exam_no": exam_no
            }
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
    feedbackClick: function () {
        this.setData({
            hiddenFeedback: false
        });
    },
    feedbackTypeChange(e) {
        this.setData({
            fbTypeIndex: e.detail.value
        })
    },
    feedbackDescInput: function (e) {
        this.setData({
            feedbackDesc: e.detail.value
        });
    },
    cancelFeedback: function () {
        this.setData({
            hiddenFeedback: true
        });
    },
    confirmFeedback: function (e) {
        this.setData({
            hiddenFeedback: true
        });
        var fb_type = this.data.fbTypes[this.data.fbTypeIndex]
        var questionNo = this.data.nowQuestion.question_no;
        var data = {
            'description': this.data.feedbackDesc,
            'fb_type': fb_type,
            'question_no': questionNo
        };
        var that = this;
        wx.request2({
            url: '/exam/question/feedback?exam_no=' + this.data.examNo,
            method: 'POST',
            data: data,
            success: res => {
                if (res.data.status != true) {
                    wx.showModal({
                        title: '反馈失败',
                        content: "反馈失败，请稍后重试！",
                        showCancel: false,
                        success(res) {}
                    })

                    return
                } else {
                    that.setData({
                        feedbackDesc: ""
                    })
                    wx.showToast({
                        title: "反馈成功"
                    })
                }

            }
        })
    },
    saveTrainingProcess() {
        if (that.data.examNo == null || that.data.nowQuestion == null) {
            return false;
        }
        if (this.data.progressStorageKey == "" || this.data.nowQuestionIndex <= 0) {
            return false;
        }
        app.getOrSetExamCacheData(this.data.progressStorageKey, this.data.nowQuestionIndex);

    },
    onUnload: function () {
        console.info("un load")
        this.saveBrushNum();
        this.saveTrainingProcess();
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
        if(this.data.questionNum <= 1){
            return false
        }
        var touchEndX = e.changedTouches[0].pageX;
        var touchEndY = e.changedTouches[0].pageY;
        var touchMoveX = touchEndX - touchStartX;
        var touchMoveY = touchEndY - touchStartY;

        var absMoveX = Math.abs(touchMoveX);
        var absMoveY = Math.abs(touchMoveY);
        var wChange = true;
        if (absMoveY > 0.3 * absMoveX || absMoveY > 30) {
            wChange = false;

        }

        if (wChange) {
            // 向左滑动   
            if (touchMoveX <= -93 && touchTime < 10) {
                //执行切换页面的方法
                that.after1();
            }
            // 向右滑动   
            else if (touchMoveX >= 93 && touchTime < 10) {
                that.before1();
            }
        }

        clearInterval(touchInterval); // 清除setInterval
        touchTime = 0;
    }

})