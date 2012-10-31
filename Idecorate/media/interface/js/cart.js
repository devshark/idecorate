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
            '<td class="span4">' +
                '<div class="buyItemImg">' +
                    '<div><img width="70" src="/' + img_src + data.original_image_thumbnail + '"></div>' +
                    '<div class="buyItemMeta">' +
                        '<p>' + data.name + '</p>' +
                        '<p>$' + price + '</p>'+
                    '</div>' +
                '</div>' +
            '</td>' +
            '<td class="span1"><input type="text" _pid="' + data.id + '" _pr="' + price + '" _cur="' + data.currency + '" max-length="11" name="qty" value="1" placeholder="qty"/></td>' +
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
        selected_prev_prod_qty = $(this).val()<=0 ?0:$(this).val();
    });

    $('input[name="qty"]').keyup(function(e){

        var val = $(this).val();
        val = val.replace(/[^0-9]/g,'');
        val = val.replace(/\./g, '');
        $(this).val(val);

        //this.value = this.value.replace('[^0-9\.]/g','');

        // if (!$.browser.opera){
        //     if (e.shiftKey){
        //         return false;
        //     }

        //     var action = '';
        //     if ( e.keyCode==116 || e.keyCode==37 || e.keyCode==39 || e.keyCode==9)
        //         return true;
        //     if ( e.keyCode == 8 || e.keyCode == 46){
        //         action = 'del';
        //     } else if ( (e.keyCode  < 48 || e.keyCode > 57) && (e.keyCode  < 96 || e.keyCode > 105) ){
        //         return false;
        //     }            
        //     var l = $(this).val().length;            
        //     if ( l >= 10 && action != 'del')
        //         return false;
        //     return true;
        // } else {
        //     if(!isNumeric($(this).val())){
        //         isNumeric
        //     }
        // }
        var l = $(this).val().length;
        if (l<10){
            if (!isNaN($(this).val()))
                cal(this);   
        } else {
            $(this).val($(this).val().substring(0,10));
        }
    });

    // $('input[name="qty"]').keyup(function(){
    //     if($(this).val()>0)
    //         update_cart(this);
    //     manage_computation(this);
    // });
    $('input[name="qty"]').blur(function(){
        manage_computation(this);
    });
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
        var pid = $(elm).attr('_pid');
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
    cart_total = cart_total.toFixed(2);
    $('#cart-total-cur').text('$');
    $('#cart-total-amount').text(addCommas(cart_total));
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

function update_cart(elm){
    var pid = $(elm).attr('_pid');
    var qty = $(elm).val();
    $.ajax({
        url: UPDATE_CART,
        type: "POST",
        dataType: 'json',
        data: { prod_id: pid, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(), quantity:qty }
    });
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