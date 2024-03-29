var app = getApp();
var dt = require("../common/datetime_tools.js");
var SE = require("../common/security.js");
var that;
var questionItems = [];
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
var brushList = new Array();
var brushDetail = new Array();
var STATE_WRONG = 'wrong';
var STATE_RIGHT = 'right'
var STATE_SKIP = 'skip'
var firstEnter = true;

Page({
    data: {
        remote_host: app.globalData.remote_host,
        allExams: [],
        skipNums: [1],
        skipIndex: 0,
        optionChar: app.globalData.optionChar,
        examNo: null,
        examName: "",
        mode: "traning", // 模式 traning 练习模式  wrong 错题模式
        questionNum: 0,
        nowQuestionIndex: 0,
        nowQuestion: null,
        isShowAnswer: false,
        showRemove: false, // mode=wrong 是否显示移除按钮
        isShowSubject: false,
        isReq: false,
        progressStorageKey: "",
        nosStorageKey: "",
        hiddenFeedback: true,
        fbTypes: ['题目错误', '答案错误', '解析错误', '其他'],
        fbTypeIndex: 1,
        feedbackDesc: "",
        showAD: false, // 是否显示推广信息
        richAD: [], // 推广信息
        ignoreTip: "",
        ignoreInterval: 0, // 不再提醒的间隔 小时数
        ignoreAd: false, // 一定时间内不再提醒
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
        questionItems = [];
        this.setData({
            examNo: app.globalData.defaultExamNo,
            examName: app.globalData.defaultExamName
        });
        that = this;
        SE.startSecurityMonitor();
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
            } else if ('wrong_question' in options) {
                this.enterWrongMode();
                return true;
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
    onShow: function () {
        this.getExamAD();
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
            url: '/exam/questions/?fmt_version=2&exam_no=' + exam_no + "&nos=" + nos,
            method: 'GET',
            success: res => {
                wx.hideLoading();
                if (res.data.status != true) {
                    // TODO show
                    return;
                }
                if ('se' in res.data) {
                    var r = SE.showSecurityMesg(res.data.se.action, res.data.se.message);
                    if (r) {
                        return false;
                    }
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
                            questionItems[i]["answer_rich"] = newItems[j]["answer_rich"];
                            questionItems[i]["question_source"] = newItems[j]["question_source"];
                            questionItems[i].multi = newItems[j].multi;
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
            // 判断是否仅有 1题
            if(questionItems.length == 1){
                this.showAnswer();
                return;
            }
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
        nowQuestion.index = index;
        this.setData({
            nowQuestion: nowQuestion,
            nowQuestionIndex: index,
            isShowAnswer: false,
            showRemove: false,
            feedbackDesc: ""
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
        that.setData({
            isShowAnswer: true,
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
    choseOption: function (e) {
        var choseRight = e.detail.choseRight;
        var nowQuestion = that.data.nowQuestion;
        var showRemove = false;
        if (this.data.mode == 'wrong') {
            if (choseRight) {
                this.addBrushNum(nowQuestion.question_no, STATE_RIGHT);
                showRemove = true;
            } else {
                this.addBrushNum(nowQuestion.question_no, STATE_WRONG);
            }
            this.setData({
                showRemove: showRemove
            })
            // 显示答案
            this.showAnswer();
            return;
        }
        if (choseRight) {
            this.addBrushNum(nowQuestion.question_no, STATE_RIGHT);
            // 自动进入下一题
            if (this.data.isShowAnswer == false) {
                // 当前显示答案 不进入下一题
                var interval = setInterval(function () {
                    clearInterval(interval)
                    that.after1();
                }, 1000)
            }
            else{
                this.showAnswer();
            }
        } else {
            // 记录错题
            this.addBrushNum(nowQuestion.question_no, STATE_WRONG);
            // 显示答案
            that.showAnswer();
        }

    },

    previewImage: function (event) {
        var src = event.currentTarget.dataset.src; //获取data-src
        src += '?r=' + Math.random();
        //图片预览
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
    addBrushNum: function (q_no, state) {
        if (brushList.indexOf(q_no) >= 0) {
            return false;
        }
        brushList.push(q_no);
        brushDetail.push({
            'no': q_no,
            'state': state
        });
        this.saveBrushNum();
    },
    saveBrushNum: function () {
        if (brushDetail.length <= 0) {
            return false;
        }
        var _num = brushDetail.length;
        var questions = new Array();
        while (brushDetail.length > 0) {
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
                brushDetail = brushDetail.concat(questions);
            }
        })
    },
    getFeedback: function(){
        var question_no = this.data.nowQuestion.question_no;
        var url = '/exam/question/feedback?exam_no=' + this.data.examNo;
        url += '&question_no=' + question_no;
        url += '&max_state=0&user=';
        var that = this;
        wx.request2({
            url: url,
            method: 'GET',
            success: res => {
                if (res.data.status != true) {
                } else {
                    var items = res.data.data;
                    if(items.length > 0){
                        var fbTypeIndex = that.data.fbTypes.indexOf(items[0].fb_type);
                        if(fbTypeIndex < 0){
                            fbTypeIndex = 0;
                        }
                        that.setData({
                            fbTypeIndex: fbTypeIndex,
                            feedbackDesc: items[0].description
                        })
                    }
                }

            }
        })
    },
    feedbackClick: function () {
        this.setData({
            hiddenFeedback: false
        });
        this.getFeedback();
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
    getExamAD: function () {
        if (this.data.examNo == null) {
            return false;
        }
        var now_time = dt.get_timestamp2();
        var cache_key = 'ignore_ad_time';
        var ignore_time = app.getOrSetExamCacheData(cache_key);
        if (ignore_time > now_time) {
            return false;
        }
        var that = this;
        wx.request2({
            url: '/exam/ad?exam_no=' + this.data.examNo,
            success: function (ret) {
                var r_data = ret.data;
                if (!r_data.status) {
                    return false;
                }
                if (r_data.data.enabled == false) {
                    return false;
                }
                var ignoreTip = "";

                if (r_data.data.ignore_interval > 0) {
                    var days = Math.floor(r_data.data.ignore_interval / 24);
                    if (days > 0) {
                        ignoreTip = days + "天内不再提醒";
                    } else {
                        ignoreTip = r_data.data.ignore_interval + "小时内不再提醒";
                    }
                }
                that.setData({
                    showAD: true,
                    richAD: r_data.data.ad_desc_rich,
                    ignoreTip: ignoreTip,
                    ignoreInterval: r_data.data.ignore_interval
                })

            }
        })
    },
    ignoreAction: function (e) {
        var ignoreAd = false;
        for (let i = 0, l = e.detail.value.length; i < l; ++i) {
            if (e.detail.value[i] == 'ignore') {
                ignoreAd = true;
                break
            }
        }
        this.setData({
            ignoreAd: ignoreAd
        })
    },
    knowAd: function () {
        if (this.data.ignoreAd) {
            var now_time = dt.get_timestamp2();
            var cache_key = 'ignore_ad_time';
            var ignore_time = now_time + this.data.ignoreInterval * 3600;
            app.getOrSetExamCacheData(cache_key, ignore_time);
        }
        this.setData({
            showAD: false,
        })
    },
    // 练习错题模式
    enterWrongMode: function () {
        this.setData({
            mode: 'wrong'
        });
        this.reqWrongAnswer();
    },
    reqWrongAnswer: function () {
        that = this
        var examNo = this.data.examNo;
        if (examNo == null) {
            return false;
        }
        var questionLen = questionItems.length;
        var minWrongTime = 0;
        if (questionLen <= 0) {
            wx.showLoading({
                title: '加载错题中...',
            })
        } else {
            minWrongTime = questionItems[questionLen - 1].wrong_time;
        }
        
        wx.request2({
            url: '/exam/wrong/?exam_no=' + examNo + "&min_wrong_time=" + minWrongTime,
            methods: "GET",
            success: function (res) {
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
                    addQuestionItems.sort(function (a, b) {
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
                    that.reqQuestion(0, true);
                }
            },
            fail: function ({
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
            }
        })
        questionItems.splice(nowQuestionIndex, 1);
        questionLen = questionItems.length;
        that.setData({
            questionNum: questionLen
        })
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
        this.changeNowQuestion(nowQuestionIndex);
        

    },
    // 练习错题模式 结束
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
        if (this.data.questionNum <= 1) {
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