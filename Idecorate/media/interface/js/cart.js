var action_url = '';
function add_to_cart(prod_id){
    if ($('#prod_cart_' + prod_id).length == 0){
        action_url = ADD_TO_CART_URL;
        var data = submit_action(prod_id);    
        var img_src = media_url+'products/';
        var price = data.price.toFixed(2);
        price = addCommas(price);
        var item = '<tr class="odd" id="prod_cart_' + data.id + '">' +
            '<td>' +
                '<div class="buyItemImg">' +
                    '<img src="/' + img_src + data.original_image_thumbnail + '">' +
                    '<div class="buyItemMeta">' +
                        '<h5>' + data.name + '</h5>' +
                        '<p>' + data.currency + ' ' + price + '</p>'+
                    '</div>' +
                '</div>' +
            '</td>' +
            '<td><input type="text" value="1" placeholder="qty"/></td>' +
            '<td id="subtotal_' + data.id + '">' + data.currency + ' ' + price + '</td>'+
            '</tr>';
        $('#buy-table tbody').append(item);
    }
}

function remove_from_cart(prod_id){
	action_url = REMOVE_TO_CART_URL;
	arrange_tr_class();
}

function submit_action(id){
    var data;
	$.ajax({
        url: action_url,
        type: "POST",
        dataType: 'json',
        data: { prod_id: id, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() },
        async:   false,
        beforeSend : function(){
            
        },
        success: function(response_data){
            data = response_data
        },
        error: function(msg) {
        }
    });

    return data;
}

function arrange_tr_class(){
	$('#buy-table tbody tr').each(function(i,e){
		var c = i+1;
		if (c%2){
			if($(this).hasClass('odd'))
				$(this).removeClass('odd');
			if (!$(this).hasClass('even'))
				$(this).addClass('even');
		} else {
			if($(this).hasClass('even'))
				$(this).removeClass('even');
			if (!$(this).hasClass('odd'))
				$(this).addClass('odd');
		}
	});
}

function addCommas(nStr){
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}