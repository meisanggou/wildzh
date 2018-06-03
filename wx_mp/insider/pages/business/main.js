//获取应用实例
const app = getApp()
// pages/business/main.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    project_name: "",
    project_qr: null,
    disable_recharge: true,
    recharge_num: null,
    recharge_user: null
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var myProjects = wx.getStorageSync(app.globalData.myProjectStorageKey)
    var project_qr = app.globalData.remote_host + "/file/insider/project/" + myProjects[0].project_no + "_qr.png"
    if(myProjects.length > 0){
      this.setData({
        project_name: myProjects[0].project_name,
        project_qr: project_qr
      })
    }
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
  
  },
  scanCode: function () {
    var that = this
    wx.scanCode({
      success: function (res) {
        console.info(res.result)
      },
      fail: function (res) {
        wx.showModal({
          content: "没有扫描到用户信息，请重新扫描",
          confirmText: "确定",
          showCancel: false,
        })
      }
    })
  },
  formSubmit: function(){
    console.info("form submit")
  }
})