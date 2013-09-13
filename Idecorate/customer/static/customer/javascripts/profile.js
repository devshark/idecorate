$(function(){

	$('.popupWindow').live('click',function(e){

		window.open($(this).attr('href'),'',
			'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
		e.preventDefault();

	});

	FB.init({appId: "{{ FACEBOOK_APP_ID }}", status: true, cookie: true});

	$('.delStyleboard').click(function(e){

		e.preventDefault();

		var message = 'Are you sure you want to delete this styleboard?<br/>It will be removed from your saved styleboards and will no longer be viewable online.';
        var header = 'Confirm delete styleboard';
        
        confirm(header,message, function () {
			window.location.href = $(this).attr('href');
		});
	});

	$('.styleboardWrap').live('mouseenter', function(e){

		$('.btn',this).stop(true, true).show(100).css('display','inline-block');
		

	}).live('mouseleave', function(e){

		$('.btn',this).stop(true, true).hide();
		$('.socialMediaShare').hide();
	});

	$('.operation .share').live('click', function(e){

		e.preventDefault();
		$(this).siblings('.socialMediaShare').toggle();
	});

});
function postToFeed(url,image,name,description) {

	// calling the API ...
	var obj = {
		method: 'feed',
		redirect_uri: 'http://www.facebook.com',
		link:url,//page link here
		picture: image, //add image link of product here 
		name: name, //styleboard title
		caption: 'iDecorate Weddings',
		description: description //description
	};

	function callback(response) {
		document.getElementById('msg').innerHTML = "Post ID: " + response['post_id'];
	}

	FB.ui(obj, callback);

	return false;
}