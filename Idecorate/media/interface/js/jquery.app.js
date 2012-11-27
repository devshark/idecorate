$handles   = $('.handles');
$img_menus = $('.neMenus');
objCounter = 0;
lassoStart = false;
lassoCoordinate = {startX: 0, startY: 0};
uniqueIdentifier = 1;
changesCounter = 0;
changesArray = [];
changesCurrentPosition = 0;
var handles = 'ne,se,nw,sw,n,e,s,w';
var aspectR = true;
var slideValue = 0;

$(document).ready(function () {
    //init lasso
    $('<div id="lasso"></div>').appendTo('#canvas');
    $('#canvas').attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);
    
    //remove edit button on buy tab
    $(window).hashchange( function(){
        
        if(location.hash == '#buy-tab'){
            $('#sidebar-form-wrap .myorder-edit').hide();
        }else if(location.hash == '#create-tab'){
            $('#sidebar-form-wrap .myorder-edit').show();
        }
    });
    
    $(window).hashchange();

    //draggable sidebar obj to canvas
    $(".draggable").liveDraggable({
        revert:true, 
        helper: 'clone',
        containment: 'body'
    });


    //get the maxheight sidebar name <span> and set as global
    //height for all name container <span> on the sidebar
    
    //set dropable area for the draggable sidebar objects
    $("#canvas").droppable({

        drop: function (e, ui) {

            if ($(ui.draggable)[0].id != "") {

                ui.helper.remove();
                //recreate an object based on dropped object
                var Obj = $(ui.draggable)[0];

                //set this oject to jquery
                Obj = $(Obj);

                if(Obj.hasClass('products')){
                    //custom attribute uid is a refference to populate new image 
                    var uid = Obj.attr('_uid');

                    //image source can be generated using ajax 

                    var _img_src = media_url+'products/';
                    var p_d_qty = 1;
                    var p_g_t = 'table';

                    //get image filename from DB using product_id via ajax
                    $.ajax({
                        url: PRODUCT_IMAGE_URL,
                        type: "POST",
                        data: { product_id: uid},
                        async:   false,
                        success: function(data){
                            //original
                            img_src     = '/'+_img_src+data.original_image;
                            img_w       = data.original_image_w;
                            img_h       = data.original_image_h;
                            img_w_bg    = data.original_image;
                            img_wo_bg   = data.no_background;
                            p_d_qty     = data.default_quantity;
                            p_g_t       = data.guest_table;

                            //create new image using image object
                            var newObj = create_instance({
                                        _uid     : uid,
                                        _event   : e,
                                        _src     : img_src,
                                        _img_wo_b: img_wo_bg,
                                        _img_w_b : img_w_bg,
                                        _width   : img_w,
                                        _height  : img_h,
                                        _p_d_qty : p_d_qty,
                                        _p_g_t   : p_g_t
                                    });
                        },
                        error: function(msg) {
                            alert(msg);
                        }
                    });

                    //ajax add to cart
                    add_to_cart(uid, p_d_qty, p_g_t);

                }else if(Obj.hasClass('em')){

                    var em_id = Obj.attr('id');
                    var em_dbID = em_id.split('-');
                    var type = Obj.attr('_type');

                    object = create_instance_embellishments(em_dbID[1],e,type);

                }

            }
        }
    });

    $("#canvas").mousemove(function(e){
        e.preventDefault();
        if(lassoStart && $('.selected').length == 0) {
            var x = e.pageX - $(this).offset().left;
            var y = e.pageY - $(this).offset().top;

            var lassoLeft = 0;
            var lassoTop = 0;
            var lassoWidth = 0;
            var lassoHeight = 0;

            if(x > lassoCoordinate.startX) {
                lassoLeft = lassoCoordinate.startX;
                lassoWidth = x - lassoCoordinate.startX;
            } else {
                lassoLeft = x;
                lassoWidth = lassoCoordinate.startX - x;
            }

            if(y > lassoCoordinate.startY) {
                lassoTop = lassoCoordinate.startY;
                lassoHeight = y - lassoCoordinate.startY;
            }else {
                lassoTop = y;
                lassoHeight = lassoCoordinate.startY - y;
            }

            $('#lasso').css('display', 'block'); 
            $('#lasso').css({'left':lassoLeft, 'top':lassoTop});
            $('#lasso').width(lassoWidth);
            $('#lasso').height(lassoHeight);
        }
    }).mousedown(function(e){
        if($('.selected').length == 0) {

            var x = e.pageX - $(this).offset().left;
            var y = e.pageY - $(this).offset().top;
            lassoCoordinate.startX = x;
            lassoCoordinate.startY = y;
            lassoStart = true;   
        }
    }).mouseup(function(e){
        lassoStart = false;
        var x = e.pageX - $(this).offset().left;
        var y = e.pageY - $(this).offset().top;
        lassoCoordinate.startX = 0;
        lassoCoordinate.startY = 0;
        $('#lasso').width(0);
        $('#lasso').height(0);
        $('#lasso').css('display', 'none');
    });

    //drag the selected product together with its handle on the fly
    $('.unselected').liveDraggable({
        helper: 'original',
        cursor: 'move',
        containment: '#canvas',
        start : function(e, ui){
            
            transform($(this));
        },
        drag : function(e, ui){
            
            transform($(this));
        },
        stop : function(e, ui){
            
            transform($(this));

            //set center coordinated for rotate plugin
            set_ctr_attr($(this));

            //track event
            eventTracker($(this),'move');

        }
    });

    //onmouse down show handles for selected product
    if($.browser.msie){
        var handled = false;
        $('#canvas').on('mousedown','.unselected',function(e){

            if($(this).hasClass('embellishment')){
                update_menu($(this).find('img'), true);
            }else{
                update_menu($(this).find('img'));
            }

            if(!$(this).hasClass('selected')){

                $(this).addClass('selected').siblings().removeClass('selected');

                transform($(this));

                //set center coordinated for rotate plugin
                set_ctr_attr($('.selected'));
            }
            
            handled = true; 
            $(document).unbind('click');

        }).mouseup(function(e){
            if(!handled){
                $(document).click(function(e){
                    remove_handles(e);
                    eventTracker(e.target, 'unselect');
                });
            }else{
                setTimeout(function(){
                    $(document).click(function(e){
                        remove_handles(e);
                        eventTracker(e.target, 'unselect');
                    });
                }, 300)
            }
            handled = false;
        });

        $handles.on('click mousedown','.ui-resizable-handle, ui-rotatable-handle, .ui-rotatable-handle-tip',function(e){
            handled = true; 
            $(document).unbind('click');
        }).mouseup(function(e){
            if(!handled){
                $(document).click(function(e){
                    remove_handles(e);
                    eventTracker(e.target, 'unselect');
                });
            }else{
                setTimeout(function(){
                    $(document).click(function(e){
                        remove_handles(e);
                        eventTracker(e.target, 'unselect');
                    });
                }, 300)
            }
            handled = false;
        });

    }else{
        $('#canvas').on('mousedown','.unselected',function(e){

            if($(this).hasClass('embellishment')){
                update_menu($(this).find('img'), true);
            }else{
                update_menu($(this).find('img'));
            }

            if(!$(this).hasClass('selected')){

                $(this).addClass('selected').siblings().removeClass('selected');

                transform($('.selected'));
                
                //set center coordinated for rotate plugin
                set_ctr_attr($('.selected'));
            }
            cancelBubble(e);

        });
    }

    //draggable handles binds style on selected obj
    if($.browser.msie && $.browser.version < 9.0){//while IE is not yet supported
        handles = 'ne,se,nw,sw';
    }

    $handles.draggable({
        helper: 'original',
        cursor: 'move',
        containment:'#canvas',
        start: function(e, ui){

            transform($(this));

        },
        drag: function(e, ui){

            transform($(this));

        },
        stop: function(e, ui){

            transform($(this));
            //track event
            eventTracker($('.selected'),'move');

            //set center coordinated for rotate plugin
            set_ctr_attr($(this));
        }
    }).resizable({
        handles: handles,
        minWidth: 50,
        aspectRatio: aspectR,
        start : function(e, ui){
            
        },
        resize: function(e, ui){
            
            transform($(this));
        },
        stop : function(e, ui){
            //set center coordinated for rotate plugin
            set_ctr_attr($(this));

            //track event
            eventTracker($('.selected'),'resize');

        }
    }).rotatable({rotateAlso:'.selected'});

    //hide handles and menus
    $(document).click(function(e){
        var click =  $.contains($('#canvas .handles, #canvas .handles .handle')[0],e.target) ? true : e.target == $('#canvas .handles');
        
        if(!click){
            remove_handles(e);
            eventTracker(e.target, 'unselect');
        }

    }).keydown(function(e){
        
        if(!$.browser.mozilla) {
            if((e.keyCode == 8 || e.keyCode == 46) && $('.selected').length > 0) {
                e.preventDefault();
                $('#remove-btn').trigger('click');
            }
        }
    });

    //REMOVE PRODUCT IN FIREFOX
    $('html').keypress(function(e){

        if($.browser.mozilla) {
            if((e.keyCode == 8 || e.keyCode == 46) && $('.selected').length > 0) {
                e.preventDefault();
                $('#remove-btn').trigger('click');
                return false;
            }
        }

    });

    //remove selected obj
    $('#remove-btn').click(function(e){
        e.preventDefault();
        objCounter--;
        updateZIndex($('.selected'));
        
        var selected_uid = $('.product.selected').attr('_uid');
        var count = 0;
        $('.product.unselected').each(function(){
            if (selected_uid == $(this).attr('_uid'))
                count++;
        });

        if (count<=1 && selected_uid != undefined)
            remove_from_cart(parseInt(selected_uid,10));

        var removedElement = $('.selected');

        $('.selected').remove();

        eventTracker(removedElement,'remove');

        //show or hide upper left menu of canvas;
        hide_canvas_menu();
    });

    $('#flip-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        flip($('.selected'));
    });

    $('#flap-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        flap($('.selected'));
    });

    //forward selected obj
    $('#forward-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        obj = $('.selected');
        moveNext(obj);
    });

    //backward selected obj
    $('#backward-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        obj = $('.selected');
        moveBack(obj);
    });

    //clone selected obj
    $('#clone-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        //show or hide upper left menu of canvas;
        hide_canvas_menu();
        obj = $('.selected');
        cloneObj(obj);
    });

    //make selected product image PNG
    $('#transBg-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        if($('.selected').length == 1){change_img($('.selected'),false);}

    });

    //make selected product image JPG
    $('#whiteBg-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);

        if($('.selected').length == 1){change_img($('.selected'),true);}

    });

    // create custom image crop
    $('#customBg-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        display_modal(MODAL_SRC.replace('0',$('.selected > img').attr('src').replace('/media/products/','')));
    });

    // close modal
    $('#close-modal').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        close_modal();
    });

    //dont remove handles and selected object when modal window is displayed
    $('#modal-window, #page-mask').click(function(e){
        cancelBubble(e);
    });

    //create new canvas remove session and products
    $('#new').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        new_canvas($(this).attr('href'));
    });

    initProductPositions();

    $('#redo').click(function(e){
        e.preventDefault();
        //show or hide upper left menu of canvas;
        hide_canvas_menu();
        redo_styleboard();
    });

    $('#undo').click(function(e){
        e.preventDefault();
        //show or hide upper left menu of canvas;
        hide_canvas_menu();
        undo_styleboard();
    });

    /*  
    embellishments
    this is where embellishment related function calls
    starts as well as with the inits,events,variables
    */

    $('#colorPicker').ColorPicker({
        color: '#000000',
        onShow: function (colpkr) {
            $(colpkr).fadeIn(500);
            return false;
        },
        onHide: function (colpkr) {
            $(colpkr).fadeOut(500);
            return false;
        },
        onChange: function (hsb,hex,rgb) {
            $('#colorPicker div').css('backgroundColor', '#' + hex);
        },
        onSubmit: function(hsb,hex,rgb){
            $('.colorpicker').fadeOut(500);
            var object = $('.selected').find('img');
            change_color(object,rgb);
            return false;
        }
    });

    $('.colorpicker').click(function(e){
        cancelBubble(e);
    });
    if(!$.browser.msie){
        $( "#slider" ).slider({
            range: "max",
            min: 1,
            max: 100,
            value: slideValue,
            slide: function( event, ui ) {
                $('.selected img').css({
                    'zoom': 1,
                    'opacity' : ui.value*0.01,
                    'filter': 'alpha(opacity='+ui.value+')'
                });
                $('.selected').attr('_opacity',ui.value);
                eventTracker($('.selected'), 'set_opacity');
            }
        });

        $('#canvas').on('click mousedown', '.embellishment.shape,.embellishment.pattern,.embellishment.text,.embellishment.texture', function(e){
            cancelBubble(e);
            slideValue = parseInt($(this).attr('_opacity'));
            embellishment_handle_set(slideValue);
        });
    }else{
        $('#opacity-control-wrap').hide();
        if($.browser.version >= 9.0){
            $( "#slider" ).slider({
                range: "max",
                min: 1,
                max: 100,
                value: slideValue,
                slide: function( event, ui ) {
                    $('.selected img').css({
                        'zoom': 1,
                        'opacity' : ui.value*0.01,
                        'filter': 'alpha(opacity='+ui.value+')'
                    });
                    $('.selected').attr('_opacity',ui.value);
                    eventTracker($('.selected'), 'set_opacity');
                }
            });

            $('#canvas').on('click mousedown', '.embellishment.shape,.embellishment.pattern,.embellishment.text,.embellishment.texture', function(e){
                cancelBubble(e);
                slideValue = parseInt($(this).attr('_opacity'));
                embellishment_handle_set(slideValue);
            });
        }
    }

    //show or hide upper left menu of canvas;
    hide_canvas_menu();

});



//embelishments functions start
function create_instance_embellishments(em_dbID,event,type){

    //GLOBAL var objCounter is for setting z-index for each created instance
    objCounter++;

    var object = $('<div/>');
    object.attr({
        '_uid': em_dbID,
        'class': type.toLowerCase()+' embellishment unselected'
    }).css({
        zIndex : objCounter,
        position: 'absolute',
        left: '-5000px'
    });

    var obj_image   = $('<img/>');
    var imgWidth    = 0;
    var imgHeight   = 0;

    obj_image.attr({
        'src': '/generate_embellishment/?embellishment_id='+em_dbID+'&embellishment_color=000000000&embellishment_thumbnail=0'
    }).css({
        width: '100%',
        height: 'auto'
    });

    obj_image.load(function(){
        
        imgWidth = obj_image.width();
        imgHeight = obj_image.height();
        var dimensions  = aspectratio(imgWidth, imgHeight, .80);
        var imgTop      = event.pageY-$('#canvas').offset().top-dimensions['height']/2;
        var imgLeft     = event.pageX-$('#canvas').offset().left-dimensions['width']/2;

        object.css({
            left:imgLeft,
            top:imgTop,
            width:dimensions['width'],
            height:dimensions['height']
        });

        set_ctr_attr(object);

        transform(object);

        eventTracker(object, 'create_embellishment');

    }).appendTo(object);
    
    object.appendTo('#canvas');

    if(!object.hasClass('selected')){
        object.addClass('selected').siblings('.unselected').removeClass('selected');
        object.attr('_matrix', '{"a":1, "b":0, "c":0, "d":1,"e":false,"f":false}');
        object.attr('_handle', ['nw','sw','se','ne','w','s','e','n']);
        if(type.toLowerCase() == 'shape' || type.toLowerCase() == 'texture' || type.toLowerCase() == 'text' || type.toLowerCase() == 'pattern'){
            object.attr('_opacity', 100);
            $( "#slider" ).slider({value:100});
        }
        slideValue = 100;
        embellishment_handle_set(slideValue);
    }
    update_menu(object,true);
    hide_canvas_menu();

    return object;
}

function change_color(object,rgb){
    var selected        = object.parent()
    var default_style   = object.attr('style');
    var object_dbID     = selected.attr('_uid');
    var new_img         = $('<img/>');
    var new_obj_src     = '/generate_embellishment/?embellishment_id='+object_dbID+'&embellishment_color='+$.strPad(rgb.r,3)+$.strPad(rgb.g,3)+$.strPad(rgb.b,3)+'&embellishment_thumbnail=0'
    object.remove();//remove old object
    new_img.attr({//append new object
        'src': new_obj_src,
        'style': default_style
    }).appendTo(selected);

    eventTracker(new_img, 'change_color');
}

function embellishment_handle_set(slideValue){
    $( "#slider" ).slider({value:slideValue});
    if($('.selected').hasClass('shape') || $('.selected').hasClass('texture') || $('.selected').hasClass('pattern') || $('.selected').hasClass('text')){
        $handles.resizable({aspectRatio:false});
        $('.selected img').height('100%');
    }else{
        $handles.resizable({aspectRatio:true});
    }
}
//embelishments functions end


//product functions start
function create_instance(options){
    var Obj_img = $('<img />').attr({'src':options._src+ "?" + new Date().getTime(),'_nb':options._img_wo_b,'_wb':options._img_w_b}).hide().load(function () {
        var imgWidth    = options._width;
        var imgHeight   = options._height;
        var dimensions  = aspectratio(imgWidth, imgHeight, .60);
        var imgTop      = options._event.pageY-$('#canvas').offset().top-dimensions['height']/2;
        var imgLeft     = options._event.pageX-$('#canvas').offset().left-dimensions['width']/2;

        //create instance of this object
        object = create_new_object({
                id          : options._uid,
                img         : this,
                imgW        : dimensions['width'],
                imgH        : dimensions['height'],
                def_qty     : options._p_d_qty,
                gst_tb      : options._p_g_t,
                container   : $('<div />'),
                addclass    : 'product unselected'
            });

        //show menus
        update_menu($(this));
        
        $('.selected').removeClass('selected');
        var fakeObj = $('<div/>').css({top:imgTop,left:imgLeft,width:dimensions['width'],height:dimensions['height']})
        transform(fakeObj);

        //append to canvas the newly created instance
        setTimeout(function(){
            append_to_canvas(options._event,object,objCounter,imgTop,imgLeft);
        },500);

        //GLOBAL var objCounter is for setting z-index for each created instance
        objCounter++;

    }).fadeIn(1000, function(e){
        //track event
        eventTracker(object,'create');        
    });

}

function create_new_object(options){

    object = options.container;
    object.addClass(options.addclass);
    object.attr('_uid', options.id);
    object.attr('def_qty', options.def_qty);
    object.attr('gst_tb', options.gst_tb);
    object.append(options.img).width(options.imgW).height(options.imgH);
    object.find('img').width('100%').height('auto');

    if(!object.hasClass('selected')){object.addClass('selected');}
    
    return object;
}

function append_to_canvas(event, obj, index, top, left){

    object = obj;
    object.appendTo('#canvas');
    object_top = top;
    object_left = left;
    object.css({top : object_top, left: object_left, zIndex: index });
    object.attr({'object_id':uniqueIdentifier});
    
    uniqueIdentifier++;
    if(object.hasClass('selected')){
        object.siblings('.unselected').removeClass('selected');
        object.attr('_matrix', '{"a":1, "b":0, "c":0, "d":1,"e":false,"f":false}');
        object.attr('_handle', ['nw','sw','se','ne','w','s','e','n']);
        set_ctr_attr(object);
    }

    //show or hide upper left menu of canvas;
    hide_canvas_menu();

    return object;
}

function flip(obj){ //e
    m = $.parseJSON(obj.attr('_matrix'));
    m.b = m.b>0 || m.b<0 ? (m.b*-1) : m.b;
    var matrix = 'matrix('+ m.a +', '+m.b+', '+ m.c +', '+ (m.d*-1) +', 0, 0)',
        ie_matrix = "progid:DXImageTransform.Microsoft.Matrix(M11='"+(m.a*-1)+"', M12='"+m.b+"', M21='"+m.c+"', M22='"+(m.d*-1)+"', sizingMethod='auto expand')";         

    if($.browser.msie && $.browser.version == 9.0) {
        $('.handles, .selected').css({
            '-ms-transform'    : matrix
        });
    }else if($.browser.msie && $.browser.version < 9.0){
        $('.handles, .selected').css({
            'filter'           : ie_matrix,
            '-ms-filter'       : '"' + ie_matrix + '"'
        });
    }else{
        $('.handles, .selected').css({
            '-moz-transform'   : matrix,
            '-o-transform'     : matrix,
            '-webkit-transform': matrix,
            'transform'        : matrix
        });
    }

    obj.attr('_matrix','{"a":'+m.a+',"b":'+m.b+',"c":'+m.c+',"d":'+(m.d*-1)+',"e":'+!m.e+',"f":'+m.f+'}');

    obj.attr('_handle',change_cursor(obj.attr('_handle')));

    eventTracker(obj,'flip');
}


function flap(obj){ //f
    m = $.parseJSON(obj.attr('_matrix'));
    m.c = m.c<0 || m.c>0? (m.c*-1) : m.c;
    var matrix = 'matrix('+(m.a*-1)+', '+m.b +', '+m.c+', '+ m.d +', 0, 0)',
        ie_matrix = "progid:DXImageTransform.Microsoft.Matrix(M11='"+m.a+"', M12='"+(m.b*-1)+"', M21='"+(m.c*-1)+"', M22='"+m.d+"', sizingMethod='auto expand')";         

    if($.browser.msie && $.browser.version == 9.0) {
        $('.handles, .selected').css({
            '-ms-transform'    : matrix
        });
    }else if($.browser.msie && $.browser.version < 9.0){
        $('.handles, .selected').css({
            'filter'           : ie_matrix,
            '-ms-filter'       : '"' + ie_matrix + '"'
        });
    }else{
        $('.handles, .selected').css({
            '-moz-transform'   : matrix,
            '-o-transform'     : matrix,
            '-webkit-transform': matrix,
            'transform'        : matrix
        });
    }

    obj.attr('_matrix','{"a":'+(m.a*-1)+',"b":'+m.b+',"c":'+m.c+',"d":'+m.d+',"e":'+m.e+',"f":'+!m.f+'}');
    
    obj.attr('_handle',change_cursor(obj.attr('_handle')));

    eventTracker(obj,'flap');
}

function set_ctr_attr(obj){

    x = parseFloat(parseFloat(obj.offset().left + obj.width() * 0.5));
    y = parseFloat(parseFloat(obj.offset().top + obj.height() * 0.5));
    if($.browser.msie && $.browser.version < 9.0){

    }
    $handles.attr({'ctr':'{"x":'+x+',"y":'+y+'}'});
    //$('.selected').attr({'ctr':'{"x":'+x+',"y":'+y+'}'});
}

function aspectratio(width, height, percent){

    var dimension = new Array();
    var aspectRatio = height/width;
    dimension['width'] = width*percent;
    dimension['height'] = aspectRatio*dimension['width'];

    return dimension;
}

function remove_handles(event){

    if(event.target != $('.handles')[0]){
    
        $handles.css('display','none');
        $img_menus.css('display','none');
        if($('.unselected').hasClass('selected')){
            $('.unselected').removeClass('selected');
            return true;
        }
    
    }
}

function update_menu(obj,img_menu){

    img_menu = img_menu ? img_menu : false;
    
    $img_menus.show();

    if(img_menu){
        $('.imgBgControlWrap').hide();
        if(obj.hasClass('image') || obj.parent().hasClass('image') || obj.parent().hasClass('border') || obj.hasClass('border')){
            $('.colorAdjustment').hide();
        }else{
            $('.colorAdjustment').show();
        }
    }else{
        $('.imgBgControlWrap').show();
        $('.colorAdjustment').hide();
    }

    var _src        = '/'+media_url+'products/';
    var wo_bg_img   = obj.attr('_nb');
    var w_bg_img    = obj.attr('_wb');

    $('#whiteBg-btn').css({
        'background-image':"url("+_src+w_bg_img+")",
        'background-size':'contain',
        'filter': 'progid:DXImageTransform.Microsoft.AlphaImageLoader(src="'+_src+w_bg_img+'",sizingMethod="scale")',
        '-ms-filter': 'progid:DXImageTransform.Microsoft.AlphaImageLoader(src="'+_src+w_bg_img+'",sizingMethod="scale")'
    });

    $('#customBg-btn').css({
        'background-image':"url("+_src+w_bg_img+")",
        'background-size':'contain',
        'filter': 'progid:DXImageTransform.Microsoft.AlphaImageLoader(src="'+_src+w_bg_img+'",sizingMethod="scale")',
        '-ms-filter': 'progid:DXImageTransform.Microsoft.AlphaImageLoader(src="'+_src+w_bg_img+'",sizingMethod="scale")'
    });

    $('#transBg-btn div').css({
        'background-image':"url("+_src+wo_bg_img+")",
        'background-size':'contain',
        'filter': 'progid:DXImageTransform.Microsoft.AlphaImageLoader(src="'+_src+wo_bg_img+'",sizingMethod="scale")',
        '-ms-filter': 'progid:DXImageTransform.Microsoft.AlphaImageLoader(src="'+_src+wo_bg_img+'",sizingMethod="scale")'
    });

}

function transform(obj) {
    selected_zIndex = $('.selected').css('z-index');
    $('.selected').attr('style',obj.attr('style')).css({'z-index':selected_zIndex});
    $handles.attr('style',obj.attr('style')).css({'z-index':'','display':'block'});
    $('.fakeHandle').attr('style',obj.attr('style')).css({
        zIndex:'',
        top: '', 
        left: '',
        display: '',
        position: '',
        '-moz-transform'   : '',
        '-o-transform'     : '',
        '-webkit-transform': '',
        '-ms-transform'    : '',
        'transform'        : '',
        'filter'           : '',
        '-ms-filter'       : ''
    });
}

function moveNext(obj) {
        
    var currentZIndex = parseInt(obj.css('z-index'));
    var nextIndex = currentZIndex + 1;

    if(nextIndex > objCounter) {
        //cannot move
    } else {
        $('.unselected').each(function(e){
            if(parseInt($(this).css('z-index')) == nextIndex) {
                $(this).css('z-index', (parseInt($(this).css('z-index')) - 1));
            }
        });

        obj.css('z-index', nextIndex);
        eventTracker(obj, 'forward');
    }

}

function moveBack(obj) {

    var currentZIndex = parseInt(obj.css('z-index'));
    var backIndex = currentZIndex - 1;

    if(backIndex < 1) {
        //cannot move
    } else {
        $('.unselected').each(function(e){
            if(parseInt($(this).css('z-index')) == backIndex) {
                $(this).css('z-index', (parseInt($(this).css('z-index')) + 1));
            }
        });

        obj.css('z-index', backIndex);
        eventTracker(obj, 'backward');
    }   
     
}

function updateZIndex(obj) {

    var currentZIndex = parseInt(obj.css('z-index'));

    $('.unselected').each(function(e){
        if(parseInt($(this).css('z-index')) > currentZIndex) {
            $(this).css('z-index', (parseInt($(this).css('z-index')) - 1));
        }
    });
}

function cloneObj(obj) {

    var cloned_obj = obj.clone().appendTo('#canvas');
    objCounter++;

    cloned_obj.siblings('.unselected').removeClass('selected');
    cloned_obj.css({
        zIndex : objCounter,
        top : parseInt(obj.css('top'),10)+20,
        left : parseInt(obj.css('left'),10)+20
    });

    cloned_obj.attr('object_id',uniqueIdentifier);

    uniqueIdentifier++;

    if(cloned_obj.hasClass('embellishment')){
        update_menu(cloned_obj.find('img'), true);
    }else{
        update_menu(cloned_obj.find('img'));
    }

    transform(cloned_obj);

    //track event
    eventTracker(cloned_obj, 'clone');
}

function eventTracker(currentObject, eventType) {
    //console.log(eventType);
    if(eventType != 'unselect' && eventType != 'undo' && eventType != 'redo') {

        var product_objects = '';
        var embellishment_objects = '';

        var clonedObject = $('.product.unselected').clone();
        var clonedObject2 = $('.embellishment.unselected').clone();

        clonedObject.each(function(e){
            $(this).removeClass('selected');
            product_objects += $(this).prop('outerHTML');

        });

        clonedObject2.each(function(e){
            $(this).removeClass('selected');
            embellishment_objects += $(this).prop('outerHTML');

        });

        var cloned_table = $('.table').clone();

        $('.dynamic_qty').each(function(e){

            var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
            cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

        });

        if(changesCounter != (changesArray.length - 1)) {
            changesArray.splice(changesCounter + 1, changesArray.length - changesCounter);
        }

        changesArray.push({ guests: $('#guests').val(),tables: $('#tables').val(), buy_table_html: cloned_table.html(),action_url: action_url, total: total, quantity: quantity, selected_prev_prod_qty: selected_prev_prod_qty, obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects });
        changesCounter++;
    }

    setProductPositions();
}

function change_img(obj, background){

    var _src    = obj.find('img').attr('src');
    var _nb     = obj.find('img').attr('_nb');
    var _wb     = obj.find('img').attr('_wb');
    var _style  = obj.find('img').attr('style');
    var __src   = (background == false) ? '/'+media_url+'products/'+_nb : '/'+media_url+'products/'+_wb;

    var _img    = $('<img />').attr({'src':__src, 'style': _style, '_wb':_wb, '_nb':_nb});
    
    obj.html(_img);
    eventTracker(obj,'change_background');
}

function display_modal(iframe_src){
    var iframe  = $('<iframe />').attr({'class':'modalIframe','id':'modal-iframe','src':iframe_src});
    var modal   = $('#modal-window'),
        _left   = $(window).width()/2-modal.width()/2,
        frame   = $('#iframe-wrap').append(iframe);

    $('#page-mask').css({display:'block'});
    modal.append(frame).css({display:'block',left:_left});

}

function close_modal(){
    $('#page-mask').css({display:'none'});
    $('#modal-window iframe').remove();
    $('#modal-window').css({display:'none'});
}

function get_product_object_json(){
    var product_objects = [];
    var canvas_offset = $('#canvas').offset();
    var canvas_left = canvas_offset.left;
    var canvas_top = canvas_offset.top;
    $('.product.unselected').each(function(e){
        var elm = $(this);
        var elm_offset = elm.offset();
        var elm_left = elm_offset.left;
        var elm_top = elm_offset.top;
        var product_left = Math.round(elm_left-canvas_left);
        var product_top = Math.round(elm_top-canvas_top);
        var style = $(this).attr('style');
        var _zindex = $(this).css('z-index');
        var _matrix = $(this).attr('_matrix');
        var _img = [];
        var elm_img = $(this).find('img');
        var _src = $(elm_img).attr('src');
        var _nb = $(elm_img).attr('_nb');
        var _wb = $(elm_img).attr('_wb');
        var _handle = $(this).attr('_handle');
        var _uid = $(this).attr('_uid');
        var _def_qty = $(this).attr('def_qty');
        var _gst_tb = $(this).attr('gst_tb');
        var _angle = $(this).attr('_angle');
        _img.push({ src:_src, nb:_nb, wb:_wb, style:$(elm_img).attr('style') });
        product_objects.push({uid:_uid, def_qty:_def_qty, gst_tb:_gst_tb, left:product_left,top:product_top,style:style,matrix:_matrix,zindex:_zindex,handle:_handle, angle:_angle,img:_img});
    });
    var product_array = new Array();
    for (var i in product_objects){
        var x = product_objects[i].zindex;
        //product_objects[x] = product_objects[i];
        product_array[x-1] = product_objects[i];
    }    
    keys(product_array).sort();
    return product_array;
}

function keys(obj){
    var keys = [];
    for(var key in obj)
    {
        if(obj.hasOwnProperty(key))
        {
            keys.push(key);
        }
    }
    return keys;
}

function setProductPositions(func) {

    var product_objects = '';
    var embellishment_objects = '';

    var clonedObject = $('.product.unselected').clone();
    var clonedObject2 = $('.embellishment.unselected').clone();

    clonedObject.each(function(e){
        $(this).removeClass('selected');
        product_objects += $(this).prop('outerHTML');

    });

    clonedObject2.each(function(e){
        $(this).removeClass('selected');
        embellishment_objects += $(this).prop('outerHTML');

    });

    var cloned_table = $('.table').clone();

    $('.dynamic_qty').each(function(e){

        var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
        cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

    });

    $.ajax({
        url: SET_PRODUCT_POSITION_URL,
        type: "POST",
        data: { guests: $('#guests').val(),tables: $('#tables').val(), buy_table_html: cloned_table.html(),action_url: action_url, total: total, quantity: quantity, selected_prev_prod_qty: selected_prev_prod_qty, obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects },
        beforeSend : function(){
            
        },
        success: function(response_data){
            if(typeof func != "undefined") {
                func();
            }
        },
        error: function(msg) {
        }
    });
}

function closeModalForm() {
    $('#close-modal').trigger('click');
}

function setSelectedImage(imgName) {
    $('.selected > img').attr('src',imgName);

    var _nb = $('.selected > img').attr('_nb');
    var _wb = $('.selected > img').attr('_wb');
    var style = $('.selected > img').attr('style');

    $('.selected').html('<img src="' + imgName + '" _nb="' + _nb + '" _wb="' + _wb + '" style="' + style + '" />');


    closeModalForm();
    eventTracker($('.selected'),'crop');
}

function initProductPositions() {
    if(PRODUCT_POSITIONS != '') {
        uniqueIdentifier = parseInt(PRODUCT_POSITIONS['unique_identifier']);
        objCounter = parseInt(PRODUCT_POSITIONS['obj_counter']);
        changesCounter = parseInt(PRODUCT_POSITIONS['changes_counter']);
        action_url = PRODUCT_POSITIONS['action_url'];
        total = parseFloat(PRODUCT_POSITIONS['total']);
        quantity = parseInt(PRODUCT_POSITIONS['quantity']);
        selected_prev_prod_qty = parseInt(PRODUCT_POSITIONS['selected_prev_prod_qty']);

        $('#canvas').append(PRODUCT_POSITIONS['product_objects']);
        $('#canvas').append(PRODUCT_POSITIONS['embellishment_objects']);

        $('.table').html(PRODUCT_POSITIONS['buy_table_html']);
        $('#tables').val(PRODUCT_POSITIONS['tables']);
        $('#guests').val(PRODUCT_POSITIONS['guests']);

        attachEventToQty();
        manage_subtotal();
        manage_total();
    }

    var product_objects = '';
    var embellishment_objects = '';
    var clonedObject = $('.product.unselected').clone();
    var clonedObject2 = $('.embellishment.unselected').clone();

    clonedObject.each(function(e){
        $(this).removeClass('selected');
        product_objects += $(this).prop('outerHTML');

    });

    clonedObject2.each(function(e){
        $(this).removeClass('selected');
        embellishment_objects += $(this).prop('outerHTML');

    });

    var cloned_table = $('.table').clone();

    $('.dynamic_qty').each(function(e){

        var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
        cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

    });

    changesArray.push({ guests: $('#guests').val(),tables: $('#tables').val(), buy_table_html: cloned_table.html(),action_url: action_url, total: total, quantity: quantity, selected_prev_prod_qty: selected_prev_prod_qty, obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects });
    
}

function changeProductPositions(pos) {

    remove_handles($.event);

    uniqueIdentifier = parseInt(pos['unique_identifier']);
    objCounter = parseInt(pos['obj_counter']);
    //changesCounter = parseInt(pos['changes_counter']);
    action_url = pos['action_url'];
    total = parseFloat(pos['total']);
    quantity = parseInt(pos['quantity']);
    selected_prev_prod_qty = parseInt(pos['selected_prev_prod_qty']);

    $('.product.unselected').remove();
    $('.embellishment.unselected').remove();
    $('#canvas').append(pos['product_objects']);
    $('#canvas').append(pos['embellishment_objects']);
    $('.table').html(pos['buy_table_html']);
    $('#tables').val(pos['tables']);
    $('#guests').val(pos['guests']);

    attachEventToQty();
    manage_subtotal();
    manage_total();

}

function cancelBubble(e) {
    var evt = e ? e:window.event;
    if (evt.stopPropagation)    evt.stopPropagation();
    if (evt.cancelBubble!=null) evt.cancelBubble = true;
}

function undo_styleboard() {
    if(changesCounter > 0) {
        changesCounter--;
        changeProductPositions(changesArray[changesCounter]);
        remove_all_cart();

        var clonedTable = $('.table').clone();
        $('.table').html('');


        $(clonedTable).find('.dynamic_qty').each(function(e){
            add_to_cart($(this).attr('_pid'), $(this).attr('_dq'), $(this).attr('_gs'));
        });

        $('.table').html($(clonedTable).html());

        attachEventToQty();
        manage_subtotal();
        manage_total();
        styleboardH();
        
        eventTracker($('#canvas'),'undo');
    }
}

function redo_styleboard() {
    if(changesCounter < (changesArray.length - 1)) {
        changesCounter++;
        changeProductPositions(changesArray[changesCounter]);
        remove_all_cart();

        var clonedTable = $('.table').clone();
        $('.table').html('');


        $(clonedTable).find('.dynamic_qty').each(function(e){
            add_to_cart($(this).attr('_pid'), $(this).attr('_dq'), $(this).attr('_gs'));
        });

        $('.table').html($(clonedTable).html());

        attachEventToQty();
        manage_subtotal();
        manage_total();
        styleboardH();

        eventTracker($('#canvas'),'redo');
    }
}

function change_cursor(option){

    var type = $.parseJSON($('.selected').attr('_matrix'));
    var handles = [];
    var options = option.split(',');
    handles = options;
    
    var position = [{"top":"-5px","left":"-5px","bottom":"auto","right":"auto","display":"block"},
                    {"top":"auto","left":"-5px","bottom":"-5px","right":"auto","display":"block"},
                    {"top":"auto","left":"auto","bottom":"-5px","right":"-5px","display":"block"},
                    {"top":"-5px","left":"auto","bottom":"auto","right":"-5px","display":"block"},
                    {"top":"auto","left":"auto","bottom":"auto","right":"auto","display":"none"},
                    {"top":"auto","left":"auto","bottom":"auto","right":"auto","display":"none"},
                    {"top":"auto","left":"auto","bottom":"auto","right":"auto","display":"none"},
                    {"top":"auto","left":"auto","bottom":"auto","right":"auto","display":"none"}];
    var newObj;
    $.each(handles, function(index, value){
        newObj = $('.ui-resizable-'+value);
        newObj.css(position[index]);
    });

    return handles;
}

function new_canvas(url){
    var r = confirm("Are you sure you want to discard your changes?");
    if (r){
        window.location = url;
    }else{
        return false;
    }
}

function hide_canvas_menu(){
    var warning = 'WARNING!!! Object inside the canvas exceed the 50 item limit: '+objCounter+' items.';
    if(objCounter < 1){
        $('.nwMenus').hide();
        $('#canvas').css('background-image','url(/media/images/canvasbg.jpg)');
    }else if(objCounter > 50){
        $('#canvas').css('background-image','url()');
        $('#object-counter').text(warning).show();
        $('.nwMenus').show();
        $('#save').unbind('click');
    }else{
        $('#canvas').css('background-image','url()');
        $('#save').bind('click',function(e){
            if ($('#canvas-wrap .unselected').length>0){
                pop_save_styleboard();
            }
            e.preventDefault();
        });
        $('#object-counter').hide();
        $('.nwMenus').show();
    }
}

(function ($) {
   $.fn.liveDraggable = function (opts) {
      this.live("mouseover", function(e) {
         if (!$(this).data("init")) {
            $(this).data("init", true).draggable(opts);
         }
      });
      return $();
   }

   //extending the attr function to return all attrs
   // duck-punching to make attr() return a map
    var _old = $.fn.attr;
    $.fn.attr = function() {
      var a, aLength, attributes, map;
      if (this[0] && arguments.length === 0) {
              map = {};
              attributes = this[0].attributes;
              aLength = attributes.length;
              for (a = 0; a < aLength; a++) {
                      map[attributes[a].name.toLowerCase()] = attributes[a].value;
              }
              return map;
      } else {
              return _old.apply(this, arguments);
      }
  }

    $.strPad = function(i,l,s) {
        var o = i.toString();
        if (!s) { s = '0'; }
        while (o.length < l) {
            o = s + o;
        }
        return o;
    };

    var oldSetOption = $.ui.resizable.prototype._setOption;
    $.ui.resizable.prototype._setOption = function(key, value) {
        oldSetOption.apply(this, arguments);
        if (key === "aspectRatio") {
            this._aspectRatio = !!value;
        }
    };

}(jQuery));


//product functions end
