// ◄ =&#9668; 
// ► = &#9658; 
// ▼ = &#9660; 
// ▲ = &#9650;
(function($){
        $.fn.dropdown = function(options){

                var defaults = {
                        subClass : 'subMenu',
                        linkTag : 'a',
                        linkedClass : 'link',
                        noLinkTag : 'span', 
                        noLinkedClass : 'noLink',
                        firstArrow : '&#9660;',
                        otherArrow : '&#9658;',
                        offset: 0
                }

                var options = $.extend(defaults,options);

                this.each(function(){
                        //add class to the menu for css usage
                        if(!$(this).hasClass('dropdown')){
                                $(this).addClass('dropdown');
                        }
                        //add class to the ul that resides under its parent li
                        var submenus = $('li',this).children('ul').addClass(options.subClass);
                        //add class on both linked and non-linked li child text
                        $('.dropdown li '+options.linkTag).addClass(options.linkedClass);
                        $('.dropdown li '+options.noLinkTag).addClass(options.noLinkedClass);
                        //append span container for arrow if li has ul child
                        if($('.dropdown li').has('ul').length){
                                if($('.dropdown li ul').hasClass(options.subClass)){
                                        $('.'+options.subClass).parent().find(options.linkTag+':first').addClass('hasSub');
                                        $('.'+options.subClass).parent().find(options.noLinkTag+':first').addClass('hasSub');
                                }
                        }
                        //start hover event
                        $('.dropdown li').hover(function(e){
                                //add class to hovered li
                                $(this).addClass("hover");
                                //use hoverFlow plugin to prevent queue building on animated objects
                                $('ul:first', this).hoverFlow(e.type, {
                                        'height': 'show',
                                        'marginTop': 'show',
                                        'marginBottom': 'show',
                                        'paddingTop': 'show',
                                        'paddingBottom': 'show'
                                }).show();
                                //check child ul position in preparation on checking scroll buildup
                                if($(this).has('ul').length){
                                        options.offset = $('ul:first', this).offset().left+$('ul:first', this).width();
                                        console.log($(window).width());
                                        if(options.offset > $(window).width()){
                                                $('ul:first', this).css({
                                                        left : '-'+$(this).outerWidth(true)+'px'
                                                });
                                        }
                                }

                        },function(e){

                                $(this).removeClass("hover");

                                $('ul:first', this).hoverFlow(e.type, {
                                        'height': 'hide',
                                        'marginTop': 'hide',
                                        'marginBottom': 'hide',
                                        'paddingTop': 'hide',
                                        'paddingBottom': 'hide'
                                }).hide();
                        });

                });

				$('.hasSub').append($('<span class="arrow"/>'));
                $('.arrow').append(options.firstArrow);

                if($('.dropdown li ul li').has('ul').length){

                	$('.dropdown ul .arrow').html(options.otherArrow);
                }

                return this;

        }
})(jQuery);