/*! Copyright (c) 2013 Ryan Angeles
 * Licensed under the MIT License (LICENSE.txt).
 *
 * Version: 1.3
 * 
 * Requires: 1.2.2+
 */
 
(function($){
    $.fn.colresize = function(options){

        var defaults = {
            column_count        : 0,
            wrapper_class       : 'displayTable',
            wrapper             : this,
            specific_children   : false,
            resizeRow : function(cells, from, to){

                console.log(from,to);

                var arr = $.makeArray();

                if(to != undefined){
                    cells.slice(from, to).each(function(){

                        arr.push($(this).height());
                        console.log(arr)

                    }).css('height', Math.max.apply( Math, arr ));
                }
            }
        }

        var options = $.extend(defaults,options);

        this.each(function(){

        	options.wrapper.addClass(options.wrapper_class); // main container of divs to be resize

        	wrapper = options.wrapper;

			is_empty = wrapper.is(':empty');

			if(!is_empty){ //check if container is not empty

				var cells           = $(wrapper).children();
                var index_array     = $.makeArray();
                var position_top    = 0;
                
                cells.each(function(index,dom_ele){

                    if(index == cells.length-1){

                        index_array.push(cells.length-1);

                        position_top = 'stop';

                    }

                    if($(dom_ele).position().top != position_top){

                        if(index_array[1]){

                            index_array.shift();

                        }

                        if(position_top != 'stop'){

                            index_array.push(index);

                        }

                        options.resizeRow(cells,index_array[0],index_array[1]);

                    }

                    position_top = $(dom_ele).position().top;

                });

			}

        });

        return options.wrapper;

    }
})(jQuery);
