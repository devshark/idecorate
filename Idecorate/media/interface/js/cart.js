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
        return false;
    });
    buy_tab_resize();
    $(window).resize(buy_tab_resize);
    $('#buyTab').click(function(){
        buy_tab_resize();
    });
});

function buy_tab_resize(){
    var ph = $('#sidebar').height()-$('#sidebar-nav').outerHeight(true)-$('#sidebar-form-wrap').height()-$('#buy-tab .buyTableWrap .table .thead').outerHeight(true)-$('#buy-tab .buyTableWrap .table .tfoot').height()-$('#buy-tab .checkOutWrap').outerHeight(true)-20;
    $('#buy-tab .buyTableWrap .table .tbody').css('height',ph+'px')
}

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

        var item = '<tr id="prod_cart_' + data.id + '">' +
            '<td class="span3">' +
                '<div class="buyItemImg">' +
                    '<div><img width="70" src="/' + img_src + data.original_image_thumbnail + '"></div>' +
                    '<div class="buyItemMeta">' +
                        '<p>' + data.name + '</p>' +
                        '<p>$' + price + '</p>'+
                    '</div>' +
                '</div>' +
            '</td>' +
            '<td class="span3"><input type="text" _pid="' + data.id + '" _pr="' + price + '" _cur="' + data.currency + '" max-length="11" name="qty" value="1" placeholder="qty"/></td>' +
            '<td class="amount" id="subtotal_' + data.id + '">$' + price + '</td>'+
            '</tr>';
        $('#buy-table tbody').append(item);
        var cart_total = total.toFixed(2);
        cart_total = addCommas(cart_total);
        $('#cart-total-amount').text(cart_total);
        $('#cart-total-cur').text('$');
        attachEventToQty();
    }
}

function attachEventToQty() {
        $('input[name="qty"]').focus(function(){
            selected_prev_prod_qty = $(this).val()<=0 ?1:$(this).val();
        });

        $('input[name="qty"]').keydown(function(e){
            if (e.shiftKey){
                return false;
            }

            var action = '';
            if ( e.keyCode==116 || e.keyCode==37 || e.keyCode==39 || e.keyCode==9)
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

        $('input[name="qty"]').keyup(function(){
            var pid = $(this).attr('_pid');
            var qty = $(this).val();

            if ( qty<=0 ){
                if (!$(this).hasClass('input-error'))
                    $(this).addClass('input-error');
                qty = 0;
            } else {
                if ($(this).hasClass('input-error'))
                    $(this).removeClass('input-error');                
            }

            var mod = 'i';
            var dif = 0;
            if ( qty < selected_prev_prod_qty ){
                mod = 'd';
                dif = (selected_prev_prod_qty-qty);
            } else if ( qty > selected_prev_prod_qty ){
                dif = (qty-selected_prev_prod_qty);
            }

            var pr = $(this).attr('_pr').replace(',','');
            var cur = $(this).attr('_cur');
            pr = parseInt(pr);
            var price = pr*qty;
            var sub_total = '$' + (addCommas(price.toFixed(2)));
            $('#subtotal_'+pid).text(sub_total);
            if ( mod == 'd' )
                total = total - (pr*dif);
            else
                total = total + (pr*dif);
            var cart_total = total.toFixed(2);
            cart_total = addCommas(cart_total);
            $('#cart-total-amount').text(cart_total);
            selected_prev_prod_qty = qty;
        });    
}

function isNumeric(fData)
{
    var reg = new RegExp("^[0-9]$");
    return (reg.test(fData));
}

function remove_from_cart(prod_id){
    //console.log(prod_id)

    var diffTotal = (parseFloat($('[_pid="' + prod_id + '"]').attr('_pr')) * parseFloat($('[_pid="' + prod_id + '"]').val())).toFixed(2)
    total -= diffTotal;
    $('#cart-total-amount').text(addCommas(total.toFixed(2)));

    //console.log(diffTotal);
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