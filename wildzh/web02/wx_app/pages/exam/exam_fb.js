var nickNameCache = {};
// pages/me/exam_usage.js
Page({

    /**
     * 页面的初始数据
     */
    data: {
        examNo: null,
        validOpinion: ['有效意见', '无效意见'],
        pickerIndex: 0,
        detailIndex: -1,
        feedbacks: [],
        nickNames: [],
        hiddenModal: true,
        subTemps: ['BvdlC-Wv_oTNseRF8xSu_5B-r2dxv5GIbApYLgqoHMw'],
        showSubscription: true,
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        var examNo = null;
        if ("examNo" in options) {
            examNo = options['examNo'];
            this.getFeedback(examNo);
            this.setData({
                examNo: examNo
            })
        }
        else {
            wx.showModal({
                title: '未指定题库',
                content: "指定题库后，才能查看使用情况",
                showCancel: false,
                success(res) {
                    wx.switchTab({
                        url: "/pages/me/me"
                    })
                }
            })
            return false;
        }
        var that = this;
        wx.getSetting({
            withSubscriptions: true,
            success (res) {
                var show = true;
                var subscriptionsSetting = res.subscriptionsSetting;
                for(var i=0; i<that.data.subTemps.length;i++){
                    var _id = that.data.subTemps[i];
                    if(_id in subscriptionsSetting){
                        if(subscriptionsSetting[_id] == 'accept'){
                            continue
                        }
                    }
                    show = true;
                    break;
                }
                that.setData({
                    showSubscription: show
                })
              }
        })
    },
    showDetail: function(e){
        var index = e.currentTarget.dataset.index;
        if(index == this.data.detailIndex){
            index = -1;
        }
        this.setData({
            detailIndex: index
        })
    },
    bindPeriodChange: function (e) {
        var periodIndex = parseInt(e.detail.value);
        this.setData({
            periodIndex: periodIndex
        })
        this.getFeedback(this.data.examNo);
    },
    getFeedback: function (examNo) {
        wx.showLoading({
            title: '加载中...',
            mask: true
        })
        var that = this;
        wx.request2({
            url: '/exam/question/feedback?exam_no=' + examNo,
            method: 'GET',
            success: res => {
                wx.hideLoading();
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                if (resData.length <= 0) {
                    return false;
                }
                var noMapIndex = {};
                var feedbacks = [];
                for(var i=0;i<resData.length;i++){
                    var rItem = resData[i];
                    rItem.fb_key = rItem.user_no + "-" + rItem.question_no;
                    if(rItem.description.length <= 0){
                        rItem.description = "<未填写>"
                    }
                    feedbacks.push(rItem);
                }
                feedbacks.sort(function (a, b) {
                    if(a.state != b.state){
                        return b.state - a.state;
                    }
                    return a.update_time - b.update_time;
                })
                that.setData({
                    feedbacks: feedbacks
                })
                that.getNickNames(feedbacks);
                
            }
        })
    },
    getNickNames: function (userItems) {
        var user_list = [];
        var nickNames = [];
        for (var i = 0; i < userItems.length; i++) {
            if (userItems[i].user_no in nickNameCache) {
                nickNames.push({'user_no': userItems[i].user_no, 'nick_name': nickNameCache[userItems[i].user_no]});
            }
            else {
                user_list.push(userItems[i].user_no);
                nickNames.push({'user_no': userItems[i].user_no, 'nick_name': null});
            }
        }
        var that = this;
        if (user_list.length <= 0) {
            this.setData({
                nickNames: nickNames
            })
            return true;
        }
        var data = { 'user_list': user_list }
        
        wx.request2({
            url: '/user/nicknames',
            method: 'POST',
            data: data,
            success: res => {
                if (res.data.status == false) {
                    return false;
                }
                var resData = res.data.data;
                var l1 = resData.length;
                for(var j=0;j<l1;j++){
                    var nItem = resData[j];
                    if(nItem['nick_name'] == null){
                        nItem['nick_name'] = '';
                    }
                    nickNameCache[nItem.user_no] = nItem['nick_name'];
                }

                var l2 = nickNames.length;
                for (var i = 0; i < l2; i++) {
                    var uItem = nickNames[i];
                    if(uItem['nick_name'] != null){
                        continue;
                    }
                    if(uItem.user_no in nickNameCache){
                        uItem['nick_name'] = nickNameCache[uItem.user_no];
                    }
                }
                that.setData({
                    nickNames: nickNames
                })

            }
        })
    },
    feedbackClick:function(){
        this.setData({
            hiddenModal: false
        });
    },
    feedbackPickerChange(e){
        this.setData({
            pickerIndex: e.detail.value
        })
    },
    feedbackDescInput: function(e){
        this.setData({
            feedbackDesc: e.detail.value
        });
    },
    toQuestion: function(){
        if(this.data.detailIndex < 0){
            return false;
        }
        var currentFB = this.data.feedbacks[this.data.detailIndex];
        wx.navigateTo({
            url: "../questions/question?select_mode=-1&question_no=" + currentFB.question_no
        })
    },
    cancelFeedback: function(){
        this.setData({
            hiddenModal: true
        });
    },
    confirmFeedback: function(e){
        this.setData({
            hiddenModal: true
        });
        var currentIndex = this.data.detailIndex;
        var currentFeedback = this.data.feedbacks[this.data.detailIndex];
        console.info(currentFeedback);
        var state = 4;
        if(this.data.pickerIndex == 1){
            state = 3;
        }
        var data = {'result': this.data.feedbackDesc, 'state': state, 'question_no': currentFeedback.question_no, 'user_no': currentFeedback.user_no, 'exam_no': this.data.examNo};

        var that = this;
        wx.request2({
            url: '/exam/question/feedback?exam_no=' + this.data.examNo,
            method: 'PUT',
            data: data,
            success: res => {
                if (res.data.status != true) {
                    wx.showModal({
                        title: '处理失败',
                        content: res.data.data,
                        showCancel: false,
                        success(res) {
                        }
                    })
                    
                    return
                }
                else{
                    var feedbacks = that.data.feedbacks;
                    feedbacks.splice(currentIndex, 1)
                    that.setData({
                        feedbackDesc: "",
                        feedbacks: feedbacks,
                        detailIndex: -1
                    })
                    wx.showToast({
                        title:"处理成功"
                    })
                }
                
            }
        })
    },
    subscribeMessage: function(){
        wx.requestSubscribeMessage({
            tmplIds: this.data.subTemps,
            success (res) {
                console.info(res);
             }
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