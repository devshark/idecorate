var pannelResize = function(elements){

    $(elements).height(0);
    $.each($(elements), function(index, element){

        $(element).height($(element).parents('.cell').outerHeight(true)-$(element).siblings().outerHeight(true)-2);

    });
};

var ProductInfo = function(){

    Object.defineProperties(this,{
        pannel:{
            value : $('#product_info_page'),
            writable : true,
            enumerable : true
        },
        toggle_button : {
            value : $('#product_info_page').find('a.toggle'),
            writable : true,
            enumerable : true
        },
        close_button : {
            value : $('#product_info_page').find('a.close'),
            writable : true,
            enumerable : true
        },
        iframe : {
            value : $('<iframe id="product_page_frame" />'),
            writable : true,
            enumerable : true
        },
        __class : {
            value : 'productInfoPage'
        },
        __product_id : {
            value : 0,
            writable : true
        }
    });
};

Object.defineProperties(ProductInfo.prototype,{

    pannelResize:{
        value: function(){

            var baseElement = $('#styleboard');
            var positionTop = baseElement.find('thead').outerHeight(true);
            var pannelHeight = (baseElement.height() - positionTop >= 500) ? baseElement.height() - positionTop : 500;
            this.pannel.css({
                top: positionTop,
                height: pannelHeight-(this.pannel.outerHeight(true) - this.pannel.height())
            });
        },
        enumerable : true
    },
    closePannel: {
        value: function(){

            var self = this;
            self.pannel.animate({right:"-100%"},600, function(){
                self.toggle_button.removeClass('hide');
                self.pannel.addClass('hidden');
            });
        },
        enumerable : true
    },
    togglePannel: {
        value: function(){

            if(this.toggle_button.hasClass('hide')){
                this.pannel.animate({right:"-55%"},300);
            }else{
                this.pannel.animate({right:"0"},300);
            }
            this.toggle_button.toggleClass('hide');
        },
        enumerable : true
    },
    openPannel: {
        value: function(){

            var self = this;
            if(self.pannel.hasClass('hidden') || !this.toggle_button.hasClass('hide')){
                self.pannel.animate({right:"0"},600, function(){
                    self.toggle_button.addClass('hide');
                    self.pannel.removeClass('hidden');
                });
            };
        },
        enumerable : true
    } 
 });

var generateProductPannel = function(){

    var productInfo = new ProductInfo();
    productInfo.pannelResize();
    productInfo.toggle_button.click(function(e){
        productInfo.togglePannel();
        e.preventDefault();
    });
    productInfo.close_button.click(function(e){
        productInfo.closePannel();
        e.preventDefault();
    });
    return productInfo;
};

$(function(){

    /*================================================
        - set heights on page loads
        - set heights on window resize
    =================================================*/
    pannelResize('.sideBarItems, #canvas');
    productInfo = generateProductPannel();
    
});

var resizing;

$(window).resize(function(){

    clearTimeout(resizing);

    resizing = setTimeout(function(){

        pannelResize('.sideBarItems, #canvas');
        productInfo.pannelResize();

    }, 100);

});