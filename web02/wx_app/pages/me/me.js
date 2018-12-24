var app = getApp();
var that;
Page({

  
  data: {
    userPic: '',
    QB1AllScore: '无记录',
    QB2AllScore: '无记录',
    QB2AllScore: '无记录',
    frequency1: '无记录',
    frequency2: '无记录',
    frequency3: '无记录',
    lastTime:'无记录'
  },

  
  onLoad: function (options) {
    that=this;
    var userItem = wx.getStorageSync(app.globalData.userInfoStorageKey)
    if (userItem.avatar_url) {
      that.setData({
        userPic: userItem.avatar_url,
        register: true,
        realName: userItem.nick_name,
        department: "暂未开放",
      })
    }
    let current = Bmob.User.current();
    var currentUserId = current.objectId;
    const queryUser = Bmob.Query('_User');
    queryUser.get(currentUserId).then(res => {
      var userPic = res.userPic;
      var nickName = res.nickName;
      console.log(nickName)
      var realName = res.realName;
      var department = res.department;
      var workNumber = res.workNumber;
      var lastTime;
      const queryHistory = Bmob.Query("history");
      queryHistory.order("-updatedAt");
      queryHistory.equalTo("userID", "==", currentUserId);
      queryHistory.find().then(res => {
        if (res.length==0){
          that.setData({
            userPic: userPic,
            nickName: nickName,
            realName: realName,
            department: department,
            workNumber: workNumber,
          })
        }
        else{
          lastTime = res[0].updatedAt;
          for (var i = 0; i < res.length; i++) {
            if (res[i].QB == '测试题库第一套') {
              var QB1AllScore = res[i].allScore;
              var frequency1 = res[i].frequency;
            }
            else if (res[i].QB == '测试题库第二套') {
              var QB2AllScore = res[i].allScore;
              var frequency2 = res[i].frequency;
            }
            else if (res[i].QB == '测试题库第三套') {
              var QB3AllScore = res[i].allScore;
              var frequency3 = res[i].frequency;
            }
          }
          that.setData({
            userPic: userPic,
            nickName: nickName,
            lastTime: lastTime,
            realName: realName,
            department: department,
            workNumber: workNumber,
            QB1AllScore: QB1AllScore,
            QB2AllScore: QB2AllScore,
            QB2AllScore: QB2AllScore,
            frequency1: frequency1,
            frequency2: frequency2,
            frequency3: frequency3,
          })
        }

      
      });
    }).catch(err => {
      console.log(err)
    })
    
  },

  feedBack:function(){
    wx.navigateTo({
      url: '../feedBack/feedBack'
    })
  }

  
})