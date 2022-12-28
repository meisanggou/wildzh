// pages/videos/video_index.js
var app = getApp();
Page({

    /**
     * 页面的初始数据
     */
    data: {
        remote_host: app.globalData.remote_host,
        videos: []
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

    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow: function () {
        this.getVideos();
    },
    getVideos: function(){
        var examNo = app.globalData.defaultExamNo;
        var that = this;
        wx.request2({
          url: '/video/map?exam_no=' + examNo,
          success: res => {
            var resData = res.data.data;
            for(var i=0;i<resData.length;i++){
                var desc = resData[i].video_desc;
                if(desc.length > 30){
                    desc = desc.substr(0, 30) + ' ...';
                }
                resData[i].short_desc = desc;
            }
            that.setData({
                videos: resData
            })
          }
        })
    },
    toVideo: function(e){
        console.info(e);
        var video_uuid = e.currentTarget.dataset.videoUuid;
        wx.navigateTo({
            url: '../videos/video_play?video_uuid=' + video_uuid
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

    },

    /**
     * 用户点击右上角分享
     */
    onShareAppMessage: function () {

    }
})