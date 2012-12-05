$(document).ready(function(){
	populate_save_styleboard();
});

function populate_save_styleboard(){
	if (PERSONALIZE_ITEM != ''){
		var raw_item = PERSONALIZE_ITEM; //.replace('filter: progid:dximagetransform.microsoft.','').replace('filter:progid:dximagetransform.microsoft.','');		
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
			elm.attr('_handle',v.handle);
			elm.attr('_opacity',v.opacity);
			elm.attr('def_qty',v.def_qty);
			elm.attr('gst_tb',v.gst_tb);
			elm.attr('_text',v.text);
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
			img.attr('src',v.img[0].src);
			img.attr('style',v.img[0].style);
			img.attr('_nb',v.img[0].nb);
			img.attr('_wb',v.img[0].wb);
			img.appendTo(elm);
			elm.appendTo('#canvas');
			objCounter++;			
		});
		setTimeout(make_center,0);
		get_cart_items();
	}
}

function make_center(){
	var array_x = [];
	var array_y = [];
	var canvas_height = $('#canvas').height();
	var canvas_width = $('#canvas').width();

	var canvas_y = canvas_height/2;
	var canvas_x = canvas_width/2;

	$('#canvas .unselected').each(function(){
		var h = $(this).height();
		var w = $(this).width();


		var hy = h/2;
		var hx = w/2;

		array_y.push($(this).css('top'));
		array_x.push($(this).css('left'));
	});

	getCenter(array_x);
	getCenter(array_y);
}

function getCenter(array) {

	//sort the array first
	array = array.sort();
	//get the index
	var ind = array.length / 2;
	ind = parseInt(Math.round(ind));
	
	return array[ind - 1];
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
		attachEventToQty();
		manage_total();			
	},'json');
}