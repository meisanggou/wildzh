var _app = getApp();
var captureScreenNumKey = 'capture_screen_num';
var _currentAction = '';

function startSecurityMonitor() {
    wx.onUserCaptureScreen((res) => {
        var _cacheNum = _app.getOrSetCacheData(captureScreenNumKey);
        if (_cacheNum == null) {
            _cacheNum = 0
        }
        _cacheNum = _cacheNum + 1;
        recordCaptureScreen(_cacheNum);
    })
    // 进入检查有没有 未提交的截屏记录
    var cacheNum = _app.getOrSetCacheData(captureScreenNumKey);
    if (cacheNum != null && cacheNum >= 1) {
        recordCaptureScreen(cacheNum);
    }
}

function showSecurityMesg(action, message) {
    // return true 调用方应终止活动
    // return false 可继续
    if (_currentAction == 'exit') {
        return true;
    }
    if (action == 'normal') {
        return false;
    }
    if (action == 'exit') {
        _currentAction = action
        wx.showModal({
            content: message,
            showCancel: false,
            success(res) {
                wx.navigateBack({
                    delta: 1,
                })
                _currentAction = '';
            }
        })
        return true;
    }
    else{
        wx.showModal({
            content: message,
            showCancel: false
        })
    }
    return false;
}

function recordCaptureScreen(num) {
    let cPages = getCurrentPages();
    var data = {
        'times': num,
        'path': cPages[cPages.length - 1].route
    };

    function _error(num) {
        _app.getOrSetCacheData(captureScreenNumKey, num);
        if (num > 3) {
            showSecurityMesg('exit', '当前网络异常【S-CS】，返回上一级');
        }
    }
    wx.request2({
        url: '/security/capture/screen',
        method: 'POST',
        data: data,
        success: res => {
            if (res.statusCode == 200) {
                if (res.data.status == false) {
                    _error(num);
                } else {
                    _app.getOrSetCacheData(captureScreenNumKey, 0);
                    showSecurityMesg(res.data.se['action'], res.data.se['message'])
                }
            } else {
                _error(num);
            }
        },
        fail: function () {
            _error(num);
        }
    })
    // wx.showToast({
    //     title: '发现截屏',
    // })
}


module.exports = {
    startSecurityMonitor: startSecurityMonitor,
    recordCaptureScreen: recordCaptureScreen,
    showSecurityMesg: showSecurityMesg
};