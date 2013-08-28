$(function() {

    var menuIcon = $('<span id="menu_icon" class="menuIconWrap" />');
    menuIcon.html($('<img src="/static/images/img_trans.gif" alt="menu icon" class="menuIcon" />'));

    $('.iDdropdown').simpleDropdown({
        arrows : true,
        arrowUp : $('<img src="/static/images/img_trans.gif" alt="arrow up" class="arrowUp" />'),
        arrowRight : $('<img src="/static/images/img_trans.gif" alt="arrow right" class="arrowRight" />'),
        arrowDown : $('<img src="/static/images/img_trans.gif" alt="arrow down" class="arrowDown" />'),
        arrowLeft : $('<img src="/static/images/img_trans.gif" alt="arrow left" class="arrowLeft" />')
    });

    $('.iDdropdown .active').parents('li:last').addClass('iconized');

    addMenuIcon(menuIcon,$('.iconized'));
    
    $('.iDdropdown').children('li').hover(function(e){
        if(!$(this).hasClass('iconized')){
            addMenuIcon(menuIcon,$(this));
        }
    },
    function(e){

        if(!$(this).hasClass('iconized')){
            addMenuIcon(menuIcon,$('.iconized'));
        }
    });


    cartDisplay = iDCartDisplay.initializeDisplay({
        wrapper : $('#cart_frame'),
        iframeSrc : CART_URL,
        displayCounter : true,
        showTrigger : $('#my_order')
    });

    if(cartDisplay.displayCounter){
        cartDisplay.__itemCountWrapper.prepend($('<img src="/static/images/img_trans.gif" alt="close cart" />'));
        cartDisplay.__cartWrapper.parent().append(cartDisplay.__itemCountWrapper);
    }

    cartDisplay.__showTrigger.add(cartDisplay.__itemCountWrapper).click(function(e){

        e.preventDefault();
        $('.iconized').removeClass('iconized iDCart');

        if(!cartDisplay.displayed){

            $(this).parents('li:last').addClass('iconized iDCart');

        }else{

            $('.iDdropdown .active').parents('li:last').addClass('iconized');

        }
        cartDisplay.toggleDisplay();
        addMenuIcon(menuIcon,$('.iconized'));

    });
    cartDisplay.__hideTrigger.append($('<img src="/static/images/img_trans.gif" alt="close cart" />'));
    cartDisplay.__hideTrigger.click(function(e){

        e.preventDefault();        

        if(cartDisplay.displayed){

            $('.iconized').removeClass('iconized iDCart');
            $('.iDdropdown .active').parents('li:last').addClass('iconized');
            cartDisplay.toggleDisplay();
            addMenuIcon(menuIcon,$('.iconized'));

        }

    });



    var bannerCentering = function(){

        $('#banner_img').css({marginLeft:(($('#banner_img').width()-$('#banner').width())/2)*-1});

    };
    
    bannerCentering();
    $(window).resize(bannerCentering);

    var footer_hieght = $('footer').outerHeight(true);

    $('footer').height(0);

    scrollAnimation = function(){ 

        var header_height = $('#header').outerHeight(true);

        if ($(this).scrollTop() > header_height) {
            
            $('footer').stop().animate({height:footer_hieght},200);

        }else{

            $('footer').stop().animate({height:0},200);
        }
    }; 

    $(window).scroll(scrollAnimation);

    $('#back_to_top').click(function(e){

        e.preventDefault();

        $(window).unbind('scroll');

        $('html, body').animate({scrollTop:0}, 400, function(){

            $('footer').animate({height:0},200);
            $(window).scroll(scrollAnimation);
            
        });

    });

});