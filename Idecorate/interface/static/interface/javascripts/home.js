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
            searchBox.find('.searchBox').toggle();
        });
    };

    searchBoxTransform();
    $(window).resize(searchBoxTransform);

});