// pages/videos/video_play.js
var app = getApp();
var remote_host = app.globalData.remote_host;
var playTime = 0;
var lastPlayTime = 0;
var intervalReportTime = 5;
Page({

    /**
     * 页面的初始数据
     */
    data: {
        videoUuid: "",
        videoSrc: "",
        videoDesc: "",
        initialTime: 0,
        navIndex: 1
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        var video_uuid = options.video_uuid;
        this.getVideoInfo(video_uuid);
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
    getVideoInfo: function(video_uuid){
        var that = this;
        wx.request2({
            url: '/video/entries/' + video_uuid,
            success: res => {
              var resData = res.data.data;
              var videoInfo = resData['info'];
              var videoSrc = remote_host + videoInfo['video_location'];
              var videoDesc = videoInfo['video_desc'];
              var initialTime = resData['progress']['play_seconds'];
              var videoTitle = videoInfo['video_title'];
              that.setData({
                videoUuid: videoInfo.video_uuid,
                videoSrc: videoSrc,
                videoDesc: videoDesc,
                initialTime: initialTime,
                videoTitle: videoTitle
              })
            }
          })
    },
    playTimeUpdate: function(event){
      playTime = event.detail.currentTime;
      if(playTime > lastPlayTime + intervalReportTime){
        lastPlayTime = playTime;
        this.reportPlayTime(lastPlayTime);
      }
    },
    reportPlayTime: function(playTime){
      var data = {'video_uuid': this.data.videoUuid, 'play_seconds': playTime};
      wx.request2({
        url: '/video/progress',
        method: 'PUT',
        data: data,
        success: function(res){

        }
      })
    },
    changeNav: function(event){
      console.info(event);
      var index = parseInt(event.currentTarget.dataset.index);
      this.setData({
        'navIndex': index
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