var app = getApp();
var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
var questionItems;
var com = require("../common/common.js");
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
        subject_name: "",
        chapters: [],
        chapter_name: '',
        isReq: false,
        progressStorageKey: "",
        answerIndex: null,
        subjects_array: [],
    },

    onLoad: function (options) {
        var currentUser = app.getOrSetCurrentUserData();
        if (currentUser != null) {
            if ("role" in currentUser) {
                if ((currentUser.role & 2) == 2) {}
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
            this.getExam(that.data.examNo);
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
            this.setData({
                progressStorageKey: progressStorageKey
            });
            args_url += "exam_no=" + that.data.examNo;
            args_url += "&compress=true"
            wx.request2({
                url: '/exam/questions/no/?' + args_url,
                method: 'GET',
                success: res => {
                    var _questions = that.extractQuestionNos(res.data.data['nos']);
                    questionItems = _questions
                    that.setData({
                        questionNum: _questions.length
                    })
                    if (questionItems.length <= 0) {
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
    getExam: function (examNo) {
        var that = this;
        wx.request2({
            url: '/exam/info/?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                var allExams = [];
                var resData = res.data.data;
                var errorMsg = '';
                if (res.data.status == false || resData.length <= 0) {
                    errorMsg = '未查询到题库详情，切换题库'
                    wx.showModal({
                        title: '错误',
                        content: errorMsg,
                        showCancel: false,
                        success(res) {
                            wx.navigateBack({
                                delta: 1
                            })
                        }
                    })
                    return false;
                }
                var examItem = resData[0];
                if (examItem['exam_role'] > 3) {
                    errorMsg = '无权限进行操作！';
                    wx.showModal({
                        title: '无权限',
                        content: errorMsg,
                        showCancel: false,
                        success(res) {
                            wx.navigateBack({
                                delta: 1
                            })
                        }
                    })
                    return false;
                }
                var subjects = []
                if ('subjects' in examItem) {
                    var _subjects = examItem['subjects'];
                    for (var i = 0; i < _subjects.length; i++) {
                        var _item = _subjects[i];
                        if (_item.enable == true) {
                            _item['value'] = i;
                            subjects.push(_item);
                        }
                    }
                }
                that.setData({
                    subjects_array: subjects,
                });
                wx.hideLoading();
            },
            fail: res => {
                errorMsg: '未能成功加载题库信息，检查网络或重试！'
                wx.showModal({
                    title: '错误',
                    content: errorMsg,
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
    extractQuestionNos: function (nos_l) {
        if (typeof nos_l == "string" || nos_l == null) {
            return [];
        }
        var items = [];
        var examNo = this.data.examNo;
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
                            questionItems[i]["question_chapter"] = newItems[j]["question_chapter"];
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
                        questionNum: questionItems.length
                    });
                    that.changeNowQuestion(startIndex);
                } else if (startIndex == that.data.nowQuestionIndex) {
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
        var subject_index = -1;
        for (var i = 0; i < this.data.subjects_array.length; i++) {
            if (this.data.subjects_array[i].value == nowQuestion.question_subject) {
                subject_index = i;
                break
            }
        }
        this.setData({
            nowQuestion: nowQuestion,
            nowQuestionIndex: index,
            answerIndex: answerIndex
        })
        this.changeNowSubject(subject_index);
        this.setSkipNums(index + 1, questionItems.length);
    },
    changeNowSubject: function (index) {
        if (index == null) {
            index = -1;
        }
        var selected = index;
        var nowQuestion = this.data.nowQuestion;
        var subjects = this.data.subjects_array;
        var subject_name = '-';
        var chapters = [];
        var chapter_name = '-';
        if (selected >= 0 && selected < subjects.length) {
            var subject_name = subjects[selected].name;
            var current_sj = subjects[selected].value;
            if ('chapters' in subjects[selected]) {
                chapters = subjects[selected]['chapters'];
            }
            if (nowQuestion.question_subject == current_sj) {
                if (com.find_index(chapters, nowQuestion.question_chapter, 'name') >= 0) {
                    chapter_name = nowQuestion.question_chapter;
                } else {
                    nowQuestion.question_chapter = null;
                }
            } else {
                nowQuestion.question_subject = current_sj;
                nowQuestion.question_chapter = null;
            }
        } else {
            nowQuestion.question_chapter = null;
            nowQuestion.question_subject = null;
        }
        console.info(chapter_name);
        this.setData({
            nowQuestion: nowQuestion,
            subject_name: subject_name,
            chapters: chapters,
            chapter_name: chapter_name
        })
    },
    pickerSubjectChange: function (event) {
        var selected = event.detail.value;
        this.changeNowSubject(selected);
    },
    changeChapter: function (event) {
        var selected = event.detail.value;
        var nowQuestion = this.data.nowQuestion;
        var chapters = this.data.chapters;
        if (selected < chapters.length) {
            var chapter_name = chapters[selected].name;
            nowQuestion.question_chapter = chapter_name;
            this.setData({
                nowQuestion: nowQuestion,
                chapter_name: chapter_name
            })
        }
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
    updateAnswer: function () {},

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
        uData.question_chapter = nowQuestion.question_chapter
        nowQuestion.forceUpdate = true;
        console.info(uData);
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