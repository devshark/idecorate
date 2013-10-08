var productCatalogue = (function(productCatalogue){

    var Category = function(data){

        Object.defineProperties(this,{
            ele:{
                value : $('<a href="#"/>'),
                writable : true,
                enumerable : true
            },
            __id : {
                value : data.id
            },
            __thumb : {
                value : data.thumbnail
            },
            __name : {
                value : data.name
            },
            __parent : {
                value : data.parent
            },
            __class : {
                value : 'categories'
            }
        });

    };

    Object.defineProperties(Category.prototype, {
        click :{
            value : function(callback){

                var self = this;

                self.ele.click(function(event){

                    if($.isFunction(callback)){

                        callback.apply(null,[self, event])

                    }
                });

            },
            enumerable : true
        },
        __loadItem : {
            value : function(uuid){

                return this.ele.addClass(this.__class).text(this.__name).attr('object-id',uuid);

            }
        }
    });

    var Product = function(data){

        Object.defineProperties(this,{
            ele:{
                value : $('<div/>'),
                writable : true,
                enumerable : true
            },
            __id : {
                value : data.product.id
            },
            __name : {
                value : data.product.name
            },
            __description : {
                value : data.product.description
            },
            __thumb : {
                value : data.product.thumb
            },
            __opaque_image : {
                value : data.product.opaque_image
            },
            __transparent_image : {
                value : data.product.transparent_image
            },
            __categories : {
                value : data.product.categories
            },
            __default_quantity : {
                value : data.product.default_quantity
            },
            __default_quantity_unit : {
                value : data.product.default_quantity_unit
            },
            __unit_price : {
                value : data.unit_price
            },
            __class : {
                value : 'productItem products'
            },
            info_btn : {
                value : $('<a class="btn info"><img src="/static/images/img_trans.gif"><h4>Info</h4></a>')
            }
        });

    };
    Object.defineProperties(Product.prototype, {
        __loadItem : {
            value : function(uuid){

                var elementItem = this.ele;
                var productImage = $('<span class="productImage" />');
                var image = $('<img alt="'+this.__name+'" />');
                var productInfo = $('<span class="productInfo"/>'); 
                var itemOperation = $('<div class="itemOperation"/>');

                image.attr('src', MEDIA_URL + 'products/' + this.__thumb);
                productImage.append(image);

                productInfo.append('<h4>'+ this.__name +'</h4>');
                productInfo.append('<h3>$'+ parseFloat(this.__unit_price).toFixed(2) +'</h3>');
                productInfo.append('<h5>'+ this.__default_quantity + ' per ' + this.__default_quantity_unit +'</h5>');

                itemOperation.append('<span class="btn"><img src="/static/images/img_trans.gif"><h4>Drag To<span>Styleboard</span></h4></span>');
                itemOperation.append(this.info_btn.attr('href', PRODUCT_PAGE + this.__id + '/'));

                elementItem.addClass(this.__class).attr('object-id',uuid);
                elementItem.append([productImage, productInfo, itemOperation]);

                return elementItem
            }
        }
    });

    var ProductCatalogue = function(){

        Object.defineProperties(this,{
            __category_container:{
                value : $('.pannel.category')
            },
            __product_container : {
                value : $('.pannel.product')
            },
            __search_box :{
                value : $('#keyword_textbox')
            },
            __search_submit :{
                value : $('#keyword_search_btn')
            },
            keyword :{
                value : null,
                writable : true,
                enumerable : true
            },
            category_id : {
                value : 0,
                writable : true,
                enumerable : true
            },
            categories : {
                value : {},
                writable : true,
                enumerable : true
            },
            products : {
                value : {},
                writable : true,
                enumerable : true
            },
            page_products : {
                value : [],
                writable : true,
                enumerable : true
            },
            total_page : {
                value : 0,
                writable : true,
                enumerable : true
            },
            page : {
                value : 0,
                writable : true,
                enumerable : true
            }
        });
    };

    Object.defineProperties(ProductCatalogue.prototype, {
        clearCategories :{
            value : function(){

                var self = this;
                self.__category_container.children('.categoryList').remove();
                self.categories = {};

            },
            enumerable : true
        },
        displayCategories :{
            value : function(){

                var self = this;
                var categoryList = $('<ul class="categoryList" />');

                for(var key in self.categories){

                    if(self.categories.hasOwnProperty(key)){

                        var item = $('<li/>');

                        self.categories[key].click(function(object,event){

                            $('#load_all_products').remove();
                            object.ele.parent().addClass('active').siblings().removeClass('active');
                            categoryList.prepend('<li id="load_all_products"><a href="#">all</a></li>');
                            event.preventDefault();
                            self.category_id = object.__id;
                            self.page = 0;
                            self.generateProducts();

                        });

                        item.html(self.categories[key].__loadItem(key));
                        categoryList.append(item);

                    }
                }

                $('#load_all_products').live('click', 'a', function(event){

                    event.preventDefault();
                    self.page = 0;
                    self.category_id = 0;
                    self.generateProducts();
                    $(this).siblings().removeClass('active');
                    $(this).remove();

                });

                self.__category_container.append(categoryList);

            },
            enumerable : true
        },
        generateCategories :{
            value : function(){

                var self = this;
                self.clearCategories();
                serverRequest({}, REQUEST_CATEGORIES, function(response){

                    var data = $.parseJSON(response.categories);
                    
                    $.each(data,function(index, value){

                        categoryData = {
                            id : value.pk,
                            thumbnail : value.fields.thumbnail,
                            name : value.fields.name,
                            parent : value.fields.parent
                        }
             
                        var uuid = Math.uuid(12, 62);
                        self.categories[uuid] = new Category(categoryData);

                    });

                    self.displayCategories();
                });

            },
            enumerable : true
        },
        clearProducts :{
            value : function(){

                var self = this;
                self.__product_container.find('.mCSB_container').children('.productItem').remove();
                self.products = {};

            },
            enumerable : true
        },
        displayProducts :{
            value : function(){

                var self = this;
                $.each(self.page_products, function(index, value){

                    if(self.products.hasOwnProperty(value)){

                        var product = self.products[value].__loadItem(value);
                        var product_info = self.products[value].info_btn;
                        self.__product_container.find('.mCSB_container').append(product);

                        product.draggable({
                            revert:true,
                            appendTo: "body",
                            cursor : "move",
                            containment: "body", 
                            helper: function(){

                                var cloned = $(this).clone();
                                var productName = self.products[value].__name;
                                cloned.find('.productInfo, .itemOperation').remove();
                                cloned.append('<h3>'+ productName +'</h3>');
                                return cloned;

                            }
                        });

                        product_info.click(function(e){
                            productPage.openPannel(self.products[value].__id);
                            e.preventDefault();
                        });

                    }

                });

                self.__product_container.mCustomScrollbar("update");

                if(self.page == 0) {
                    self.__product_container.mCustomScrollbar("scrollTo", "top");
                }

            },
            enumerable : true
        },
        generateProducts :{
            value : function(){

                var self = this;

                if(self.page == 0) {
                    self.clearProducts();
                }

                self.page_products = []

                var postData = {category_id: self.category_id, product_page: self.page, product_keyword: self.keyword};
                serverRequest(postData, REQUEST_PRODUCTS, function(response){

                    self.total_page = response.total_page;
                    var data = $.parseJSON(response.products);
                    
                    $.each(data,function(index, value){

                        productData = {
                            product : value.fields.product,
                            unit_price : value.fields._unit_price
                        }
             
                        var uuid = Math.uuid(12, 62);
                        self.products[uuid] = new Product(productData);
                        self.page_products.push(uuid); 

                    });

                    self.displayProducts();
                });

            },
            enumerable : true
        }
    });

    productCatalogue.createProductCatalogue = function(){

        var productCatalogue = new ProductCatalogue();

        return productCatalogue;

    };

    return productCatalogue;

}(productCatalogue || {}));


var embellishmentCatalogue = (function(embellishmentCatalogue){

    var Category = function(data){

        Object.defineProperties(this,{
            ele:{
                value : $('<a href="#"/>'),
                writable : true,
                enumerable : true
            },
            __id : {
                value : data.id
            },
            __title : {
                value : data.title
            },
            __description : {
                value : data.description
            },
            __class : {
                value : 'embellishmentsCategories'
            }
        });

    };

    Object.defineProperties(Category.prototype, {
        click :{
            value : function(callback){

                var self = this;

                self.ele.click(function(event){

                    if($.isFunction(callback)){

                        callback.apply(null,[self, event])

                    }
                });

            },
            enumerable : true
        },
        __loadItem : {
            value : function(uuid){

                return this.ele.addClass(this.__class).text(this.__title).attr('object-id',uuid);

            }
        }
    });

    var Embellishment = function(data){

        Object.defineProperties(this,{
            ele:{
                value : $('<div/>'),
                writable : true,
                enumerable : true
            },
            __id : {
                value : data.id
            },
            __description : {
                value : data.description
            },
            __image : {
                value : data.image
            },
            __thumb : {
                value : data.thumb
            },
            __font : {
                value : data.font
            },
            __class : {
                value : 'embellishmentItem'
            }
        });

    };
    Object.defineProperties(Embellishment.prototype, {
        __loadItem : {
            value : function(uuid){

                var elementItem = this.ele;
                var embellishmentImage = $('<span class="embellishmentImage" />');
                var image = $('<img alt="'+this.__type+'" />');
                var itemOperation = $('<div class="itemOperation"/>');
                if(this.__type.__id == 6){
                    image.attr('src', '/generate_text/?font_size=120&amp;font_text=Abc&amp;font_color=000000000&amp;font_id='+ this.__id +'&amp;font_thumbnail=1');
                }else{
                    image.attr('src', '/generate_embellishment/?embellishment_id='+ this.__id +'&amp;embellishment_color=000000000&amp;embellishment_thumbnail=1&amp;embellishment_size=120');
                }
                embellishmentImage.append(image);

                itemOperation.append('<span class="btn"><img src="/static/images/img_trans.gif"><h4>Drag To<span>Styleboard</span></h4></span>');
                
                elementItem.addClass(this.__class + " " + this.__type.__title.toLowerCase()).attr('object-id',uuid);
                elementItem.append([embellishmentImage, itemOperation]);

                return elementItem
            }
        }
    });

    var EmbellishmentCatalogue = function(){

        Object.defineProperties(this,{
            __category_container:{
                value : $('.pannel.embellishmentCategory')
            },
            __embellishment_container : {
                value : $('.pannel.embellishment')
            },
            category_id : {
                value : 0,
                writable : true,
                enumerable : true
            },
            categories : {
                value : {},
                writable : true,
                enumerable : true
            },
            embellishments : {
                value : {},
                writable : true,
                enumerable : true
            },
            page_embellishments : {
                value : [],
                writable : true,
                enumerable : true
            },
            total_page : {
                value : 0,
                writable : true,
                enumerable : true
            },
            page : {
                value : 0,
                writable : true,
                enumerable : true
            }
        });
    };

    Object.defineProperties(EmbellishmentCatalogue.prototype, {
        clearCategories :{
            value : function(){

                var self = this;
                self.__category_container.children('.embellishmentCategoryList').remove();
                self.categories = {};

            },
            enumerable : true
        },
        displayCategories :{
            value : function(){

                var self = this;
                var categoryList = $('<ul class="embellishmentCategoryList" />');

                for(var key in self.categories){

                    if(self.categories.hasOwnProperty(key)){

                        var item = $('<li/>');

                        self.categories[key].click(function(object,event){

                            $('#load_all_embellishments').remove();
                            object.ele.parent().addClass('active').siblings().removeClass('active');
                            categoryList.prepend('<li id="load_all_embellishments"><a href="#">all</a></li>');
                            event.preventDefault();
                            self.category_id = object.__id;
                            self.page = 0;
                            self.generateEmbellishments();

                        });

                        item.html(self.categories[key].__loadItem(key));
                        categoryList.append(item);

                    }
                }

                $('#load_all_embellishments').live('click', 'a', function(event){

                    event.preventDefault();
                    self.page = 0;
                    self.category_id = 0;
                    self.generateEmbellishments();
                    $(this).siblings().removeClass('active');
                    $(this).remove();

                });

                self.__category_container.append(categoryList);

            },
            enumerable : true
        },
        generateCategories :{
            value : function(){

                var self = this;
                self.clearCategories();
                serverRequest({}, REQUEST_EMBELLISHMENT_CATEGORIES, function(response){

                    var data = $.parseJSON(response.embellishment_categories);
                    
                    $.each(data,function(index, value){

                        categoryData = {
                            id : value.pk,
                            title : value.fields.name,
                            description : value.fields.name
                        }
             
                        var uuid = Math.uuid(12, 62);
                        self.categories[uuid] = new Category(categoryData);

                    });
                    var uuid = Math.uuid(12, 62);
                    self.categories[uuid] = new Category({id:6, title: "Text", description : "Text embellishment"});

                    self.displayCategories();
                });

            },
            enumerable : true
        },
        clearEmbellishments :{
            value : function(){

                var self = this;
                self.__embellishment_container.find('.mCSB_container').children('.embellishmentItem').remove();
                self.embellishments = {};

            },
            enumerable : true
        },
        displayEmbellishments :{
            value : function(){

                var self = this;
                $.each(self.page_embellishments, function(index, value){

                    if(self.embellishments.hasOwnProperty(value)){

                        var embellishment = self.embellishments[value].__loadItem(value);
                        self.__embellishment_container.find('.mCSB_container').append(embellishment);

                        embellishment.draggable({
                            revert:true,
                            appendTo: "body",
                            cursor : "move",
                            containment: "body", 
                            helper: function(){

                                var cloned = $(this).clone();
                                cloned.find('.itemOperation').remove();
                                return cloned;

                            }
                        });
                    }

                });
                self.__embellishment_container.find('img').load(function(){
                    self.__embellishment_container.mCustomScrollbar("update");
                });
                if(self.page == 0) {
                    self.__embellishment_container.mCustomScrollbar("scrollTo", "top");
                }

            },
            enumerable : true
        },
        generateEmbellishments :{
            value : function(){

                var self = this;

                if(self.page == 0) {
                    self.clearEmbellishments();
                }

                self.page_embellishments = []

                var postData = {embellishment_category_id: self.category_id, embellishment_page: self.page};
                serverRequest(postData, REQUEST_EMBELLISHMENT, function(response){

                    self.total_page = response.total_page;
                    var data = $.parseJSON(response.embellishments);
                    
                    $.each(data,function(index, value){

                        embellishmentData = {
                            id : value.pk,
                            description : value.fields.description,
                            image : value.fields.image,
                            thumb : value.fields.image_thumb,
                            font : value.fields.font,
                            type : (value.fields.e_type === undefined) ? 6 : value.fields.e_type
                        }
             
                        var uuid = Math.uuid(12, 62);
                        var embellishment = new Embellishment(embellishmentData); 

                        for(var key in self.categories){
                            var category = self.categories[key];
                            if(category.__id == embellishmentData.type){
                                Object.defineProperties(embellishment,{
                                    __type:{
                                        value : category
                                    }
                                });
                            }
                        }

                        self.embellishments[uuid] = embellishment
                        self.page_embellishments.push(uuid); 

                    });

                    self.displayEmbellishments();
                });

            },
            enumerable : true
        }
    });

    embellishmentCatalogue.createEmbellishmentCatalogue = function(){

        var embellishmentCatalogue = new EmbellishmentCatalogue();

        return embellishmentCatalogue;

    };

    return embellishmentCatalogue;

}(embellishmentCatalogue || {}));


var templateCatalogue = (function(templateCatalogue){

    var Template = function(data){

        Object.defineProperties(this,{
            ele:{
                value : $('<div/>'),
                writable : true,
                enumerable : true
            },
            __id : {
                value : data.id
            },
            __description : {
                value : data.description
            },
            __name : {
                value : data.name
            },
            __class : {
                value : 'templateItem'
            }
        });

    };
    Object.defineProperties(Template.prototype, {
        __loadItem : {
            value : function(uuid){

                var elementItem = this.ele;
                var templateImage = $('<span class="templateImage" />');
                var image = $('<img alt="'+this.__name.toLowerCase().replace(" ", "_")+'" />');
                var itemOperation = $('<div class="itemOperation"/>');
                image.attr('src', '/styleboard/generate_styleboard_template_view/' + this.__id + '/140/120/');
                templateImage.append(image);
                itemOperation.append('<span class="btn"><img src="/static/images/img_trans.gif"><h4>Drag To<span>Styleboard</span></h4></span>');
                elementItem.addClass(this.__class).attr('object-id',uuid);
                elementItem.append([templateImage, itemOperation]);

                return elementItem
            }
        }
    });

    var TemplateCatalogue = function(){

        Object.defineProperties(this,{
            __template_container : {
                value : $('#templates')
            },
            templates : {
                value : {},
                writable : true,
                enumerable : true
            },
            page_templates : {
                value : [],
                writable : true,
                enumerable : true
            },
            total_page : {
                value : 0,
                writable : true,
                enumerable : true
            },
            page : {
                value : 0,
                writable : true,
                enumerable : true
            }
        });
    };

    Object.defineProperties(TemplateCatalogue.prototype, {
        clearTemplates :{
            value : function(){

                var self = this;
                self.__template_container.find('.mCSB_container').children('.templateItem').remove();
                self.templates = {};

            },
            enumerable : true
        },
        displayTemplates :{
            value : function(){

                var self = this;
                $.each(self.page_templates, function(index, value){

                    if(self.templates.hasOwnProperty(value)){

                        var template = self.templates[value].__loadItem(value);
                        self.__template_container.find('.mCSB_container').append(template);

                        template.draggable({
                            revert:true,
                            appendTo: "body",
                            cursor : "move",
                            containment: "body", 
                            helper: function(){

                                var cloned = $(this).clone();
                                cloned.find('.itemOperation').remove();
                                return cloned;

                            }
                        });
                    }

                });
                self.__template_container.find('img').load(function(){
                    self.__template_container.mCustomScrollbar("update");
                });
                if(self.page == 0) {
                    self.__template_container.mCustomScrollbar("scrollTo", "top");
                }

            },
            enumerable : true
        },
        generateTemplates :{
            value : function(){

                var self = this;

                if(self.page == 0) {
                    self.clearTemplates();
                }

                self.page_templates = []

                var postData = {template_page: self.page};
                serverRequest(postData, REQUEST_TEMPLATE, function(response){

                    self.total_page = response.total_page;
                    var data = $.parseJSON(response.templates);
                    
                    $.each(data,function(index, value){

                        templateData = {
                            id : value.pk,
                            name : value.fields.name,
                            description : value.fields.description
                        }
             
                        var uuid = Math.uuid(12, 62);
                        var template = new Template(templateData); 
                        
                        self.templates[uuid] = template
                        self.page_templates.push(uuid); 

                    });

                    self.displayTemplates();
                });

            },
            enumerable : true
        }
    });

    templateCatalogue.createTemplateCatalogue = function(){

        var templateCatalogue = new TemplateCatalogue();

        return templateCatalogue;

    };

    return embellishmentCatalogue;

}(embellishmentCatalogue || {}));


var productPage = (function(productPage){

    
    var ProductFrame = function(){

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

    Object.defineProperties(ProductFrame.prototype,{

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
                self.pannel.animate({width:0},300, function(){
                    self.toggle_button.removeClass('hide');
                    self.pannel.addClass('hidden');
                });
            },
            enumerable : true
        },
        togglePannel: {
            value: function(){

                if(this.toggle_button.hasClass('hide')){
                    this.pannel.animate({width:0, right: '-40px'},300);
                }else{
                    this.pannel.animate({width:"55%",right: 0},300);
                }
                this.toggle_button.toggleClass('hide');
            },
            enumerable : true
        },
        __frameChange:{
            value: function(){

                this.iframe.attr({src:PRODUCT_PAGE + this.__product_id + '/', class: 'productInfoIframe'});
                this.pannel.append(this.iframe);
            }
        },
        openPannel: {
            value: function(product_id){

                var self = this;

                if(self.pannel.hasClass('hidden') || !this.toggle_button.hasClass('hide')){
                    self.pannel.removeClass('hidden');
                    self.pannel.animate({width:"55%",right: 0},300, function(){
                        self.toggle_button.addClass('hide');
                    });
                };
                if(self.__product_id != product_id){
                    self.iframe.remove();
                    self.__product_id = parseInt(product_id);
                    self.pannel.find('.loadingIcon').removeClass('hidden');
                    setTimeout(function(){
                        self.__frameChange();
                        self.iframe.load(function(){
                            self.pannel.find('.loadingIcon').addClass('hidden');
                        });
                    },300);
                }
            },
            enumerable : true
        } 
     });

    productPage.generateProductPannel = function(){

        var productInfo = new ProductFrame();
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

    return productPage;

}(productPage || {}));

var serverRequest = function(data, url, success, fail){

    var request;
    request = $.ajax({
        url: url,
        type: "POST",
        data: data,
        async: true
    });

    request.done(function (response, textStatus, jqXHR){

        if($.isFunction(success)){

            success.apply(null, [response]);

        }
        
    });

    request.fail(function (jqXHR, textStatus, errorThrown){
        
        if($.isFunction(fail)){

            fail.apply(null, [textStatus, errorThrown]);

        }

    });

    request.always(function(){

    });

    return request;
};

var pannels = {
    '#products' : {
        element : $('#products'),
        is_empty: function(){
            return ($.isEmptyObject(productCatalogue.categories) && $.isEmptyObject(productCatalogue.products)) ? true : false;
        },
        action : function(){
            productCatalogue.__product_container.mCustomScrollbar({
                scrollInertia:200,
                scrollButtons:{
                    enable:false
                },
                theme: 'dark-thick',
                callbacks:{
                    onTotalScrollOffset : 50,
                    onTotalScroll:function(){

                        if(productCatalogue.page <= productCatalogue.total_page ){
                            ++productCatalogue.page;
                            productCatalogue.generateProducts();
                        }
                        
                    }
                },   
                advanced:{  
                    updateOnBrowserResize:true,   
                    updateOnContentResize:true   
                }
            });
            productCatalogue.generateCategories();
            productCatalogue.generateProducts();
        }
    },
    '#embellishments' : {
        element : $('#embellishments'),
        is_empty: function(){
            return ($.isEmptyObject(embellishmentCatalogue.categories) && $.isEmptyObject(embellishmentCatalogue.embellishments)) ? true : false;
        },
        action : function(){
            embellishmentCatalogue.__embellishment_container.mCustomScrollbar({
                scrollInertia:200,
                scrollButtons:{
                    enable:false
                },
                theme: 'dark-thick',
                callbacks:{
                    onTotalScrollOffset : 50,
                    onTotalScroll:function(){

                        if(embellishmentCatalogue.page <= embellishmentCatalogue.total_page ){
                            ++embellishmentCatalogue.page;
                            embellishmentCatalogue.generateEmbellishments();
                        }
                        
                    }
                },   
                advanced:{  
                    updateOnBrowserResize:true,   
                    updateOnContentResize:true   
                }
            });
            embellishmentCatalogue.generateCategories();
            embellishmentCatalogue.generateEmbellishments();
        }
    },
    '#templates' : {
        element : $('#templates'),
        is_empty: function(){
            return $.isEmptyObject(templateCatalogue.templates);
        },
        action : function(){
            templateCatalogue.__template_container.mCustomScrollbar({
                scrollInertia:200,
                scrollButtons:{
                    enable:false
                },
                theme: 'dark-thick',
                callbacks:{
                    onTotalScrollOffset : 50,
                    onTotalScroll:function(){

                        if(templateCatalogue.page <= templateCatalogue.total_page ){
                            ++templateCatalogue.page;
                            templateCatalogue.generateTemplates();
                        }
                        
                    }
                },   
                advanced:{  
                    updateOnBrowserResize:true,   
                    updateOnContentResize:true   
                }
            });
            templateCatalogue.generateTemplates();
        }
    },
    '#wishlist' : {
        element : $('#wishlist'),
        is_empty: function(){
            return $.isEmptyObject(wishlist);
        },
        action : function(){
            console.log('load wishlist functions here');
        }
    }
};

$(function(){

    /*================================================
       - CATALOGUE OBJECTS
    =================================================*/
    productCatalogue = productCatalogue.createProductCatalogue();
    embellishmentCatalogue = embellishmentCatalogue.createEmbellishmentCatalogue();
    templateCatalogue = templateCatalogue.createTemplateCatalogue();
    /*================================================
       - PRODUCT PANNEL
    =================================================*/
    productPage = productPage.generateProductPannel();

    productCatalogue.__search_box.prop('disabled', false);
    productCatalogue.__search_submit.prop('disabled', false);
    productCatalogue.__search_box.parent().removeClass('disabled');
    if(pannels['#products'].is_empty()){
        pannels['#products'].action();
    }
    productCatalogue.__search_box.keypress(function(e) {
        code = e.which;
        if(code==13) {
            productCatalogue.__search_submit.click();
        }
    });
    productCatalogue.__search_submit.click(function() {
        if(productCatalogue.__search_box.val() != '' && productCatalogue.keyword != productCatalogue.__search_box.val()) {
            productCatalogue.keyword = productCatalogue.__search_box.val();
            productCatalogue.generateProducts();
            $('.clearSearch').removeClass('hidden');
        }
    });

    $('.clearSearch').click(function(e){
        e.preventDefault();
        productCatalogue.keyword = '';
        productCatalogue.page = 0;
        productCatalogue.category_id = 0;
        productCatalogue.__search_box.val('');
        productCatalogue.generateProducts();
        $('.clearSearch').addClass('hidden');
    });

    $('.sideBarMenu a').click(function(e){

        e.preventDefault();
        var link = $(this);
        var pannel = pannels[link.attr('href')];
        if(pannel.is_empty()){
            pannel.action();
        }
        if(link.attr('href') == '#products'){
            productCatalogue.__search_box.prop('disabled', false);
            productCatalogue.__search_submit.prop('disabled', false);
            productCatalogue.__search_box.parent().removeClass('disabled');
        }else{
            productCatalogue.__search_box.prop('disabled', true);
            productCatalogue.__search_submit.prop('disabled', true);
            productCatalogue.__search_box.parent().addClass('disabled');
        }
        link.addClass('tabActive')
            .parent()
            .siblings()
            .children('a')
            .removeClass('tabActive');
        pannel.element.show()
            .addClass('pannelActive')
            .siblings('.tabs').hide()
            .removeClass('pannelActive');
    });
});
