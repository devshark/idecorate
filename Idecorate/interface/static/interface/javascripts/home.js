$(function() {


    var bannerCentering = function(){

        $('#banner_img').css({marginLeft:(($('#banner_img').width()-$('#banner').width())/2)*-1});

    };

    $('#banner_img').one('load', function() {

      bannerCentering();
      $(this).show();

    }).each(function() {

      if(this.complete) $(this).load();

    });
    $(window).resize(bannerCentering);
    

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


    var loadMoreResults = function() {

        orig_page = page;
        page++;
        $.ajax({
            url: LOADMOREURL,
            data:{'page':page, 'keywords':keywords},
            type:'POST',
            success:function(data) {

                $container.isotope('insert',$(data));

                if(keywords!=null) {

                    $container.isotope('reLayout');

                }
            },
            error:function() {

                page = orig_page;

            }
        });

    };

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
 
    $('.filter li a').click(function(e){

        if($(this).attr('id') != 'search_result'){

            var selector = $(this).attr('data-filter');
            $(this).addClass('active').parent().siblings().children('a').removeClass('active');

            if(keywords != null) {
                keywords = null;
                page = 0;
                loadMoreResults();                
            }

            $container.isotope('reloadItems');
            $container.isotope({ filter: selector });

        }

        e.preventDefault();

    });

    $(window).scroll(function() {

        if($(window).scrollTop() == $(document).height() - $(window).height()) {

            loadMoreResults();

        }
    });

    searchItems = function(e){

        if(e.which == 13 || e.type == 'click'){

            $('#search_result').addClass('active').parent().siblings().children('a').removeClass('active');
            $container.isotope('remove', $container.children());
            keywords = $('#search_input').val();
            page = 0;
            loadMoreResults();
            $container.isotope({filter: '*'});
            $container.isotope('reloadItems');

        }

    };
    
    $('#search_input').keypress(function(e){ searchItems(e); })
    $('.searchBtn').click(function(e){  searchItems(e); });

    $('.itemWrap.products').live('hover', function(e){

        (e.type == 'mouseenter')? $('.operationWrap', this).stop(true, true).show(100) : $('.operationWrap', this).stop(true, true).hide();

    });


});