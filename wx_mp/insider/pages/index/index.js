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
    if ("project_no" in options) {
      wx.navigateTo({
        url: '../pay?project_no=' + options["project_no"]
      })
    }
    var userItem = wx.getStorageSync(app.globalData.userInfoStorageKey)
    if(userItem.avatar_url != null){
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
    // wx.request2({
    //   url: '/insider/project/',
    //   method: "GET",
    //   success: res => {
    //     var r_data = res.data
    //     if (r_data["status"] == false) {
    //       return false
    //     }
    //     else if (r_data["data"].length > 0) {
    //       var is_business = true
    //     }
    //     else {
    //       var is_business = false
    //     }
    //     this.setData({
    //       is_business: is_business
    //     })
    //   }
    // })
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
        wx.setStorageSync(app.globalData.userInfoStorageKey, res.data.data)
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
        console.info(res.result)
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
