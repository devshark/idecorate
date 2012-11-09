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
            setProductPositions(function(){
                window.location.href = CHECKOUT_URL;    
            });
            
        } else {
            setProductPositions();
            if ( error == 2 )
                alert('Quantity must not be less than 1.');
            else {
                alert('No item to checkout.');
            }
        }
        return false;
    });
    $('#guests').keyup(function(){
        var val = $(this).val();
        val = val.replace(/[^0-9]/g,'');
        val = val.replace(/\./g, '');
        $(this).val(val);
        var l = $(this).val().length;
        if (l<=5){
            if (!isNaN($(this).val()))
                manage_my_order();
        } else {
            $(this).val($(this).val().substring(0,5));
        }        
    });
    $('#tables').keyup(function(){
        var val = $(this).val();
        val = val.replace(/[^0-9]/g,'');
        val = val.replace(/\./g, '');
        $(this).val(val);
        var l = $(this).val().length;
        if (l<=5){
            if (!isNaN($(this).val()))
                manage_my_order();
        } else {
            $(this).val($(this).val().substring(0,5));
        }
    });

    $('#createTab').click(function(){
        if($('input[name="qty"]').length>0){
            if($('.myorder-edit a').hasClass('hidden'))
                $('.myorder-edit a').removeClass('hidden');
        }
    });
    $('#buyTab').click(function(){
        if(!$('.myorder-edit a').hasClass('hidden'))
            $('.myorder-edit a').addClass('hidden');
    });

    $('.myorder-edit a').click(function(){
        if(!$('.myorder-edit a').hasClass('hidden'))
            $('.myorder-edit a').addClass('hidden');
    });
});

function hasError(){
    var c = false;
    if ( $('input[name="qty"]').length > 0 ){
        $('input[name="qty"]').each(function(){
            if ($(this).val()<=0 ){                
                c = 2;
            }
        });
    } else {
        c = 1;
    }
    return c;
}

function add_to_cart(prod_id,default_quantity,guest_table){
    
    if ($('#prod_cart_' + prod_id).length == 0){
        action_url = ADD_TO_CART_URL;
        var qty = 1;
        var tables = parseInt($('#tables').val());
        var guests = parseInt($('#guests').val());
        if(tables>0 || guests>0){
            if ((guest_table=='Table' || guest_table=='table' || guest_table=='Tables' || guest_table=='tables') && tables>0){
                qty = tables*default_quantity;
            } 

            if ((guest_table=='Guest' || guest_table=='guest' || guest_table=='Guests' || guest_table=='guests') && tables>0) {
                qty = guests*default_quantity;
            }            
        }   

        var data = addToCart_submit_action(prod_id,qty);    
        var img_src = media_url+'products/';
        var price = data.price;
        var subtotal = price*qty;
        total = (price+total);
        price = price.toFixed(2);
        price = addCommas(price);
        subtotal = subtotal.toFixed(2);
        subtotal = addCommas(subtotal);

        var item = '<tr id="prod_cart_' + data.id + '">' +
            '<td class="span4">' +
                '<div class="buyItemImg">' +
                    '<div><img width="70" src="/' + img_src + data.original_image_thumbnail + '"></div>' +
                    '<div class="buyItemMeta">' +
                        '<p>' + data.name + '</p>' +
                        '<p>$' + price + '</p>'+
                    '</div>' +
                '</div>' +
            '</td>' +
            '<td class="span1"><input class="dynamic_qty" type="text" _pid="' + data.id + '" _pr="' + price + '" _cur="' + data.currency + '" _gs="' + data.guest_table + '" _dq="' + data.default_quantity + '" max-length="11" name="qty" value="' + qty + '" placeholder="qty"/></td>' +
            '<td class="amount" id="subtotal_' + data.id + '">$' + subtotal + '</td>'+
            '</tr>';
        $('#buy-table tbody').append(item);
        attachEventToQty();
        manage_total();
    }
}

function attachEventToQty() {
    $('input[name="qty"]').focus(function(){
        selected_prev_prod_qty = $(this).val()<=0 ?0:$(this).val();
    });

    $('input[name="qty"]').keyup(function(e){
        var val = $(this).val();
        val = val.replace(/[^0-9]/g,'');
        val = val.replace(/\./g, '');
        $(this).val(val);
        var l = $(this).val().length;
        if (l<10){
            if (!isNaN($(this).val()))
                cal(this);   
        } else {
            $(this).val($(this).val().substring(0,10));
        }
    });
    $('input[name="qty"]').blur(function(){
        manage_computation(this);
    });
}

function manage_my_order(){
    var tables = $('#tables').val()>0?$('#tables').val():1;
    var guests = $('#guests').val()>0?$('#guests').val():1;

    $('input[name="qty"]').each(function(){
        var gs = $(this).attr('_gs');
        var dq = $(this).attr('_dq');
        dq = parseInt(dq);
        if ((gs=='Table' || gs=='table' || gs=='Tables' || gs=='tables') && tables>0){
            $(this).val(tables*dq);
            update_cart(this);
        } 
        if ((gs=='Guest' || gs=='guest' || gs=='Guests' || gs=='guests') && tables>0) {
            $(this).val(guests*dq);
            update_cart(this);
        }
    });
    manage_subtotal();
    manage_total();
}

function cal(elm){
    if($(elm).val()>0)
        update_cart(elm);
    manage_computation(elm);
}

function manage_computation(elm){
    var pid = $(elm).attr('_pid');
    var qty = $(elm).val();

    if ( qty<=0 ){
        if (!$(elm).hasClass('input-error'))
            $(elm).addClass('input-error');
        qty = 0;
    } else {
        if ($(elm).hasClass('input-error'))
            $(elm).removeClass('input-error');                
    }

    var pr = $(elm).attr('_pr').replace(',','');
    var cur = $(elm).attr('_cur');
    pr = parseFloat(pr);
    var price = pr*qty;
    
    var sub_total = '$' + (addCommas(price.toFixed(2)));
    $('#subtotal_'+pid).text(sub_total);
    selected_prev_prod_qty = qty;
    manage_total();
}

function manage_subtotal(){
    $('input[name="qty"]').each(function(){
        var pid = $(this).attr('_pid');
        var pr = $(this).attr('_pr').replace(',','');
        pr = parseFloat(pr);
        var qty = $(this).val()<=0?0:$(this).val();
        qty = parseInt(qty);
        var subtotal = pr*qty;
        var sub_total = '$' + (addCommas(subtotal.toFixed(2)));
        $('#subtotal_'+pid).text(sub_total);
    });
}

function manage_total(){
    var cart_total = 0;
    $('input[name="qty"]').each(function(){
        var pr = $(this).attr('_pr').replace(',','');
        pr = parseFloat(pr);
        var qty = $(this).val()<=0?0:$(this).val();
        qty = parseInt(qty);
        var subtotal = pr*qty;
        cart_total = cart_total + subtotal;
    });
    total = cart_total;

    if (cart_total > 0){
        if($('.myorder-edit a').hasClass('hidden') && !$('#buyTab').hasClass('active'))
            $('.myorder-edit a').removeClass('hidden');
    } else {
        if(!$('.myorder-edit a').hasClass('hidden'))
            $('.myorder-edit a').addClass('hidden');
    }

    cart_total = cart_total.toFixed(2);
    $('#cart-total-cur').text('$');
    cart_total = addCommas(cart_total);
    $('#cart-total-cur').text('$');
    $('#cart-total-amount').text(cart_total);
    $('#my-order-total').text('$'+cart_total);
}

function isNumeric(fData)
{
    var reg = new RegExp("^[0-9]$");
    return (reg.test(fData));
}

function remove_from_cart(prod_id){


	action_url = REMOVE_TO_CART_URL;
    //alert(prod_id);
    $.ajax({
        url: action_url,
        type: "POST",
        data: { prod_id: prod_id, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() },
        async:   false,
        success: function(response_data){
            data = response_data;
            var diffTotal = (parseFloat($('[_pid="' + prod_id + '"]').attr('_pr')) * parseFloat($('[_pid="' + prod_id + '"]').val())).toFixed(2)
            total -= diffTotal;
            $('#cart-total-amount').text(addCommas(total.toFixed(2)));
            arrange_tr_class();
            $('#prod_cart_'+prod_id).remove();
            manage_total();
        },
        error: function(msg) {
        }
    });

}

function update_cart(elm){
    var pid = $(elm).attr('_pid');
    var qty = $(elm).val();
    $.ajax({
        url: UPDATE_CART,
        type: "POST",
        dataType: 'json',
        data: { prod_id: pid, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(), quantity:qty, guests: $('#guests').val(), tables: $('#tables').val() }
    });
}

function addToCart_submit_action(id,qty){
    var data;
	$.ajax({
        url: action_url,
        type: "POST",
        dataType: 'json',
        data: { prod_id: id, quantity: qty, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(), guests: $('#guests').val(), tables: $('#tables').val() },
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