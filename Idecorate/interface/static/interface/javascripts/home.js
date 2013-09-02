$(function() {

    $(window).resize(bannerCentering);

    var bannerCentering = function(){

        $('#banner_img').css({marginLeft:(($('#banner_img').width()-$('#banner').width())/2)*-1});

    };

    $('#banner_img').one('load', function() {

      bannerCentering();
      $(this).show();

    }).each(function() {

      if(this.complete) $(this).load();

    });
    

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

    searchBoxTransform();
    $(window).resize(searchBoxTransform);

    var $container = $('#items_wrapper');
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
 
    $('.filter li a').click(function(){
        $(this).addClass('active');
        $(this).parent().siblings().children('a').removeClass('active')
 
        var selector = $(this).attr('data-filter');
        $container.isotope({
            filter: selector,  
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
         return false;
    }); 

});