var app = getApp();
var lastExamNo = null;
var lastUpdateSource = 0;
var dt = require("../common/datetime_tools.js");
Page({

    data: {
        subjects_array: [], // 选择科目
        subjects_modes: [
            [],
            []
        ], // 选择科目 和 题型
        strategies_array: [], // 策略列表
        stragety_index: -1,
        errorMsg: "题库信息加载中...",
        cacheSelectedKey: "selectedAnswerOptions"
    },
    onLoad: function (options) {
        var canUpdate = false;
        var currentUser = app.getOrSetCurrentUserData();
        if (currentUser != null && typeof currentUser == "object") {
            if ("role" in currentUser) {
                if ((currentUser.role & 2) == 2) {
                    canUpdate = true;
                }
            }
        }
        this.setData({
            canUpdate: canUpdate
        })
        if ("to" in options) {
            this.setData({
                to: options["to"]
            })
        }

    },
    onShow: function () {
        this.refreshExam(false);
    },
    refreshExam(force) {
        var examNo = app.globalData.defaultExamNo;
        if (examNo) {} else {
            wx.showModal({
                title: '未选择题库',
                content: "未选择题库,确定进入【我的】选择题库",
                showCancel: false,
                success(res) {
                    wx.switchTab({
                        url: "/pages/me/me"
                    })
                }
            });
            this.setData({
                errorMsg: '请先选择一个题库'
            })
            return false;
        }
        var nowT = dt.get_timestamp2();
        var intervalT = nowT - lastUpdateSource;
        if (intervalT < 300 && lastExamNo == examNo && force == false) {
            return false;
        }
        this.getExam(examNo);
        this.getExamStrategies(examNo);
    },
    getExam: function (examNo) {
        var that = this;
        wx.request2({
            url: '/exam/info/?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                var resData = res.data.data;
                var errorMsg = '';
                if (res.data.status == false || resData.length <= 0) {
                    errorMsg = '未查询到题库详情，切换题库'
                    that.setData({
                        errorMsg: errorMsg
                    })
                    return false;
                }
                var examItem = resData[0];
                if (examItem['exam_role'] > 10) {
                    errorMsg = '无权限进行操作，请先升级成会员！';
                }
                var select_modes = [{
                    'name': '全部题型',
                    'value': -1
                }];
                if ('select_modes' in examItem) {
                    var _select_modes = examItem['select_modes'];
                    for (var i = 0; i < _select_modes.length; i++) {
                        var _item = _select_modes[i];
                        if (_item.enable == true) {
                            _item['value'] = i;
                            select_modes.push(_item);
                        }
                    }
                }
                var subjects_array = [{
                    "value": -1,
                    "name": "全部科目"
                }];
                if ('subjects' in examItem) {
                    var _subjects = examItem['subjects'];
                    for (var i = 0; i < _subjects.length; i++) {
                        var _item = _subjects[i];
                        if (_item.enable == true) {
                            _item['value'] = i;
                            subjects_array.push(_item);
                        }
                    }
                }
                that.setData({
                    errorMsg: errorMsg,
                    subjects_array: subjects_array,
                    subjects_modes: [subjects_array, select_modes]
                });
                wx.hideLoading();
            },
            fail: res => {
                that.setData({
                    errorMsg: '未能成功加载题库信息，检查网络或重试！'
                });
            }
        })
    },
    getExamStrategies: function (examNo) {
        var that = this;
        wx.request2({
            url: '/exam/strategy/' + examNo,
            method: 'GET',
            success: res => {
                lastUpdateSource = dt.get_timestamp2();
                lastExamNo = examNo;
                var resData = res.data.data;
                var strategies = resData['strategies'];
                that.setData({
                    strategies_array: strategies
                });
                wx.hideLoading();
            },
            fail: res => {}
        })
    },
    randomAnswer(e) {
        var indexs = e.detail.value;
        var subject_value = this.data.subjects_modes[0][indexs[0]].value;
        var mode_value = this.data.subjects_modes[1][indexs[1]].value;
        this.startAnswer(mode_value, subject_value, null);
    },
    strategySubjectChange(e) {
        var index = e.detail.value;
        var strategy_id = e.currentTarget.dataset.id;
        var subject_value = this.data.subjects_array[index].value;
        this.startAnswer(null, subject_value, strategy_id);
    },
    startAnswer(sm_value, sj_value, strategy_id) {
        app.getOrSetCacheData(this.data.cacheSelectedKey, this.data);
        var url = "answer2?from=home";
        if (strategy_id != null) {
            url += "&strategy_id=" + strategy_id;
        } else {
            if (sm_value >= -1) {
                url += "&select_mode=" + sm_value;
            }
        }
        if (sj_value >= 0) {
            url += "&question_subject=" + sj_value;
        }
        wx.navigateTo({
            url: url
        })
    },
    onPullDownRefresh: function () {
        this.refreshExam(true);
        wx.stopPullDownRefresh({
            complete: (res) => {},
        })
    }
})