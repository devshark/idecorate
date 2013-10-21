var iDimageTool = (function (iDimageTool) {

    var PenPoint = function(coordinates){
        Object.defineProperties(this, {
            __ele : {
                value : $('<div class="penPoint"/>'),
                enumerable : true
            },
            __coordinates : {
                value : coordinates,
                enumerable : true
            }
        });
    };


    Object.defineProperties(PenPoint.prototype, {
        load : {
            value : function(){
                var self = this;
                self.__ele.css({left:self.__coordinates[0], top:self.__coordinates[1]});
            },
            enumerable : true
        }
    });


    var Canvas = function(element){
        Object.defineProperties(this, {
            __ele : {
                value : element,
                enumerable : true
            },
            __canvas : {
                value : $('<canvas id="tool_canvas" />'),
                enumerable : true
            },
            __pen_layers :{
                value : $('<div id="pen_layers" />'),
                enumerable : true
            },
            __stroke_pattern: {
                value : $('#stroke_pattern'),
                enumerable : true
            },
            __backgroud: {
                value : $('#canvas_background'),
                enumerable : true
            },
            __image : {
                value : null,
                writable :true,
                enumerable : true
            },
            pen_points : {
                value : $.makeArray(),
                writable :true,
                enumerable: true
            },
            coordinates : {
                value : $.makeArray(),
                writable :true,
                enumerable: true
            },
            close_path : {
                value : false,
                writable :true,
                enumerable : true
            },
            selected_pen : {
                value : null,
                writable :true,
                enumerable : true
            }
        });
    };


    var getCursorPosition = function(e) {
        var x;
        var y;
        if (e.pageX != undefined && e.pageY != undefined) {
            x = e.pageX;
            y = e.pageY;
        } else {
            x = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            y = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
        }
        return [x, y];
    };


    Object.defineProperties(Canvas.prototype,{
        load : {
            value : function(image, dimension){

                var self = this;
                self.__image = image;
                var top = dimension[1]/2 -self.__image.height()/2;
                var left = dimension[0]/2 - self.__image.width()/2;
                self.__ele.css({width: dimension[0], height: dimension[1]}).addClass('polygon');
                self.__canvas.attr({width: dimension[0], height: dimension[1]});
                self.__pen_layers.css({width: dimension[0], height: dimension[1]});

                self.append([self.__pen_layers, self.__canvas, self.__image, self.__stroke_pattern]);
                self.__image.css({top:top,left:left});

                return self.__ele;
            },
            enumerable : true
        },
        polygon : {
            get : function(){
                var self = this;
                return self.__ele.hasClass('polygon');
            },
            set: function (value) {
                var currentValue = this.polygon;
                if(currentValue === value){
                    return;
                }
                if(value){
                    this.__ele.addClass("polygon");
                } else {
                    this.__ele.removeClass("polygon");
                }
            },
            enumerable : true
        },
        append : {
            value : function(elements){
                var self = this;
                self.__ele.append(elements);
            },
            enumerable : true
        },
        drawRectangle : {
            value : function(event){
                var self = this;
                var e = event;
                var top = self.__ele.height()/2 - self.__image.height()/2;
                var left = self.__ele.width()/2 - self.__image.width()/2;
                self.addPoint([left,top]);
                self.addPoint([left+self.__image.width(),top]);
                self.addPoint([left+self.__image.width(),top+self.__image.height()]);
                self.addPoint([left,top+self.__image.height()]);
                self.closePath(e);
                self.drawLine(e);
                e.preventDefault();
            },
            enumerable : true
        },
        drawLine : {
            value : function(event){
                var self = this;
                var e = event;
                var x = getCursorPosition(e)[0] - self.__ele[0].offsetLeft;
                var y = getCursorPosition(e)[1] - self.__ele[0].offsetTop;
                var canvas = self.__canvas[0];
                var context = canvas.getContext('2d');
                // new canvas for overlay
                var mask = document.createElement('canvas');
                var maskContext = mask.getContext('2d');
                mask.width = canvas.width
                mask.height = canvas.height;
                if(e.type == "mousedown" && !self.close_path){
                    self.addPoint([x,y]);
                }else{
                    if(self.selected_pen !== null){
                        self.editPoint([x,y]);
                    }
                }
                if(self.close_path){
                    with(maskContext){
                        save();
                        beginPath();
                        rect(0, 0,canvas.width,canvas.height);
                        fillStyle = createPattern(self.__backgroud[0], "repeat");
                        fill(); 
                        globalCompositeOperation = 'xor';
                        beginPath();
                        moveTo(self.coordinates[0][0],self.coordinates[0][1]);
                        $.each(self.coordinates, function(index, value){
                            lineTo(self.coordinates[index][0],self.coordinates[index][1])
                        });
                        fillStyle = "#FFFFFF";
                        fill();
                        closePath();
                        lineWidth = 1;
                        context.clearRect(0, 0, canvas.width, canvas.height);
                        strokeStyle = createPattern(self.__stroke_pattern[0], "repeat");
                        stroke();
                        restore();
                        context.drawImage(mask, 0, 0);
                    }
                }else{
                    with(context){
                        clearRect (0, 0, canvas.width, canvas.height);
                        save();
                        beginPath();
                        if(self.coordinates.length > 1){
                            moveTo(self.coordinates[0][0],self.coordinates[0][1]);
                        }else{
                            moveTo(x,y);
                        }
                        $.each(self.coordinates, function(index, value){
                            lineTo(self.coordinates[index][0],self.coordinates[index][1])
                        });
                        lineTo(x,y);
                        lineWidth = 1;
                        strokeStyle = createPattern(self.__stroke_pattern[0], "repeat");
                        stroke();
                        restore();
                    }
                }
                e.preventDefault();
            },
            enumerable : true
        },
        addPoint : {
            value : function(coordinates){
                var self = this;
                var pen_point = new PenPoint(coordinates);
                self.pen_points.push(pen_point);
                self.coordinates.push(coordinates);
                pen_point.load();
                if(!self.close_path){
                    pen_point.__ele.appendTo(self.__pen_layers);
                }
                if(self.pen_points.length > 2){
                    self.pen_points[0].__ele.on("mousedown", function(e){
                        self.closePath(e);
                    });
                }
                if(self.pen_points.length >= 1){
                    self.__ele.on("mousemove", function(e){
                        self.drawLine(event);
                    });
                }
            },
            enumerable : true
        },
        editPoint : {
            value : function(coordinates){
                var self = this;
                if(self.polygon){
                    self.pen_points[self.selected_pen].__coordinates = coordinates;
                    self.pen_points[self.selected_pen].__ele.css({left:coordinates[0],top:coordinates[1]});
                    self.coordinates[self.selected_pen] = coordinates;
                }else{
                    /*============================================
                        [adjust_both, adjust_top, adjust_left]
                    ============================================*/
                    var corners = [[0,1,3],[1,0,2],[2,3,1],[3,2,0]];
                    var both = corners[self.selected_pen][0];
                    var top = corners[self.selected_pen][1];
                    var left = corners[self.selected_pen][2];

                    self.pen_points[both].__coordinates = coordinates;
                    self.pen_points[both].__ele.css({left:coordinates[0],top:coordinates[1]});
                    self.coordinates[both] = coordinates;
                    self.pen_points[top].__coordinates[1] = coordinates[1];
                    self.pen_points[top].__ele.css({top:coordinates[1]});
                    self.coordinates[top][1] = coordinates[1];
                    self.pen_points[left].__coordinates[0] = coordinates[0];
                    self.pen_points[left].__ele.css({left:coordinates[0]});
                    self.coordinates[left][0] = coordinates[0];
                }
            },
            enumerable : true
        },
        closePath : {
            value : function(event){
                var self = this;
                var selected = null;
                var unselect = function(){
                    if (selected !== null) {
                        selected.removeClass('move');
                        selected = null;
                        self.selected_pen = null;
                        self.__ele.off("mousemove");
                    }
                };
                self.close_path = true;
                self.drawLine(event);
                $.each(self.pen_points, function(index, value){
                    value.__ele.css('cursor', 'pointer').on("mousedown", function(e){
                        selected = $(this);
                        selected.addClass('move');
                        $(document).on("mousemove", function(e){
                            self.selected_pen = index;
                            self.drawLine(e);
                        }).on("mouseup", function(){
                            $(this).off("mousemove"); // Unbind events from document
                            unselect();
                        });
                        e.preventDefault(); // disable selection
                    }).on("mouseup", function(){
                        unselect();
                    });
                });
            },
            enumerable: true
        },
        clear : {
            value : function(event){
                var self = this;
                var canvas = self.__canvas[0];
                var context = canvas.getContext('2d');
                with(context){
                    clearRect (0, 0, canvas.width, canvas.height);
                    save();
                    restore();
                }
                self.close_path = false;
                self.pen_points = $.makeArray();
                self.coordinates = $.makeArray();
                self.__pen_layers.children().remove();
            },
            enumerable: true
        }
    });


    var createCanvas = function(element){

        var element = ($(element).length < 1) ? $('<div id="'+element.replace(/^[\#]/g, '')+'"/>') : $(element);
        element.addClass('iDCanvas');

        var canvas = new Canvas(element);

        return canvas;
    };

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
                var self = this;
                var defaults = {
                    content : "",
                    link : "#",
                    subClass : false,
                    wrap : false,
                    click : false
                };
                var options = $.extend(defaults, options);
                var anchor = $("<a/>");
                var uuid = Math.uuid(12, 62);
                anchor.addClass("toolbarItem");
                anchor.attr("object-id", uuid);
                anchor.html(options.content);
                anchor.attr("href",options.link);
                if(options.subClass) anchor.addClass(options.subClass); 
                if(options.wrap){
                    var wrap = document.createElement(options.wrap);
                    anchor.appendTo($(wrap));
                    self.append($(wrap));
                }else{
                    self.append(anchor);
                }
                var item = new ToolbarItem(anchor);
                self.items[uuid] = item;
                item.__ele.on("click", function(e){
                    if(typeof options.click === "function"){
                        options.click.apply(self,[this, e]);
                    }
                    e.preventDefault();
                });
                return item;
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
        },
        append : {
            value : function(elements){
                this.__ele.append(elements);
            },
            enumerable : true
        }
    });


    var createPenToolbar = function(element){
        var element = ($(element).length < 1) ? $('<ul id="'+element.replace(/^[\#]/g, '')+'"/>') : $(element);
        element.addClass('iDPenTool');
        var pen_tool =  new Toolbar(element);
        return pen_tool;
    };


    var createOperationToolbar = function(element){
        var element = ($(element).length < 1) ? $('<ul id="'+element.replace(/^[\#]/g, '')+'"/>') : $(element);
        element.addClass('iDOperationTool');
        var operation_tool =  new Toolbar(element);
        return operation_tool;
    };


    var ImageTool = function(element){
        Object.defineProperties(this, {
            __ele: {
                value: element
            },
            canvas: {
                value: createCanvas('#outer_canvas'),
                enumerable: true
            },
            pen_tool: {
                value: createPenToolbar('#pen_tools'),
                enumerable: true
            },
            operation_tool: {
                value: createOperationToolbar('#operation_tools'),
                enumerable: true
            }
        });
    };


    Object.defineProperties(ImageTool.prototype, {
        load : {
            value : function(image, dimension){
                var self = this;
                var canvas = self.canvas.load(image, dimension);
                self.__ele.css({width : canvas.width()});
                self.append([self.pen_tool.__ele,canvas, self.operation_tool.__ele]);
            },
            enumerable : true
        },
        append : {
            value : function(elements){
                var self = this;
                self.__ele.append(elements);
            },
            enumerable : true
        }
    });

    iDimageTool.createImageTool = function(element_id){

        var element = ($(element_id).length < 1) ? $('<div id="'+element_id.replace(/^[\#]/g, '')+'"/>') : $(element_id);
        element.addClass('iDimageTool');

        var imageTool = new ImageTool(element);

        return imageTool;
    };

    return iDimageTool;

}(iDimageTool || {}));
