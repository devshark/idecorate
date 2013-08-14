HEADER = ".compactHeader";
FOOTER = ".compactFooter";
CONTENT = "#content";
BLOCKS = ".block";
CANVAS = "#canvas";
RESIZABLE = $("[resize='true']");
CANVAS_RATIO = [450,285];
$PAGE = $(window);
$HEADER = $(HEADER);
$FOOTER = $(FOOTER);
$BLOCKS = $(BLOCKS);
$CONTENT = $(CONTENT);
$CANVAS = $(CANVAS);
loaded = false;

min_height = 34;

function set_height(){

	$CANVAS.parent().css('padding-top', 0);

	var elements = RESIZABLE;

    $.each(elements,function(index,value){

        var element = $(value);

        var height = (get_content_height() > min_height) ? get_content_height() : min_height;

        if($.browser.chrome && !loaded){

			height -= 3;
			
		}

        height = height - get_siblings_height(element);

        element.parentsUntil(CONTENT).each(function(i, ele){

        	var siblings_height = get_siblings_height($(ele));

            height = height - siblings_height;

        });

        element.height(height);

    });
    
	// set_canvas_size(); // [450,285] base dimension

	loaded = true;
}

function get_siblings_height(element){

    var total = 0;

   	total += element.outerHeight(true) - element.height();

    element.parent().children(BLOCKS).not(element).each(function(i,ele){

        total += $(ele).outerHeight(true);

    });

    return total;
}

function get_min_height(){

	$CONTENT.find(BLOCKS).each(function(i, ele){

		min_height += $(ele).outerHeight(true);

	});

}

function get_content_height(){
	
	return $PAGE.height() - ($HEADER.outerHeight(true) + $FOOTER.outerHeight(true));

}

function get_canvas_max_Width(){

	return $PAGE.width() - $('#sidebar').outerWidth(true)-($CANVAS.outerWidth(true)-$CANVAS.width());

}

function set_canvas_size(){

	var ratio_w	= CANVAS_RATIO[0];
	var ratio_h	= CANVAS_RATIO[1];
	var width = $CANVAS.width();
	var height = $CANVAS.height(); 
	var ratio = 0;  
	var padding_top = 0;

 	ratio 	= (ratio_w / ratio_h);
 	width 	= height * ratio;
 	height 	= height;

 	if(width > get_canvas_max_Width()){

 		ratio 	= (ratio_h / ratio_w);
		width 	= get_canvas_max_Width();
	 	height 	= width * ratio;

 	}

	$CANVAS.width(width).height(height);
 	
 	if($('#styleboard').height() > $CANVAS.outerHeight(true)){

 		padding_top = ($('#styleboard').height() - $CANVAS.outerHeight(true)) / 2; 
 	}
    
    $CANVAS.parent().css('padding-top',padding_top);
}

function truncateStr(str, len){

	return str.substr(0,len-1)+(str.length>len?'...':'');

}

function has_scroll(el, direction) {

    direction = (direction === 'vertical') ? 'scrollTop' : 'scrollLeft';

    var result = !! el[direction];

    if (!result) {

        el[direction] = 1;

        result = !!el[direction];

        el[direction] = 0;

    }
    
    return result;
}
