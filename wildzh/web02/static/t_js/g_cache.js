/**
 * Created by zhouhenglc on 2020/2/3.
 */

var _key_prefix = 'afamily';

function set_local_storage(key, value){
    if(typeof value == 'object'){
        value = JSON.stringify(value);
    }
    key = _key_prefix + '_' + key;
    localStorage.setItem(key, value);
}

function get_local_storage(key){
    key = _key_prefix + '_' + key;
    var value = localStorage.getItem(key);
    try{
        value = JSON.parse(value);
    }
    catch(err){

    }
    return value;
}