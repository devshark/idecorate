function addMenuIcon(icon,obj){

    if(obj.length > 0){

        obj.append(icon);
        var left_position = obj.offset().left + ((obj.outerWidth() - icon.width()) / 2);
        icon.show();
        icon.offset({left : left_position});
        
    }else{

        icon.hide();

    }
}