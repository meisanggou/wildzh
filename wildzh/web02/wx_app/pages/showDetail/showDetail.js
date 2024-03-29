var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
var app = getApp();
Page({

  data: {
    remote_host: app.globalData.remote_host,
    examNo: null,
    questionList: [],
    nowQuestion: null,
    nowQuestionIndex: 0,
    totalQuestionNum: 0,
    showAnswer: false,
    questionAnswer: new Array(),
    optionChar: app.globalData.optionChar
  },


  onLoad: function (options) {
    that = this;
    var index = parseInt(options.index);
    var exam_no = options.exam_no;
    var timestamp = options.timestamp;
    var test_id = app.globalData.testIdPrefix + exam_no + "_" + timestamp;
    console.info(test_id);
    wx.getStorage({
      key: test_id,
      success: function (res) {
        var questionItems = res.data;
        that.setData({
          examNo: exam_no,
          questionList: questionItems,
          nowQuestion: questionItems[index],
          nowQuestionIndex: index,
          totalQuestionNum: questionItems.length
        })
      }
    });
  },

  backHome: function () {
    wx.navigateBack({
      delta: 1
    })
  },

  showAnswer: function () {
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var nowQuestion = that.data.nowQuestion;
    var questionAnswer = new Array();
    for (var index in nowQuestion.options) {
      if (parseInt(nowQuestion.options[index]["score"]) > 0) {
        var tmp_answer = app.globalData.optionChar[index] + "、";
        questionAnswer = questionAnswer.concat({
          'value': tmp_answer,
          'index': -1
        });
        questionAnswer = questionAnswer.concat(nowQuestion.options[index]["desc_rich"]);
      }
    }
    if (questionAnswer.length == 0) {
      questionAnswer[0] = {
        'value': "没有答案",
        'index': -1
      };
    }
    that.setData({
      showAnswer: true,
      questionAnswer: questionAnswer
    })
    this.saveBrushNum();
  },

  after1: function () {
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var totalQuestionNum = that.data.totalQuestionNum;
    var questionList = that.data.questionList;
    if (nowQuestionIndex + 1 < totalQuestionNum) {
      nowQuestionIndex++;
      that.setData({
        nowQuestion: questionList[nowQuestionIndex],
        nowQuestionIndex: nowQuestionIndex,
        showAnswer: false
      })
    }
  },

  before1: function () {
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var questionList = that.data.questionList;
    if (nowQuestionIndex != 0) {
      nowQuestionIndex--;
      that.setData({
        nowQuestion: questionList[nowQuestionIndex],
        nowQuestionIndex: nowQuestionIndex,
        showAnswer: false
      })
    }
  },

  saveBrushNum: function () {
    var nowQuestion = this.data.nowQuestion;
    if ('displayed' in nowQuestion) {
      return false;
    }
    nowQuestion['displayed'] = true;
    var questions = [{
      'no': nowQuestion.question_no,
      'state': 'skip'
    }];
    var examNo = this.data.examNo;
    var data = {
      'exam_no': examNo,
      'num': questions.length,
      'questions': questions
    }
    wx.request2({
      url: '/exam/usage?exam_no=' + examNo,
      method: 'POST',
      data: data,
      success: res => {},
      fail: function () {}
    })
  },
  onShareAppMessage: function () {

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