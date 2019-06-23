var app = getApp();
var that;
var touchTime = 0;
var touchStartX = 0; //触摸时的原点
var touchStartY = 0;
var touchInterval = null;
Page({

  data: {
    remote_host: app.globalData.remote_host,
    allExams: [],
    optionChar: app.globalData.optionChar,
    examNo: null,
    examName: "",
    questionNum: 0,
    nowQuestionIndex: 0,
    questionItems: [],
    questionAnswer: "",
    nowQuestion: null,
    showAnswer: false,
    isReq: false
  },

  onLoad: function(options) {
    that = this;
    if ("exam_no" in options) {
      var exam_no = options["exam_no"];
      var exam_name = options["exam_name"];
      var question_num = parseInt(options["question_num"]);
      that.loadExam(exam_no, exam_name, question_num);
    }
    else{
      that.getExams();
    }
    
  },
  getExams: function () {
    wx.showLoading({
      title: '加载中...',
    })
    wx.request2({
      url: '/exam/info/',
      method: 'GET',
      success: res => {
        var allExams = [];
        for (var index in res.data.data) {
          if (res.data.data[index]["question_num"] > 0) {
            allExams.push(res.data.data[index]);
          }
        }
        that.setData({
          allExams: allExams
        });
        wx.hideLoading();
      }
    })
  },
  choseExam: function(e){
    if (that.data.allExams == null || that.data.allExams.length <= 0) {
      wx.showToast({
        icon: "none",
        title: "没有可用的试题库",
        duration: 3000
      })
      return false;
    }
    var examItem = that.data.allExams[e.detail.value];
    that.loadExam(examItem.exam_no, examItem.exam_name, examItem.question_num);
  },
  loadExam: function (examNo, examName, questionNum){
    wx.showLoading({
      title: '加载中...',
    })
    that.setData({
      examNo: examNo,
      examName: examName,
      questionNum: questionNum
    })
    var start_no = 0;
    var process = wx.getStorageSync(app.globalData.studyProcessKey);
    console.info(process);
    if (process) {
      if (examNo in process) {
        start_no = process[examNo];
        if (start_no >= questionNum) {
          start_no = 0;
        }
      }
    }
    that.reqQuestion(examNo, start_no, 0);
  },
  after: function(afterNum) {
    if(that.data.nowQuestion == null){
      return false;
    }
    var nowQuestion = that.data.nowQuestion;
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var questionItems = that.data.questionItems;
    var questionLen = questionItems.length;
    var nextIndex = nowQuestionIndex + afterNum;
    if (nowQuestion.question_no >= that.data.questionNum) {
      // 判断是否当前是否是最后一题
      wx.showToast({
        title: "已完成所有学习",
        duration: 3000
      });
      return true;
    }
    if (nextIndex < questionLen) {
      // 调到的题 已经获取
      var nowQuestion = questionItems[nextIndex];
      that.setData({
        nowQuestion: nowQuestion,
        nowQuestionIndex: nextIndex,
        showAnswer: false
      })
      if (questionLen - nextIndex < 11) {
        // 剩余低于10条 预先获取数据
        // 如果已经获取全部数据不再获取
        if (questionItems[questionLen - 1].question_no < that.data.questionNum) {
          that.reqQuestion(that.data.examNo, questionItems[questionLen - 1].question_no + 1, nextIndex)
        }
      }
    } else {
      // 要获得的数据没有预加载
      if (questionItems[questionLen - 1].question_no < that.data.questionNum) {
        // 还有数据可以获取
        wx.showLoading({
          title: '加载中...',
        })
        that.reqQuestion(that.data.examNo, questionItems[questionLen - 1].question_no + 1, nextIndex)
      } else {
        // 已经获取所有数据
        nextIndex = questionLen - 1;
        var nowQuestion = questionItems[nextIndex];
        that.setData({
          nowQuestion: nowQuestion,
          nowQuestionIndex: nextIndex,
          showAnswer: false
        })
      }
    }
  },
  after1: function() {
    that.after(1);
  },

  after10: function() {
    that.after(10);
  },
  before: function (preNum){
    var nowQuestion = that.data.nowQuestion;
    var nowQuestionIndex = that.data.nowQuestionIndex;
    var questionItems = that.data.questionItems;
    var preIndex = nowQuestionIndex - preNum;
    if (nowQuestion.question_no <= 1) {
      // 判断是否当前是否是最一题
      wx.showToast({
        title: "已是第一题",
        icon: "none",
        duration: 1000
      });
      return true;
    }
    if (preIndex >= 0) {
      // 调到的题 已经获取
      var nowQuestion = questionItems[preIndex];
      that.setData({
        nowQuestion: nowQuestion,
        nowQuestionIndex: preIndex,
        showAnswer: false
      })

    } else {
      // 要获得的数据没有预加载
      if (questionItems[0].question_no > 1) {
        // 还有数据可以获取
        wx.showLoading({
          title: '加载中...',
        })
        that.reqQuestion(that.data.examNo, questionItems[0].question_no - 1, preIndex, true);
      } else {
        // 已经获取所有数据
        preIndex = 0;
        var nowQuestion = questionItems[preIndex];
        that.setData({
          nowQuestion: nowQuestion,
          nowQuestionIndex: preIndex,
          showAnswer: false
        })
      }
    }
  },
  before1: function() {
    that.before(1)

  },

  before10: function() {
    that.before(10)
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
  reqQuestion: function(exam_no, start_no, showIndex, desc = false) {
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
    wx.request2({
      url: '/exam/questions/?exam_no=' + exam_no + "&num=20&start_no=" + start_no + "&desc=" + desc,
      method: 'GET',
      success: res => {
        wx.hideLoading();
        if (res.data.status == false) {
          return;
        }
        var newItems = res.data.data;
        var questionItems = null;
        var currentItems = that.data.questionItems;
        var currentLen = currentItems.length;
        var newLen = newItems.length;
        if (currentItems.length <= 0) {
          questionItems = newItems;
        } else if (newItems.length <= 0) {
          questionItems = currentItems;
        } else if (newItems[0].question_no > currentItems[currentLen - 1].question_no) {
          questionItems = currentItems.concat(newItems);
        } else if (newItems[newLen - 1].question_no < currentItems[0].question_no) {
          questionItems = newItems.concat(currentItems);
          showIndex += newLen;
        }
        if (showIndex >= questionItems.length) {
          showIndex = questionItems.length - 1;
        }
        else if(showIndex < 0){
          showIndex = 0;
        }
        // 判断 是否questionItems有题
        if (questionItems.length <= 0) {
          // 没有试题 有问题
        }
        that.setData({
          questionItems: questionItems,
          nowQuestion: questionItems[showIndex],
          nowQuestionIndex: showIndex
        });
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
  choseItem: function(e) {
    var choseIndex = parseInt(e.currentTarget.dataset.choseitem);
    var questionItems = that.data.questionItems;
    var nowQuestion = that.data.nowQuestion;
    var nowQuestionIndex = that.data.nowQuestionIndex;
    for (var index in questionItems[nowQuestionIndex]["options"]) {
      nowQuestion["options"][index]["class"] = "noChose";
      
    }
    if (parseInt(nowQuestion["options"][choseIndex]["score"]) > 0) {
      nowQuestion["options"][choseIndex]["class"] = "chose";
      // 自动进入下一题
      var interval = setInterval(function() {
        clearInterval(interval)
        that.after1();
      }, 1000)
    } else {
      nowQuestion["options"][choseIndex]["class"] = "errorChose";
      // 显示答案
      that.showAnswer();
      // 记录错题
      that.recordWrong(that.data.examNo, [nowQuestion.question_no]);
    }
    that.setData({
      nowQuestion: nowQuestion
    })
  },
  recordWrong: function (exam_no, wrong_question){
    wx.request2({
      url: '/exam/wrong/',
      method: "POST",
      data: { "question_no": wrong_question, "exam_no": exam_no }
    })
  },
  onUnload: function() {
    console.info("un load")
    if(that.data.examNo == null || that.data.nowQuestion == null){
      return false;
    }
    var process = wx.getStorageSync(app.globalData.studyProcessKey);
    if (process) {
      process[that.data.examNo] = that.data.nowQuestion.question_no;
    } else {
      process = {};
      process[that.data.examNo] = that.data.nowQuestion.question_no;
    }
    wx.setStorage({
      key: app.globalData.studyProcessKey,
      data: process,
    })
  },
  // 触摸开始事件
  touchStart: function(e) {
    touchStartX = e.touches[0].pageX; // 获取触摸时的原点
    touchStartY = e.touches[0].pageY;
    // 使用js计时器记录时间    
    touchInterval = setInterval(function() {
      touchTime++;
    }, 100);
  },
  // 触摸结束事件
  touchEnd: function(e) {
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