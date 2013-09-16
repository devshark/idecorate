$(function(){

	FB.init({appId: FACEBOOK_APP_ID, status: true, cookie: true});

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
function postToFeed() {

	// calling the API ...
	var obj = {
		method: 'feed',
		redirect_uri: 'http://www.facebook.com',
		link: 'http://{{ request|get_host }}/styleboard/view/{{ styleboard.styleboard_item.id }}/', //page link here
		picture: 'http://{{ request|get_host }}/styleboard/generate_styleboard_view/{{ styleboard.styleboard_item.id }}/450/285/', //add image link of product here 
		name: '{{ styleboard.styleboard_item.name }}', //styleboard title
		caption: 'iDecorate Weddings',
		description: "{{ styleboard.styleboard_item.description|truncateDescription }}" //description
	};

	function callback(response) {
		document.getElementById('msg').innerHTML = "Post ID: " + response['post_id'];
	}

	FB.ui(obj, callback);

	return false;
}