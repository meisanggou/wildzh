/**
 * Created by msg on 10/20/16.
 */


$(document).ready(function(){
    console.info("welcome");
    var m_vm = new Vue({
        el: "#div_main_menu",
        data: {
            menu: {},
            current_m: {}
        },
        methods: {
            next_level_menu: function(index){
                console.info(index);
                console.info(this.menu);
                console.info(this.menu.sub);
                var m = this.menu.sub[index];
                if("sub" in m) {
                    m.parent = this.menu;
                    this.menu = m;
                }
                else if("url" in m){
                    location.href = m.url;
                }
            },
            superior_menu: function(){
                this.menu = this.menu.parent;
            }
        }
    });
    my_async_request2("/menu/", "GET", null, function(data){
        m_vm.menu = {"sub": data};
        m_vm.current_menu = m_vm.menu
    });
});