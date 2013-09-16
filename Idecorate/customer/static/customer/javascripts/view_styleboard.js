$(function(){

	$('#btnSubmitBuy').click(function(e){

		e.preventDefault();
		var clear_session_sbid = $.post( '{% url clear_session_sbid %}', { clear: 'clear' } );
		clear_session_sbid.done(function( data ) {
			
			$('#formCheckout').submit();

		});

	});

	$('.popupWindow').live('click',function(e){

		window.open($(this).attr('href'),'',
			'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
		e.preventDefault();

	});

});