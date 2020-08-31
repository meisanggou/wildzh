// pages/me/info.js
function verify_username(rule, value, param, models) {
    var patt = /^[\w]+$/;
    if (!patt.test(value)) {
        return '账户名仅允许由数字字母下划线组成';
    }
}

Page({

    /**
     * 页面的初始数据
     */
    data: {
        userName: null,
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
        formData: {}
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        this.getUserData();

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
                that.setData({
                    userName: userData['user_name'],
                    [`formData.user_name`]: userData['user_name']
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
                }
                else{
                    delete(data['user_name']);
                    that.setUserNamePassword(data);
                }
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
                    });
                }
                else{
                    that.setData({
                        error: res.data.data
                    })
                }

                console.info(res);
                wx.hideLoading();
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