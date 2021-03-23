var app = getApp();
var dt = require("../common/datetime_tools.js");
var that;
var newNickName = '';
var noExamName = '未选择';
var lastUpdateUserKey = 'updateUserTime'

Page({
    data: {
        register: false,
        userNo: "",
        userAvatar: "",
        nickName: "",
        hiddenUnickName: true,
        allExams: [],
        examName: noExamName,
        examNo: 0,
        examEndTime: null,
        examTip: "未拥有当前题库所有操作权限",
        currentTip: null,
        brushNum: 0,  // 刷题数
        ranking: 0, // 排名
        accuracy: '100%',
        version: app.globalData.version,
        useProfile: true,
        shareToken: ''
    },
    onLoad: function (options) {
        this.getShareInfo();
        if (app.globalData.defaultExamNo != null) {
            this.setData({
                examName: app.globalData.defaultExamName,
                examNo: app.globalData.defaultExamNo
            })
        }
        var useProfile = wx.canIUse('getUserProfile');
        this.setData({
            useProfile: useProfile
        })
        this.loadCacheUserInfo()
        this.reportVersion();
        options['share_token'] = 'ZXhhbXwxNTg1Mzk2MzcxfDZ8fDcsMTYxNzA2MzQ1Mw=='
        if('share_token' in options){
            var st = options['share_token'];
            this.receiveShare(st);
        }
    },
    onShow: function () {
        this.getExams();
        this.loadCacheUserInfo();
    },
    onShareAppMessage: function(res){
        var t = this.data.shareToken.token;
        var title = '成功邀请朋友，朋友和您均可随机获得1-7天,题库：' + this.data.examName + ' 的会员';
        return {
            title: title,
            path: '/pages/me?share_token=' + t
          }
    },
    loadCacheUserInfo: function () {
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
    getUserInfo2: function(){
        var that = this;
        wx.getUserProfile({
            desc: '同步用户头像信息到小程序',
            success: function(e){
                console.info(e);
                var userInfo = e.userInfo
                var data = {
                    "avatar_url": userInfo.avatarUrl,
                    "nick_name": userInfo.nickName
                }
                wx.showLoading({
                    title: '登录中...',
                    mask: true
                })
                that.updateUserInfoAction(data);
            }
        })
    },
    updateUserInfoAction: function (data) {
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
    updateNickNameClick: function () {
        if (this.data.userNo == "") {
            return false;
        }
        wx.navigateTo({
            url: "./info"
        })
        return;

    },
    getExams: function () {
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
                else{
                }
                that.setData({
                    allExams: allExams,
                    examName: examName,
                    examNo: examNo,
                    examIndex: examIndex
                });
                that.getBrushNum();
                if (examNo != 0 && allExams[examIndex].exam_role <= 3) {
                    that.getTips();
                }
                wx.hideLoading();
                that.getShareInfo();
            },
            fail: res => {
                that.getShareInfo();
                that.setData({
                    examTip: '网络连接错误，请检查网络'
                })
            }
        })
    },
    getBrushNum: function () {
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
                brushNum: 0
            });
            return false;
        }
        that = this;
        wx.request2({
            url: '/exam/usage?period_no=-1&exam_no=' + examNo,
            method: 'GET',
            success: res => {
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                var brushNum = resData['num'];
                var rightNum = resData['right_num'];
                var accuracy = '0%';
                if(rightNum > 0){
                    accuracy = parseInt(rightNum * 100 / brushNum) + '%';
                }
                that.setData({
                    brushNum: brushNum,
                    accuracy: accuracy
                });
                that.getRanking(brushNum);
            }
        })
    },
    getRanking: function (brushNum) {
        if(brushNum <= 0){
            return false;
        }
        var examNo = this.data.examNo;
        var that = this;
        wx.request2({
            url: '/exam/usage/ranking?exam_no=' + examNo + '&num=' + brushNum,
            method: 'GET',
            success: res => {
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                var ranking = resData['ranking'];
                that.setData({
                    ranking: ranking
                });
            }
        })

    },
    getTips: function () {
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
                if (resData.length <= 0) {
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
    examChange: function (e) {
        var examIndex = e.detail.value;
        var currentExam = this.data.allExams[examIndex];
        this.setData({
            examNo: currentExam.exam_no,
            examName: currentExam.exam_name,
            examIndex: examIndex
        });
        app.setDefaultExam(currentExam);
        this.getBrushNum();
        if (currentExam.exam_role <= 3) {
            this.getTips();
        }
        this.getShareInfo();
    },
    lookExam: function () {
        wx.navigateTo({
            url: "../exam/exam_info?examNo=" + this.data.examNo
        })
    },
    changeAvatar: function () {

        return false;
        // TODO 本次发版暂不支持更换头像
        wx.navigateTo({
            url: "./avatar"
        })
    },
    reportVersion: function(){
        var key = 'version';
        var cacheVersion = app.getOrSetCacheData2(key);
        
        if(cacheVersion != app.globalData.version){
            var data = {'version': app.globalData.version};
            wx.request2({
                url: '/version/wx',
                method: 'POST',
                data: data,
                success: res => {
                    if(res.data.status){
                        app.getOrSetCacheData2(key, app.globalData.version);
                    }
                }
            })
        }
    },
    getShareInfo: function(){
        wx.hideShareMenu();
        this.setData({
            shareToken: ''
        })
        var examName = this.data.examName;
        var examNo = this.data.examNo;
        if(examName == noExamName || examNo <= 0){
            return false;
        }
        var data = {'resource': 'exam', 'resource_id': examNo};
        wx.request2({
          url: '/share/token',
          method: 'POST',
          data: data,
          success: res => {
              var r_data = res.data;
              if(r_data.status != true){
                  return false;
              }
              this.setData({
                shareToken: r_data.data
            })
          }
        })
    },
    receiveShare: function(token){
        var data = {'action': 'dry-run', 'token': token}
        wx.request2({
            url: '/share/token/action',
            method: 'POST',
            data: data,
            success: res => {
                var r_data = res.data;
                if(r_data.status != true){
                    return false;
                }
                console.info(r_data)
            }
          })
    }
})