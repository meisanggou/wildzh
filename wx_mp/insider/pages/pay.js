// pages/pay.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    error_info: true,
    project_name: ""
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this
    if (!"project_no" in options) {
      this.setData({
        error_info: "请扫描"
      })
    }
    else {
      this.setData({
        error_info: ""
      })
      wx.request2({
        url: '/insider/project/mine/?project_no=' + options.project_no,
        method: "GET",
        success: res => {
          if (res.statusCode != 200) {
            that.setData({
              error_info: "内部出错请稍后重试" + res.statusCode
            })
          }
          else if (res.data.status == false) {
            that.setData({
              error_info: res.data.data
            })
          }
          else {
            var pro_item = res.data.data
            console.info(pro_item)
            that.setData({
              project_name: pro_item.project_name
            })
          }
        },
        fail: res => {
          that.setData({
            error_info: "内部出错请稍后重试."
          })
        }

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
        var project_no = res.result
        wx.navigateTo({
          url: 'pay?project_no=' + project_no
        })
      },
      fail: function (res) {
        wx.showModal({
          content: "没有扫描到商家信息，请重新扫描",
          confirmText: "确定",
          showCancel: false,
        })
      }
    })
  }
})