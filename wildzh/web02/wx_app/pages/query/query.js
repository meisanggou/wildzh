// pages/query/query.js
var app = getApp();
Page({

  /**
   * 页面的初始数据
   */
  data: {
    examNo: "",
    noResult: false,
    queryStr: "",
    betterExams: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad() {
    this.setData({
      search: this.search.bind(this)
    })
  },
  replaceImg: function (s) {
    var ss = s.replace(/(\[\[([/\w\.]+?):([\d\.]+?):([\d\.]+?)\]\])/g, '<img>');
    return ss;
  },
  search: function (value) {
    var that = this;
    if (value.length <= 0) {
      return new Promise((resolve, reject) => {
        resolve([]);
        that.setData({
          noResult: false,
          queryStr: "",
          betterExams: []
        })
      })
    }
    var data = {
      'query_str': value,
      'exam_no': this.data.examNo
    }

    var queryStr = value;
    return new Promise((resolve, reject) => {
      wx.request2({
        url: '/exam/query2',
        method: 'POST',
        data: data,
        success: res => {
          wx.hideLoading();
          if(res.statusCode != 200){
            return false;
          }
          
          if (res.data.status == false) {
            return;
          }
          var betterExams = []
          var items = res.data.data;
          if ('current' in res.data.data) {
            items = res.data.data['current'];
          }
          if ('better_exams' in res.data.data) {
            betterExams = res.data.data['better_exams'];
          }
          for (var i = 0; i < items.length; i++) {
            var item = items[i];
            item['text'] = that.replaceImg(item['question_desc']);
            item['value'] = item['question_no'];
          }
          resolve(items);
          var noResult = false;
          if (items.length <= 0) {
            var noResult = true;
          }
          that.setData({
            noResult: noResult,
            queryStr: queryStr,
            betterExams: betterExams
          })
        },
        fail: function ({
          errMsg
        }) {}
      })
    })
  },
  selectResult: function (e) {
    var item = e.detail.item;
    var question_no = item['question_no'];
    wx.navigateTo({
      url: "../training/training?select_mode=-1&question_no=" + question_no
    })
  },
  toChangeExam(e) {
      console.info(e);
      var examIndex = e.currentTarget.dataset.examIndex;
      if(examIndex >= this.data.betterExams.length){
        return false;
      }
      var examItem = this.data.betterExams[examIndex];
      if(examItem.exam_role <= app.globalData.roleMap.partDesc){
        var msg = '您需要切换到题库【' + examItem.exam_name + '】再进行搜索，点击确定进入【我的】切换题库' 
        wx.showModal({
          title: '需要切换题库',
          content: msg,
          showCancel: true,
          success(res) {
            wx.switchTab({
              url: "/pages/me/me"
            })
          }
        });
      }
      else{
        // 无权限
        var msg = '您暂时无访问题库【' + examItem.exam_name + '】的权限' 
        wx.showModal({
          title: '无权访问题库',
          content: msg,
          showCancel: false,
          success(res) {
          }
        });
      }
      console.info(examItem);
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
    if(examNo != this.data.examNo){
      this.setData({
        examNo: examNo
      });
      let searchbarComponent = this.selectComponent('#searchbar'); // 页面获取自定义组件实例
      var e = {'detail': {'value': this.data.queryStr}}
      searchbarComponent.inputChange(e);
    }
    
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