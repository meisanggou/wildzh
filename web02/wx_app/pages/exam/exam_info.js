// pages/me/exam_info.js
var app = getApp();
Page({

    /**
     * 页面的初始数据
     */
    data: {
        remote_host: app.globalData.remote_host,
        isAdmin: false,
        acl: '',
        acl_warn: '',
        examNo: null,
        examPic: null,
        examName: '',
        examDescRich: []
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        var examNo = null;
        if ("examNo" in options) {
            examNo = options['examNo'];
            this.getExams(examNo);
        }
        else{
            wx.showModal({
                title: '未指定题库',
                content: "指定题库后，才能查看详情",
                showCancel: false,
                success(res) {
                    wx.switchTab({
                        url: "/pages/me/me"
                    })
                }
            })
            return false;
        }
    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady: function () {

    },
    getExams: function (examNo) {
        var that = this;
        wx.request2({
            url: '/exam/info/?rich=true&exam_no=' + examNo,
            method: 'GET',
            success: res => {
                var allExams = [];
                var resData = res.data.data;
                if(res.data.status == false || resData.length <= 0){
                    wx.showModal({
                        title: '题库不存在',
                        content: "未查询到题库详情，确认返回，切换题库",
                        showCancel: false,
                        success(res) {
                            wx.switchTab({
                                url: "/pages/me/me"
                            })
                        }
                    })
                    return false;
                }
                var examItem = resData[0];
                var isAdmin = false;
                var acl = '';
                var acl_warn = '';
                var e_role = examItem['exam_role'];
                if(e_role <= 3){
                    isAdmin = true;
                }
                else{
                    if(e_role == 20){
                        acl = '部分题目';
                        acl_warn = '(非公开题目无法查看)';
                    }
                    else if(e_role == 22){
                        acl = '部分题目的题目与答案';
                        acl_warn = '(不包含解析)';
                    }
                    else if(e_role == 25){
                        acl = '部分题目的题目';
                        acl_warn = '(不包含答案与解析)';
                    }
                }
                that.setData({
                    examNo: examItem['exam_no'],
                    examName: examItem['exam_name'],
                    examDescRich: examItem['rich_exam_desc'],
                    isAdmin: isAdmin,
                    acl: acl,
                    acl_warn: acl_warn
                });
                wx.hideLoading();
            }
        })
    },
    toGrantPage: function(){
        var examNo = this.data.examNo;
        if(examNo == null){
            return false;
        }
        wx.navigateTo({
            url: "exam_member?examNo=" + this.data.examNo
        })
    },
    toFBPage: function () {
        var examNo = this.data.examNo;
        if (examNo == null) {
            return false;
        }
        wx.navigateTo({
            url: "exam_fb?examNo=" + this.data.examNo
        })
    },
    toUsagePage: function () {
        var examNo = this.data.examNo;
        if (examNo == null) {
            return false;
        }
        wx.navigateTo({
            url: "exam_usage?examNo=" + this.data.examNo
        })
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