var app = getApp();
var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
Page({
  data: {
    remote_host: app.globalData.remote_host,
    optionChar: app.globalData.optionChar,
    examNo: null,
    examName: "",
    questionNum: 0,
    nowQuestionIndex: 0,
    questionItems: [],
    questionAnswer: "",
    nowQuestion: null,
    showAnswer: false,
    showRemove: false,
    isReq: false
  },


  onLoad: function(options) {
    that = this;
    if (!("exam_no" in options)) {
      wx.showModal({
        title: '页面加载失败',
        content: "页面缺少必要的参数，确定返回首页",
        showCancel: false,
        success(res) {
          wx.navigateBack({
            delta: 1
          })
        }
      })
      return false;
    }
    wx.showLoading({
      title: '加载中...',
    })
    var examNo = options["exam_no"];
    var examName = options["exam_name"];
    // 获取错题列表
    wx.request2({
      url: '/exam/wrong/?exam_no=' + examNo,
      methods: "GET",
      success: function(res) {
        if (res.data.status != true) {
          wx.hideLoading();
          wx.showModal({
            title: '无法获取错题信息',
            content: "无法正确获取信息，确定返回首页",
            showCancel: false,
            success(res) {
              wx.navigateBack({
                delta: 1
              })
            }
          })
          return false;
        }
        var questionItems = res.data.data;
        if (questionItems.length <= 0) {
          wx.hideLoading();
          wx.showModal({
            title: '无错题',
            content: "没有发现错题，确定返回首页",
            showCancel: false,
            success(res) {
              wx.navigateBack({
                delta: 1
              })
            }
          })
        }
        // 按照一定规则 排序 questionItems
        that.setData({
          examNo: examNo,
          examName: examName,
          questionItems: questionItems
        })
        // 请求questionItems
        that.reqQuestion(examNo, 0, 0);
      },
      fail: function({
        errMsg
      }) {
        wx.hideLoading();
        wx.showModal({
          title: '页面请求失败',
          content: "无法连接远程主机获取错题信息，确定返回首页",
          showCancel: false,
          success(res) {
            wx.navigateBack({
              delta: 1
            })
          }
        })
      }
    })
  },
  reqQuestion: function(exam_no, startIndex, showIndex) {
    if (exam_no == null) {
      console.info("Can not req, examNo is null");
      return false;
    }
    var isReq = that.data.isReq;
    if (isReq == true) {
      return false;
    } else {
      that.setData({
        isReq: true
      })
    }
    var questionItems = that.data.questionItems;
    var nos = "";
    var endIndex = startIndex + 13;
    if (endIndex > questionItems.length) {
      endIndex = questionItems.length;
    }
    for (var i = startIndex; i < endIndex; i++) {
      nos += "," + questionItems[i].question_no;
    }
    wx.request2({
      url: '/exam/questions/?exam_no=' + exam_no + "&nos=" + nos,
      method: 'GET',
      success: res => {
        wx.hideLoading();
        if (res.data.status == false) {
          return;
        }
        var newItems = res.data.data;
        for (var i = endIndex - 1; i >= startIndex; i--) {
          for (var j = 0; j < newItems.length; j++) {
            if (questionItems[i].question_no == newItems[j].question_no) {
              questionItems[i]["question_desc"] = newItems[j]["question_desc"];
              questionItems[i]["question_desc_url"] = newItems[j]["question_desc_url"];
              questionItems[i]["options"] = newItems[j]["options"];
              questionItems[i]["answer"] = newItems[j]["answer"];
              break;
            }
          }
        }
        // 判断 是否questionItems有题
        if (questionItems.length <= 0) {
          // 没有错题 有问题
        }
        if (showIndex != null) {
          that.setData({
            questionItems: questionItems,
            nowQuestion: questionItems[showIndex],
            nowQuestionIndex: showIndex,
            questionNum: questionItems.length
          });
        }
        that.setData({
          isReq: false
        })
      },
      fail: function({
        errMsg
      }) {
        wx.hideLoading();
        console.log('request fail', errMsg)
        that.setData({
          isReq: false
        })
      }
    })
  },
  remove: function() {
    var nowQuestion = that.data.nowQuestion;
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var questionItems = that.data.questionItems;
    var questionLen = questionItems.length;
    wx.request2({
      url: '/exam/wrong/?exam_no=' + that.data.examNo,
      method: "DELETE",
      data: {
        "question_no": nowQuestion.question_no
      },
      success: function(res) {
        console.info(res.data);
      }
    })
    questionItems.splice(nowQuestionIndex, 1);
    if (questionItems.length <= 0) {
      wx.showModal({
        title: '无错题',
        content: "已经没有错题，确定返回首页",
        showCancel: false,
        success(res) {
          wx.navigateBack({
            delta: 1
          })
        }
      })
      return true;
    }
    if (nowQuestionIndex >= questionLen) {
      nowQuestionIndex = nowQuestionIndex - 1;
    }
    that.setData({
      nowQuestion: questionItems[nowQuestionIndex],
      questionItems: questionItems,
      nowQuestionIndex: nowQuestionIndex,
      questionNum: questionItems.length,
      showAnswer: false,
      showRemove: false
    })

  },
  after: function(afterNum) {
    var nowQuestion = that.data.nowQuestion;
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var questionItems = that.data.questionItems;
    var questionLen = questionItems.length;
    var nextIndex = nowQuestionIndex + afterNum;
    if (nowQuestionIndex >= questionItems.length - 1) {
      // 判断是否当前是否是最后一题
      wx.showToast({
        title: "已是最后一题",
        icon: "none",
        duration: 2000
      });
      return true;
    }
    if (nextIndex >= questionItems.length) {
      nextIndex = questionItems.length - 1;
    }
    if ("options" in questionItems[nextIndex]) {
      //错题 已经获取内容
      var nowQuestion = questionItems[nextIndex];
      that.setData({
        nowQuestion: nowQuestion,
        nowQuestionIndex: nextIndex,
        showAnswer: false,
        showRemove: false
      })
      // 判断紧接着10条是否都已预获取数据
      for (var i = 1; i < 11 && nextIndex + i < questionLen; i++) {
        if (!("options" in questionItems[nextIndex + i])) {
          that.reqQuestion(that.data.examNo, nextIndex + i, null);
          break;
        }
      }
    } else {
      // 错题没有获取内容
      wx.showLoading({
        title: '加载中...',
        mask: true
      })
      that.reqQuestion(that.data.examNo, nextIndex, nextIndex)
    }
  },
  after1: function() {
    that.after(1);
  },

  after10: function() {
    that.after(10);
  },
  before: function(preNum) {
    var nowQuestion = that.data.nowQuestion;
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var questionItems = that.data.questionItems;
    var preIndex = nowQuestionIndex - preNum;
    if (nowQuestionIndex <= 0) {
      // 判断是否当前是否是第一题
      wx.showToast({
        title: "已是第一题",
        icon: "none",
        duration: 1000
      });
      return true;
    }
    if (preIndex <= 0) {
      preIndex = 0;
    }
    var nowQuestion = questionItems[preIndex];
    that.setData({
      nowQuestion: nowQuestion,
      nowQuestionIndex: preIndex,
      showAnswer: false,
      showRemove: false
    })


  },
  before1: function() {
    that.before(1);
  },

  before10: function() {
    that.before(10);
  },
  choseItem: function(e) {
    var choseIndex = parseInt(e.currentTarget.dataset.choseitem);
    var questionItems = that.data.questionItems;
    var nowQuestion = that.data.nowQuestion;
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var showRemove = false;
    for (var index in questionItems[nowQuestionIndex]["options"]) {
      nowQuestion["options"][index]["class"] = "noChose";
    }
    if (parseInt(nowQuestion["options"][choseIndex]["score"]) > 0) {
      nowQuestion["options"][choseIndex]["class"] = "chose";
      showRemove = true;
    } else {
      nowQuestion["options"][choseIndex]["class"] = "errorChose";
    }
    that.setData({
      nowQuestion: nowQuestion,
      showRemove: showRemove
    })
    // 显示答案
    that.showAnswer();
  },
  showAnswer: function(e) {
    var nowQuestion = that.data.nowQuestion;
    var questionAnswer = "没有答案"
    for (var index in nowQuestion.options) {
      if (parseInt(nowQuestion.options[index]["score"]) > 0) {
        questionAnswer = app.globalData.optionChar[index] + "、" + nowQuestion.options[index]["desc"];
      }
    }
    that.setData({
      showAnswer: true,
      questionAnswer: questionAnswer
    })
  },
  // 触摸开始事件
  touchStart: function (e) {
    touchStartX = e.touches[0].pageX; // 获取触摸时的原点
    touchStartY = e.touches[0].pageY;
    // 使用js计时器记录时间    
    touchInterval = setInterval(function () {
      touchTime++;
    }, 100);
  },
  // 触摸结束事件
  touchEnd: function (e) {
    var touchEndX = e.changedTouches[0].pageX;
    var touchEndY = e.changedTouches[0].pageY;
    var touchMoveX = touchEndX - touchStartX;
    var touchMoveY = touchEndY - touchStartY;
    if (Math.abs(touchMoveY) < 0.618 * Math.abs(touchMoveX)) {
      // 向左滑动   
      if (touchMoveX <= -30 && touchTime < 10) {
        //执行切换页面的方法
        that.after1();
      }
      // 向右滑动   
      if (touchMoveX >= 30 && touchTime < 10) {
        that.before1();
      }
    }

    clearInterval(touchInterval); // 清除setInterval
    touchTime = 0;
  }


})