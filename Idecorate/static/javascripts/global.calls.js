$(function() {
    
    $(':input[placeholder]').placeholder();

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
            
            $this.children('a').append($arrow).click(function(e){

                e.preventDefault();

                $this.children('ul').slideToggle(200,function(){

                    $this.siblings().children('ul').slideUp(100);

                });

            });
        }

    });

    $.modal.defaults.closeHTML = '<a title="Close" class="modalCloseImg simplemodal-close">&#10005;</a>';
    $.modal.defaults.position = ["15%",];

    $('#login_account_header, #login_account_footer').click(function(e){

        e.preventDefault();
        $('#user_access').modal({
            overlayClose: true
        });

    });

    $('#news_letter').click(function(e){

        e.preventDefault();
        $('#newsletter_form_wrap').modal({
            closeClass:'closeModalBtn',
            overlayClose: true
        });

    });

    var site_access_request;

    $("#login_form, #signup_form").submit(function(event){

        var $form = $(this);
        var $inputs = $form.find("input, select, button, textarea");
        var serializedData = $form.serialize();
        $('.formMessages').children().remove();
        
        if (site_access_request) {

            site_access_request.abort();

        }

        $inputs.prop("disabled", true);
        site_access_request = $.ajax({
            url: $form.attr('action'),
            type: "post",
            data: serializedData
        });

        site_access_request.done(function (response, textStatus, jqXHR){

            $form.find('.formMessages').html(response.messages);

            if(response.response == "success"){
                
                location.reload();

            }

        });

        site_access_request.fail(function (jqXHR, textStatus, errorThrown){

            var error = "<p>Cant proccess your request. Please try again</p>";
            $form.find('.formMessages').html(error);

        });

        site_access_request.always(function(){

            $inputs.prop("disabled", false);

        });

        event.preventDefault();
    });

    var newsletter_request;

    $('#newsletter_form').submit(function(event) {

        var $form = $(this);
        var $inputs = $form.find("input, select, button, textarea");
        var serializedData = $form.serialize();
        $('.formMessages').children().remove();

        if (newsletter_request) {

            newsletter_request.abort();

        }

        $inputs.prop("disabled", true);
        newsletter_request = $.ajax({
            url: $form.attr('action'),
            type: "POST",
            data: serializedData
        });

        newsletter_request.done(function (response, textStatus, jqXHR){

            $form.find('.formMessages').html(response.messages);

            if(response.response == "success"){
                
                $.modal.close();

                var header = 'Subscribe to our newsletter';
                var message = response.messages + '<h3>Thank you</h3>';

                response_message(header, message);

            }

        });

        newsletter_request.fail(function (jqXHR, textStatus, errorThrown){

            var error = "<p>Cant proccess your request. Please try again</p>";
            $form.find('.formMessages').html(error);

        });

        newsletter_request.always(function(){

            $inputs.prop("disabled", false);

        });

        event.preventDefault();

    });

});