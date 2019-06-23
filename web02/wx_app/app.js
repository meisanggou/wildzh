var remote_host = "https://meisanggou.vicp.net"
// var remote_host = "http://172.16.110.10:2401"
// remote_host = "http://127.0.0.1:2400"
App({
  onLaunch: function () {
    var that = this;
    wx.getSystemInfo({
      success: function (res) {
        that.screenWidth = res.windowWidth;
        that.screenHeight = res.windowHeight;
        that.pixelRatio = res.pixelRatio;
      }
    });
    console.info("App Lunch")
    wx.remote_host = remote_host
    wx.session_storage_key = "wildzh_insider_session"
    wx.request2 = function (req) {
      var origin_req = req;
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
            console.info(res.statusCode);
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
      // if(failFunc != null){
      //   return wx.request(req).catch(failFunc);
      // }
      return wx.request(req)
    }
    // 登录
    wx.login({
      success: res => {
        wx.request({
          url: wx.remote_host + '/user/login/wx/',
          method: "POST",
          data: { "code": res.code },
          success: res => {
            console.info("App Wx Login Success")
            wx.setStorageSync(that.globalData.userInfoStorageKey, res.data.data)
            wx.setStorageSync(wx.session_storage_key, res.header["Set-Cookie"])
          }
        })
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })
  },
  globalData: {
    userInfo: null,
    nowQuestionList:[],
    nowAnswerResultList: [],
    wrongAnswerList: [],
    score:0,
    choseQB:'',
    allTestIdKey: "wildzh_testids",
    testIdPrefix: "wildzh_test_",
    sessionStorageKey: "wildzh_insider_session",
    userInfoStorageKey: "wildzh_current_user",
    myProjectStorageKey: "wildzh_my_projects",
    studyProcessKey: "wildzh_study_process",
    remote_host: remote_host,
    userItem: {},
    optionChar: ["A", "B", "C", "D", "E", "F", "G", "H"]
  }
})