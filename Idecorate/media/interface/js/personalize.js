$(document).ready(function(){
	populate_save_styleboard();
});

function populate_save_styleboard(){
	if (PERSONALIZE_ITEM != ''){
		var raw_item = PERSONALIZE_ITEM.replace("\n", "\\n").replace("\r",'');
		var item = eval(raw_item);
		var canvas_height = $('#canvas').height();
		var canvas_width = $('#canvas').width();
		$.each(item, function(i,v){			
			var elm = $('<div />');
			elm.attr('_angle',v.angle);
			elm.addClass(v._type);
			if (v._type!='product')
				elm.addClass('embellishment');
			elm.addClass('unselected');
			elm.addClass('ui-draggable');
			if (v.uid)
				elm.attr('_uid',v.uid);
			elm.attr('style',v.style);
			var filter = {};
			if($.browser.msie && $.browser.version == 7.0){
	            filter = {'filter':'none'};
	        }else if($.browser.msie && $.browser.version == 8.0){
	            filter = {'msfilter':'none','-ms-filter':'none'};
	        }
	        elm.css(filter);

			elm.attr('_handle',v.handle);
			elm.attr('_opacity',v.opacity);
			elm.attr('def_qty',v.def_qty);
			elm.attr('gst_tb',v.gst_tb);

			elm.attr('_text',unescape(v.text));
			elm.attr('_rgb',v.rgb);

			elm.attr('_matrix','{"a":'+v.matrix[0].a+',"b":'+v.matrix[0].b+',"c":'+v.matrix[0].c+',"d":'+v.matrix[0].d+',"e":'+v.matrix[0].e+',"f":'+v.matrix[0].f+'}');

			var matrix = 'matrix('+ v.matrix[0].a +', '+ v.matrix[0].b +', '+ v.matrix[0].c +', '+ v.matrix[0].d +', 0, 0)',
        	    ie_matrix = "progid:DXImageTransform.Microsoft.Matrix(M11='"+v.matrix[0].a+"', M12='"+v.matrix[0].b+"', M21='"+v.matrix[0].c+"', M22='"+v.matrix[0].d+"', sizingMethod='auto expand')";        	
            if($.browser.msie && $.browser.version == 9.0) {
                elm.css({
                    '-ms-transform'    : matrix
                });
            }else if($.browser.msie && $.browser.version < 9.0){
                elm.css({
                    'filter'           : ie_matrix,
                    '-ms-filter'       : '"' + ie_matrix + '"'
                });
            }else{
                elm.css({
                    '-moz-transform'   : matrix,
                    '-o-transform'     : matrix,
                    '-webkit-transform': matrix,
                    'transform'        : matrix
                });
            }

			var img = $('<img />');
			var img_src = v.img[0].src.indexOf("?") != -1?v.img[0].src+'&random='+i:v.img[0].src+'?random='+i;
			img.attr('src',img_src);
			img.attr('style',v.img[0].style);
			img.attr('_nb',v.img[0].nb);
			img.attr('_wb',v.img[0].wb);
			if($.browser.msie && $.browser.version < 9.0){
				img.load(function(){
					// do nothing
				}).appendTo(elm);;
			} else 
				img.appendTo(elm);
			elm.appendTo('#canvas');			
			objCounter++;			
		});
		setTimeout(make_center,0);
		get_cart_items();
	}
}

function make_center(){
	var percent			= 100;
	var box 			= computeBboxDimension();
	var canvas_Width 	= $('#canvas').width();
	var canvas_Height 	= $('#canvas').height();
	var box_Height		= box.height;
	var box_Width		= box.width;
	var box_lowestLeft 	= box.lowestLeft;
	var box_lowestTop 	= box.lowestTop;
	var new_box_width 	= canvas_Width;
	var new_box_height 	= canvas_Height;
	var plus_top		= 0;
	var plus_left		= 0;

	if((canvas_Width < box_Width) || (canvas_Height < box_Height)){
		var width_diff 		= box_Width-canvas_Width;
		var height_diff 	= box_Height-canvas_Height;
		var ratio 			= box_Width/box_Height;//aspect ratio of bounding box
		
		if(width_diff >= height_diff){
			new_box_width 	= canvas_Width;
			new_box_height 	= new_box_width/ratio;
			percent 		= new_box_width/box_Width;
			plus_top		= (canvas_Height/2)-(new_box_height/2);
		}else{
			new_box_height 	= canvas_Height;
			new_box_width 	= new_box_height*ratio;
			percent 		= new_box_width/box_Width;
			plus_left		= (canvas_Width/2)-(new_box_width/2);
		}

		$('#canvas .unselected').each(function(){
			var each_aspect 		= do_aspectratio($(this).width(),$(this).height(),percent);
			var present_top 		= parseFloat($(this).css('top'));
			var present_left 		= parseFloat($(this).css('left'));

			var at_zeroX_axis 		= present_left-box_lowestLeft;
			var old_width			= box_Width;
			var new_width			= new_box_width;
			var each_percentX		= at_zeroX_axis/old_width;
			var at_zeroY_axis 		= present_top-box_lowestTop;
			var old_height			= box_Height;
			var new_height			= new_box_height;
			var each_percentY		= at_zeroY_axis/old_height;

			$(this).css({
				width:each_aspect.width,
				height:each_aspect.height,
				top: (new_height*each_percentY)+plus_top,
				left:(new_width*each_percentX)+plus_left
			});
		});

	}else{
		var ctr_diff = canvas_bb_ctr_diff(box.centerY,box.centerX);

	    $('#canvas .unselected').each(function(){
	        $(this).css({
	            top:parseFloat($(this).css('top'))+ctr_diff.y,
	            left:parseFloat($(this).css('left'))+ctr_diff.x
	        });
	    });
	}
}

function canvas_bb_ctr_diff(box_centerY, box_centerX){
    var ctr_diff 	= {};
    ctr_diff['x'] 	= $('#canvas').width()/2 - box_centerX;
    ctr_diff['y'] 	= $('#canvas').height()/2 - box_centerY;

    return ctr_diff;
}

function do_aspectratio(width, height, percent){
	
	var dimension = new Array();
    var aspectRatio = height/width;
    dimension['width'] = width*percent;
    dimension['height'] = aspectRatio*dimension['width'];

    return dimension;
}

function do_round(value){
	var val = 0;
	var rounded = 0;
	if(typeof value === 'number' && value % 1 == 0){
		rounded = value;
	}else{
		val = parseFloat(value);
		rounded = val.toFixed(2);
	}
	return rounded; 
}

function computeBboxDimension() {

    var lowestTop = 0;
    var highestTop = 0;
    var lowestLeft = 0;
    var highestLeft = 0;
	var finalWidth = 0;
    var finalHeight = 0;

    $('#canvas .unselected').each(function(e){
            
        if(lowestTop == 0) {
            lowestTop = parseFloat($(this).css('top').replace('px',''));
        } else {
            if(parseFloat($(this).css('top').replace('px','')) < lowestTop) {
                lowestTop = parseFloat($(this).css('top').replace('px',''));
            }
        }
        
        if(highestTop == 0) {
            highestTop = parseFloat($(this).css('top').replace('px','')) + parseFloat($(this).css('height').replace('px',''));
        } else {
            if((parseFloat($(this).css('top').replace('px','')) + parseFloat($(this).css('height').replace('px',''))) > highestTop) {
                highestTop = parseFloat($(this).css('top').replace('px','')) + parseFloat($(this).css('height').replace('px',''));
            }
        }

        if(lowestLeft == 0) {
            lowestLeft = parseFloat($(this).css('left').replace('px',''));
        } else {
            if(parseFloat($(this).css('left').replace('px','')) < lowestLeft) {
                lowestLeft = parseFloat($(this).css('left').replace('px',''));
            }
        }

        if(highestLeft == 0) {
            highestLeft = parseFloat($(this).css('left').replace('px','')) + parseFloat($(this).css('width').replace('px',''));
        } else {
            if((parseFloat($(this).css('left').replace('px','')) + parseFloat($(this).css('width').replace('px',''))) > highestLeft) {
                highestLeft = parseFloat($(this).css('left').replace('px','')) + parseFloat($(this).css('width').replace('px',''));
            }
        }
            
            
    });
    
    finalWidth = highestLeft - lowestLeft;
    finalHeight = highestTop - lowestTop;
    
    return {
        'width':finalWidth,
        'height':finalHeight,
        'centerX':finalWidth / 2 + lowestLeft,
        'centerY':finalHeight / 2 + lowestTop,
        'lowestLeft':lowestLeft,
        'lowestTop':lowestTop
    };

}

function get_cart_items(){
	$.get(GET_PERSONALIZE_CART_URL+'?id='+PERSONALIZE_ID,function(data){
		var img_src = media_url+'products/';
		$.each(data,function(i,v){
			var price = v.price.toFixed(2);
	        price = addCommas(price);
	        var subtotal = v.sub_total.toFixed(2);
	        subtotal = addCommas(subtotal);

	        var item = '<tr id="prod_cart_' + v.id + '">' +
	            '<td class="span4">' +
	                '<div class="buyItemImg">' +
	                    '<div><img width="70" src="/' + img_src + v.original_image_thumbnail + '"></div>' +
	                    '<div class="buyItemMeta">' +
	                        '<p>' + v.name + '</p>' +
	                        '<p>$' + price + '</p>'+
	                    '</div>' +
	                '</div>' +
	            '</td>' +
	            '<td class="span1"><input class="dynamic_qty" type="text" _pid="' + v.id + '" _pr="' + price + '" _cur="' + v.currency + '" _gs="' + v.guest_table + '" _dq="' + v.default_quantity + '" max-length="11" name="qty" value="' + v.quatity + '" placeholder="qty"/></td>' +
	            '<td class="amount" id="subtotal_' + v.id + '">$' + subtotal + '</td>'+
	            '</tr>';
	        $('#buy-table tbody').append(item);
		});
		manage_total();			
	},'json');
}