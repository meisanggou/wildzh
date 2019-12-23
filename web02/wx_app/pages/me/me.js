var app = getApp();
var that;
Page({
    data: {
        register: false,
        userNo: "",
        userAvatar: "",
        nickName: "",
        allExams: [],
        examName: "未选择",
        examNo: 0,
        showManExam: false,
        version: "4.6.0"
    },
    onLoad: function(options) {
        if (app.globalData.defaultExamNo != null) {
            this.setData({
                examName: app.globalData.defaultExamName,
                examNo: app.globalData.defaultExamNo
            })
        }
        var currentUser = app.getOrSetCurrentUserData();
        console.info(currentUser);
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
        wx.request2({
            url: '/user/info/',
            method: 'PUT',
            data: data,
            success: res => {
                var userItem = res.data.data
                console.info(userInfo)
                wx.setStorageSync(app.globalData.userInfoStorageKey, userItem)
                that.setData({
                    userAvatar: userItem.avatar_url,
                    nickName: userItem.nick_name
                })
                wx.hideLoading();
            }
        })

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
                            console.info(resData[index]);
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
                wx.hideLoading();
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
        })
        app.setDefaultExam(currentExam);
    },
    managerExam: function(){
        wx.navigateTo({
            url: "exam_member?examNo=" + this.data.examNo
        })
    }
})