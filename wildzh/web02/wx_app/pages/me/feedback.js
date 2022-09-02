// pages/me/feedback.js
var app = getApp();
Page({

    /**
     * 页面的初始数据
     */
    data: {
        examNo: -1,
        fbItems: [],
        fbNum: 0,
        fbAvailNum: 0,
        fbPendingNum: 0
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        this.setData({
            examNo: app.globalData.defaultExamNo
        });
        this.getFeedback();
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
    setFeedbackItems(items){
        var fbNum = items.length;
        var fbAvailNum = 0;
        var fbPendingNum = 0;
        for(var i=0;i<fbNum;i++){
            var state = items[i].state;
            var state_desc = '未知';
            if(state < 1){
                fbPendingNum += 1;
                state_desc = '未处理';
            }
            else if(state == 4){
                fbAvailNum += 1;
                state_desc = '有效反馈';
            }
            else if(state == 3){
                state_desc = '无效反馈';
            }
            else{
                state_desc = '未知';
            }
            items[i].state_desc = state_desc;
        }
        this.setData({
            fbItems: items,
            fbNum: fbNum,
            fbAvailNum: fbAvailNum,
            fbPendingNum: fbPendingNum
        })
    },
    getFeedback: function(){
        var url = '/exam/question/feedback?exam_no=' + this.data.examNo;
        url += '&max_state=4&user=';
        var that = this;
        wx.request2({
            url: url,
            method: 'GET',
            success: res => {
                if (res.data.status != true) {
                    wx.showToast({
                      title: '获取反馈列表失败，可尝试下拉重试',
                      duration: 5000,
                    })
                } else {
                    var items = res.data.data;
                    that.setFeedbackItems(items);
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
        this.getFeedback();
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