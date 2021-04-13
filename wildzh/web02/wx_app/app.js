var remote_host = "https://meisanggou.vicp.net"
var version = "6.5.0";
var session_storage_key = "wildzh_insider_session";
var exam_storage_key = "wildzh_current_exam";
remote_host = "https://wild.gene.ac"

remote_host = "http://127.0.0.1:2400"

function getOrSetCacheData(key, value = null) {
    // 同步存储数据
    var g_key = "wildzh_cache_" + key;
    if (value == null || value == undefined) {
        value = wx.getStorageSync(g_key);
        if (value == "" || value == undefined) {
            value = null;
        }
        return value;
    }
    wx.setStorageSync(g_key, value);
    return value
}

function getOrSetCacheData2(key, value) {
    // 异步存储数据
    var g_key = "wildzh_cache_" + key;
    if (value == null || value == undefined) {
        value = wx.getStorageSync(g_key);
        if (value == "" || value == undefined) {
            value = null;
        }
        return value;
    }
    wx.setStorage({
        key: g_key,
        data: value
    });
    return value
}

function getOrSetCacheVersion (value){
    var key = 'version';
    var cacheVersion = getOrSetCacheData2(key, value);
    return cacheVersion;
}

App({
    onLaunch: function () {
        var that = this;
        console.info("App Lunch")
        wx.remote_host = remote_host
        wx.session_storage_key = session_storage_key;
        wx.removeStorage({
            key: wx.session_storage_key,
        })
        wx.login({
            success: res => {
                wx.request({
                    url: wx.remote_host + '/user/login/wx/',
                    method: "POST",
                    data: {
                        "code": res.code
                    },
                    success: res => {
                        if (res.statusCode == 200 && res.data.status == true) {
                            console.info("auto wx login success")
                            that.getOrSetCurrentUserData(res.data.data)
                            wx.setStorageSync(wx.session_storage_key, res.header["Set-Cookie"])
                        }
                    }
                })
                // 发送 res.code 到后台换取 openId, sessionKey, unionId
            }
        })

        wx.request2 = function (req) {
            var screenData = that.getScreenInfo();
            var origin_req = req;
            if ("header" in req) {
                req.header["rf"] = "async";
                req.header["Cookie"] = wx.getStorageSync(wx.session_storage_key);

            } else {
                req.header = {
                    rf: "async",
                    Cookie: wx.getStorageSync(wx.session_storage_key),
                }
            }
            req.header['X-Device-Screen-Width'] = screenData.width;
            req.header['X-VMP-Version'] = version;
            req.header['X-REQ-API'] = 'v1';
            var cacheVersion = getOrSetCacheVersion();
            var newVersion = false;
            if(cacheVersion != version){
                req.header['X-VMP-Version-N'] = version;
                console.info('new version')
                newVersion = true
            }
            if (req.url[0] == "/") {
                req.url = wx.remote_host + req.url
            }
            var retry = 0;
            if ('retry' in req) {
                retry = req.retry
            }
            if ("success" in req) {
                var origin_success = req.success
                req.success = function (res) {
                    if(newVersion){
                        getOrSetCacheVersion(version);
                    }
                    getOrSetCacheVersion
                    if (res.statusCode != 302 && res.statusCode != 401) {
                        origin_success(res);
                    } else if (retry < 3) {
                        wx.login({
                            success: res => {
                                wx.request({
                                    url: wx.remote_host + '/user/login/wx/',
                                    method: "POST",
                                    data: {
                                        "code": res.code
                                    },
                                    success: res => {
                                        if (res.statusCode == 200 && res.data.status == true) {
                                            console.info("auto wx login success")
                                            that.getOrSetCurrentUserData(res.data.data)
                                            wx.setStorageSync(wx.session_storage_key, res.header["Set-Cookie"])
                                            req.retry = retry + 1;
                                            wx.request2(req)
                                        }
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
        wx.user_ping = function(callback){
            wx.request2({
              url: '/user/ping',
              success: function(res){
                  callback(res);
              },
              fail: function(res){
                  callback(res);
              }
            })
        }
        this.getDefaultExam();
        return true;
        // 登录
        wx.login({
            success: res => {
                wx.request({
                    url: wx.remote_host + '/user/login/wx/',
                    method: "POST",
                    data: {
                        "code": res.code
                    },
                    success: res => {
                        console.info("App Wx Login Success")
                        that.getOrSetCurrentUserData(res.data.data)
                        wx.setStorageSync(wx.session_storage_key, res.header["Set-Cookie"])
                    }
                })
                // 发送 res.code 到后台换取 openId, sessionKey, unionId
            }


        })
        this.getScreenInfo(false);
    },
    setDefaultExam: function (examItem) {
        this.globalData.defaultExamNo = examItem["exam_no"];
        this.globalData.defaultExamName = examItem["exam_name"];
        wx.setStorageSync(exam_storage_key, examItem);
    },
    getDefaultExam: function () {
        var currentExam = wx.getStorageSync(exam_storage_key);
        if (currentExam != null && currentExam != undefined) {
            this.globalData.defaultExamNo = currentExam["exam_no"];
            this.globalData.defaultExamName = currentExam["exam_name"];
        }
    },
    getOrSetCacheData: getOrSetCacheData,
    getOrSetCacheData2: getOrSetCacheData2,
    getOrSetCurrentUserData: function (value = null) {
        return this.getOrSetCacheData(this.globalData.userInfoStorageKey, value);
    },
    getOrSetExamCacheData: function (key, value = null) {
        if (this.globalData.defaultExamNo == null) {
            return null;
        }
        var g_key = this.globalData.defaultExamNo + "_" + key;
        return this.getOrSetCacheData2(g_key, value);
    },
    getScreenInfo: function (needReturn = true) {
        if (this.globalData.screenData != null) {
            return this.globalData.screenData;
        }
        var that = this;
        if (needReturn == true) {
            var res = wx.getSystemInfoSync()
            that.globalData.screenData = new Object();
            that.globalData.screenData["width"] = res.windowWidth;
            that.globalData.screenData["height"] = res.windowHeight;
            return that.globalData.screenData;
        } else {
            wx.getSystemInfo({
                success(res) {
                    console.info(res.safeArea);
                    that.globalData.screenData = new Object();
                    that.globalData.screenData["width"] = res.windowWidth;
                    that.globalData.screenData["height"] = res.windowHeight;
                }
            })
            return null;
        }
    },
    globalData: {
        version: version,
        userInfo: null,
        nowQuestionList: [],
        nowAnswerResultList: [],
        wrongAnswerList: [],
        allTestIdKey: "wildzh_testids",
        testIdPrefix: "wildzh_test_",
        sessionStorageKey: session_storage_key,
        userInfoStorageKey: "current_user",
        myProjectStorageKey: "wildzh_my_projects",
        studyProcessKey: "wildzh_study_process", //待废弃
        examStorageKey: exam_storage_key,
        remote_host: remote_host,
        userItem: {},
        optionChar: ["A", "B", "C", "D", "E", "F", "G", "H"],
        defaultExamNo: null,
        defaultExamName: "",
        screenData: null,
        roleMap: {
            'owner': 1,
            'superAdmin': 2,
            'admin': 3,
            'member': 5,
            'partDesc': 25
        }
    }
})