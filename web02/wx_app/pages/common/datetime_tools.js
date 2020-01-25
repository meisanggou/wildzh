/**
 * Created by msg on 2/7/17.
 */

function timestamp_2_datetime(ts) {
    var dt = new Date(parseInt(ts) * 1000);
    var y = dt.getFullYear();
    var M = dt.getMonth() + 1;
    var d = dt.getDate();
    var h = dt.getHours(); 
    var m = dt.getMinutes();
    var s = dt.getSeconds();
    var n_str = y + "-" + M + "-" + d + " " + h + ":" + m + ":" + s
    return n_str;
}

function timestamp_2_date(ts) {
    var dt = new Date(parseInt(ts) * 1000);
    var y = dt.getFullYear();
    var M = dt.getMonth() + 1;
    var d = dt.getDate();
    var h = dt.getHours();
    var m = dt.getMinutes();
    var s = dt.getSeconds();
    var n_str = y + "-" + M + "-" + d;
    return n_str;
}

function get_timestamp() {
    return (new Date()).valueOf();
}


function get_timestamp2() {
    return parseInt(get_timestamp() / 1000);
}


function datetime_2_timestamp(dt_str) {
    var ts = Date.parse(dt_str);
    return ts / 1000;
}

function today_timestamp() {
    var today = new Date();
    return datetime_2_timestamp(today.toLocaleDateString());
}

function duration_show(d) {
    var s_duration = ""; //"(" + d + "秒)";
    var r = d % 60;
    s_duration = r + "秒" + s_duration;
    d = parseInt(d / 60);
    if (d <= 0) {
        return s_duration;
    }
    r = d % 60;
    s_duration = r + "分" + s_duration;
    d = parseInt(d / 60);
    if (d <= 0) {
        return s_duration;
    }
    r = d % 24;
    s_duration = r + "小时" + s_duration;
    d = parseInt(d / 24);
    if (d <= 0) {
        return s_duration;
    }
    s_duration = d + "天" + s_duration;

    return s_duration;
}

function get_current_month() {
    var M = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
    var current_date = new Date();
    var y = current_date.getFullYear();
    var m = current_date.getMonth();
    return y + M[m];
}

function get_past_months() {
    var M = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
    var current_date = new Date();
    var y = current_date.getFullYear();
    var m = current_date.getMonth();
    var months = [];
    for (var i = 0; i < m; i++) {
        months[i] = y + M[i];
    }
    return months;
}

module.exports = {
    today_timestamp: today_timestamp,
    get_timestamp2: get_timestamp2,
    timestamp_2_datetime: timestamp_2_datetime,
    datetime_2_timestamp: datetime_2_timestamp,
    timestamp_2_date: timestamp_2_date
};
