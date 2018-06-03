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
    user_avatar: null,
    errorJine: false,
    errorUser: false
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
        wx.request2({
          url: '/user/whoIsHe/',
          method: "POST",
          data: {"en_user": res.result},
          success: res=> {
            if(res.statusCode != 200){
              wx.showModal({
                content: "内部出错请稍后重试" + res.statusCode,
                confirmText: "确定",
                showCancel: false,
              })
            }
            else if(res.data.status == false){
              wx.showModal({
                content: res.data.data,
                confirmText: "确定",
                showCancel: false,
              })
            }
            else{
              var user_item = res.data.data
              var u = user_item.nick_name
              if(u == null){
                u = user_item.user_no
              }
              that.setData({
                user_avatar: user_item.avatar_url,
                recharge_user_no: user_item.user_no,
                recharge_user: u         
              })
            }
          },
          fail: res=>{
            wx.showModal({
              content: "内部出错请稍后重试.",
              confirmText: "确定",
              showCancel: false,
            })
          }
        })
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
  formSubmit: function (event){
   var form_data = event.detail.value
   this.setData({
     errorUser: false,
     errorJine: false
   })
   if(form_data.jine.length <= 0){
     this.setData({
       errorJine: true
     })
     return false
   }
   if (form_data.user_no.length <= 0) {
     this.setData({
       errorUser: true
     })
     return false
   }
    console.info("form submit")
  }
})