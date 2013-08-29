$(function(){
    
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

});