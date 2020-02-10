var app = getApp();
var dt = require("../common/datetime_tools.js");
var that;
var newNickName = '';

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
        showManExam: false,
        examEndTime: null,
        brushNum: -1,
        version: "5.0.1"
    },
    onLoad: function(options) {
        if (app.globalData.defaultExamNo != null) {
            this.setData({
                examName: app.globalData.defaultExamName,
                examNo: app.globalData.defaultExamNo
            })
        }
        var currentUser = app.getOrSetCurrentUserData();
        if(currentUser != null){
            if("user_no" in currentUser){
                this.setData({
                    userNo: currentUser.user_no
                })
            }
            if(currentUser.avatar_url){
                this.setData({
                    userAvatar: currentUser.avatar_url,
                    nickName: currentUser.nick_name
                })
            }
        }
    },
    onShow: function () {
        this.getExams();
    },
    getUserInfo: function (e) {
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
    updateUserInfoAction: function (data){
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
                    nickName: userItem.nick_name
                })
                wx.hideLoading();
            }
        })

    },
    updateNickNameClick: function(){
        this.setData({
            hiddenUnickName: false
        })
    },
    nickNameChange: function(e){
        var nNickName = e.detail.value;
        newNickName = nNickName;
    },
    cancelUnickName: function(){
        this.setData({
            hiddenUnickName: true
        })
    },
    confirmUnickName: function() {
        console.info('start update nick name');
        this.setData({
            hiddenUnickName: true,
            nickName: newNickName
        })
        var data = {
            "nick_name": newNickName
        }
        wx.showLoading({
            title: '更新中...',
            mask: true
        })
        this.updateUserInfoAction(data);
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
                var examName = this.data.examName;
                var showManExam = false;
                for (var index in resData) {
                    if (resData[index]["question_num"] > 0) {
                        if (resData[index].exam_no == this.data.examNo){
                            examName = resData[index].exam_name;
                            examNo = resData[index].exam_no;
                            if (resData[index].exam_role <= 3) {
                                showManExam = true;
                            }
                        }
                        
                        allExams.push(resData[index]);
                    }
                }
                if(examNo == 0){
                    examName = "未选择";
                }
                
                that.setData({
                    allExams: allExams,
                    examName: examName,
                    examNo: examNo,
                    showManExam: showManExam
                });
                that.getBrushNum();
                wx.hideLoading();
            }
        })
    },
    getBrushNum: function () {
        var examNo = this.data.examNo;
        var examEndTime = null;
        var allExams = this.data.allExams;
        for(var i=0;i<allExams.length;i++){
            if(allExams[i].exam_no == examNo){
                if('end_time' in allExams[i]){
                    var end_time = allExams[i]['end_time'];
                    if (end_time == null){
                        examEndTime = '无期限'
                    }
                    else if(end_time <= 0){
                        // 不显示 有效期
                        break;
                    }
                    else{
                        examEndTime = dt.timestamp_2_date(end_time);
                    }
                }
                break;
            }
        }
        this.setData({
            examEndTime: examEndTime
            }
        )
        if(examNo == 0){
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
                if(res.data.status == false){
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
    examChange: function(e) {
        var examIndex = e.detail.value;
        var showManExam = false;
        var currentExam = this.data.allExams[examIndex];
        if (currentExam.exam_role <= 3) {
            showManExam = true;
        }
        this.setData({
            examNo: currentExam.exam_no,
            examName: currentExam.exam_name,
            showManExam: showManExam
        });
        app.setDefaultExam(currentExam);
        this.getBrushNum();
    },
    lookExam: function(){
        wx.navigateTo({
            url: "../exam/exam_info?examNo=" + this.data.examNo
        })
    }
})