var action_url = '';
var total = 0;
var quantity = 1;
var selected_prev_prod_qty = 0;
$(document).ready(function(){
    var cart_triggered = false;
    $('.checkoutButton').click(function(){
        var url = $(this).parent().attr('href');

        var error = hasError();

        if ( !error ){
            window.location.href = CHECKOUT_URL;
        } else {
            if ( error == 2 )
                alert('Quantity must not be less than 1.');
            else {
                alert('No item to checkout.');
            }
        }
        //return false;
    });
});

function hasError(){
    var c = false;
    if ( $('input[name="qty"]').length > 0 ){
        $('input[name="qty"]').each(function(){
            if ($(this).hasClass('input-error')){                
                c = 2;
            }
        });
    } else {
        c = 1;
    }
    return c;
}

function add_to_cart(prod_id){
    if ($('#prod_cart_' + prod_id).length == 0){
        action_url = ADD_TO_CART_URL;
        var data = submit_action(prod_id);    
        var img_src = media_url+'products/';
        var price = data.price;
        total = (price+total);
        price = price.toFixed(2);
        price = addCommas(price);

        var item = '<tr class="odd" id="prod_cart_' + data.id + '">' +
            '<td>' +
                '<div class="buyItemImg">' +
                    '<img width="70" src="/' + img_src + data.original_image_thumbnail + '">' +
                    '<div class="buyItemMeta">' +
                        '<h5>' + data.name + '</h5>' +
                        '<p>' + data.currency + ' ' + price + '</p>'+
                    '</div>' +
                '</div>' +
            '</td>' +
            '<td><input type="text" _pid="' + data.id + '" max-length="11" name="qty" value="1" placeholder="qty"/></td>' +
            '<td class="amount" id="subtotal_' + data.id + '">' + data.currency + ' ' + price + '</td>'+
            '</tr>';
        $('#buy-table tbody').append(item);
        var cart_total = total.toFixed(2);
        cart_total = addCommas(cart_total);
        $('#cart-total-amount').text(cart_total);
        $('#cart-total-cur').text(data.currency);        
        $('input[name="qty"]').focus(function(){
            selected_prev_prod_qty = $(this).val()<=0 ?1:$(this).val();
        });

        $('input[name="qty"]').keydown(function(e){            
            var action = '';
            if ( e.keyCode==116 || e.keyCode==37 || e.keyCode==39)
                return true;
            if ( e.keyCode == 8 || e.keyCode == 46){
                action = 'del';
            } else if ( (e.keyCode  < 48 || e.keyCode > 57) && (e.keyCode  < 96 || e.keyCode > 105) ){
                return false;
            }            
            var l = $(this).val().length;            
            if ( l >= 10 && action != 'del')
                return false;
            return true;
        });

        $('input[name="qty"]').blur(function(){                    
            var pid = $(this).attr('_pid');
            var qty = $(this).val();

            if ( qty<=0 ){
                if (!$(this).hasClass('input-error'))
                    $(this).addClass('input-error');
            } else {
                if ($(this).hasClass('input-error'))
                    $(this).removeClass('input-error');
                var mod = 'i';
                var dif = 0;
                if ( qty < selected_prev_prod_qty ){
                    mod = 'd';
                    dif = (selected_prev_prod_qty-qty);
                } else if ( qty > selected_prev_prod_qty ){
                    dif = (qty-selected_prev_prod_qty);
                }

                if ( dif > 0 ){
                    $.ajax({
                        url: UPDATE_CART,
                        type: "POST",
                        dataType: 'json',
                        data: { prod_id: pid, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(), quantity: qty },
                        async:   false,
                        beforeSend : function(){
                            
                        },
                        success: function(response_data){
                            var price = response_data.price*qty;
                            var sub_total = response_data.currency + ' ' + (addCommas(price.toFixed(2)));
                            $('#subtotal_'+pid).text(sub_total);
                            if ( mod == 'd' )
                                total = total - (response_data.price*dif);
                            else
                                total = total + (response_data.price*dif);
                            var cart_total = total.toFixed(2);
                            cart_total = addCommas(cart_total);
                            $('#cart-total-amount').text(cart_total);

                        },
                        error: function(msg) {
                        }
                    });
                }
            }
        });
    }
}

function remove_from_cart(prod_id){
    //console.log(prod_id)
	action_url = REMOVE_TO_CART_URL;
	arrange_tr_class();
    $('#prod_cart_'+prod_id).remove();
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