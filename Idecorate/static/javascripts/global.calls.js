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
            
            $this.children('a').append($arrow).click(function(e){

                e.preventDefault();

                $this.children('ul').slideToggle(200,function(){

                    $this.siblings().children('ul').slideUp(100);

                });

            });
        }

    });

    $.modal.defaults.closeHTML = '<a title="Close" class="modalCloseImg simplemodal-close">&#10005;</a>';

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


    $("#login_form, #signup_form").submit(function(event){

        var $form = $(this);
        var $inputs = $form.find("input, select, button, textarea");
        var serializedData = $form.serialize();
        $('.formMessages').children().remove();
        
        if (request) {

            request.abort();

        }

        $inputs.prop("disabled", true);
        request = $.ajax({
            url: $form.attr('action'),
            type: "post",
            data: serializedData
        });

        request.done(function (response, textStatus, jqXHR){

            $form.find('.formMessages').html(response.messages);

            if(response.response == "success"){
                
                location.reload();

            }

        });

        request.fail(function (jqXHR, textStatus, errorThrown){

            var error = "<p>Cant proccess your request. Please try again</p>";
            $form.find('.formMessages').html(error);

        });

        request.always(function(){

            $inputs.prop("disabled", false);

        });

        event.preventDefault();
    });


    $('#newsletter_form').submit(function(event) {

        var $form = $(this);
        var $inputs = $form.find("input, select, button, textarea");
        var serializedData = $form.serialize();
        $('.formMessages').children().remove();

        if (request) {

            request.abort();

        }

        $inputs.prop("disabled", true);
        request = $.ajax({
            url: $form.attr('action'),
            type: "POST",
            data: serializedData
        });

        request.done(function (response, textStatus, jqXHR){

            $form.find('.formMessages').html(response.messages);

            if(response.response == "success"){
                
                $.modal.close();
                var successModal =  $('#modal_default_messages');
                var successModalMessage = response.messages;
                successModalMessage += '<h3>Thank you</h3><a href="#" class="btn closeModalBtn">Ok</a>';
                successModal.addClass('newsletterSubscribe');
                successModal.find('.legend').text('Subscribe to our newsletter');
                successModal.find('.fieldsetContent').html(successModalMessage)
                successModal.modal({
                    closeClass:'closeModalBtn',
                    overlayClose: true
                });

            }

        });

        request.fail(function (jqXHR, textStatus, errorThrown){

            var error = "<p>Cant proccess your request. Please try again</p>";
            $form.find('.formMessages').html(error);

        });

        request.always(function(){

            $inputs.prop("disabled", false);

        });

        event.preventDefault();

    });

});