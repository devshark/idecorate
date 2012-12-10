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
			var img_src = v.img[0].src.indexOf("?") != -1?v.img[0].src+i:v.img[0].src+'?'+i;
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
	var bb = computeBboxDimension();
	var canvasW = $('#canvas').width();
	var canvasH = $('#canvas').height();
	var bbH		= bb.height;
	var bbW		= bb.width;

	var ctr_diff = canvas_bb_ctr_diff(bb.centerY,bb.centerX);

	$('#canvas .unselected').each(function(){
		$(this).css({
			top:parseFloat($(this).css('top'))+ctr_diff.y,
			left:parseFloat($(this).css('left'))+ctr_diff.x
		});
	});

}

function canvas_bb_ctr_diff(bbH, bbW){
	var ctr_diff 	= {}
	var canvas_ctr 	= {};
	var bb_ctr 		= {'x':bbW, 'y':bbH};
	canvas_ctr['x'] = $('#canvas').width()/2;
	canvas_ctr['y'] = $('#canvas').height()/2;
	ctr_diff['x'] = canvas_ctr.x - bb_ctr.x;
	ctr_diff['y'] = canvas_ctr.y - bb_ctr.y;

	return ctr_diff;
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
            'width': finalWidth,
            'height': finalHeight,
            'centerX': finalWidth / 2 + lowestLeft,
            'centerY': finalHeight / 2 + lowestTop
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