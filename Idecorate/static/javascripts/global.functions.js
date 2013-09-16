function confirm(header, message, callback) {

    $('#modal_confirm_prompt').modal({ 
        closeClass:'closeModalBtn',
        overlayClose: true,
        onShow: function (dialog) {

            var modal = this;
             

            $('.fieldsetContent', dialog.data[0]).html(message);

            if(header !== undefined){

                $('.legendWrap', dialog.data[0]).html('<span class="legend">'+header+'</span>');

            }else{

                $('.legendWrap', dialog.data[0]).html('<span class="legend">Confirm</span>');
            }  

            $('.confirmYes', dialog.data[0]).click(function() {

                if ($.isFunction(callback)) {

                    callback.apply();

                }

                modal.close();
            });
        }
    });
}

function response_message(header, message) {

    $('#modal_default_messages').modal({ 
        closeClass:'closeModalBtn',
        overlayClose: true,
        onShow: function (dialog) {

            var modal = this;

            $('.fieldsetContent', dialog.data[0]).html(message);

            if(header !== undefined){

                $('.legendWrap', dialog.data[0]).html('<span class="legend">'+header+'</span>');

            }else{

                $('.legendWrap', dialog.data[0]).html('<span class="legend">Message</span>');
            }
        }
    });
}


function addMenuIcon(icon,obj){

    if(obj.length > 0){

        obj.append(icon);
        var left_position = obj.offset().left + ((obj.outerWidth() - icon.width()) / 2);
        icon.show();
        icon.offset({left : left_position});
        
    }else{

        icon.hide();

    }
};


scrollAnimation = function(){ 

    var header_height = $('#header').outerHeight(true);

    ($(this).scrollTop() > header_height)? $('footer').slideDown(200) : $('footer, .FooterMenu ul').slideUp(200);
    
    repositionFooter();
}; 


repositionFooter = function(){

	var $footer = $('footer');
	var $window = $(window);
	var scroll_left = $window.scrollLeft();
	
	$footer.css({marginLeft: scroll_left * -1});
	
};