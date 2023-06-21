// pages/me/info.js
var app = getApp();
var dt = require("../common/datetime_tools.js");
var that;
var lastUpdateUserKey = 'updateUserTime'

function verify_username(rule, value, param, models) {
    var patt = /^[a-z]+[\w]+$/;
    if (!patt.test(value)) {
        return '账户名必须字母开头，且仅允许由数字字母下划线组成';
    }
}

function verify_nickname(rule, value, param, models) {
    var currentTime = dt.get_timestamp2();
    var lastTime = app.getOrSetCacheData2(lastUpdateUserKey);
    var intervalTime = 3600 * 24 * 30;
    var msg = '昵称可在30天内更新一次！';
    if (lastTime != null && currentTime - lastTime < intervalTime) {
        return msg;
    } 
}

Page({

    /**
     * 页面的初始数据
     */
    data: {
        userName: null,
        nickName: '',
        avatarUrl: '/images/unregister.png',
        showTopTips: false,
        rules: [{
                'name': 'user_name',
                'rules': [{
                    'minlength': 6,
                    'message': '账户名应超过5个字符'
                }, {
                    'maxlength': 20,
                    'message': '账户名应不超过20个字符'
                }, {
                    'validator': verify_username
                }]
            }, {
                'name': 'password',
                'rules': [{
                    'minlength': 6,
                    'message': '密码长度不能小于6位'
                }, {
                    'maxlength': 15,
                    'message': '密码长度太长'
                }]
            },
            {
                'name': 're_password',
                'rules': [{
                    'equalTo': 'password',
                    'message': '两次输入密码不一致'
                }]
            }
        ],
        formData: {},
        n_rules: [{
            'name': 'nick_name',
            'rules': [{
                'minlength': 2,
                'message': '昵称至少2个字符'
            }, {
                'maxlength': 15,
                'message': '昵称不能超过15个字符'
            }, {
                'validator': verify_nickname
            }]
        }],
        n_form_data: {}
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        this.getUserData();

    },
    getUserInfo2: function () {
        var that = this;
        wx.getUserProfile({
            desc: '同步用户头像信息到小程序',
            success: function (e) {
                console.info(e);
                var userInfo = e.userInfo
                var data = {
                    "avatar_url": userInfo.avatarUrl,
                    "nick_name": userInfo.nickName
                }
                wx.showLoading({
                    title: '更新中...',
                    mask: true
                })
                that.updateUserInfoAction(data);
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
    getUserData: function () {
        var that = this;
        wx.request2({
            url: '/user/info/',
            method: 'GET',
            success: res => {
                var userData = res.data.data[0];
                app.getOrSetCurrentUserData(userData);
                that.setData({
                    userName: userData['user_name'],
                    [`formData.user_name`]: userData['user_name'],
                    nickName: userData['nick_name'],
                    avatarUrl: userData['avatar_url'],
                    [`n_form_data.nick_name`]: userData['nick_name']
                });
                wx.hideLoading();
            }
        })
    },
    formInputChange(e) {
        const {
            field
        } = e.currentTarget.dataset
        this.setData({
            [`formData.${field}`]: e.detail.value
        })
    },
    formNickNameChange(e) {
        const {
            field
        } = e.currentTarget.dataset
        this.setData({
            [`n_form_data.${field}`]: e.detail.value
        })
    },
    submitForm: function () {
        this.selectComponent('#form').validate((valid, errors) => {
            console.log('valid', valid, errors)
            if (!valid) {
                const firstError = Object.keys(errors)
                if (firstError.length) {
                    this.setData({
                        error: errors[firstError[0]].message
                    })

                }
            } else {
                var data = this.data.formData;
                var that = this;
                if (this.data.userName == null) {
                    var userName = data['user_name'];
                    var c = '确定要将账户名设置为 ' + userName + '吗？一经设置不可修改！';
                    wx.showModal({
                        title: '确认设置',
                        content: c,
                        showCancel: true, //是否显示取消按钮
                        success: function (res) {
                            if (res.cancel) {
                                //点击取消,默认隐藏弹框
                            } else {
                                that.setUserNamePassword(data);
                            }
                        },
                    })
                } else {
                    delete(data['user_name']);
                    that.setUserNamePassword(data);
                }
            }
        })
    },
    submitNickNameForm: function () {
        var that = this;
        this.selectComponent('#n_form').validate((valid, errors) => {
            console.log('valid', valid, errors)
            if (!valid) {
                const firstError = Object.keys(errors)
                if (firstError.length) {
                    this.setData({
                        error: errors[firstError[0]].message
                    })

                }
            } else {
                // if(this.data.nickName == this.data.n_form_data['nick_name']){
                //     that.setData({
                //         error: '昵称未发生改变'
                //     })
                //     return false;
                // }
                
                // var data = this.data.n_form_data;
                this.getUserInfo2();
            }
        })
    },
    setUserNamePassword: function (data) {
        var that = this;
        wx.request2({
            url: '/user/username',
            data: data,
            method: 'PUT',
            success: res => {
                if (res.data.status == true) {
                    var userData = res.data.data;
                    that.setData({
                        userName: userData['user_name'],
                        [`formData.userName`]: userData['user_name']
                    });
                    wx.showToast({
                        title: '设置成功',
                        duration: 2500
                    });
                } else {
                    that.setData({
                        error: res.data.data
                    })
                }

                wx.hideLoading();
            }
        })
    },
    updateUserInfoAction: function (data) {
        var that = this;
        wx.request2({
            url: '/user/info/',
            method: 'PUT',
            data: data,
            success: res => {
                var userItem = res.data.data
                app.getOrSetCurrentUserData(userItem);
                wx.hideLoading();
                app.getOrSetCacheData2(lastUpdateUserKey, dt.get_timestamp2());
                wx.showToast({
                    title: '更新成功',
                    duration: 2000
                });
                that.setData({
                    nickName: userItem.nick_name,
                    avatarUrl: userItem.avatar_url
                })
            }
        })

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