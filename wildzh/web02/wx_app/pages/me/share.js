// pages/me/share.js
var app = getApp();
Page({

    /**
     * 页面的初始数据
     */
    data: {
        examNo: 0,
        examName: '',
        shareToken: '',
        tips: [{
            'title': '成功邀请指：',
            'items': [{
                'text': '好友从未加入邀请的题库'
            }, {
                'text': '好友必须主动接受邀请'
            }]
        }, {
            'title': '邀请成功后：',
            'items': [{
                'text': '好友将随机获赠一定天数题库成员资格'
            }, {
                'text': '您将随机随机获赠一定天数题库成员资格'
            }]
        }, , {
            'title': '注意事项：',
            'items': [{
                'text': '请将邀请链接发给需要的好友'
            }, {
                'text': '如果好友打开链接，超过一半不接受，我们将有权取消您的邀请权利'
            }]
        }]
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        this.setData({
            examNo: app.globalData.defaultExamNo,
            examName: app.globalData.defaultExamName
        });
        if (this.data.examNo != null) {
            this.getShareInfo();
        } else {
            wx.showModal({
                title: '未选择题库',
                content: "未选择邀请的题库,确定进入【我的】选择题库，再次尝试邀请",
                showCancel: false,
                success(res) {
                    wx.switchTab({
                        url: "/pages/me/me"
                    })
                }
            })
        }

    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow: function () {

    },
    onShareAppMessage: function (res) {
        var t = this.data.shareToken.token;
        var title = '一起加入题库【' + this.data.examName + '】开始刷题';
        var shareObj = {
            title: title,
            path: '/pages/me/me?share_token=' + t
        }
        if ('image_url' in this.data.shareToken) {
            var url = app.globalData.remote_host + this.data.shareToken.image_url;
            console.info(url);
            shareObj['imageUrl'] = url;
        }
        return shareObj
    },
    getShareInfo: function () {
        wx.hideShareMenu();
        this.setData({
            shareToken: ''
        })
        var examNo = this.data.examNo;

        var data = {
            'resource': 'exam',
            'resource_id': examNo
        };
        var that = this;
        wx.request2({
            url: '/share/token',
            method: 'POST',
            data: data,
            success: res => {
                var r_data = res.data;
                if (r_data.status != true) {
                    return false;
                }
                that.setData({
                    shareToken: r_data.data
                })
                wx.showShareMenu({
                    withShareTicket: true,
                });
                if ('tips' in r_data.data) {
                    var tips = [];
                    for (let i = 0, len = r_data.data.tips.length; i < len; i++) {
                        var item = r_data.data.tips[i];
                        var o = {
                            'title': item.title,
                            'items': []
                        };
                        for (let j = 0, l2 = item.items.length; j < l2; j++) {
                            o.items.push({
                                'text': item.items[j]
                            })
                        }
                        tips.push(o);
                    }
                    if (tips.length > 0) {
                        that.setData({
                            tips: tips
                        })
                    }
                }

            }
        })
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

    }
})