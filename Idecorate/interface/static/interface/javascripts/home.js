$(function() {

    FB.init({appId: FACEBOOK_APP_ID, status: true, cookie: true});

    $('.popupWindow').live('click',function(e){

        window.open($(this).attr('href'),'',
            'menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=600,width=600');
        e.preventDefault();

    });

    $('#banner_img').one('load', function() {

      bannerCentering();
      $(this).show();

    }).each(function() {

      if(this.complete) $(this).load();

    });
    $(window).resize(bannerCentering);
    
    
    searchBoxTransform();
    $(window).resize(searchBoxTransform);


    $container.isotope({
        filter: '*',    
        layoutMode : 'masonry',
        masonry: {
            columnWidth: 250
        },
        animationOptions: {
            duration: 750,
            easing: 'linear',
            queue: false
        }
    });
 
    $('.filter li a').click(function(e){

        if($(this).attr('id') != 'search_result'){

            var selector = $(this).attr('data-filter');
            $(this).parent().siblings().children('a').removeClass('active');
            $(this).addClass('active');
            // $container.isotope('remove',$('.noMoreResults'));

            if($(this).attr('id') == 'wish_list'){
                
                $container.isotope('remove', $container.children());
                resetVars();
                wishlist = true;                
                loadMoreResults();
                $container.isotope('reloadItems');

            }else if($(this).attr('id') == 'celebrity_styleboards'){

                $container.isotope('remove', $container.children());
                resetVars();
                celebrity_styleboards = true;
                loadMoreResults();
                $container.isotope('reloadItems');

            } else {

                if(wishlist || celebrity_styleboards) {
                    resetVars();
                    loadMoreResults();
                    $container.isotope('reloadItems');                   
                }

                if(keywords != null) {
                    resetVars();
                    loadMoreResults();  
                    $container.isotope('reloadItems');              
                }
                
                $container.isotope('reloadItems');
                $container.isotope({ filter: selector });

            }

        }

        e.preventDefault();

    });

    $(window).scroll(function() {

        if($(window).scrollTop() == $(document).height() - $(window).height()) {

            loadMoreResults();

        }
    });

    $('#load_more').click(function(e){
        e.preventDefault();
        loadMoreResults();
    });

    
    $('#search_input').keypress(function(e){ searchItems(e); })
    $('.searchBtn').click(function(e){  searchItems(e); });

    $('.itemWrap:not(.wishlist)').live('mouseenter', function(e){

        $('.operationWrap', this).stop(true, true).show(100);

    }).live('mouseleave', function(e){

        $('.operationWrap',this).stop(true, true).hide();
        $('.socialMediaShare').hide();
    });

    $('.operationWrap .shareProduct').live('click', function(e){

        e.preventDefault();
        $(this).siblings('.socialMediaShare').toggle();
    });

});

$('#items_wrapper').children().hide();
$(window).load(function(){ $('#items_wrapper').children().show(100); });


var searchBoxTransform = function(){

    var filterBar = $('.filterBar');
    var searchBox = $('.searchBoxWrap');
    var searchIcon = $('a.searchIcon');

    if(filterBar.width() < 1220){
        searchIcon.show();
        searchBox.find('.searchBox').hide().addClass('transform');

    }else{
        searchIcon.hide();
        searchBox.find('.searchBox').show().removeClass('transform');
    }

    searchIcon.click(function(e){
        e.preventDefault();
        searchBox.find('.searchBox').toggle();
    });
};


var searchItems = function(e){

    if(e.which == 13 || e.type == 'click'){

        $('#search_result').addClass('active').parent().siblings().children('a').removeClass('active');
        $container.isotope('remove', $container.children());
        resetVars();
        keywords = $('#search_input').val();
        var is_empty = loadMoreResults();

        // if(is_empty){

        //     $container.isotope('remove',$('.noMoreResults'));
        //     $container.isotope('insert',$('<h2 class="noMoreResults">Your search yielded no results.</h2>')); 
        //     $container.isotope('reLayout');
        // }
        //$container.isotope({filter: '*'});
        $container.isotope('reloadItems');

    }

};

var home_items_request;
var loadMoreResults = function() {

    var is_empty_result = false;
    $('#load_more_wrap').hide();
    orig_page = page;
    page++;

    options = {
        'page' : page,
        'keywords' :keywords
    }

    if(wishlist) {
        options['wishlist'] = true;
    }

    if(celebrity_styleboards) {
        options['celebrity_styleboards'] = true;
    }

    home_items_request = $.ajax({
        url: LOADMOREURL,
        type: "POST",
        data: options,
        async: false
    });

    home_items_request.done(function (response, textStatus, jqXHR){

        $container.isotope('insert',$(response));

        if(keywords!=null) {

            $container.isotope('reLayout');
        }
        
        is_empty_result = (response.trim() == "")
    });

    home_items_request.fail(function (jqXHR, textStatus, errorThrown){
        
        page = orig_page;
        $('#load_more_wrap').show();

    });

    home_items_request.always(function(){

        $container.isotope('reLayout');

    });

    return is_empty_result;

};


var resetVars = function() {
    page = 0;
    keywords = null;
    wishlist = false;
    celebrity_styleboards = false;
}


var addToWishList = function(object_type, object_id) {

    $.ajax({
        url: ADD_WISHLIST_URL_AJAX,
        type: 'POST',
        data: {'object_type':object_type, 'object_id':object_id},
        success: function(data) {
            
        },
        error: function() {

        }
    });
    
}


var bannerCentering = function(){

    $('#banner_img').css({marginLeft:(($('#banner_img').width()-$('#banner').width())/2)*-1});

};


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

