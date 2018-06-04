// pages/pay.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    error_info: "加载中...",
    needRecharge: false,
    project_no: null,
    project_name: ""
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this
    if (!("project_no" in options)) {
      this.setData({
        error_info: "请扫描商家二维码"
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
            var yue = 0
            var needRecharge = false
            if(pro_item.is_member == true){
              yue += pro_item.yue + pro_item + zs_yue
            }
            if(yue <= 0){
              var needRecharge = true
            }

            that.setData({
              project_name: pro_item.project_name,
              project_no: pro_item.project_no,
              yue: 0,
              needRecharge: needRecharge
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
  },
  submitPay: function(event){
    var form_data = event.detail.value
    if(form_data.amount.length <= 0){
      this.setData({
        errorAmount: true
      })
      return ""
    }
    form_data.project_no = this.data.project_no
    wx.request2({
      url: '/insider/pay/',
      method: "POST",
      data: form_data,
      success: res => {
        if (res.statusCode != 200) {
          wx.showModal({
            content: "内部出错请稍后重试" + res.statusCode,
            confirmText: "确定",
            showCancel: false,
          })
        }
        else if (res.data.status == false) {
          wx.showModal({
            content: res.data.data,
            confirmText: "确定",
            showCancel: false,
          })
        }
        else {
          wx.showModal({
            content: "付款成功",
            confirmText: "确定",
            showCancel: false,
          })
          that.setData({
            user_nick_name: null,
            user_no: null
          })
        }
      },
      fail: res => {
        wx.showModal({
          content: "内部出错请稍后重试.",
          confirmText: "确定",
          showCancel: false,
        })
      }
    })
  },
  recharge: function(){
    wx.switchTab({
      url: '/pages/mine/me',
    })
  }
})