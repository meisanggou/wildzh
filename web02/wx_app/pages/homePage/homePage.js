var that;
var app = getApp();
Page({

  data: {
    name: '未登录',
    department: '未登录',
    userPic: '../../images/signIn.png',
    register: null,
    allExams: null
  },


  onLoad: function(options) {
    that = this;
    that.getExams();
    var interval = setInterval(function() {
      var userItem = wx.getStorageSync(app.globalData.userInfoStorageKey)
      if (userItem.avatar_url) {
        clearInterval(interval);
        that.setData({
          userPic: userItem.avatar_url,
          register: true,
          name: userItem.nick_name,
          department: "暂未开放",
        })
      }
    }, 500);

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
    wx.request2({
      url: '/user/info/',
      method: 'PUT',
      data: data,
      success: res => {
        var userItem = res.data.data
        console.info(userInfo)
        wx.setStorageSync(app.globalData.userInfoStorageKey, userItem)
        that.setData({
          userItem: userItem,
          userPic: userItem.avatar_url,
          register: true,
          name: userItem.nick_name,
          department: "暂未开放",
        })
        wx.hideLoading();
      }
    })

  },
  getExams: function() {
    wx.request2({
      url: '/exam/info/',
      method: 'GET',
      success: res => {
        var allExams = [];
        for (var index in res.data.data) {
          if (res.data.data[index]["question_num"] > 0) {
            allExams.push(res.data.data[index]);
          }
        }
        that.setData({
          allExams: allExams
        });
        wx.hideLoading();
      }
    })
  },
  wrongExams: function(e) {
    console.info("wrong exams");
    var register = that.data.register;
    if (register != true) {
      wx.showToast({
        icon: "none",
        title: "请先点击登录",
        duration: 5000
      })
      return false;
    }
    var allExams = that.data.allExams;
    if (allExams == null) {
      wx.showLoading({
        title: '正在加载试题库',
        mask: true
      })
    } else if(allExams.length <= 0) {
      wx.showToast({
        icon: "none",
        title: "没有可用的试题库",
        duration: 3000
      })
    }
  },
  answer: function(e) {
    var register = that.data.register;
    if (register != true) {
      wx.showToast({
        icon: "none",
        title: "请先点击登录",
        duration: 5000
      })
      // wx.navigateTo({
      //   url: '../register/register'
      // })
    } else {
      if (that.data.allExams == null ||that.data.allExams.length <= 0) {
        wx.showToast({
          icon: "none",
          title: "没有可用的试题库",
          duration: 3000
        })
        return false;
      }
      var examItem = that.data.allExams[e.detail.value];
      wx.navigateTo({
        url: '../answer/answer?exam_no=' + examItem.exam_no + "&exam_name=" + examItem.exam_name
      })
    }

  },

  wrong: function(e) {
    var register = that.data.register;
    if (register != true) {
      wx.showToast({
        icon: "none",
        title: "请先点击登录",
        duration: 5000
      })
    } else {
      if (that.data.allExams == null || that.data.allExams.length <= 0) {
        wx.showToast({
          icon: "none",
          title: "没有可用的试题库",
          duration: 3000
        })
        return false;
      }
      var examItem = that.data.allExams[e.detail.value];
      wx.navigateTo({
        url: '../wrongAnswer/wrongAnswer?exam_no=' + examItem.exam_no + "&exam_name=" + examItem.exam_name
      })
    }

  },

  study: function(e) {
    var register = that.data.register;
    if (register != true) {
      wx.showToast({
        icon: "none",
        title: "请先点击登录",
        duration: 5000
      })
    } else {
      if (that.data.allExams == null || that.data.allExams.length <= 0) {
        wx.showToast({
          icon: "none",
          title: "没有可用的试题库",
          duration: 3000
        })
        return false;
      }
      var examItem = that.data.allExams[e.detail.value];
      wx.navigateTo({
        url: '../training/training?exam_no=' + examItem.exam_no + "&exam_name=" + examItem.exam_name + "&question_num=" + examItem.question_num
      })
    }

  },

  rank: function(e) {
    var register = that.data.register;
    if (register != true) {
      wx.showToast({
        icon: "none",
        title: "请先点击登录",
        duration: 5000
      })
    } else {
      var choseQB = that.data.QBArray[e.detail.value]
      wx.navigateTo({
        url: '../rank/rank?choseQB=' + choseQB
      })
    }
  },
  onPullDownRefresh: function(e) {
    that.getExams();
  }

})