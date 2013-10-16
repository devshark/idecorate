var iDcanvas = (function(iDcanvas){

    var CanvasItem = function(){

        Object.defineProperties(this, {
            ele : {
                value : $('<div class="canvasItem"/>'),
                writable : true,
                enumerable : true
            },
            image : {
                value : $('<img/>'),
                enumerable : true,
                writable : true
            }
            ,
            item_attribute : {
                value : {
                    style : {
                        width : 0,
                        height : 0,
                        zIndex : 0,
                        top: 0,
                        left: 0
                    },
                    matrix : [1,0,0,1],
                    rotation : 0
                },
                enumerable : true,
                writable : true
            },
            resize : {
                value : true,
                enumerable : true,
                writable : true
            },
            aspect : {
                value : 0.5,
                enumerable : true,
                writable : true
            },
            draggable : {
                value : false,
                enumerable : true,
                writable : true
            },
            __class : {
                value : "canvasItem unselected ",
                writable : true
            }
        });

    };


    Object.defineProperties(CanvasItem.prototype, {
        mousedown : {
            value : function(callback){
                this.__ele.on('mousedown', function(){
                    callback();
                });
            },
            enumerable : true
        },
        is_resize : {
            get: function(){
                return this.resize;
            },
            set: function(value){
                if(this.resize != value){
                    this.resize = value;
                }
            }
        },
        is_draggable : {
            get: function(){
                return this.draggable;
            },
            set: function(value){
                if(this.draggable != value){
                    this.draggable = value;
                }
            }
        },
        resizeByAspect : {
            value : function(base_dimension){

                var dimension = {},
                current_width = base_dimension.width,
                current_height = base_dimension.height,
                aspect_ratio = current_height/current_width;

                var new_width = current_width * this.aspect;
                dimension['width'] = new_width;
                dimension['height'] = aspect_ratio*new_width;

                return dimension;
            }
        }
    });


    var Product = function(data){

        CanvasItem.call(this);

        Object.defineProperties(this,{
            __id : {
                value : data.id,
                enumerable : true,
            },
            __name : {
                value : data.name,
                enumerable : true,
            },
            __description : {
                value : data.description,
                enumerable : true,
            },
            __opaque_image : {
                value : data.opaque_image,
                enumerable : true,
            },
            __transparent_image : {
                value : data.transparent_image,
                enumerable : true,
            },
            __cropped_image : {
                value : "",
                enumerable : true,
            },
            __default_quantity : {
                value : data.default_quantity,
                enumerable : true,
            },
            __default_quantity_unit : {
                value : data.default_quantity_unit,
                enumerable : true,
            },
            __unit_price : {
                value : data.unit_price,
                enumerable : true,
            },
            __dimension : {
                value : data.image_size,
                enumerable : true,
            },
            __class : {
                value : this.__class + "products"
            }
        });
    };


    Product.prototype = Object.create(CanvasItem.prototype, {
        __loadItem : {
            value : function(uuid){
                var self = this;
                var element = self.ele;
                var image = self.image;
                image.attr({
                    src: MEDIA_URL + 'products/' + self.__opaque_image + '?c='+new Date().getTime(),
                    alt:self.__name
                });
                element.addClass(self.__class).attr('object-id',uuid);
                element.append(image);

                return element
            }
        }
    });


    var ToolbarItem = function(element){

        Object.defineProperty(this, "__ele", {
            value: (element !== "undefined") ? $(element) : $('<li/>')
        });
    };

    Object.defineProperties(ToolbarItem.prototype, {
        toggleActiveState: {
            value : function () {
                this.activated = !this.activated;
            },
            enumerable : true
        },
        enabled: {
            get: function () {
                return !this.__ele.hasClass("disabled");
            },
            set: function (value) {
                var currentValue = this.enabled;
                if(currentValue === value){
                    return;
                }
                if(value){
                    this.__ele.removeClass("disabled");
                } else {
                    this.__ele.addClass("disabled");
                }
            }
        },
        activated: {
            get: function () {
                return this.__ele.hasClass("active");
            },
            set: function (value) {
                var currentValue = this.activated;
                if(currentValue === value){
                    return;
                }
                if(value){
                    this.__ele.addClass("active");
                } else {
                    this.__ele.removeClass("active");
                }
            }
        }
    });

    var createToolbarItems = function(elements){


    };

    var Toolbar = function (toolbarElement) {

        var items = toolbarElement.find(".toolbarItem");

        Object.defineProperties(this, {
            __ele: {
                value: toolbarElement
            },
            items: {
                value: createToolbarItems(items),
                enumerable: true
            }
        });
    };

    Object.defineProperties(Toolbar.prototype, {
        add: {
            value: function (options) {
                var li = $("<li/>");
                var uuid = Math.uuid(12, 62);
                li.addClass("toolbarItem");
                li.attr("object-id", uuid);
                if(options.subClass !== undefined){
                    li.addClass(options.subClass);
                }
                this.__ele.append(li);
                var item = new ToolbarItem(li);
                this.items[uuid] = item;
            },
            enumerable : true
        },
        remove: {
            value: function (uuid) {
                if (!this.items.hasOwnProperty(uuid)) {
                    throw new Error("Error: undefined toolbar item Object");
                }else{
                    var item = this.items[uuid];
                    item.__ele.remove();
                    delete item;

                    item = null;
                }
            },
            enumerable : true
        }
    });


    var ProductMenu = function(canvas){

        Object.defineProperties(this, {
            ele : {
                value : $('.itemTransformMenu'),
                writable : true,
                enumerable : true
            },
            menus : {
                value : {},
                enumerable : true,
                writable : true
            },
            active : {
                value : false,
                enumerable : true,
                writable : true
            },
            canvas: {
                value : canvas,
                writable : true,
                enumerable : true
            }
        });

    };


    var generateProductMenu = function(canvas){
        return new ProductMenu(canvas);
    };


    var generateCanvasItems = function(){
        items = {}

        return items;
    };

    var Canvas = function(){

        Object.defineProperties(this,{
            __ele:{
                value : $('#canvas')
            },
            __item_handle :{
                value : $('.handleWrap')
            },
            canvas_items : {
                value : generateCanvasItems(),
                enumerable : true
            },
            item_menus : {
                value : {},
                enumerable : true
            },
            canvas_menus : {
                value : {},
                enumerable : true
            },
            product_menus : {
                value : generateProductMenu(this),
                enumerable : true
            },
            object_count:{
                value : 0,
                enumerable: true,
                writable: true
            },
            empty: {
                value : true,
                enumerable: true,
                writable: true
            }
        });

    };

    Object.defineProperties(Canvas.prototype,{
        isEmpty:{
            get : function(){
                return this.empty;
            },
            set : function(value){
                if(value != this.empty){
                    this.empty = value;
                }
            },
            enumerable : true
        },
        init:{
            value : function(){
                if(!this.isEmpty){
                    this.arrangeCanvasItems();
                }
                this.dropableCanvas();
            },
            enumerable : true
        },
        addCanvasItem : {
            value : function(item_type,item_id){
                var self = this;
                var uuid = Math.uuid(12, 62);
                if(item_type == 'product'){
                    if(productCatalogue.products.hasOwnProperty(item_id)){
                        var base_object = productCatalogue.products[item_id];
                        var data = {};
                        data['id'] = base_object.__id;
                        data['name'] = base_object.__name;
                        data['description'] = base_object.__description;
                        data['opaque_image'] = base_object.__opaque_image;
                        data['transparent_image'] = base_object.__transparent_image;
                        data['default_quantity'] = base_object.__default_quantity;
                        data['default_quantity_unit'] = base_object.__default_quantity_unit;
                        data['unit_price'] = base_object.__unit_price;
                        data['image_size'] = base_object.__opaque_image_size;

                        self.canvas_items[uuid] = new Product(data);
                        self.canvas_items[uuid].is_draggable = true;
                    }else{
                        throw new Error("Error: undefined product Object");
                    }
                }
                return uuid;
            },
            enumerable : true
        },
        removeCanvasItem : {
            value : function(){
                var self = this,
                selected = self.__ele.find('.selected');
                if(selected.length > 1){
                    //error: selected should always be one and one only!!!!
                }else{
                    var item_key = selected.attr('object-id');
                    delete self.canvas_items[item_key];
                    self.deSelectItems();
                    selected.remove();
                }
            },
            enumerable : true
        },
        arrangeCanvasItems : {
            value : function(){

            },
            enumerable : true
        },
        dropItem : {
            value : function(uuid, e, ui){
                var self = this;
                if(self.canvas_items.hasOwnProperty(uuid)){
                    var item = self.canvas_items[uuid];
                    var element = item.__loadItem(uuid);
                    var dimension = (item.is_resize) ? item.resizeByAspect(item.__dimension) : item.__dimension;
                    ++self.object_count;
                    var data = {
                        width: dimension.width,
                        zIndex: self.object_count,
                        height: dimension.height,
                        top: (e.pageY - self.__ele.offset().top) - (dimension.height / 2),
                        left: (e.pageX - self.__ele.offset().left) - (dimension.width / 2)
                    };
                    var attribute = self.updateItem(item, data , "drop");
                    element.css(attribute);
                    self.__ele.append(element);

                    if(item.is_draggable){
                        var attribute;
                        element.mousedown(function(e){
                            self.showHandle(self.selectItem($(this)));
                            e.preventDefault();     
                        }).draggable({
                            drag: function(e, ui){
                                attribute = self.updateItem(item, {
                                    top: ui.position.top,
                                    left: ui.position.left
                                } , "drag");
                                self.__item_handle.css({
                                    top : attribute.top,
                                    left : attribute.left
                                });
                            },
                            stop: function(e, ui){
                                self.__item_handle.css({
                                    top : attribute.top,
                                    left : attribute.left
                                });
                            }
                        });
                        element.trigger('mousedown');
                    }
                }else{
                    throw new Error("Error: undefined canvas item Object");
                }
            },
            enumerable : true
        },
        dropableCanvas : {
            value : function(){
                var self = this;
                var uuid;
                if(!$.isEmptyObject(self.template_items)){
                    // create template box as dropable
                }else{
                    self.__ele.droppable({
                        drop: function (e, ui) {
                            if ($(ui.draggable)[0].id != "") {
                                ui.helper.remove();
                                var item_id = $(ui.draggable).attr('object-id');
                                var item_type = $(ui.draggable).attr('class').split(' ');
                                var index = item_type.indexOf('ui-draggable');
                                if(index != -1){
                                    item_type.splice(index, 1);
                                }
                                if($.inArray('productItem', item_type) > -1){
                                    uuid = self.addCanvasItem('product', item_id);
                                }
                                self.dropItem(uuid, e, ui);
                            }
                        }
                    });
                    self.enableHandle();
                }
                /*==============================================
                    - misc events for canvas
                    - canvas still works without this
                    - no need to make this as Canvas method
                ================================================*/
                $(document).keydown(function(e){
                    var code = e.keyCode || e.which;
                    if(code == 46 || code == 8) { 
                        self.removeCanvasItem();
                    }
                }).click(function(e){
                    var click =  $.contains(self.__ele.children()[0],e.target);
                    if(!click){
                        self.deSelectItems();
                    }
                });
            },
            enumerable : true
        },
        selectItem: {
            value : function(element){
                var selected = element.addClass('selected');
                selected.siblings('.unselected').removeClass('selected');
                return selected;
            },
            enumerable : true
        },
        deSelectItems: {
            value : function(){
                var self = this;
                self.__ele.children('.unselected').removeClass('selected');
                self.hideHandle();
            },
            enumerable : true
        },
        updateItem:{
            value : function(item, data, update_type){
                var self = this;
                var defaults = item.item_attribute.style;
                var update = $.extend({}, defaults, data);
                item.item_attribute.style = update;

                return item.item_attribute.style;
            },
            enumerable: true
        },
        enableHandle : {
            value : function(){
                var self = this,
                selected_id,
                selected,
                attribute;
                self.__item_handle.draggable({
                    handle: ".filler",
                    start: function(e, ui){
                        selected = self.__ele.find('.selected');
                        selected_id = selected.attr('object-id');
                    },
                    drag: function(e, ui){
                        attribute = self.updateItem(self.canvas_items[selected_id], {
                            top: ui.position.top,
                            left: ui.position.left
                        } , "drag");
                        selected.css(attribute);
                    },
                    stop : function(e, ui){
                        selected.css(attribute);

                    }
                }).resizable({
                    aspectRatio: true,
                    handles: 'ne, se, sw, nw',
                    minWidth: 50,
                    start: function(e, ui){
                        selected = self.__ele.find('.selected');
                        selected_id = selected.attr('object-id');
                    },
                    resize : function(e, ui){
                        attribute = self.updateItem(self.canvas_items[selected_id], {
                            height: $(this).height(),
                            width: $(this).width(),
                            top : parseInt($(this).css('top')),
                            left: parseInt($(this).css('left'))
                        } , "resize");
                        $('.filler', this).width(attribute.width).height(attribute.height);
                        selected.css(attribute);
                    }
                }).rotatable();
            },
            enumerable : true
        },
        showHandle : {
            value : function(selected_element){
                var self = this;
                self.__item_handle.removeClass('hidden invisible').css({
                    top : selected_element.css('top'),
                    left : selected_element.css('left'),
                    width : selected_element.width(),
                    height : selected_element.height()
                }).find('.filler').css({
                    width : selected_element.width(),
                    height : selected_element.height()
                });
            },
            enumerable : true
        },
        hideHandle : {
            value : function(){
                var self = this;
                self.__item_handle.addClass('hidden invisible');
            },
            enumerable : true
        }
    });
    
    iDcanvas.createCanvas = function(){

        var canvas =  new Canvas();
        return canvas;

    };

    return iDcanvas;

}(iDcanvas || {}));

var canvas = iDcanvas.createCanvas();
canvas.init();
