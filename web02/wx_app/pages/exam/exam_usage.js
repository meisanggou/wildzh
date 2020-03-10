var nickNameCache = {};
// pages/me/exam_usage.js
Page({

    /**
     * 页面的初始数据
     */
    data: {
        periods: ['一周情况', '两周情况', '三周情况', '四周情况'],
        periodIndex: 0,
        usageItems: []
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        var examNo = null;
        if ("examNo" in options) {
            examNo = options['examNo'];
            this.getUsage(examNo, 1);
            this.setData({
                examNo: examNo
            })
        }
        else {
            wx.showModal({
                title: '未指定题库',
                content: "指定题库后，才能查看使用情况",
                showCancel: false,
                success(res) {
                    wx.switchTab({
                        url: "/pages/me/me"
                    })
                }
            })
            return false;
        }
    },
    bindPeriodChange: function (e) {
        var periodIndex = parseInt(e.detail.value);
        this.setData({
            periodIndex: periodIndex
        })
        this.getUsage(this.data.examNo, periodIndex + 1);
    },
    getUsage: function (examNo, offsetNum) {
        wx.showLoading({
            title: '加载中...',
            mask: true
        })
        var that = this;
        wx.request2({
            url: '/exam/usage/state?offset_num=' + offsetNum + '&exam_no=' + examNo,
            method: 'GET',
            success: res => {
                wx.hideLoading();
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                if (resData.length <= 0) {
                    return false;
                }
                var noMapIndex = {};
                var usageItems = [];
                for(var i=0;i<resData.length;i++){
                    var rItem = resData[i];
                    if(rItem.user_no in noMapIndex){
                        var index = noMapIndex[rItem.user_no];
                        usageItems[index].num = usageItems[index].num + rItem.num;
                    }
                    else{
                        usageItems.push(rItem);
                        noMapIndex[rItem.user_no] = usageItems.length - 1;
                    }
                }
                usageItems.sort(function (a, b) {
                    return b.num - a.num;
                })
                that.getNickNames(usageItems);
                
            }
        })
    },
    getNickNames: function (usageItems) {
        var user_list = [];
        for (var i = 0; i < usageItems.length; i++) {
            if (usageItems[i].user_no in nickNameCache) {
                usageItems[i].nick_name = nickNameCache[usageItems[i].user_no];
            }
            else {
                user_list.push(usageItems[i].user_no);
            }
        }

        if (user_list.length <= 0) {
            this.setData({
                usageItems: usageItems
            })
            return true;
        }
        var data = { 'user_list': user_list }
        var that = this;
        wx.request2({
            url: '/user/nicknames',
            method: 'POST',
            data: data,
            success: res => {
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                var l1 = resData.length;
                for(var j=0;j<l1;j++){
                    var nItem = resData[j];
                    nickNameCache[nItem.user_no] = nItem['nick_name'];
                }

                var l2 = usageItems.length;
                for (var i = 0; i < l2; i++) {
                    var uItem = usageItems[i];
                    if('nick_name' in uItem){
                        continue;
                    }
                    if(uItem.user_no in nickNameCache){
                        uItem['nick_name'] = nickNameCache[uItem.user_no];
                    }
                }
                that.setData({
                    usageItems: usageItems
                })

            }
        })
    },
    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady: function () {

    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow: function () {

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