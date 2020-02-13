// pages/me/exam_usage.js
Page({

    /**
     * 页面的初始数据
     */
    data: {
        usageItems: []
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        var examNo = null;
        if ("examNo" in options) {
            examNo = options['examNo'];
            this.getUsage(examNo);
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
    getUsage: function (examNo){
        var that = this;
        wx.request2({
            url: '/exam/usage/state?offset_num=1&exam_no=' + examNo,
            method: 'GET',
            success: res => {
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                if(resData.length <= 0){
                    return false;
                }
                resData.sort(function (a, b) {
                    return b.num - a.num;
                })
                that.setData({
                    usageItems: resData
                })
                var user_list = [];
                for(var i=0;i<resData.length;i++){
                    user_list.push(resData[i].user_no);
                }
                that.getNickNames(user_list);
            }
        })
    },
    getNickNames: function (user_list) {
        var data = { 'user_list': user_list}
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
                var usageItems = that.data.usageItems;
                var l1 = resData.length;
                var l2 = usageItems.length;
                for(var i=0;i<l2;i++){
                    var uItem = usageItems[i];
                    for(var j=0;j<l1;j++){
                        var nItem = resData[j];
                        if(nItem.user_no == uItem.user_no){
                            uItem['nick_name'] = nItem['nick_name'];
                            break;
                        }
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