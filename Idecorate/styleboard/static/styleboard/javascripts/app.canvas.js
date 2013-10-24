var iDcanvas = (function(iDcanvas){

    var CanvasItem = function(){

        Object.defineProperties(this, {
            ele : {
                value : $('<div/>'),
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
                    width : 0,
                    height : 0,
                    zIndex : 0,
                    top: 0,
                    left: 0,
                    matrix : [1,0,0,1],
                    degree : 0,
                    radian : 0,
                    flip : false,
                    flop : false,
                    use_image : ""
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
                writable : true,
                enumerable : true
            },
            generated :{
                value :  false,
                enumerable : true,
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
            },
            enumerable : true
        },
        is_draggable : {
            get: function(){
                return this.draggable;
            },
            set: function(value){
                if(this.draggable != value){
                    this.draggable = value;
                }
            },
            enumerable : true
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
            },
            enumerable : true
        },
        styles : {
            value : function(){
                var self = this;
                var matrix = 'matrix('+ self.item_attribute.matrix.join(',') +', 0, 0)';
                styles = {
                    width               : self.item_attribute.width,
                    height              : self.item_attribute.height,
                    zIndex              : self.item_attribute.zIndex,
                    top                 : self.item_attribute.top,
                    left                : self.item_attribute.left,
                    '-moz-transform'    : matrix,
                    '-o-transform'      : matrix,
                    '-webkit-transform' : matrix,
                    '-ms-transform'     : matrix,
                    'transform'         : matrix
                };
                return styles;
            },
            enumerable : true
        },
        updateAppearance : {
            value : function(){
                var self = this;
                self.ele.css(self.styles());
            },
            enumerable : true
        },
        updateImage : {
            value : function(){
                var self = this;
                self.ele.find('img')[0].src = (self.generated) ? self.item_attribute.use_image :self.__item_directory + self.item_attribute.use_image;
            },
            enumerable : true
        },      
        toggleFlip: {
            value : function () {
                this.item_attribute.flip = !this.item_attribute.flip;
                this.item_attribute.matrix[0] = -this.item_attribute.matrix[0];
                this.item_attribute.matrix[2] = -this.item_attribute.matrix[2];
            },
            enumerable : true
        },
        toggleFlop: {
            value : function () {
                this.item_attribute.flop = !this.item_attribute.flop;
                this.item_attribute.matrix[1] = -this.item_attribute.matrix[1];
                this.item_attribute.matrix[3] = -this.item_attribute.matrix[3];
            },
            enumerable : true
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
                writable : true
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
                value : this.__class + "products",
                enumerable : true
            },
            __item_directory : {
                value :  MEDIA_URL + 'products/',
                enumerable : true
            }
        });
    };


    Product.prototype = Object.create(CanvasItem.prototype, {
        __loadItem : {
            value : function(uuid){
                var self = this;
                var element = self.ele;
                self.image.attr({ alt:self.__name });
                element.addClass(self.__class).attr('object-id',uuid);
                element.append(self.image);
                self.updateImage();

                return element
            },
            enumerable : true
        }
    });


    var ToolbarItem = function(element){

        Object.defineProperty(this, "__ele", {
            value: (element !== "undefined") ? $(element) : $('<a/>')
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

        var items = {};
        elements.each(function(index, value){
            var uuid = Math.uuid(12,62);
            var item = $(value).attr('object-id', uuid);
            items[uuid] = new ToolbarItem(item);
        });
        return items;
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
                var anchor = $("<a/>");
                var uuid = Math.uuid(12, 62);
                anchor.addClass("toolbarItem");
                anchor.attr("object-id", uuid);
                if(options.subClass !== undefined){
                    anchor.addClass(options.subClass);
                }
                this.__ele.append(anchor);
                var item = new ToolbarItem(anchor);
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
        }
    });

    var CanvasMenu = function(element){

        Toolbar.apply(this,[element]);

        Object.defineProperties(this, {
            canvas_states: {
                value: $.makeArray(),
                enumerable : true,
                writable : true
            },
            current_state_index: {
                value: 0,
                enumerable : true,
                writable : true
            }
        });
    };

    CanvasMenu.prototype = Object.create(Toolbar.prototype, {
        saveStyleboard : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this);
                }
            },
            enumerable: true 
        },
        startNew : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this);
                }
            },
            enumerable: true 
        },
        undo : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this);
                }
            },
            enumerable: true 
        },
        redo : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this);
                }
            },
            enumerable: true 
        },
        print : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this);
                }
            },
            enumerable: true 
        },
        pdf : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this);
                }
            },
            enumerable: true 
        }
    });

    var ItemMenu = function(element){

        Toolbar.apply(this,[element]);

        Object.defineProperty(this, "selected_item", {
            value: null,
            enumerable: true,
            writable: true
        });
    };

    ItemMenu.prototype = Object.create(Toolbar.prototype, {
        remove : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this, [this.selected_item, "remove"]);
                }
            },
            enumerable: true 
        },
        flip : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this, [this.selected_item, "flip"]);
                }
            },
            enumerable: true 
        },
        flop : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this, [this.selected_item, "flop"]);
                }
            },
            enumerable: true 
        },
        clone : {
            value : function(callback){
                var clone = function(src_object){
                    var mixin = function(dest, source, copyFunc) {
                        var name, s, i, empty = {};
                        for(name in source){
                            s = source[name];
                            if(!(name in dest) || (dest[name] !== s && (!(name in empty) || empty[name] !== s))){
                                dest[name] = copyFunc ? copyFunc(s) : s;
                            }
                        }
                        return dest;
                    }
                    if(!src_object || typeof src_object != "object" || Object.prototype.toString.call(src_object) === "[object Function]"){
                        return src_object;
                    }
                    if(src_object.nodeType && "cloneNode" in src_object){
                        return src_object.cloneNode(true);
                    }
                    if(src_object instanceof Date){
                        return new Date(src_object.getTime());
                    }
                    if(src_object instanceof RegExp){
                        return new RegExp(src_object);
                    }
                    var r, i, l;
                    if(src_object instanceof Array){
                        r = [];
                        for(i = 0, l = src_object.length; i < l; ++i){
                            if(i in src_object){
                                r.push(clone(src_object[i]));
                            }
                        }
                    }else{
                        r = src_object.constructor ? new src_object.constructor() : {};
                    }
                    return mixin(r, src_object, clone);
                };
                
                if(typeof callback === "function"){
                    callback.apply(this, [clone(this.selected_item), "clone"]);
                }
            },
            enumerable: true 
        },
        forward : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this, [this.selected_item, "forward"]);
                }
            },
            enumerable: true 
        },
        backward : {
            value : function(callback){
                if(typeof callback === "function"){
                    callback.apply(this, [this.selected_item, "backward"]);
                }
            },
            enumerable: true 
        },
        productInfo : {
            value : function(){
                if(this.selected_item.ele.hasClass('products')){
                    productPage.openPannel(this.selected_item.__id);
                }
                return;
            },
            enumerable: true 
        },
        setItem : {
            value : function(item){
                this.selected_item = item;
                this.enabled = true;
            },
            enumerable: true 
        },
        unSetItem: {
            value : function(){
                this.selected_item = null;
                this.enabled = false;
            },
            enumerable: true 
        }
    });


    var ProductMenu = function(element){

        Toolbar.apply(this,[element]);

        Object.defineProperty(this, "selected_product", {
            value: null,
            enumerable: true,
            writable: true
        });
    };


    ProductMenu.prototype = Object.create(Toolbar.prototype, {
        transformOpaque : {
            value : function(callback){
                var self = this;
                self.selected_product.item_attribute.use_image  = self.selected_product.__opaque_image;
                self.selected_product.generated = false;
                self.selected_product.updateImage();
                if(typeof callback === "function"){
                    callback.apply(self, [self.selected_product, "opaque"]);
                }
            },
            enumerable: true 
        },
        transformTransparent : {
            value : function(callback){
                var self = this;
                self.selected_product.item_attribute.use_image = self.selected_product.__transparent_image;
                self.selected_product.generated = false;
                self.selected_product.updateImage();
                if(typeof callback === "function"){
                    callback.apply(self, [self.selected_product, "transparent"]);
                }
            },
            enumerable: true 
        },
        transformCrop : {
            value : function(callback){
                var self = this;
                $('#modal_crop').modal({
                    onShow: function (dialog) {
                        var iframe = $('<iframe id="iDCropIframe"/>');
                        iframe.attr({
                            src: '/app/crop/?filename=' + escape(self.selected_product.item_attribute.use_image),
                            width : 450,
                            height : 480 
                        });
                        $(dialog.data[0]).html(iframe);
                    }
                });
                if(typeof callback === "function"){
                    callback.apply(self, [self.selected_product, "crop"]);
                }
            },
            enumerable: true 
        },
        iconChange: {
            value: function(object){

                var self = this;
                self.selected_product = object;
                var images = {
                    "opaque" : self.selected_product.__opaque_image,
                    "transparent" : self.selected_product.__transparent_image,
                    "crop" : self.selected_product.__transparent_image,
                };
                for(var key in self.items){
                    if(self.items.hasOwnProperty(key)){
                        self.items[key].__ele.find("img")[0].src = MEDIA_URL + 'products/' + images[self.items[key].__ele[0].id];
                    }
                }
                self.enabled = true;
            },
            enumerable: true 
        },
        iconRemove : {
            value : function(){

                var self = this;
                for(var key in self.items){
                    if(self.items.hasOwnProperty(key)){
                        self.items[key].__ele.find("img")[0].src = "/static/images/img_trans.gif";
                    }
                }
                self.selected_product = null;
                self.enabled = false;
                
            },
            enumerable: true 
        }
    });


    var generateCanvasItems = function(){
        var items = {}

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
                value : new ItemMenu($('.itemMenu')),
                enumerable : true
            },
            canvas_menus : {
                value : new CanvasMenu($('.canvasMenu')),
                enumerable : true
            },
            product_menus : {
                value : new ProductMenu($('.productTransformMenu')),
                enumerable : true
            },
            object_count:{
                value : 0,
                enumerable: true,
                writable: true
            }
        });
    };


    Object.defineProperties(Canvas.prototype,{
        init:{
            value : function(){
                if(!this.empty){
                    this.arrangeCanvasItems();
                }
                this.dropableCanvas();
            },
            enumerable : true
        },
        empty:{
            get : function(){
                return this.__ele.hasClass('empty');
            },
            set : function(value){
                var currentValue = this.empty;
                if(currentValue === value){
                    return;
                }
                if(value){
                    this.__ele.addClass("empty");
                } else {
                    this.__ele.removeClass("empty");
                }
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
                    --self.object_count;
                    var item_key = selected.attr('object-id');
                    delete self.canvas_items[item_key];
                    self.deSelectItems();
                    selected.remove();
                    if(self.object_count < 1){
                        self.empty = true;
                    }
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
            value : function(uuid, e, clone){
                var self = this;
                if(self.canvas_items.hasOwnProperty(uuid)){
                    var item = self.canvas_items[uuid];
                    var dimension = (item.is_resize) ? item.resizeByAspect(item.__dimension) : item.__dimension;
                    var data = {};
                    ++self.object_count;
                    if(clone && clone !== "undefined"){
                        item.ele.attr("class","").find("img").remove();
                        data = {
                            zIndex: self.object_count,
                            top : item.item_attribute.top + 20,
                            left : item.item_attribute.left + 20
                        };
                    }else{
                        data = {
                            width: dimension.width,
                            zIndex: self.object_count,
                            height: dimension.height,
                            top: (e.pageY - self.__ele.offset().top) - (dimension.height / 2),
                            left: (e.pageX - self.__ele.offset().left) - (dimension.width / 2)
                        };
                        self.savingPoint(uuid, "drop");
                    }
                    var element = item.__loadItem(uuid);
                    var attribute = self.updateItemAttribute(item, data);
                    self.__ele.append(element);

                    if(item.is_draggable){
                        var attribute;
                        element.mousedown(function(e){
                            self.showHandle(self.selectItem($(this)));
                            if(item.__class.search('products') != -1){
                                self.product_menus.iconChange(item);
                            }
                            self.item_menus.setItem(item);
                            e.preventDefault();     
                        }).draggable({
                            drag: function(e, ui){
                                attribute = self.updateItemAttribute(item, {
                                    top: ui.position.top,
                                    left: ui.position.left
                                });
                                self.__item_handle.css({
                                    top : attribute.top,
                                    left : attribute.left
                                });
                            },
                            stop: function(e, ui){
                                self.savingPoint($(this).attr('object-id'),"drag");
                            }
                        });
                        element.trigger('mousedown');
                    }
                    if(self.object_count > 0){
                        self.empty = false;
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
                                    var item = self.canvas_items[uuid];
                                    item.item_attribute.use_image = item.__opaque_image;
                                }
                                self.dropItem(uuid, e);
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
                        for(var key in self.item_menus.items){
                            if(self.item_menus.items.hasOwnProperty(key)){
                                var item = item_menu.items[key].__ele;
                                if(item[0].id == "remove"){
                                    item.trigger('click');
                                }
                            }
                        }
                    }
                }).click(function(e){
                    var click =  $.contains(self.__ele.children()[0],e.target) || $(e.target).parents('ul').hasClass('toolBar') || $(e.target).hasClass('simplemodal-overlay') || $(e.target).hasClass('simplemodal-close');
                    if(!click){
                        self.deSelectItems();
                        self.product_menus.iconRemove();
                        self.item_menus.unSetItem();
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
        updateItemAttribute:{
            value : function(item, data){
                var self = this;
                var defaults = item.item_attribute;
                var update = $.extend({}, defaults, data);
                item.item_attribute = update;
                item.updateAppearance();
                return item.item_attribute;
            },
            enumerable: true
        },
        savingPoint:{
            value : function(uuid, action_type){
                var self = this;
                console.log(action_type + "-object: " + uuid)
                ++self.canvas_menus.current_state;
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
                        attribute = self.updateItemAttribute(self.canvas_items[selected_id], {
                            top: ui.position.top,
                            left: ui.position.left
                        });
                    },
                    stop: function(e, ui){
                        self.savingPoint(selected_id, "drag");
                    }
                }).resizable({
                    aspectRatio: true,
                    handles: 'all',
                    minWidth: 50,
                    start: function(e, ui){
                        selected = self.__ele.find('.selected');
                        selected_id = selected.attr('object-id');
                    },
                    resize : function(e, ui){
                        attribute = self.updateItemAttribute(self.canvas_items[selected_id], {
                            height: $(this).height(),
                            width: $(this).width(),
                            top : parseInt($(this).css('top')),
                            left: parseInt($(this).css('left'))
                        });
                        $('.filler', this).width(attribute.width).height(attribute.height);
                    },
                    stop: function(e, ui){
                        self.savingPoint(selected_id, "resize");
                    }
                }).rotatable({
                    matrix : true,
                    start : function(e,ui){
                        selected = self.__ele.find('.selected');
                        selected_id = selected.attr('object-id');
                    },
                    rotate : function(e, ui){
                        $('body, .handleWrap .filler').css('cursor', "url(/static/styleboard/javascripts/jquery/rotatable/rotate.png), auto");
                        var matrix = ui.matrix.current;
                        var radian = ui.radian.current;
                        var degree = ui.degree.current;
                        attribute = self.updateItemAttribute(self.canvas_items[selected_id], {
                            matrix : matrix,
                            degree : degree,
                            radian : radian
                        });
                    },
                    stop : function(e, ui){
                        $('body, .handleWrap .filler').css('cursor', "");
                        self.updateHandle(attribute.degree);
                        self.savingPoint(selected_id, "rotate");
                    }
                });
            },
            enumerable : true
        },
        showHandle : {
            value : function(selected_element){
                var self = this;
                if(self.canvas_items.hasOwnProperty(selected_element.attr('object-id'))){
                    var selected = self.canvas_items[selected_element.attr('object-id')];
                    var styles = $.extend({},selected.styles());
                    delete styles.zIndex;
                    self.__item_handle.attr('rotation',selected.item_attribute.radian);
                    self.__item_handle.attr('flip',selected.item_attribute.flip);
                    self.__item_handle.attr('flop',selected.item_attribute.flop);
                    self.__item_handle.removeClass('hidden invisible').css(styles).find('.filler').css({
                        width : selected.item_attribute.width,
                        height : selected.item_attribute.height
                    });
                    self.updateHandle(selected.item_attribute.degree);
                }else{
                    throw new Error("Error: undefined canvas item Object");
                }
            },
            enumerable : true
        },
        hideHandle : {
            value : function(){
                var self = this;
                self.__item_handle.addClass('hidden invisible');
            },
            enumerable : true
        },
        updateHandle : {
            value : function(angle){
                var handles = this.__item_handle;
                var between = function(angle, min, max){
                    return angle >= min && angle <= max;
                };
                if(between(angle, 338,359)|| between(angle, 0,22)){//1
                    handles.addClass('n').removeClass('e s w nw ne se sw');
                }else if(between(angle, 23,66)){//2
                    handles.addClass('ne').removeClass('n e s w nw se sw');
                }else if (between(angle, 67, 112)) {//3;
                    handles.addClass('e').removeClass('n s w nw ne se sw');
                }else if(between(angle, 113,157)){//4
                    handles.addClass('se').removeClass('n e s w nw ne sw');
                }else if(between(angle, 158,202)){//5
                    handles.addClass('s').removeClass('n e w nw ne se sw');
                }else if(between(angle, 203,247)){//6
                    handles.addClass('sw').removeClass('n e s w nw ne se');
                }else if(between(angle, 248,292)){//7
                    handles.addClass('w').removeClass('n e s nw ne se sw');
                }else if(between(angle, 293,337)){//8
                    handles.addClass('nw').removeClass('n e s w sw ne se');
                } 
                if(handles.hasClass('n') || handles.hasClass('e') || handles.hasClass('s') || handles.hasClass('w')){
                    handles.find('.ui-resizable-n, .ui-resizable-e, .ui-resizable-s, .ui-resizable-w').hide();
                    handles.find('.ui-resizable-nw, .ui-resizable-ne, .ui-resizable-se, .ui-resizable-sw').show();
                }else{
                    handles.find('.ui-resizable-nw, .ui-resizable-ne, .ui-resizable-se, .ui-resizable-sw').hide();
                    handles.find('.ui-resizable-n, .ui-resizable-e, .ui-resizable-s, .ui-resizable-w').show();
                }
            }
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
var product_menu = canvas.product_menus;
var item_menu = canvas.item_menus;

for(var key in product_menu.items){
    if(product_menu.items.hasOwnProperty(key)){
        product_menu.items[key].__ele.click(function(e){
            if(product_menu.selected_product != null){
                if(this.id == 'opaque'){
                    product_menu.transformOpaque(function(selected_product, action_type){

                        canvas.savingPoint(selected_product.ele.attr('object-id'),action_type);
                    });
                }else if(this.id == 'transparent'){
                    product_menu.transformTransparent(function(selected_product, action_type){

                        canvas.savingPoint(selected_product.ele.attr('object-id'),action_type);
                    });
                }else if(this.id == 'crop'){
                    product_menu.transformCrop();
                }
            }
            e.preventDefault();
        });   
    }
}

for(var key in item_menu.items){
    if(item_menu.items.hasOwnProperty(key)){
        item_menu.items[key].__ele.click(function(e){
            if(item_menu.selected_item != null){
                if(!item_menu.__ele.hasClass('disabled')){
                    if(this.id == 'info'){
                        item_menu.productInfo();
                    }else if(this.id == 'remove'){
                        item_menu.remove(function(selected_object, action_type){
                            canvas.removeCanvasItem();
                            canvas.product_menus.iconRemove();
                            canvas.item_menus.unSetItem();
                            canvas.savingPoint(selected_object.ele.attr('object-id'),action_type);
                        });
                    }else if(this.id == 'backward'){
                        item_menu.backward(function(selected_object, action_type){
                            var currentIndex = selected_object.item_attribute.zIndex;
                            var prevIndex = currentIndex - 1;
                            if(prevIndex >= 1) {
                                for(var key in canvas.canvas_items){
                                     if(canvas.canvas_items.hasOwnProperty(key)){
                                        var item = canvas.canvas_items[key];
                                        if(item.item_attribute.zIndex == prevIndex){
                                            item.item_attribute.zIndex = currentIndex;
                                            item.updateAppearance();
                                        }
                                     }
                                }
                                selected_object.item_attribute.zIndex = prevIndex;
                                selected_object.updateAppearance();
                                canvas.savingPoint(selected_object.ele.attr('object-id'),action_type);
                            }
                        });
                    }else if(this.id == 'forward'){ 
                        item_menu.forward(function(selected_object, action_type){
                            var currentIndex = selected_object.item_attribute.zIndex;
                            var nextIndex = currentIndex + 1;
                            if(nextIndex <= canvas.object_count) {
                                for(var key in canvas.canvas_items){
                                     if(canvas.canvas_items.hasOwnProperty(key)){
                                        var item = canvas.canvas_items[key];
                                        if(item.item_attribute.zIndex == nextIndex){
                                            item.item_attribute.zIndex = currentIndex;
                                            item.updateAppearance();
                                        }
                                     }
                                }
                                selected_object.item_attribute.zIndex = nextIndex;
                                selected_object.updateAppearance();
                                canvas.savingPoint(selected_object.ele.attr('object-id'), action_type);
                            }
                        });
                    }else if(this.id == 'clone'){
                        item_menu.clone(function(cloned_object, action_type){
                            var uuid = Math.uuid(12,62); 
                            cloned_object.ele.attr('object-id', uuid);
                            canvas.canvas_items[uuid] = cloned_object;
                            canvas.dropItem(uuid,e, true);
                            canvas.savingPoint(uuid, action_type);
                        });
                    }else if(this.id == 'flip'){
                        item_menu.flip(function(selected_object, action_type){
                            selected_object.toggleFlip();
                            selected_object.updateAppearance();
                            canvas.savingPoint(selected_object.ele.attr('object-id'), action_type);
                        });
                    }else if(this.id == 'flop'){
                        item_menu.flop(function(selected_object, action_type){
                            selected_object.toggleFlop();
                            selected_object.updateAppearance();
                            canvas.savingPoint(selected_object.ele.attr('object-id'), action_type);
                        });
                    }
                }
            }
            e.preventDefault();
        });   
    }
}