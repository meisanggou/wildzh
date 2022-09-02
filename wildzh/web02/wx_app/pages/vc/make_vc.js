// pages/vc/make_vc.js
let videoAd = null;
let adUnitId = 'adunit-2b19f83a1d666b74';
Page({

    /**
     * 页面的初始数据
     */
    data: {
        hideLookAD: false, // 隐藏 看广告得积分
        enableLookAD: false,
        lookADItem: {},
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        
    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady: function () {
        this.initAD();
    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow: function () {
        this.actionVCGive();
    },
    initAD: function () {
        var that = this;
        if (wx.createRewardedVideoAd) {
            videoAd = wx.createRewardedVideoAd({
                adUnitId: adUnitId
            })
            videoAd.onLoad(() => {
                console.log('onLoad event emit')
            })
            videoAd.onError((err) => {
                that.setData({
                    enableLookAD: false
                })
                console.log('onError event emit', err)
            })
            videoAd.onClose((res) => {
                if (res.isEnded) {
                    that.actionVCGive('run');
                }
                console.log('onClose event emit', res)
            })
        }
        

    },
    actionVCGive: function (action) {
        var that = this;
        if (action == null) {
            action = 'check';
        }
        var data = {
            'give_type': 'browse_ad',
            'adUnitId': adUnitId,
            'action': action
        }
        wx.request2({
            url: '/vc/give',
            method: 'POST',
            data: data,
            success: res => {
                var pk = res.data;
                if(!('cr' in pk.data)){
                    that.setData({
                        hideLookAD: true
                    })
                    return;
                }
                var cr = pk.data.cr;
                if (pk.status != true) {
                    that.setData({
                        enableLookAD: false,
                        lookADItem: cr
                    })
                    if(action == 'run'){
                        wx.showModal({
                            title: '获得积分失败',
                            content: pk.data.message,
                            showCancel: false,
                            success(res) {}
                        })
                    }
                    return;
                }
                if (action != 'run') {
                    var nData = {'enableLookAD': true, 'lookADItem': cr};
                    if('tip' in pk.data.cr){
                        nData['ADTip'] = pk.data.cr.tip;
                    }
                    that.setData(nData)
                }
                else{
                    var enableLookAD = pk.data.cr.next_enable;
                    that.setData({
                        lookADItem: cr,
                        enableLookAD: enableLookAD
                    })
                    var msg = '获得' + cr.give_vc_count + '积分';
                    wx.showToast({
                        title: msg,
                        icon: "none",
                        duration: 3000
                    });
                }
            },
            fail: res => {
                that.setData({
                    hideLookAD: true,
                    enableLookAD: false
                })
            }
        })
    },
    toLookAD: function () {
        if (videoAd) {
            wx.showLoading({
              title: '加载广告中',
            })
            videoAd.show().catch(() => {
                // 失败重试
                videoAd.load()
                    .then(() => {
                        wx.hideLoading();
                        videoAd.show();
                    })
                    .catch(err => {
                        wx.hideLoading();
                        wx.showToast({
                            title: "广告加载失败，可能已达观看限制，请稍后重试！",
                            icon: "none",
                            duration: 3000
                        });
                    })
            }).then(() => {
                wx.hideLoading();
            })
        }
        else{
            wx.showToast({
                title: "广告加载失败，可能已达观看限制，请稍后重试！",
                icon: "none",
                duration: 3000
            });
        }
    },
    /**
     * 生命周期函数--监听页面隐藏
     */
    onHide: function () {

    },

    /**
     * 生命周期函数--监听页面卸载
     */
    onUnload: function () {

    },

    /**
     * 页面相关事件处理函数--监听用户下拉动作
     */
    onPullDownRefresh: function () {

    },

    /**
     * 页面上拉触底事件的处理函数
     */
    onReachBottom: function () {

    },

    /**
     * 用户点击右上角分享
     */
    onShareAppMessage: function () {

    }
})