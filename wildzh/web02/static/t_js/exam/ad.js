/**
 * Created by meisa on 2018/5/6.
 */
var ad_vm = null;

function init_info(data) {
    if (data == null) {
        var info_url = $("#info_url").val();
        my_async_request2(info_url, "GET", null, init_info);
        return 0;
    }
    if (data.length > 0) {
        ad_vm.all_exams = [];
        for (var index in data) {
            ad_vm.all_exams.push(data[index]);
        }
    }
}

$(function () {
    var data_url = $("#data_url").val();
    var upload_url= $("#upload_url").val();
    ad_vm = new Vue({
        el: "#myTabContent",
        data: {
            all_exams: [],
            current_exam_index: -1,
            ad_desc: "",
            new_pic_url: "",
            new_pic_width: 200,
            ignore_interval: 0,
            enabled: 0
        },
        methods: {
            select_exam: function () {
                var exam = this.all_exams[this.current_exam_index];
                var args = {'exam_no': exam.exam_no};
                my_async_request2(data_url, 'GET', args, function (data) {
                    console.info(data);
                    ad_vm.ad_desc = data.ad_desc;
                    ad_vm.ignore_interval = data.ignore_interval;
                    if (data.enabled) {
                        ad_vm.enabled = 1
                    }
                    else {
                        ad_vm.enabled = 0;
                    }
                })
            },
            upload_pic: function(){
                var u_files = this.$refs.filElem.files;
                if(u_files.length <= 0){
                    return 1;
                }
                var path = window.URL.createObjectURL(u_files[0]);
                ad_vm.new_pic_url = path;
                $("#img_new").css('width', this.new_pic_width + 'px');
                return 0;
            },
            change_pic_width: function(){
                if(this.new_pic_width < 10){
                    this.new_pic_width = 10;
                    //return 1;
                }
                if(this.new_pic_width > 250){
                    this.new_pic_width = 250;
                    //return 1;
                }
                $("#img_new").css('width', this.new_pic_width + 'px');
            },
            insert_pic: function(){
                var u_files = this.$refs.filElem.files;
                if(u_files.length <= 0){
                    return 1;
                }
                var width = $("#img_new").css('width');
                var height = $("#img_new").css('height');
                width = width.substr(0, width.length - 2);
                height = height.substr(0, height.length - 2);
                var data = {"pic": u_files[0]};
                upload_request(upload_url, "POST", data, function(data){
                    ad_vm.new_pic_url = data["pic"];
                    var pic_desc = '[[' + data['pic'] + ':' + width + ':' + height + ']]';
                    ad_vm.ad_desc += pic_desc;
                });
            },
            update: function () {
                if (this.current_exam_index < 0) {
                    popup_show('请先选择一个题库！');
                    return false;
                }
                var exam = this.all_exams[this.current_exam_index];
                var body = {'exam_no': exam.exam_no, 'ad_desc': this.ad_desc,
                    'ignore_interval': this.ignore_interval, 'enabled': this.enabled};
                my_async_request2(data_url, 'PUT', body, function (data) {
                    popup_show('更新成功！');
                });
            }
        }
    });
    init_info();
});