
var Bmob = null; //require('../../dist/Bmob-1.6.2.min.js');
var that;
Page({
  data: {
    image_width: getApp().screenWidth / 4 - 10,
    loading: false,
    images: [],
    urlArr: [],
    reasonList: ["功能增改", "遇到bug", "题目出错", "其他问题"],
    id: null,
    choseReason: '',
  },

  onLoad: function (options) {
    that = this;

  },

  bindSubmit: function (e) {
    var reason = that.data.choseReason;
    var content = e.detail.value.content;
    let current = Bmob.User.current();
    var currentUserId = current.objectId;
    if (!reason) {
      wx.showToast({
        title: '请选择反馈原因',
        icon: 'none',
        duration: 2000
      })
    }
    else if (!content) {
      wx.showToast({
        title: '请填写具体说明',
        icon: 'none',
        duration: 2000
      })
    }
    else {


      const queryFB = Bmob.Query('feedBack');
      const pointer = Bmob.Pointer('_User')
      const poiID = pointer.set(currentUserId)
      queryFB.set("content", content)
      queryFB.set("reason", reason)
      queryFB.set("user", poiID)
      queryFB.save().then(res => {
        wx.showModal({
          title: '反馈成功',
          content: '已经收到您的反馈，谢谢。',
          showCancel: false,
          confirmText: '我知道啦',
          confirmColor: '#7a89df',
          success: function (res) {
            if (res.confirm) {
              wx.navigateBack();
            }
          }
        })
      }).catch(err => {
        console.log(err)
      })
    }
  },

  choseReason: function (e) {
    var index = e.currentTarget.dataset.index;
    that.setData({
      id: index,
      choseReason: that.data.reasonList[index]
    })
    console.log(that.data.id)
  },

  upImg: function () {
    var that = this;
    wx.chooseImage({
      count: 9,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: function (res) {

        wx.showNavigationBarLoading()
        that.setData({
          loading: false
        })
        var urlArr = that.data.urlArr;
        var tempFilePaths = res.tempFilePaths;
        var images = that.data.images;

        that.setData({
          images: images.concat(tempFilePaths)
        });
        var imgLength = tempFilePaths.length;
        if (imgLength > 0) {
          var newDate = new Date();
          var newDateStr = newDate.toLocaleDateString();
          var j = 0;
          for (var i = 0; i < imgLength; i++) {
            var tempFilePath = [tempFilePaths[i]];
            var extension = /\.([^.]*)$/.exec(tempFilePath[0]);
            if (extension) {
              extension = extension[1].toLowerCase();
            }
            var name = newDateStr + "." + extension;
            var file = new Bmob.File(name, tempFilePath);
            file.save().then(function (res) {
              wx.hideNavigationBarLoading()
              var url = res.url();
              console.log("第" + i + "张Url" + url);
              urlArr.push({ url });
              j++;
              console.log(j, imgLength);
              that.setData({
                urlArr: urlArr,
                loading: true
              });
            },
              function (error) {
                console.log(error)
              });
          }
        }
      }
    })
    console.log(that.data.urlArr)
  },


  delete: function (e) {
    var index = e.currentTarget.dataset.index;
    var images = that.data.images;
    var urlArr = that.data.urlArr;
    urlArr.splice(index, 1);
    images.splice(index, 1);
    that.setData({
      images: images,
      urlArr: urlArr
    });
    console.log(that.data.urlArr)
  }
})