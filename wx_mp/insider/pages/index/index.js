//index.js
//获取应用实例
const app = getApp()

Page({
  data: {
    motto: 'Welcome',
    userInfo: {},
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
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
        hasUserInfo: true
      })
    } else if (this.data.canIUse) {
      // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
      // 所以此处加入 callback 以防止这种情况
      app.userInfoReadyCallback = res => {
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        })
      }
    } else {
      // 在没有 open-type=getUserInfo 版本的兼容处理
      wx.getUserInfo({
        success: res => {
          app.globalData.userInfo = res.userInfo
          this.setData({
            userInfo: res.userInfo,
            hasUserInfo: true
          })
        }
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
    // console.info(app.globalData.hasLogin)
    // if (app.globalData.hasLogin === false) {
    //   wx.login({
    //     success: function(){

    //     }
    //   })
    // }
    console.log(e)
    app.globalData.userInfo = e.detail.userInfo
    console.info(e.detail.userInfo)
    // this.setData({
    //   userInfo: e.detail.userInfo,
    //   hasUserInfo: true
    // })
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
