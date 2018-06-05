//获取应用实例
const app = getApp()
// pages/mine/my.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    needRegister: true,
    userItem: {},
    identity_qr: null

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    console.info("page me on load")
    wx.request2({
      url: '/user/whoIam/',
      method: "GET",
      success: res => {
        if (res.statusCode == 200) {
          var userItem = res.data.data
          wx.setStorage({
            key: app.globalData.userInfoStorageKey,
            data: userItem,
          })
          var shy_me = encodeURIComponent(userItem.shy_me)
          var identity_qr = app.globalData.remote_host + "/user/qr/?whoIs=" + shy_me
          var needRegister = true
          if(userItem["avatar_url"] != null){
            needRegister = false
          }
          this.setData({
            userItem: userItem,
            identity_qr: identity_qr,
            needRegister: needRegister
          })
        }

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
    console.info("Pull down Refresh")
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

  },
  register: function (e) {
    var that = this
    var userInfo = e.detail.userInfo
    var data = { "avatar_url": userInfo.avatarUrl, "nick_name": userInfo.nickName }
    wx.request2({
      url: '/user/info/',
      method: 'PUT',
      data: data,
      success: res => {
        var userItem = res.data.data
        wx.setStorage(app.globalData.userInfoStorageKey, userItem)
        that.setData({
          needRegister: false,
          userItem: userItem
        })
      }
    })
  }
})