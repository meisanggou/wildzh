// pages/me/info.js
Page({

    /**
     * 页面的初始数据
     */
    data: {
        showTopTips: false,
        rules: [{
            'name': 'user_name',
            'rules': [{
                'minlength': 5,
                'message': '账户名应超过5个字符'
            }, {
                'maxlength': 20,
                'message': '账户名应不超过20个字符'
            }]
        }],
        formData: {}
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        var rules = [];
        var username_rule = {
            'name': 'user_name',
            'rules': [{
                'minlength': 5,
                'message': '账户名应超过5个字符'
            }]
        }
        rules.push(username_rule);
        this.setData({
            rules: rules
        });
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
                wx.showToast({
                    title: '校验通过'
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