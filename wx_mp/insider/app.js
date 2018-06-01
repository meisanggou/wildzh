//app.js
App({
  onLaunch: function (options) {
    console.info("App Lunch")
    var that = this
    wx.remote_host = "http://127.0.0.1:2400"
    wx.session_storage_key = "wildzh_insider_session"
    wx.request2 = function (req) {
      var origin_req = req
      if ("header" in req) {
        req.header["rf"] = "async"
        req.header["Cookie"] = wx.getStorageSync(wx.session_storage_key)
      }
      else {
        req.header = { rf: "async", Cookie: wx.getStorageSync(wx.session_storage_key) }
      }
      if (req.url[0] == "/") {
        req.url = wx.remote_host + req.url
      }
      if ("success" in req && !("retry" in req)) {
        var origin_success = req.success
        req.success = function (res) {
          if (res.statusCode != 302) {
            origin_success(res);
          }
          else {
            wx.login({
              success: res => {
                wx.request({
                  url: wx.remote_host + '/user/login/wx/',
                  method: "POST",
                  data: { "code": res.code },
                  success: res => {
                    console.info("auto wx login success")
                    wx.setStorageSync(that.globalData.userInfoStorageKey, res.data.data)
                    wx.setStorageSync(wx.session_storage_key, res.header["Set-Cookie"])
                    req.retry = 1
                    wx.request2(req)
                  }
                })
                // 发送 res.code 到后台换取 openId, sessionKey, unionId
              }
            })
          }
        }
      }
      wx.request(req)
    }
    // 展示本地存储能力
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
    // 登录
    wx.login({
      success: res => {
        wx.request({
          url: wx.remote_host + '/user/login/wx/',
          method: "POST",
          data: { "code": res.code },
          success: res => {
            console.info("App Wx Login Success")
            console.info(that.globalData)
            wx.setStorageSync(that.globalData.userInfoStorageKey, res.data.data)
            wx.setStorageSync(wx.session_storage_key, res.header["Set-Cookie"])
          }
        })
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })
    // 获取用户信息
    // wx.getSetting({
    //   success: res => {
    //     if (res.authSetting['scope.userInfo']) {
    //       // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
    //       wx.getUserInfo({
    //         success: res => {
    //           // 可以将 res 发送给后台解码出 unionId
    //           this.globalData.userInfo = res.userInfo

    //           // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
    //           // 所以此处加入 callback 以防止这种情况
    //           if (this.userInfoReadyCallback) {
    //             this.userInfoReadyCallback(res)
    //           }
    //         }
    //       })
    //     }
    //   }
    // })
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
  globalData: {
    userInfo: null,
    sessionStorageKey: "wildzh_insider_session",
    userInfoStorageKey: "wildzh_current_user"
  }
})