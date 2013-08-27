function addMenuIcon(icon,obj){

    if(obj.length > 0){

        obj.append(icon);
        var left_position = obj.offset().left + ((obj.outerWidth() - icon.width()) / 2);
        icon.show();
        icon.offset({left : left_position});
        
    }else{

        icon.hide();

    }
}

var iDCartDisplay = (function(iDCartDisplay){

    var createHideTrigger = function(element){

        var ele = element;
        
        if(ele === undefined){
            ele = $('<a id="close_cart" class="closeCartBtn" href="#" />');
        }

        return ele;
    };
    
    var Cart = function(options){

        Object.defineProperties(this,{
            display : {
                value: false,
                writable: true
            },
            displayCounter:{
                value: (options.displayCounter === undefined) ? false : options.displayCounter,
                writable: true
            },
            __cartWrapper:{
                value : options.wrapper
            },
            __iframeSrc : {
                value : options.iframeSrc
            },
            __showTrigger:{
                value : options.showTrigger,
                enumerable : true
            },
            __hideTrigger:{
                value : createHideTrigger(options.hideTrigger),
                enumerable : true
            },
            __itemCountWrapper: {
                value: $('<span id="item_counter" class="iDitemCouter"><var>O</var> items</span>'),
                enumerable : true
            }
        });
    };

    Object.defineProperties(Cart.prototype,{
        displayed: {
            get : function(){

                return this.display;
            },
            set : function(value){

                currentValue = this.display;

                if (currentValue === value) {

                    return;
                    
                }

                this.display = value;
            },
            enumerable: true
        },
        toggleDisplay: {
            value: function(){

                var self = this;

                if(!this.displayed){

                    this.buidCart().load(function(){

                        self.__cartWrapper.slideDown(300, function(){

                            self.__hideTrigger.show();

                        });

                    });

                    this.__itemCountWrapper.hide();
                    this.displayed = true;

                }else{

                    this.__cartWrapper.slideUp('fast');
                    this.__hideTrigger.hide();

                    if(this.displayCounter){

                        this.__itemCountWrapper.show();
                    }

                    this.displayed = false;

                }
            },
            enumerable: true
        },
        buidCart: {

            value: function(){
    
                var iframe = $('<iframe />');
                iframe.attr({src:this.__iframeSrc, class: 'cartIframe'});
                this.__cartWrapper.append(this.__hideTrigger, iframe);

                return iframe;

            },
            enumerable: true,
            configuralble : false

        }
    });

    iDCartDisplay.initializeDisplay = function(options){

        return new Cart(options);
    }

    return iDCartDisplay;

}(iDCartDisplay || {}));