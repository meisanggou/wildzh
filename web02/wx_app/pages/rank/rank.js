var Bmob = null; //require('../../dist/Bmob-1.6.2.min.js');
var that;
Page({


  data: {
    rankList:[]
  },

  
  onLoad: function (options) {
    that=this;
    wx.showLoading({
      title: '加载中...',
    })
    var choseQB = options.choseQB;
    const queryHistory = Bmob.Query("history");
    queryHistory.equalTo("QB", "==", choseQB);
    queryHistory.include('user', 'post');
    queryHistory.order("-score");
    queryHistory.find().then(res => {
      console.log(res)
      that.setData({
        rankList: res,

      })
      wx.hideLoading()
    });
  },



  
})