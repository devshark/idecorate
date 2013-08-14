/*! Copyright (c) 2013 Ryan Angeles
 * Licensed under the MIT License (LICENSE.txt).
 *
 * Version: 1.0
 * 
 * Requires: 1.2.2+
 */

(function($) {
 
    var methods = {
        init: function(options) {
 
            // Repeat over each element in selector
            return this.each(function() {
                var $this = $(this);
 
                // Attempt to grab saved settings, if they don't exist we'll get "undefined".
                var settings = $this.data('simpleDropdown');
 
                // If we could't grab settings, create them from defaults and passed options
                if(typeof(settings) == 'undefined') {
 
                    var defaults = {
                        subMenuClass : 'subMenu',
                        arrows : false,
                        arrowUp : '&#9650;',
                        arrowDown : '&#9660;',
                        arrowRight : '&#9658;',
                        arrowLeft : '&#9668;',
                        mouseOver : function(event){},
                        mouseOut : function(event){},
                        mouseDown : function(event){},
                        initialize : function(object){}
                    }
 
                    settings = $.extend({}, defaults, options);
 
                    // Save our newly created settings
                    $this.data('simpleDropdown', settings);
                } else {
                    // We got settings, merge our passed options in with them (optional)
                    settings = $.extend({}, settings, options);
 
                    // If you wish to save options passed each time, add:
                    // $this.data('simpleDropdown', settings);
                }
 
                // run code here
                if(!$this.hasClass('simpleDropdown')){
                    $this.addClass('simpleDropdown');
                }

                $('a',this).each(function(){

                    var isClickable = ($(this).attr('href') == "#" || $(this).attr('href') == "") ? 'nonClickable' : 'clickable';

                    $(this).addClass(isClickable);

                    $(this).on('mousedown click', function(e){
                        if($(this).hasClass('nonClickable')){
                            e.preventDefault();
                        }
                        settings.mouseDown.call(this, e, this);
                    });
                });

                //add class to the ul that resides under its parent li
                $('li', this).children('ul').addClass(settings.subMenuClass);
                
                //append span container for arrow if li has ul child
                var subMenus = $this.find('li ul');

                if(subMenus.hasClass(settings.subMenuClass)){
                    subMenus.parent().children('a').addClass('hasSubMenu');
                }

                settings.initialize.call(this, this);

                if(settings.arrows){

                    $('.hasSubMenu',$this).append($('<span class="arrowWrapper"/>'));
                    $this.children('li:first').find('.arrowWrapper').html(settings.arrowDown);
                    $('.subMenu',$this).find('.arrowWrapper').html(settings.arrowRight);
                    
                }

                //start hover event
                $('li', this).hover(function(e){
                    //add class to hovered li
                    $(this).addClass("hover");
                    $('ul:first', this).stop(true, true).slideDown("fast");

                    if($(this).has('ul').length){
                        settings.offset = $('ul:first', this).offset().left+$('ul:first', this).width();
                        if(settings.offset > $(window).width()){
                            $('ul:first', this).css({
                                left : '-'+$(this).outerWidth(true)+'px'
                            });
                        }
                    }
                    if(settings.arrows){

                        var arrow = ($(this).parents('.subMenu').length > 0) ? settings.arrowLeft : settings.arrowUp;
                        if(typeof(arrow) == 'object'){
                            arrow = arrow.clone();
                        }
                        $('> .hasSubMenu >.arrowWrapper',this).html(arrow);
                    }
                    settings.mouseOver.call(this, e, this);

                },function(e){
                    $(this).removeClass("hover");
                    $('ul:first', this).hide();
                    if(settings.arrows){

                        var arrow = ($(this).parents('.subMenu').length > 0) ? settings.arrowRight : settings.arrowDown;
                        if(typeof(arrow) == 'object'){
                            arrow = arrow.clone();
                        }
                        $('> .hasSubMenu >.arrowWrapper',this).html(arrow);
                    }
                    settings.mouseOut.call(this, e, this);
                });
            });
        },
        destroy: function(options) {
            // Repeat over each element in selector
            return $(this).each(function() {
                var $this = $(this);
 
                // run code here
 
                // Remove settings data when deallocating our plugin
                $this.removeData('simpleDropdown');
            });
        },
        val: function(options) {
            // code here, use .eq(0) to grab first element in selector
            // we'll just grab the HTML of that element for our value
            var someValue = this.eq(0).html();
 
            // return one value
            return someValue;
        }
    };
 
    $.fn.simpleDropdown = function() {
        var method = arguments[0];
 
        if(methods[method]) {
            method = methods[method];
            arguments = Array.prototype.slice.call(arguments, 1);
        } else if( typeof(method) == 'object' || !method ) {
            method = methods.init;
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.simpleDropdown' );
            return this;
        }
 
        return method.apply(this, arguments);
 
    }
 
})(jQuery);