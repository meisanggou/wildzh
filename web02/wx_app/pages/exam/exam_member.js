var app = getApp();
var dt = require("../common/datetime_tools.js");

Page({

    data: {
        allExams: [],
        isQuery: true,
        select_modes: ['普通用户'],
        memberNo: "",
        currentMember: {},
        flows: [],
        endTime: '2016-09-01 11:20:00',
        byDays: true,
        selectDayIndex: 2,
        gDays: [],
        index: 0,
        roleIndex: 0
    },
    onLoad: function(options) {
        var examNo = null;
        if ("examNo" in options) {
            examNo = options['examNo'];
        }
        this.getExams(examNo);
        var gDays = [{
            'desc': '一天',
            'value': 1
        }, {
            'desc': '一星期',
            'value': 7
        }, {
            'desc': '一个月',
            'value': 30
        }, {
            'desc': '半年',
            'value': 183
        }, {
            'desc': '一年',
            'value': 365
        }, {
            'desc': '两年',
            'value': 730
        }]
        this.setData({
            gDays: gDays
        })
    },
    getExams: function(examNo = null) {
        var that = this;
        wx.request2({
            url: '/exam/info/?is_admin=true',
            method: 'GET',
            success: res => {
                var allExams = [];
                var resData = res.data.data;
                var selectIndex = that.data.index;
                for (var index in resData) {
                    if (resData[index].exam_no == examNo) {
                        selectIndex = index;
                    }
                    allExams.push(resData[index]);
                }

                that.setData({
                    allExams: allExams,
                    index: selectIndex
                });
                wx.hideLoading();
            }
        })
    },
    inputNoChange: function(e) {
        var v = e.detail.value;
        this.setData({
            memberNo: v
        })
    },
    bindPickerChange(e) {
        this.setData({
            index: parseInt(e.detail.value)
        })
    },
    toQuery() {
        this.setData({
            isQuery: true,
        })
    },
    bindDateChange(e) {
        var endTime = e.detail.value + " 23:59:59";
        this.setData({
            endTime: endTime
        })
    },
    switchbyDaysChange(e) {
        this.setData({
            byDays: e.detail.value
        })
        if (e.detail.value == true) {
            this.setEndTime();
        }
    },
    bindDaysChange(e) {
        var selectDayIndex = e.detail.value;
        this.setData({
            selectDayIndex: selectDayIndex
        })
        this.setEndTime();
    },
    setEndTime() {
        var selectDayIndex = this.data.selectDayIndex;
        var days = this.data.gDays[selectDayIndex]['value'];
        var now_t = dt.get_timestamp2();
        var v_t = days * 24 * 3600 + now_t;
        var v_s = dt.timestamp_2_datetime(v_t);
        this.setData({
            endTime: v_s
        })
    },
    stringGrantTime(insertTime){
        var nowT = dt.get_timestamp2();
        var intervalT = nowT - insertTime;
        var hSeconds = 3600 * 24;
        var prefix = "";
        if(intervalT < hSeconds){
            prefix = "一天内";
        }
        else if(intervalT < hSeconds * 30){
            prefix = "一月内";
        }
        return prefix;
    },
    queryAction: function() {
        var memberNo = this.data.memberNo;
        var examNo = this.data.allExams[this.data.index].exam_no;
        if (memberNo.length <= 0) {
            wx.showToast({
                title: '请输入用户编号',
                icon: 'none',
                duration: 2000
            })
            return false;
        }
        var data = {
            'member_no': memberNo,
            'exam_no': examNo,
            'flows': 'true'
        };
        var that = this;
        wx.request2({
            url: '/exam/member',
            method: 'GET',
            data: data,
            success: res => {
                if (res.data.status != true) {
                    wx.showModal({
                        title: '无法查询',
                        content: res.data.data,
                        showCancel: false,
                        success(res) {

                        }
                    })
                } else {
                    var mData = res.data.data;
                    var currentMember = {};
                    var rFlows = mData.flows;
                    var fLen = 2;
                    if(rFlows.length < 2){
                        fLen = rFlows.length;
                    }
                    var flows = [];
                    for(var i=0;i<fLen;i++){
                        var fItem = rFlows[i];
                        var s = that.stringGrantTime(fItem.update_time);
                        var oFlow = { 'prefix': s, 'grantTime': dt.timestamp_2_date(fItem.update_time), 'endTime': dt.timestamp_2_date(fItem.end_time), 'updateTime': fItem.update_time}
                        flows.push(oFlow);
                    }
                    if (mData == null) {
                        currentMember = {
                            'memberRole': '无权限',
                            'memberEndTime': '无',
                            'exam_role': -1
                        };
                    } else {
                        currentMember = mData.current;
                        if (currentMember.exam_role == 5) {
                            currentMember.memberRole = '普通用户';
                        } else {
                            currentMember.memberRole = currentMember.exam_role;
                        }
                        if (currentMember.end_time == null) {
                            currentMember.memberEndTime = "永久";
                        } else {
                            currentMember.memberEndTime = dt.timestamp_2_datetime(currentMember.end_time);
                            if (dt.get_timestamp2() > currentMember.end_time){
                                currentMember.memberEndTime = currentMember.memberEndTime + "(已过期)";
                            }
                        }
                    }
                    that.setData({
                        isQuery: false,
                        currentMember: currentMember,
                        flows: flows
                    })
                    that.setEndTime();
                }
            }
        })

    },
    grantAction: function() {
        var memberNo = this.data.memberNo;
        var examNo = this.data.allExams[this.data.index].exam_no;
        var now_t = dt.get_timestamp2();
        var currentMember = this.data.currentMember;
        var sEndTime = this.data.endTime;
        var grantEndTime = dt.datetime_2_timestamp(this.data.endTime);
        var that = this;
        if (grantEndTime < now_t) {
            if (currentMember.exam_role < 0) {
                wx.showModal({
                    title: '警告！',
                    content: '授权时间小于当前时间，无法授权！',
                    showCancel: false,
                    success(res) {
                    }
                })
            } else {
                // 授权时间小于当前时间，将删除该用户授权
                wx.showModal({
                    title: '警告！',
                    content: '授权时间小于当前时间，将删除该用户授权，删除？',
                    success(res) {
                        if (res.confirm) {
                            that.addMember(examNo, memberNo, grantEndTime);
                        } else if (res.cancel) {
                            console.log('用户点击取消')
                        }
                    }
                })
            }
        }
        if(currentMember.exam_role < 0){
            that.addMember(examNo, memberNo, grantEndTime);
        }
        else{
            // 更新用户授权时间
            var s = "更新用户授权有效期由 " + currentMember.memberEndTime + " 变为 " + sEndTime + " 确定？";
            wx.showModal({
                title: '更新授权',
                content: s,
                success(res) {
                    if (res.confirm) {
                        that.addMember(examNo, memberNo, grantEndTime);
                    } else if (res.cancel) {
                    }
                }
            })
        }
        return true;

    },
    addMember: function(examNo, memberNo, endTime) {
        var data = {
            'member_no': memberNo,
            'exam_no': examNo,
            'end_time': endTime,
            'allow_update': true
        };
        var that = this;
        wx.request2({
            url: '/exam/member',
            method: 'POST',
            data: data,
            success: res => {
                if (res.data.status != true) {
                    wx.showModal({
                        title: '无法授权',
                        content: res.data.data,
                        showCancel: false,
                        success(res) {
                        }
                    })
                } else {
                    wx.showToast({
                        title: '成功',
                        icon: 'success',
                        duration: 2000
                    })
                    that.queryAction();
                }
            }
        })

    }

})