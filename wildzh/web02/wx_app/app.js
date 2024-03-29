var remote_host = "https://wild.gene.ac"
var version = "7.2.4";
var session_storage_key = "wildzh_insider_session";
var exam_storage_key = "wildzh_current_exam";
var reqRandom = 100; // 用于某些资源防止缓存，加到请求参数中

// remote_host = "http://127.0.0.1:2400"

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

function getOrSetCurrentUserData(value = null) {
    var userInfoStorageKey = "current_user";
    if (value && value.avatar_url) {
        reqRandom = reqRandom + 1;
        if (value.avatar_url.substr(0, 1) == "/") {
            value.avatar_url = remote_host + value.avatar_url + '?r=' + reqRandom;
        }
    }
    return getOrSetCacheData(userInfoStorageKey, value);
}

function getOrSetCacheVersion(value) {
    var key = 'version';
    var cacheVersion = getOrSetCacheData2(key, value);
    return cacheVersion;
}

function mp_login(callback) {
    var device_data = {};
    try {
        const res = wx.getSystemInfoSync()
        device_data['system'] = res['system'];
        device_data['brand'] = res['brand'];
        device_data['model'] = res['model'];
        device_data['pixelRatio'] = res['pixelRatio'];
        device_data['screenWidth'] = res['screenWidth'];
        device_data['screenHeight'] = res['screenHeight'];
        device_data['version'] = res['version'];
    } catch (e) {
        // Do something when catch error
    }

    wx.login({
        success: res => {
            wx.request({
                url: remote_host + '/user/login/wx/',
                method: "POST",
                data: {
                    "code": res.code,
                    "device": device_data
                },
                success: res => {
                    if (res.statusCode == 200 && res.data.status == true) {
                        console.info("auto wx login success")
                        var userData = res.data.data;
                        getOrSetCurrentUserData(userData)
                        wx.setStorageSync(wx.session_storage_key, res.header["Set-Cookie"])
                        if (callback) {
                            callback();
                        }
                    }
                }
            })
            // 发送 res.code 到后台换取 openId, sessionKey, unionId
        }
    })
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
        mp_login();

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
            if (cacheVersion != version) {
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
                    if (newVersion) {
                        getOrSetCacheVersion(version);
                    }
                    if (res.statusCode != 302 && res.statusCode != 401) {
                        origin_success(res);
                    } else if (retry < 3) {
                        mp_login(function () {
                            req.retry = retry + 1;
                            wx.request2(req)
                        })

                    }
                }
            }
            // if(failFunc != null){
            //   return wx.request(req).catch(failFunc);
            // }
            return wx.request(req)
        }
        wx.user_ping = function (callback) {
            wx.request2({
                url: '/user/ping',
                success: function (res) {
                    callback(res);
                },
                fail: function (res) {
                    callback(res);
                }
            })
        }
        this.getDefaultExam();
        return true;
    },

    getOrSetCacheData: getOrSetCacheData,
    getOrSetCacheData2: getOrSetCacheData2,
    getOrSetCurrentUserData: getOrSetCurrentUserData,
    setDefaultExam: function (examItem) {
        var key = 'default.exam';
        this.globalData.defaultExamNo = examItem["exam_no"];
        this.globalData.defaultExamName = examItem["exam_name"];
        this.getOrSetCacheData(key, examItem);
    },
    getDefaultExam: function () {
        var key = 'default.exam';
        var currentExam = this.getOrSetCacheData(key);
        if (currentExam != null && currentExam != undefined) {
            this.globalData.defaultExamNo = currentExam["exam_no"];
            this.globalData.defaultExamName = currentExam["exam_name"];
        }
        return currentExam;
    },
    getOrSetExamCacheData: function (key, value) {
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