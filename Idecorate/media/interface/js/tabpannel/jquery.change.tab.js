(function( $ ) {
  $.fn.changeTab = function(options) {
    
    options = $.extend({activeTabClass:"activeTab",activePanel:"activePannel",defaultTab:"li:first-child"}, options);
        
        var defTab      = this.find('ul li:first-child'),
            pannelID    = $('a', defTab).attr('href'),
            pannels     = [];

            defTab.addClass(options.activeTabClass);
            $(pannelID).css('display','block');

            this.find('ul li').each(function(e){
                pannels[e] = $('a',this).attr('href');
            });

    return  this.find('ul li').each(function(e){
                $(this).on('click',function(e){
                    if($(this).hasClass(options.activeTabClass) === false){
                        $(this).siblings('li').removeClass(options.activeTabClass);
                        $(this).addClass(options.activeTabClass);
                        defTab = $(this);
                    }
                });

                $('a',this).click(function(ev){
                    ev.preventDefault();
                    for (var i=0; i < pannels.length; i++) {
                        if(pannels[i] == $(this).attr('href')){
                            $(pannels[i]).css('display','block');
                        }else{
                            $(pannels[i]).css('display','none');
                        }
                    };
                });
            });
  };
})( jQuery );