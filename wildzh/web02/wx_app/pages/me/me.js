var app = getApp();
var dt = require("../common/datetime_tools.js");
var that;
var newNickName = '';
var lastUpdateUserKey = 'updateUserTime'

Page({
    data: {
        register: false,
        userNo: "",
        userAvatar: "",
        nickName: "",
        hiddenUnickName: true,
        allExams: [],
        examName: "未选择",
        examNo: 0,
        examEndTime: null,
        examTip: "未拥有当前题库所有操作权限",
        currentTip: null,
        brushNum: -1,
        version: app.globalData.version
    },
    onLoad: function(options) {
        if (app.globalData.defaultExamNo != null) {
            this.setData({
                examName: app.globalData.defaultExamName,
                examNo: app.globalData.defaultExamNo
            })
        }
        this.loadCacheUserInfo()
    },
    onShow: function() {
        this.getExams();
        this.loadCacheUserInfo();
    },
    loadCacheUserInfo: function(){
        var currentUser = app.getOrSetCurrentUserData();
        if (currentUser != null) {
            if ("user_no" in currentUser) {
                this.setData({
                    userNo: currentUser.user_no
                })
            }
            if (currentUser.avatar_url) {
                this.setData({
                    userAvatar: currentUser.avatar_url,
                    nickName: currentUser.nick_name
                })
            }
        }
    },
    getUserInfo: function(e) {
        var that = this
        var userInfo = e.detail.userInfo
        var data = {
            "avatar_url": userInfo.avatarUrl,
            "nick_name": userInfo.nickName
        }
        wx.showLoading({
            title: '登录中...',
            mask: true
        })
        this.updateUserInfoAction(data);

    },
    updateUserInfoAction: function(data) {
        var that = this;
        wx.request2({
            url: '/user/info/',
            method: 'PUT',
            data: data,
            success: res => {
                var userItem = res.data.data
                wx.setStorageSync(app.globalData.userInfoStorageKey, userItem)
                that.setData({
                    userAvatar: userItem.avatar_url,
                    nickName: userItem.nick_name,
                    userNo: userItem.user_no
                })
                wx.hideLoading();
                app.getOrSetCacheData2(lastUpdateUserKey, dt.get_timestamp2());
            }
        })

    },
    updateNickNameClick: function() {
        if(this.data.userNo == ""){
            return false;
        }
        wx.navigateTo({
            url: "./info"
        })
        return;
        
    },
    getExams: function() {
        that = this;
        wx.request2({
            url: '/exam/info/',
            method: 'GET',
            success: res => {
                var allExams = [];
                var resData = res.data.data;
                var examNo = 0;
                var examIndex = 0;
                var examName = this.data.examName;
                for (var index in resData) {
                    if (resData[index]["question_num"] > 0) {
                        if (resData[index].exam_no == this.data.examNo) {
                            examName = resData[index].exam_name;
                            examNo = resData[index].exam_no;
                            examIndex = index;
                        }

                        allExams.push(resData[index]);
                    }
                }
                if (examNo == 0) {
                    examName = "未选择";
                }

                that.setData({
                    allExams: allExams,
                    examName: examName,
                    examNo: examNo,
                    examIndex: examIndex
                });
                that.getBrushNum();
                if(examNo != 0 && allExams[examIndex].exam_role <= 3){
                    that.getTips();
                }
                wx.hideLoading();
            }
        })
    },
    getBrushNum: function() {
        var examNo = this.data.examNo;
        var examEndTime = null;
        var allExams = this.data.allExams;
        var examTip = '';
        for (var i = 0; i < allExams.length; i++) {
            if (allExams[i].exam_no == examNo) {
                if (allExams[i].exam_role > 10) {
                    examTip = '未拥有当前题库所有操作权限';
                }
                if ('end_time' in allExams[i]) {
                    var end_time = allExams[i]['end_time'];
                    if (end_time == null) {
                        examEndTime = '无期限'
                    } else if (end_time <= 0) {
                        // 不显示 有效期
                        break;
                    } else {
                        examEndTime = dt.timestamp_2_date(end_time);
                    }
                }

                break;
            }
        }
        this.setData({
            examEndTime: examEndTime,
            examTip: examTip
        })
        if (examNo == 0) {
            that.setData({
                brushNum: -1
            });
            return false;
        }
        that = this;
        wx.request2({
            url: '/exam/usage?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                var brushNum = resData['num'];
                that.setData({
                    brushNum: brushNum
                });
            }
        })
    },
    getTips: function() {
        var examNo = this.data.examNo;
        var examTip = '';
        var currentTip = null;
        this.setData({
            currentTip: null
        })
        that = this;
        wx.request2({
            url: '/exam/tips?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                if(resData.length <= 0){
                    return;
                }
                currentTip = resData[0];
                examTip = currentTip.tip;
                that.setData({
                    examTip: examTip,
                    currentTip: currentTip
                })
                
            }
        })
        
    },
    examChange: function(e) {
        var examIndex = e.detail.value;
        var currentExam = this.data.allExams[examIndex];
        this.setData({
            examNo: currentExam.exam_no,
            examName: currentExam.exam_name,
            examIndex: examIndex
        });
        app.setDefaultExam(currentExam);
        this.getBrushNum();
        if(currentExam.exam_role <= 3){
            this.getTips();
        }
    },
    lookExam: function() {
        wx.navigateTo({
            url: "../exam/exam_info?examNo=" + this.data.examNo
        })
    },
    changeAvatar: function(){
        wx.navigateTo({
            url: "./avatar"
        })
    }
})