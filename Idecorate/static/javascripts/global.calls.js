$(function() {

    menuIcon = $('<span id="menu_icon" class="menuIconWrap" />');
    menuIcon.html($('<img src="/static/images/img_trans.gif" alt="menu icon" class="menuIcon" />'));

    $('.iDdropdown').simpleDropdown({
        arrows : true,
        arrowUp : $('<img src="/static/images/img_trans.gif" alt="arrow up" class="arrowUp" />'),
        arrowRight : $('<img src="/static/images/img_trans.gif" alt="arrow right" class="arrowRight dark" />'),
        arrowDown : $('<img src="/static/images/img_trans.gif" alt="arrow down" class="arrowDown" />'),
        arrowLeft : $('<img src="/static/images/img_trans.gif" alt="arrow left" class="arrowLeft dark" />')
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

    scrollAnimation();
    $(window).scroll(scrollAnimation);

    $('#back_to_top').click(function(e){

        e.preventDefault();

        $(window).unbind('scroll');

        $('html, body').animate({scrollTop:0}, 400, function(){

            scrollAnimation();
            $(window).scroll(scrollAnimation);
            
        });

    });

    repositionFooter();
    $(window).resize(repositionFooter);

    $('.FooterMenu').children('li').each(function(){

        var $this = $(this);
        var $arrow = $('<span class="arrowWrapper"><img src="/static/images/img_trans.gif" alt="arrow" class="arrowDown dark" /></span>');

        if ($this.children('ul').length > 0) {
            $this.children('a').append($arrow);
        }

        $this.click(function(e){

            e.preventDefault();

            $this.children('ul').slideToggle(200,function(){

                $this.siblings().children('ul').slideUp(100);

            });

        });

    });

});