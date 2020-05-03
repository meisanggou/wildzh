function find_index(array, value, key){
    var index = -1;
    if(key == undefined || key == null){
        return array.indexOf(value);
    }
    for(var i=0;i<array.length;i++){
        if(key in array[i]){
            if(array[i][key] == value){
                index = i;
                break
            }
        }
    }
    return index;
}


module.exports = {
    find_index: find_index,
};