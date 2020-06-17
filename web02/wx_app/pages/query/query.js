// pages/query/query.js
var app = getApp();
Page({

  /**
   * 页面的初始数据
   */
  data: {
    examNo: ""
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    this.setData({
      search: this.search.bind(this)
    })
  },
  search: function (value) {
    console.info(value);
    var data = {
      'query_str': value,
      'exam_no': this.data.examNo
    }
    return new Promise((resolve, reject) => {
      wx.request2({
        url: '/exam/query',
        method: 'POST',
        data: data,
        success: res => {
          wx.hideLoading();
          if (res.data.status == false) {
            return;
          }
          var items = res.data.data;
          for(var i=0;i<items.length;i++){
            var item = items[i];
            item['text'] = item['question_desc'];
            item['value'] = item['question_no'];
          }
          resolve(items);
          console.info(res.data);
        },
        fail: function ({errMsg}) {
        }
      })
    })
  },
  selectResult: function (e) {
    console.log('select result', e.detail)
    var item = e.detail.item;
    var question_no = item['question_no'];
    wx.navigateTo({
      url: "../training/training?select_mode=-1&question_no=" + question_no
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
    var examNo = app.globalData.defaultExamNo;
    if (examNo) {} else {
      wx.showModal({
        title: '未选择题库',
        content: "未选择题库,确定进入【我的】选择题库",
        showCancel: false,
        success(res) {
          wx.switchTab({
            url: "/pages/me/me"
          })
        }
      });
      return false;
    }
    this.setData({
      examNo: examNo
    });
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