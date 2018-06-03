//index.js
//获取应用实例
const app = getApp()

Page({
  data: {
    motto: 'Welcome',
    userInfo: {},
    userItem: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    needRegister: true
  },
  //事件处理函数
  bindViewTap: function () {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  onLoad: function (options) {
    console.info("index on Load")
    if ("project_no" in options) {
      wx.navigateTo({
        url: '../pay?project_no=' + options["project_no"]
      })
    }

    var userItem = wx.getStorageSync(app.globalData.userInfoStorageKey)
    if(userItem == ""){
      this.setData({
        needRegister: false
      })
    }
    else if(userItem.avatar_url != null){
      this.setData({
        needRegister: false,
        userItem: userItem
      })
    }
    else{
      this.setData({
        needRegister: true
      })
    }
    wx.request2({
      url: '/insider/project/',
      method: "GET",
      success: res => {
        var r_data = res.data
        if (r_data["status"] == false) {
          return false
        }
        else if (r_data["data"].length > 0) {
          // wx.setStorageSync(app.globalData.myProjectStorageKey, r_data["data"])
          wx.setStorage({
            key: app.globalData.myProjectStorageKey,
            data: r_data["data"],
          })
          var is_business = true
        }
        else {
          var is_business = false
        }
        this.setData({
          is_business: is_business
        })
        var userItem = wx.getStorageSync(app.globalData.userInfoStorageKey)
        this.setData({
          userItem: userItem
        })
      }
    })
  },
  onReady: function () {
    console.info("index on Ready")
  },

  register: function (e) {
    var that = this
    var userInfo = e.detail.userInfo
    var data = {"avatar_url": userInfo.avatarUrl, "nick_name": userInfo.nickName}
    wx.request2({
      url: '/user/info/',
      method: 'PUT',
      data: data,
      success: res=>{
        var userItem = res.data.data
        wx.setStorageSync(app.globalData.userInfoStorageKey, userItem)
        that.setData({
          needRegister: false,
          userItem: userItem
        })
      }
    })
  },
  join: function () {
    wx.navigateTo({
      url: '../business/join'
    })
  },
  business_main: function () {
    wx.navigateTo({
      url: '../business/main'
    })
  },
  scanCode: function () {
    var that = this
    wx.scanCode({
      success: function (res) {
        var project_no = res.result
        wx.navigateTo({
          url: '../pay?project_no=' + project_no
        })
      },
      fail: function (res) {
        wx.showModal({
          content: "没有扫描到商家信息，请重新扫描",
          confirmText: "确定",
          showCancel: false,
        })
      }
    })
  }
})
