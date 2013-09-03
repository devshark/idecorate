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