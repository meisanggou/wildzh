// pages/vc/goods.js
Page({

    /**
     * 页面的初始数据
     */
    data: {
        vcBalance: 0,
        vcExpenses: 0,
        hiddenModal: true,
        goods: [],
        goodIndex: -1
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        // this.getVCstatus();
        // this.getVCGoods();
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
        this.getVCstatus();
        this.getVCGoods();
    },
    updateGoods: function(goods){
        for(let i=0,l=goods.length;i<l;i++){
            goods[i]['id'] = goods[i].good_type + '-' + goods[i].good_id;
            if(goods[i].available == 'conditional'){
                this.isEnableGoods(goods[i].good_type, goods[i].good_id);
            }
        }
        this.setData({
            goods: goods
        })
    },
    getVCstatus: function () {
        var that = this;
        wx.request2({
            url: '/vc/status',
            method: 'GET',
            success: res => {
                var pk = res.data;
                if (pk.status != true) {
                    return;
                }
                var data = pk.data;
                var vcBalance = data.balance + data.sys_balance;
                var vcExpenses = data.expenses + data.sys_expenses;
                that.setData({
                    vcBalance: vcBalance,
                    vcExpenses: vcExpenses
                })
            }
        })
    },
    getVCGoods: function () {
        var that = this;
        wx.request2({
            url: '/vc/goods',
            method: 'GET',
            success: res => {
                var pk = res.data;
                if (pk.status != true) {
                    return;
                }
                var data = pk.data;
                that.updateGoods(data.goods);
            }
        })
    },
    toMakeVCPage: function(){
        wx.navigateTo({
            url: "make_vc"
        })
    },
    isEnableGoods: function (good_type, good_id) {
        var that = this;
        var url_args = 'good_type=' + good_type + '&good_id=' + good_id;
        wx.request2({
            url: '/vc/goods/condition?' + url_args,
            method: 'GET',
            success: res => {
                var pk = res.data;
                if (pk.status != true) {
                    return;
                }
                var data = pk.data;
                for(let i=0,l=that.data.goods.length;i<l;i++){
                    var good_item = that.data.goods[i];
                    if(good_item.good_type == good_type && good_item.good_id == good_id){
                        good_item['available'] = data.available;
                        that.setData({
                            ['goods[' + i + '].available']: data.available 
                        })
                        break;
                    }
                }
            }
        })
    },
    goodsExchange: function (g_item) {
        var that = this;
        var data = g_item;
        wx.request2({
            url: '/vc/goods/exchange',
            method: 'POST',
            data: data,
            success: res => {
                var pk = res.data;
                if (pk.status != true) {
                    wx.showModal({
                        title: '兑换失败',
                        content: pk.data,
                        showCancel: false
                    })
                    that.getVCstatus();
                    that.getVCGoods();
                    return;
                }
                var vc = pk.data.vc;
                wx.showToast({
                    title: pk.data.message
                })
                
                var vcBalance = vc.balance + vc.sys_balance;
                var vcExpenses = vc.expenses + vc.sys_expenses;
                that.setData({
                    vcBalance: vcBalance,
                    vcExpenses: vcExpenses
                })
                that.getVCGoods();
            }
        })
    },
    preExchange: function(e){
        var index = e.currentTarget.dataset.index;
        this.setData({
            hiddenModal: false,
            goodIndex: index
        })
    },
    confirmExchange: function(){
        this.setData({
            hiddenModal: true
        })
        var g_item = this.data.goods[this.data.goodIndex];
        this.goodsExchange(g_item);
    },
    cancelExchange: function(){
        this.setData({
            hiddenModal: true
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