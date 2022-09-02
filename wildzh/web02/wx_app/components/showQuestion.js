// components/showQuestion.js
var app = getApp();
var dt = require("../pages/common/datetime_tools.js");
var week_delta = 60 * 60 * 24 * 7;
var STATE_WRONG = 'wrong';
var STATE_RIGHT = 'right'
var STATE_SKIP = 'skip'
var VIDEO_EXTENSIONS = ['mp4'];

Component({
    /**
     * 组件的属性列表
     */
    properties: {
        examNo: {
            type: Number,
            value: null
        },
        nowQuestion: {
            type: Object,
            value: {}
        },
        showAnswer: {
            type: Boolean,
            value: false
        },
        mode: {
            type: String,
            value: 'training'
            // training练习模式 选错时标红 
            // answer答题模式 选错选对都一样
            // answer-show 答题模式，查看答案
        }
    },

    /**
     * 组件的初始数据
     */
    data: {
        remote_host: app.globalData.remote_host,
        isShowSubject: false,
        optionChar: app.globalData.optionChar,
        videoDesc: false,  //question_desc_url是否是视频
        options: [], // 题目选项
        multiOpts: false, //是否多选
        rightOpts: [], //正确的选项 下标
        selectedOpts: [], // 选择的选项 下标
        showConfirm: false, // 是否显示 选好了 按钮
        questionAnswer: [], // 答案,
        selectedOption: '', // 选择的答案
        erroChoseCls: "errorChose",
        tags: [] // 题目标签
    },
    observers: {
        nowQuestion: function (question) {
            if (question == null) {
                return false;
            }
            var options = question.options;
            var rightOpts = [];
            var multi = false;
            var rightOption = '';
            var selectedOpts = [];
            for (var index in options) {
                if (parseInt(options[index]["score"]) > 0) {
                    rightOpts.push(index);
                    rightOption += this.data.optionChar[index];
                }
            }
            if (rightOption.length <= 0) {
                rightOption = '无答案';
            }
            if (rightOpts.length > 1) {
                multi = true;
            }
            for (var index in options) {
                options[index]["class"] = "noChose";
            }
            if ('selectedOpts' in question) {
                selectedOpts = question.selectedOpts;
                
                for (var i = 0, l = selectedOpts.length; i < l; i++) {
                    var choseIndex = selectedOpts[i];
                    if (parseInt(options[choseIndex]["score"]) > 0) {
                        options[choseIndex]["class"] = "chose";
                    } else {
                        options[choseIndex]["class"] = this.data.erroChoseCls;;
                    }
                }
            }
            if (this.data.mode == 'answer-show') {
                for(var j=0,l=rightOpts.length;j<l;j++){
                    options[rightOpts[j]]["class"] = "chose";
                }
            }
            var videoDesc = false;
            if(question.question_desc_url){
                var _ss = question.question_desc_url.split('.');
                var extension = _ss[_ss.length - 1];
                if(VIDEO_EXTENSIONS.indexOf(extension) >= 0){
                    videoDesc = true;
                }
            }
            this.setData({
                tags: [],
                videoDesc: videoDesc,
                options: options,
                selectedOpts: selectedOpts,
                rightOption: rightOption,
                multiOpts: multi,
                rightOpts: rightOpts,
                showConfirm: false
            })
            if(this.data.showAnswer){
                this.showAnswerAction();
            }
        },
        showAnswer: function (sa) {
            if (sa == true) {
                this.showAnswerAction();
            }
        },
        mode: function (m) {
            var erroChoseCls = 'errorChose';
            if (m == 'answer') {
                var erroChoseCls = 'chose';
            }
            this.setData({
                erroChoseCls: erroChoseCls
            })
        }
    },
    /**
     * 组件的方法列表
     */
    methods: {
        calcTags: function (item) {
            if (item == null) {
                return ['首次遇到'];
            }
            var q_detail = item;
            var tags = [];
            var miss_num = q_detail['miss_num'];
            var num = q_detail['num'];
            var skip_num = q_detail['skip_num'];
            var right_num = num - skip_num - miss_num;
            var state_num = q_detail['state_num'];
            var last_miss = q_detail['last_miss'];
            var last_meet = q_detail['last_meet'];
            var last_meet_time = q_detail['last_meet_time'];
            if (miss_num == 0 && skip_num == 0) {
                tags.push('全部做对')
            } else if (miss_num == 0 && right_num > 0) {
                tags.push('从未错误')
            }
            if (skip_num == num && skip_num >= 3) {
                tags.push('多次跳过')
            } else if (right_num == 0) {
                tags.push('还未对过')
            } else if (state_num >= 3) {
                if (last_miss) {
                    tags.push('连续错误')
                } else {
                    tags.push('最近全对')
                }
            }
            if (right_num >= 1 && miss_num >= 2 * right_num) {
                tags.push('易错题');
            }
            if (last_meet_time - dt.get_timestamp2() < week_delta) {
                if (last_meet == STATE_RIGHT) {
                    tags.push('最近做对');
                } else if (last_meet == STATE_WRONG) {
                    tags.push('最近做错');
                }
            }
            return tags

        },
        getQuestionTag: function () {
            var tags = [];
            if (this.data.examNo == null || this.data.nowQuestion == null) {
                this.setData({
                    tags: tags
                });
                return false;
            }
            if (this.data.showAnswer == true) {
                // 查看答案情况 保持原有
                return true;
            }

            var nowQuestion = this.data.nowQuestion;
            var examNo = this.data.examNo;
            var that = this;
            wx.request2({
                url: '/exam/training/tags?exam_no=' + examNo + '&question_no=' + nowQuestion.question_no,
                method: 'GET',
                success: res => {
                    var res_data = res.data;
                    if (res_data.status != true) {
                        tags = [];
                    } else if (!('item' in res_data.data)) {
                        tags = [];
                    } else {
                        if ('tags' in res_data.data) {
                            tags = res_data.data.tags;
                        } else {
                            tags = that.calcTags(res_data.data.item);
                        }
                    }
                    that.setData({
                        tags: tags
                    });
                },
                fail: function () {
                    that.setData({
                        tags: []
                    });
                }
            })
        },
        choseItem: function (e) {
            if (this.data.mode == 'answer-show') {
                return false;
            }
            var options = this.data.options;
            var choseIndex = parseInt(e.currentTarget.dataset.choseitem);
            if (this.data.multiOpts) {
                var selectedOpts = this.data.selectedOpts;
                var _i = this.data.selectedOpts.indexOf(choseIndex);
                if (_i >= 0) {
                    options[choseIndex]["class"] = "noChose";
                    selectedOpts.splice(_i, 1);
                } else {
                    options[choseIndex]["class"] = "chose";
                    selectedOpts.push(choseIndex);
                }
                var showConfirm = selectedOpts.length >= 2 ? true : false;
                this.setData({
                    options: options,
                    selectedOpts: selectedOpts,
                    showConfirm: showConfirm
                })
                return false;
            } else {
                
                for (var index in options) {
                    options[index]["class"] = "noChose";
                }
                options[choseIndex]["class"] = "chose";
                var selectedOpts = [choseIndex];
                this.setData({
                    selectedOpts: selectedOpts,
                    showConfirm: false
                })
                
                return this.confirmAnswer(options);
            }


            var nowQuestionIndex = this.data.nowQuestion.index;
            var eventOptions = {};
            var eventDetail = {
                'choseIndex': choseIndex,
                'rightIndex': -1
            };
            for (var index in options) {
                options[index]["class"] = "noChose";
                if (parseInt(options[index]["score"]) > 0) {
                    eventDetail['rightIndex'] = index;
                }
            }
            if (eventDetail['rightIndex'] == choseIndex) {
                options[choseIndex]["class"] = "chose";
                eventDetail['choseRight'] = true;
            } else {
                options[choseIndex]["class"] = this.data.erroChoseCls;
                eventDetail['choseRight'] = false;
            }
            this.setData({
                options: options
            })
            this.triggerEvent('choseOption', eventDetail, eventOptions)
        },
        confirmAnswer: function (options) {
            if(options instanceof Array){
                
            }else{
                // 可能是事件触发传过来 event 因此不能用
                options = this.data.options;
            }
            var selectedOpts = this.data.selectedOpts.sort();
            var choseRight = true;
            for (var i = 0, l = options.length; i < l; i++) {
                if (parseInt(options[i]["score"]) > 0) {
                    if (options[i]["class"] != "chose") {
                        if(this.data.mode != 'answer'){
                            options[i]["class"] = "chose";
                        }
                        // TODO 是否区分 用户是否选择
                        choseRight = false;
                    }
                } else if (options[i]["class"] == "chose") {
                    // 用户选错了
                    options[i]["class"] = this.data.erroChoseCls;
                    choseRight = false;
                }
            }
            this.setData({
                options: options
            });
            var eventOptions = {};
            var eventDetail = {
                'selectedOpts': selectedOpts,
                'rightOpts': this.data.rightOpts,
                'choseRight': choseRight
            };
            this.triggerEvent('choseOption', eventDetail, eventOptions)
        },
        showAnswer: function () {
            // TODO  待废弃
            var nowQuestion = this.data.nowQuestion;
            if (nowQuestion == null) {
                return false;
            }
            var questionAnswer = new Array();

            for (var index in nowQuestion.options) {
                if (parseInt(nowQuestion.options[index]["score"]) > 0) {
                    var tmp_answer = app.globalData.optionChar[index] + "、";
                    questionAnswer = questionAnswer.concat({
                        'value': tmp_answer,
                        'index': -1
                    });
                    questionAnswer = questionAnswer.concat(nowQuestion.options[index]["desc_rich"]);
                }
            }
            if (questionAnswer.length == 0) {
                questionAnswer[0] = {
                    'value': "没有答案",
                    'index': -1
                };
            }
            this.setData({
                questionAnswer: questionAnswer
            })
        },
        showAnswerAction: function () {
            var selectedOpts = this.data.selectedOpts;
            var selectedOption = '';
            for (var i = 0, l = selectedOpts.length; i < l; i++) {
                selectedOption += this.data.optionChar[selectedOpts[i]];
            }
            if (selectedOption.length <= 0) {
                selectedOption = '未选择';
            }
            this.setData({
                selectedOption: selectedOption
            })
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
    }
})