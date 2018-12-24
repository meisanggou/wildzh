var Bmob = null; //require('../../dist/Bmob-1.6.2.min.js');
var that;
Page({

  data: {
    currentUserId: null
  },


  onLoad: function (options) {
    that = this;
  },


  registerSuccess: function (e) {
    var currentUserId = that.data.currentUserId;
    var realName = e.detail.value.realName;
    var department = e.detail.value.department;
    var workNumber = e.detail.value.workNumber;
    console.log(currentUserId)
    if (!realName) {
      wx.showToast({
        title: '请填写您的姓名',
        icon: 'none',
        duration: 2000
      })
    }
    else if (!department) {
      wx.showToast({
        title: '请填写您的部门',
        icon: 'none',
        duration: 2000
      })
    }
    else if (!workNumber) {
      wx.showToast({
        title: '请填写您的工号',
        icon: 'none',
        duration: 2000
      })
    }
    else{
      let current = Bmob.User.current();
      var currentUserId = current.objectId;
      const queryUser = Bmob.Query('_User');
      queryUser.get(currentUserId).then(res => {
        res.set('department', department)
        res.set("workNumber", workNumber);
        res.set("realName", realName);
        res.set("register", true);
        res.set("QB1Data", [{ "SC": 1, "JD": 1, "FB": 1, "BA": 1 }]);
        res.set("QB2Data", [{ "SC": 1, "JD": 1, "FB": 1, "BA": 1 }]);
        res.set("QB3Data", [{ "SC": 1, "JD": 1, "FB": 1, "BA": 1 }]);
        res.save()


        const queryWA = Bmob.Query('wrongAnswer');
        queryWA.set("userID", currentUserId);
        queryWA.set("QB1", [])
        queryWA.set("QB2", [])
        queryWA.set("QB3", [])
        queryWA.save().then(res => {
          wx.reLaunch({
            url: '../homePage/homePage'
          })
        }).catch(err => {
          console.log(err)
        })


      
      }).catch(err => {
        console.log(err)
      })
    }
  },

  






})