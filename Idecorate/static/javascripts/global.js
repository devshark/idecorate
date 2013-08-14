$(function() {

    menuIcon = $('<span id="menu_icon" class="menuIconWrap" />');
    menuIcon.html($('<img src="'+transparent+'" alt="menu icon" class="menuIcon" />'));

    $('.iDdropdown').simpleDropdown({
        arrows : true,
        arrowUp : $('<img src="'+transparent+'" alt="arrow up" class="arrowUp" />'),
        arrowRight : $('<img src="'+transparent+'" alt="arrow right" class="arrowRight" />'),
        arrowDown : $('<img src="'+transparent+'" alt="arrow down" class="arrowDown" />'),
        arrowLeft : $('<img src="'+transparent+'" alt="arrow left" class="arrowLeft" />')
    });

    if($('.iDdropdown .active').parents('.subMenu').length){
        $('.iDdropdown .active').parents('li:last').addClass('iconized');
    }else{
        $('.iDdropdown .active').parent().addClass('iconized');
    }

    addMenuIcon($('.iconized'));

    $('.iDdropdown').children('li').hover(function(e){
        if(!$(this).hasClass('iconized')){
            addMenuIcon($(this));
        }
    },
    function(e){
        if(!$(this).hasClass('iconized')){
            addMenuIcon($('.iconized'));
        }
    });
});

function addMenuIcon(obj){

    obj.append(menuIcon);
    var left_position = obj.offset().left + ((obj.width() - menuIcon.width()) / 2);
    menuIcon.show();
    menuIcon.offset({left : left_position});
}



