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
DEFAULT_TEXT_E = "I Love iDecorate";
active_object = null;


$(document).ready(function () {

     //remove edit button on buy tab
    $(window).hashchange( function(){
        
        if(location.hash == '#buy-tab'){
            $('#sidebar-form-wrap .myorder-edit').hide();
        }else if(location.hash == '#create-tab'){
            $('#sidebar-form-wrap .myorder-edit').show();
        }
    });
    
    $(window).hashchange();

    if($.browser.msie && $.browser.version == 7.0) {

        $(".draggable").liveDraggable({
            revert: true,
            helper: function(e) {
                active_object = $(this).clone();
                return $(active_object).find('img').attr('id','');
            },
            containment: 'body',
            drag:function(e,ui){
                template_fill();
                $('#canvas .box').addClass('dragHover');
            },
            stop: function(e, ui){
                template_fill();
                $('#canvas .box').removeClass('dragHover');
            }

        });

    } else {

        $(".draggable").liveDraggable({
            revert:true, 
            helper: 'clone',
            containment: 'body',
            drag:function(e,ui){
                template_fill();
                $('#canvas .box').addClass('dragHover');
            },
            stop: function(e, ui){
                template_fill();
                $('#canvas .box').removeClass('dragHover');
            }
        });

    }

    //get the maxheight sidebar name <span> and set as global
    //height for all name container <span> on the sidebar
    
    //set dropable area for the draggable sidebar objects
    droppable_all();

    //drag the selected product together with its handle on the fly
    $('.unselected').liveDraggable({
        helper: 'original',
        cursor: 'move',
        //containment: '#canvas',
        start : function(e, ui){transform($(this));},
        drag : function(e, ui){transform($(this));},
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
                //set handles direction 
                change_cursor($('.selected').attr('_handle'));
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
                //set handles direction 
                change_cursor($('.selected').attr('_handle'));
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
        //containment:'#canvas',
        start: function(e, ui){transform($(this));},
        drag: function(e, ui){transform($(this));},
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
            
            if($.browser.msie && $.browser.version == 7.0){
                reset_product();
            }
        }
    }); 


    if(!$.browser.msie){//while IE is not yet supported
        $handles.rotatable({rotateAlso:'.selected'});
    }else if($.browser.msie && $.browser.version == 9.0){
        $handles.rotatable({rotateAlso:'.selected'});
    }else if($.browser.msie && $.browser.version < 9.0){
        $('#flip-btn, #flap-btn').parent().hide();
    }

    //hide handles and menus
    $(document).click(function(e){
        unselect_all(e);

    }).keydown(function(e){
        
        if(!$.browser.mozilla) {
            if((e.keyCode == 8 || e.keyCode == 46) && $('.selected').length > 0 && e.target.type != 'textarea') {
                e.preventDefault();
                $('#remove-btn').trigger('click');
            } else if((e.keyCode == 8 || e.keyCode == 46) && $('#canvas .template.box.active').length > 0 && e.target.type != 'textarea') {
                e.preventDefault();
                $('#remove-btn').trigger('click');
            }
        }
    });

    //REMOVE PRODUCT IN FIREFOX
    $('html').keypress(function(e){

        if($.browser.mozilla) {
            if((e.keyCode == 8 || e.keyCode == 46) && $('.selected').length > 0 && e.target.type != 'textarea') {
                e.preventDefault();
                $('#remove-btn').trigger('click');
                return false;
            } else if((e.keyCode == 8 || e.keyCode == 46) && $('#canvas .template.box.active').length > 0 && e.target.type != 'textarea') {
                e.preventDefault();
                $('#remove-btn').trigger('click');
            }
        }

    });

    //remove selected obj
    $('#remove-btn').click(function(e){
        e.preventDefault();
        if($('#canvas .template').length > 0){

            var selected_uid = $('#canvas .template.box.active').find('img').attr('_uid');
            var count = 0;

            $('.templateImage.product').each(function(e){
                if(selected_uid == $(this).attr('_uid')) {
                    count++;
                }
            });

            if (count<=1 && selected_uid != undefined)
                remove_from_cart(parseInt(selected_uid,10));

            $('#canvas .template.box.active').removeClass('notEmpty').find('img').remove();
            $('#canvas .template.box').removeClass('hover active').find('span').show();
            //console.log(count);
            notEmpty = false;
        }else{
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
        }

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
        if(!$(this).hasClass('cloneFalse')){
            //show or hide upper left menu of canvas;
            obj = $('.selected');
            cloneObj(obj);
        }
        hide_canvas_menu();
    });

    //make selected product image PNG
    $('#transBg-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        if($('#canvas .template').length > 0){
            var trans   = $('#canvas .template.box.active').find('img').attr('_nb');
            var allAttr = $('#canvas .template.box.active').find('img').attr();
            change_img_template(allAttr,false);
        }else{
            if($('.selected').length == 1){change_img($('.selected'),false);}
        }

    });

    //make selected product image JPG
    $('#whiteBg-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        if($('#canvas .template').length > 0){
            var trans   = $('#canvas .template.box.active').find('img').attr('_nb');
            var allAttr = $('#canvas .template.box.active').find('img').attr();
            change_img_template(allAttr,true);
        }else{
            if($('.selected').length == 1){change_img($('.selected'),true);}
        }

    });

    // create custom image crop
    $('#customBg-btn').click(function(e){
        e.preventDefault();
        cancelBubble(e);

        if(getUrlVars($('.selected > img').attr('src'))['filename']) {
            var meta_data = getUrlVars($('.selected > img').attr('src'));
            var url_to_open = MODAL_SRC.replace('0',meta_data['filename']) + '/?&task=' + meta_data['task'] + '&otherdata=' + meta_data['otherdata'] + '&dimensions=' + meta_data['dimensions'];
            display_modal(url_to_open);
        } else {
            display_modal(MODAL_SRC.replace('0',$('.selected > img').attr('src').replace('/media/products/','')));
        }

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
        redo_styleboard();
        hide_canvas_menu();
    });

    $('#undo').click(function(e){
        e.preventDefault();
        //show or hide upper left menu of canvas;
        undo_styleboard();
        hide_canvas_menu();
    });

    /*  
    embellishments
    this is where embellishment related function calls
    starts as well as with the inits,events,variables
    */

    $("#font_id").selectbox({
        imageRegExp: /font_id/
    });

    $('.sbHolder').on('click mousedown',function(e){
        cancelBubble(e);
    });

    $("#font_id").on('click mousedown',function(e){
        cancelBubble(e);
    });

    $("#colorPicker").spectrum({
        color: "#000",
        preferredFormat: "rgb",
        showButtons: false,
        clickoutFiresChange: true,
        move: function(color) {
         var object = $('.selected').find('img');
         new_img = change_color(object,color.toRgb());
        },
        change: function(color){
            eventTracker(new_img, 'change_color');
        }
    });

    $('#text-change, #text-update').click(function(e){
        e.preventDefault();
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
            },
            stop: function(event, ui){
                eventTracker($('.selected'), 'set_opacity');
            }
        });

        $('#canvas').on('click mousedown', '.embellishment.shape,.embellishment.pattern,.embellishment.text,.embellishment.texture', function(e){
            cancelBubble(e);
            slideValue = parseInt($(this).attr('_opacity'));
            embellishment_handle_set(slideValue);
        });
    }else{
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
                },
                stop: function(event, ui){
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
        }
    }

    $('#canvas').on('click mousedown', '.text', function(e){
        change_textON_textarea($(this));
        changeSelectedFont($(this));
    });

    $('#text-update').click(function(e){
        var text_value = $('#text-change').val();
        var font_id = $('#font_id').val();
        update_text_selected(text_value,font_id);
    });

    //show or hide upper left menu of canvas;
    hide_canvas_menu();

    setTimeout('ie_message()',2500);


    //event handlers for templates
    $('.template-wrap').on('click', '.thumb', function(e){
        e.preventDefault();
        if($('#canvas .template').length > 0){
            $('#canvas .template').remove();
            manage_total();
        }
        $('#canvas').droppable('disable').fadeTo(1,1);
        objects = get_template_details($(this).attr('_uid'));

        if(objects.length > 0){
            drop_template(objects);
            box_droppable();
        }
    });
    
    if($('#canvas .template').length > 0){
        $('#canvas').droppable('disable').fadeTo(1,1);
        box_droppable();
    }
    
    var notEmpty = false;
    $('#canvas').on('mouseenter', '.box', function(e){
        $(this).addClass('hover');
        if($(this).hasClass('notEmpty')){
            notEmpty = true;
            $(this).removeClass('notEmpty');
        }
    });
    $('#canvas').on('mouseleave', '.box', function(e){
        $(this).removeClass('hover');
        if(notEmpty){
            $(this).addClass('notEmpty');
        }
        notEmpty = false;
    });

    $('#canvas').on('mousedown', '.box', function(e){
        $(this).addClass('active').siblings('.box').removeClass('active');
        update_menu($(this).find('img'));
        hide_canvas_menu();
        $(document).unbind('click');
        setTimeout(function(){
            $(document).click(function(){
                unselect_all(e);
            });
        },100);
    });

});
function unselect_all(e){
    var click =  $.contains($('#canvas .handles, #canvas .handles .handle , #canvas .box')[0],e.target) ? true : e.target == $('#canvas .handles');
        
        $('.box').removeClass('active');

        if(!click){
            remove_handles(e);
            eventTracker(e.target, 'unselect');
        }
}
//message in ie
function ie_message() {
    //view message if ie version < 9
    if($.browser.msie && $.browser.version < 9.0){
        alert('Sorry! Your browser does not support the following functionalities:  rotate, flip, flop, transparency changes, and personalizing style boards.\nPlease use one of the following browsers: Chrome, Firefox, Safari, or try upgrading your Internet Explorer to version 9.');
    }
}

function change_img_template(allAttr,background){
    var box = $('<img/>');
    var attr = allAttr;
    var _nb = attr._nb;
    var _wb = attr._wb;
    box.attr(attr);

    var __src   = (background == false) ? '/'+media_url+'products/'+_nb : '/'+media_url+'products/'+_wb;
    box.attr('src',__src);

    box.load(function(){
        $('.box.active').append(box);
        box.siblings('img').remove();
        eventTracker($(this),'change_background');
    });
}

function box_droppable(){
    $('#canvas .template.box').droppable({
        drop: function (e, ui) {

            if ($(ui.draggable)[0].id != "") {

                ui.helper.remove();
                var Obj         = $(ui.draggable)[0];
                Obj             = $(Obj);
                var _this       = this;
                var this_width  = $(_this).width();
                var this_height = $(_this).height();

                if(Obj.hasClass('products')){
                    var uid         = Obj.attr('_uid');
                    var _img_src    = media_url+'products/';
                    var p_d_qty     = 1;
                    var p_g_t       = 'table';

                    $.ajax({
                        url: PRODUCT_IMAGE_URL,
                        type: "POST",
                        data: {product_id: uid},
                        async:   false,
                        success: function(data){
                            //console.log($(_this).find('img').attr('_uid'));
                            var currentProd = $(_this).find('img').attr('_uid');
                            var img_src     = '/'+_img_src+data.original_image;
                            var img_w_bg    = data.original_image;
                            var img_wo_bg   = data.no_background;
                            var p_d_qty     = data.default_quantity;
                            var p_g_t       = data.guest_table;

                            //create new image using image object
                            var object = create_image_for_template({
                                        _box     : _this,
                                        _uid     : uid,
                                        _event   : e,
                                        _src     : img_src,
                                        _img_wo_b: img_wo_bg,
                                        _img_w_b : img_w_bg,
                                        _p_d_qty : p_d_qty,
                                        _p_g_t   : p_g_t,
                                        _width   : this_width,
                                        _height  : this_height
                                    });

                            var obj_id = $(object[0]).attr('_uid');

                        
                            if(currentProd) {


                                if(currentProd != obj_id) {

                                    var selected_uid = currentProd;
                                    var count = 0;

                                    $('.templateImage.product').each(function(e){
                                        if(selected_uid == $(this).attr('_uid')) {
                                            count++;
                                        }
                                    });

                                    if (count<=1) {
                                        //console.log('delete by product');
                                        remove_from_cart(parseInt(selected_uid,10));
                                    }


                                }

                            }

                            $(_this).children('img').remove();

                            $(object[0]).appendTo($(_this));
                            
                            if(!$(_this).hasClass('active')){
                                $(_this).addClass('active').siblings().removeClass('active');
                            }

                            add_to_cart(uid, p_d_qty, p_g_t);
                        },
                        error: function(msg){
                            alert(msg);
                        }
                    });
                    
                    template_fill();

                    setTimeout(function(){
                        eventTracker($(_this),'drop_object');
                    },100);

                    //add_to_cart(uid, p_d_qty, p_g_t);

                }else if(Obj.hasClass('em')){

                    var em_id = Obj.attr('id');
                    var em_dbID = em_id.split('-');
                    var type = Obj.attr('_type');

                    if(type == 'Text'){
                        //object = create_text_for_template(em_dbID[1],e,type);
                    }else{
                        var object = create_embellishments_for_template(em_dbID[1],e,type,this_width,this_height);
                        var currentProd = $(_this).find('img').attr('_uid');


                        if(currentProd) {

                            var selected_uid = currentProd;
                            var count = 0;

                            $('.templateImage.product').each(function(e){
                                if(selected_uid == $(this).attr('_uid')) {
                                        count++;
                                }
                            });

                            if (count<=1) {
                                remove_from_cart(parseInt(selected_uid,10));
                            }

                        }
                        //$(_this).html(object[0]);

                        $(object[0]).appendTo($(_this)).siblings('img').remove();

                        if(!$(_this).hasClass('active')){
                            $(_this).addClass('active').siblings().removeClass('active');
                        }

                        template_fill();

                        setTimeout(function(){
                            eventTracker($(_this),'drop_object');
                        },100);

                    }
                }
            }
        }
    });
}
// functions related to template
function create_embellishments_for_template(em_dbID,event,type,_width,_height){

    var object      = $('<img/>');
    var this_width    = 0;
    var this_height   = 0;
    var box_Width     = _width;
    var box_Height   = _height;

    object.attr({
        'src': '/generate_embellishment/?embellishment_id='+em_dbID+'&embellishment_color=000000000&embellishment_thumbnail=0&rand=' + new Date().getTime()
    });

    object.load(function(){
        this_width = object.width();
        this_height = object.height();

        var dim = do_fit_dimension(box_Width,box_Height,this_width,this_height);
    
        object.width(dim.width).height(dim.height).css({
            position : 'absolute',
            top: dim.top,
            left: dim.left
        });
    });

    object.addClass(type.toLowerCase()+' templateEmbellishments');
    
   if(type.toLowerCase() == 'shape' || type.toLowerCase() == 'texture' || type.toLowerCase() == 'text' || type.toLowerCase() == 'pattern'){
        object.attr('_opacity', 100);
        $( "#slider" ).slider({value:100});
    }
    slideValue = 100;
    embellishment_handle_set(slideValue);

    update_menu(object,true);
    hide_canvas_menu();

    return object;
}

function template_fill(){
    $('#canvas .template.box').each(function(i,val){
        if($(this).find('img').length > 0){
            $(this).find('span').hide();
            $(this).addClass('notEmpty');
        }else{
            $(this).addClass('hover');
            //.removeClass('notEmpty');
        }
    });
}

function create_image_for_template(options){
    var object = $('<img/>');
    var this_width;
    var this_height;
    var box_Height = options._height;
    var box_Width = options._width;

    object.attr({
        '_uid': options._uid,
        'def_qty': options._p_d_qty,
        'gst_tb': options._p_g_t,
        'src': options._src,
        '_nb': options._img_wo_b,
        '_wb': options._img_w_b
    }).addClass('templateImage product');
    
    object.load(function(){
        this_width  = object.width();
        this_height = object.height();

        var dim = do_fit_dimension(box_Width,box_Height,this_width,this_height);
    
        object.width(dim.width).height(dim.height).css({
            position : 'absolute',
            top: dim.top,
            left: dim.left
        });
    });

    update_menu(object);
    hide_canvas_menu();

    return object;
    
}

function do_fit_dimension(box_Width, box_Height, this_width, this_height){
    
    var dimension = {};
    var aspectRatio = this_height/this_width;
    var percent     = this_width
    var widthDiff   = box_Width-this_width;
    var heightDiff  = box_Height-this_height;

    //console.log(box_Width, box_Height, this_width, this_height);

    if(widthDiff < heightDiff){
        dimension['width']  = box_Width;
        dimension['height'] = dimension['width']*aspectRatio;
    }else{
        dimension['height'] = box_Height;
        dimension['width']  = dimension['height']/aspectRatio;
    }
    dimension['top']    = (box_Height/2)-(dimension['height']/2);
    dimension['left']   = (box_Width/2)-(dimension['width']/2);

    //console.log(dimension);

    return dimension;
}

function drop_template(objects){

    if($('#canvas .unselected').length > 0){
        $('#canvas .unselected').remove();
        remove_all_cart();
    }

    $.each(objects, function(i, val){
        var object  = $('<div/>');
        var img     = $('<img/>');
        var mtx     = val.matrix[0];

        if($.browser.msie && $.browser.version < 9){
            var rawMtx = rotate_global(-parseFloat(val.angle));
            mtx.a = rawMtx.a;
            mtx.b = rawMtx.b;
            mtx.c = rawMtx.c;
            mtx.d = rawMtx.d;
        }

        object.attr('_matrix', '{"a":1, "b":0, "c":0, "d":1,"e":false,"f":false}');
        object.attr('_handle', ['nw','sw','se','ne','w','s','e','n']);        
    
        object.attr({
            'opacity'   : val.opacity,
            'angle'     : val.angle,
            '_matrix'   : '{"a":'+mtx.a+', "b":'+mtx.b+', "c":'+mtx.c+', "d":'+mtx.d+',"e":'+mtx.e+',"f":'+mtx.f+'}',
            '_handle'   : val.handle,
            'rgb'       : val.rgb,
            'text'      : val.text,
            'style'     : val.style,
            '_uid'      : val.uid
        }).addClass('template');

        var matrix = 'matrix('+ mtx.a +', '+ mtx.b +', '+ mtx.c +', '+ mtx.d +', 0, 0)',
            ie_matrix = "progid:DXImageTransform.Microsoft.Matrix(M11='"+mtx.a+"', M12='"+mtx.b+"', M21='"+mtx.c+"', M22='"+mtx.d+"', sizingMethod='auto expand')";         
        if($.browser.msie && $.browser.version == 9.0) {
            object.css({
                '-ms-transform'    : matrix
            });
        }else if($.browser.msie && $.browser.version < 9.0){
            object.css({
                'filter'           : ie_matrix,
                '-ms-filter'       : '"' + ie_matrix + '"'
            });
        }else{
            object.css({
                '-moz-transform'   : matrix,
                '-o-transform'     : matrix,
                '-webkit-transform': matrix,
                'transform'        : matrix
            });
        }

        img.attr('src',val.img[0].src);

        img.load(function(){
            img.attr('style',val.img[0].style);
        });

        img.appendTo(object);

        if(val._type != 'box'){
            object.addClass('embellishment '+val._type);
        }else{
            object.addClass(val._type);
            object.html('<span>'+val.spantext+'</span>');
        }

        object.appendTo('#canvas');
        objCounter = 1;
        hide_canvas_menu();
        
    });

    make_center_template();
    setTimeout(function(){
        eventTracker($('#canvas'), 'add_template');

    },300);
    //setTimeout(make_center_template, 0);
}

function get_template_details(template_id){
    var json_data;
    
    $.ajax({
        url: GET_TEMPLATES_DETAIL_URL,
        type: "POST",
        data: { id: template_id},
        async:   false,
        success: function(data){
            data = data.split('null,').join('');
            json_data =eval(data);
        },
        error: function(msg) {
            alert(msg);
        }
    });
    return json_data;
}
// template function end


//embelishments functions start
function changeSelectedFont(el) {

    var font_id = el.attr('_uid');

    
    $('#font_id option').attr('selected',false);

    $('#font_id option[value="' + font_id + '"]').attr('selected',true);
    //$('#font_id').val(font_id);
    $('#font_id').trigger('change');
    //$('#font_id').selectbox("option", font_id);

    $('.sbSelector').html($('.sbOptions  li  a[href="#' + font_id + '"]').html());
}

function create_instance_em_text(em_dbID,event,type){
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
        'src': '/generate_text/?font_size=200&font_text=' + escape(DEFAULT_TEXT_E) + '&font_color=000000000&font_id='+em_dbID+'&font_thumbnail=0&rand=' + new Date().getTime()
    }).css({
        width: '100%',
        height: 'auto'
    });

    obj_image.load(function(){
        
        imgWidth = obj_image.width();
        imgHeight = obj_image.height();
        var dimensions  = aspectratio(imgWidth, imgHeight, .30);
        var imgTop      = event.pageY-$('#canvas').offset().top-dimensions['height']/2;
        var imgLeft     = event.pageX-$('#canvas').offset().left-dimensions['width']/2;

        $(this).attr('orig_width', imgWidth);
        $(this).attr('orig_height',imgHeight);

        object.css({
            left:imgLeft,
            top:imgTop,
            width:dimensions['width'],
            height:dimensions['height']
        });

        set_ctr_attr(object);

        transform(object);

        changeSelectedFont(object);

        eventTracker(object, 'create_embellishment');

    }).appendTo(object);
    
    object.appendTo('#canvas');

    if(!object.hasClass('selected')){
        object.addClass('selected').siblings('.unselected').removeClass('selected');
        object.attr('_matrix', '{"a":1, "b":0, "c":0, "d":1,"e":false,"f":false}');
        object.attr('_handle', ['nw','sw','se','ne','w','s','e','n']);
        object.attr('_opacity', 100);
        object.attr('_text', DEFAULT_TEXT_E);
        object.attr('_rgb', '000000000');
        $( "#slider" ).slider({value:100});
        slideValue = 100;
        embellishment_handle_set(slideValue);

        //set handles direction 
        change_cursor($('.selected').attr('_handle'));
    }
    change_textON_textarea($('.selected'));
    update_menu(object,true);
    hide_canvas_menu();

    return object;
}

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
        'src': '/generate_embellishment/?embellishment_id='+em_dbID+'&embellishment_color=000000000&embellishment_thumbnail=0&rand=' + new Date().getTime()
    });

    obj_image.load(function(){
        //alert('image load');
        
        imgWidth = obj_image.width();
        imgHeight = obj_image.height();

        var dimensions  = aspectratio(imgWidth, imgHeight, .48);
        var imgTop      = event.pageY-$('#canvas').offset().top-dimensions['height']/2;
        var imgLeft     = event.pageX-$('#canvas').offset().left-dimensions['width']/2;

        object.css({
            left:imgLeft,
            top:imgTop,
            width:dimensions['width'],
            height:dimensions['height']
        });

        $(this).css({
            width: '100%',
            height: '100%'
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
        //set handles direction 
        change_cursor($('.selected').attr('_handle'));
    }
    update_menu(object,true);
    hide_canvas_menu();

    return object;
}

function create_instance_embellishment_upload(fname){
    //GLOBAL var objCounter is for setting z-index for each created instance
    objCounter++;

    var object = $('<div/>');
    object.attr({
        'class': 'image embellishment unselected'
    }).css({
        zIndex : objCounter,
        position: 'absolute',
        left: '-5000px'
    });

    var obj_image   = $('<img/>');
    var imgWidth    = 0;
    var imgHeight   = 0;

    obj_image.attr({
        'src': '/media/embellishments/images/'+fname
    });

    obj_image.load(function(){
        
        imgWidth = obj_image.width();
        imgHeight = obj_image.height();
        var r = 1;
        var dimensions  = aspectratio(imgWidth, imgHeight, r);
        dimensions = embellishment_check_upload_image_dimension(dimensions, r);

        var imgTop      = ($('#canvas').height()/2)-(dimensions['height']/2);
        var imgLeft     = ($('#canvas').width()/2)-(dimensions['width']/2);       

        object.css({
            left:imgLeft,
            top:imgTop,
            width:dimensions['width'],
            height:dimensions['height']
        });

        $(this).css({
            width: '100%',
            height: 'auto'
        });

        set_ctr_attr(object);

        transform(object);

        eventTracker(object, 'upload_image');

    }).appendTo(object);
    
    object.appendTo('#canvas');

    if(!object.hasClass('selected')){
        object.addClass('selected').siblings('.unselected').removeClass('selected');
        object.attr('_matrix', '{"a":1, "b":0, "c":0, "d":1,"e":false,"f":false}');
        object.attr('_handle', ['nw','sw','se','ne','w','s','e','n']);        
    }
    update_menu(object,true);
    $handles.resizable({aspectRatio:true});
    hide_canvas_menu();

    //set handles direction 
    change_cursor($(object).attr('_handle'));
    
    return object;
}

function embellishment_check_upload_image_dimension(dimensions,ratio){
    var canvas_width = $('#canvas').width()-(($('#canvas').width()*10)/100);
    var canvas_height = $('#canvas').height()-(($('#canvas').height()*10)/100);    
    if (dimensions['height'] > canvas_height || dimensions['width']>canvas_width){
        ratio = ratio-.05;
        dimensions  = aspectratio(dimensions['width'], dimensions['height'], ratio);
        return embellishment_check_upload_image_dimension(dimensions, ratio)        
    } else
        return dimensions;
}

function change_color(object,rgb){
    var selected        = object.parent();
    var default_style   = object.attr('style');
    var object_dbID     = selected.attr('_uid');
    var new_img         = $('<img/>');
    var new_obj_src     = '/generate_embellishment/?embellishment_id='+object_dbID+'&embellishment_color='+$.strPad(rgb.r,3)+$.strPad(rgb.g,3)+$.strPad(rgb.b,3)+'&embellishment_thumbnail=0';
    if(selected.hasClass('text')){
        new_obj_src = '/generate_text/?font_size=200&font_text='+escape(selected.attr('_text'))+'&font_color='+$.strPad(rgb.r,3)+$.strPad(rgb.g,3)+$.strPad(rgb.b,3)+'&font_id='+object_dbID+'&font_thumbnail=0';
        selected.attr('_rgb',$.strPad(rgb.r,3)+$.strPad(rgb.g,3)+$.strPad(rgb.b,3));
    }
    object.remove();//remove old object
    new_img.attr({//append new object
        'src': new_obj_src,
        'style': default_style
    }).appendTo(selected);

    return new_img;
}

function embellishment_handle_set(slideValue){
    $( "#slider" ).slider({value:slideValue});
    if($('.selected').hasClass('shape') || $('.selected').hasClass('texture') || $('.selected').hasClass('pattern')){
        $handles.resizable({aspectRatio:false});
        $('.selected img').height('100%');
    }else{
        $handles.resizable({aspectRatio:true});
    }
}

function change_textON_textarea(object){
    var text = object.attr('_text');
    var font_id = object.attr('_uid');
    $('#text-change').val(text);
    $('#font_id').val(font_id);
}

function update_text_selected(text_value,font_id){

    if(text_value != "") {

        var object          = $('.selected');
        var default_style   = object.children('img').attr('style');
        var object_dbID     = font_id;
        var rgb             = object.attr('_rgb');
        var new_img         = $('<img/>');
        var new_image_src   = new_obj_src = '/generate_text/?font_size=200&font_text='+escape(text_value)+'&font_color='+rgb+'&font_id='+object_dbID+'&font_thumbnail=0';

        var old_height = object.height();
        var old_width = object.width();        
        var old_orig_img_width = $('.selected > img').attr('orig_width');
        var old_orig_img_height = $('.selected > img').attr('orig_height');
        var heightPercentage = old_height / old_orig_img_height * 100;
        var widthPercentage = old_width / old_orig_img_width * 100;
        var old_id = object.attr('_uid');

        object.children('img').remove();//remove old object

        new_img.attr({
            'src': new_obj_src
        }).hide();
        
        new_img.load(function(){
            
            imgWidth = new_img.width();
            imgHeight = new_img.height();

            var dimensions  = aspectratio(imgWidth, imgHeight, .30);

            $(this).attr('orig_height', imgHeight);
            $(this).attr('orig_width', imgWidth);


            new_img.attr({
                'style': default_style
            });

            if(old_id != font_id) {
                new_width = dimensions['width'];
                new_height = dimensions['height'];
            } else {
                new_width = imgWidth * (widthPercentage / 100);
                new_height = imgHeight * (heightPercentage / 100);
            }

            $handles.height(new_height);            
            $('.selected').height(new_height);
            
            $('.selected').width(new_width);
            
            $handles.width(new_width);

            new_img.show();

            object.attr('_text',text_value);
            object.attr('_uid',font_id);

            eventTracker($('.selected'), 'text_change');

        }).appendTo(object);

    } else {
        $("#text-change").val($('.selected').attr('_text'));
    }

}
//embelishments functions end


//product functions start
function droppable_all(){
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

                    if(type == 'Text'){
                        object = create_instance_em_text(em_dbID[1],e,type);
                    }else{
                        object = create_instance_embellishments(em_dbID[1],e,type);
                    }
                }
            }
        }
    });
}

function create_instance(options){
    var object;
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
    return object;
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
        //set handles direction 
        change_cursor($('.selected').attr('_handle'));
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
}

function aspectratio(width, height, percent){

    var dimension = {};
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
    
    if($('.template').length > 0) {

        if($(obj).length > 0) {
            $img_menus.show();
        } else {
            $img_menus.hide();
        }

    } else {
        $img_menus.show();
    }


    if(obj.hasClass('templateImage') || obj.hasClass('templateEmbellishments')){
        $('#customBg-btn').hide();
        $('#remove-btn').parent().siblings('li').hide();
    }

    if(img_menu || $('.template.box.active').children('.templateEmbellishments').length > 0){
        $('.imgBgControlWrap').hide();
        if(obj.hasClass('image') || obj.parent().hasClass('image') || obj.parent().hasClass('border') || obj.hasClass('border')){
            $('.colorAdjustment').hide();
        }else{
            $('.colorAdjustment').show();
            if(obj.hasClass('text') || obj.parent().hasClass('text')){
                $('#text-change-wrap').show();
                $('#opacity-control-wrap').css({'width':'47%','float':'left','margin-left':10});
            }else{
                $('#text-change-wrap').hide();
                $('#opacity-control-wrap').css({'width':'87%','float':'right','margin-left':''});
            }
        }
    }else{
        $('.imgBgControlWrap').show();
        $('.colorAdjustment').hide();
    }

    if(obj.hasClass('product') || obj.parent().hasClass('product')){
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
        var template_objects = '';

        var clonedObject = $('.product.unselected').clone();
        var clonedObject2 = $('.embellishment.unselected').clone();
        var clonedObject3 = $('.template').clone();

        clonedObject.each(function(e){
            $(this).removeClass('selected');
            product_objects += $(this).prop('outerHTML');

        });

        clonedObject2.each(function(e){
            $(this).removeClass('selected');
            embellishment_objects += $(this).prop('outerHTML');

        });

        clonedObject3.each(function(e){
            template_objects += $(this).prop('outerHTML');

        });        

        var cloned_table = $('.table').clone();

        $('.dynamic_qty').each(function(e){

            var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
            cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

        });

        if(changesCounter != (changesArray.length - 1)) {
            changesArray.splice(changesCounter + 1, changesArray.length - changesCounter);
        }

        changesArray.push({ guests: $('#guests').val(),tables: $('#tables').val(), buy_table_html: cloned_table.html(),action_url: action_url, total: total, quantity: quantity, selected_prev_prod_qty: selected_prev_prod_qty, obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects, template_objects: template_objects });
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
    var iframe  = $('<iframe />').attr({'class':'modalIframe','id':'modal-iframe','src':iframe_src, 'frameBorder': 0});
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
    $('.unselected').each(function(e){
        var elm = $(this);
        var elm_offset = elm.offset();
        var elm_left = elm_offset.left;
        var elm_top = elm_offset.top;
        var product_left = Math.round(elm_left-canvas_left);
        var product_top = Math.round(elm_top-canvas_top);
        var filter = {};
        if($.browser.msie && $.browser.version == 7.0){
            filter = {'filter':'none'};
        }else if($.browser.msie && $.browser.version == 8.0){
            filter = {'msfilter':'none','-ms-filter':'none'};
        }
        $(this).css(filter);
        var style = $(this).attr('style');
        var _zindex = $(this).css('z-index');
        var _matrix = [];
        _matrix.push($.parseJSON($(this).attr('_matrix')));        
        var _img = [];
        var elm_img = $(this).find('img');
        var _src = $(elm_img).attr('src');
        var _nb = $(elm_img).attr('_nb');
        var _wb = $(elm_img).attr('_wb');
        var _handle = $(this).attr('_handle');
        var _uid = $(this).attr('_uid');
        var _def_qty = $(this).attr('def_qty');
        var _gst_tb = $(this).attr('gst_tb');
        var _angle = 0;
        if($(this).attr('_angle')){
            _angle = $(this).attr('_angle');
        } else if($(this).attr('angle')) {
            _angle = $(this).attr('angle');
        }
        var _opacity = $(this).attr('_opacity')?$(this).attr('_opacity'):100;
        var _text = $(this).attr('_text')?escape($(this).attr('_text')):'';
        var _rgb = $(this).attr('_rgb')?$(this).attr('_rgb'):'';
        var type = 'product';
        if($(this).hasClass('text'))
            type = 'text';
        if($(this).hasClass('image'))
            type = 'image';
        if($(this).hasClass('border'))
            type = 'border';
        if($(this).hasClass('shape'))
            type = 'shape';
        if($(this).hasClass('texture'))
            type = 'texture';
        if($(this).hasClass('pattern'))
            type = 'pattern';
        _img.push({ src:_src, nb:_nb, wb:_wb, style:$(elm_img).attr('style') });
        product_objects.push({uid:_uid, _type:type, def_qty:_def_qty, gst_tb:_gst_tb, left:product_left,top:product_top,style:style,matrix:_matrix,zindex:_zindex,handle:_handle, angle:_angle, opacity:_opacity, text:_text, rgb:_rgb, cls: 'unselected', img:_img});
    });
    $('.template').each(function(){
        var elm = $(this);
        var elm_offset = elm.offset();
        var elm_left = elm_offset.left;
        var elm_top = elm_offset.top;
        var product_left = Math.round(elm_left-canvas_left);
        var product_top = Math.round(elm_top-canvas_top);
        var filter = {};
        if($.browser.msie && $.browser.version == 7.0){
            filter = {'filter':'none'};
        }else if($.browser.msie && $.browser.version == 8.0){
            filter = {'msfilter':'none','-ms-filter':'none'};
        }
        $(this).css(filter);
        var style = $(this).attr('style');
        var _zindex = $(this).css('z-index');
        var _matrix = [];
        _matrix.push($.parseJSON($(this).attr('_matrix')));        
        var _img = [];
        var elm_img = $(this).find('img');
        var _src = $(elm_img).attr('src');
        var _nb = $(elm_img).attr('_nb');
        var _wb = $(elm_img).attr('_wb');
        var _cls = $(elm_img).attr('class');
        var _handle = $(this).attr('_handle');
        var _uid = $(this).attr('_uid');
        var _def_qty = $(this).attr('def_qty');
        var _gst_tb = $(this).attr('gst_tb');
        var _angle = 0;
        if($(this).attr('_angle')){            
            _angle = $(this).attr('_angle');
        } else if($(this).attr('angle')) {
            _angle = $(this).attr('angle');            
        }
        var _opacity = $(this).attr('_opacity')?$(this).attr('_opacity'):100;
        var _text = $(this).attr('_text')?escape($(this).attr('_text')):'';
        var _rgb = $(this).attr('_rgb')?$(this).attr('_rgb'):'';
        var type = 'box';
        if($(this).hasClass('text'))
            type = 'text';
        if($(this).hasClass('image'))
            type = 'image';
        if($(this).hasClass('border'))
            type = 'border';
        if($(this).hasClass('shape'))
            type = 'shape';
        if($(this).hasClass('texture'))
            type = 'texture';
        if($(this).hasClass('pattern'))
            type = 'pattern';

        var _spantext = '';
        if(type=='box'){
            _spantext = $('span',this).text();
        }

        _img.push({ src:_src, nb:_nb, wb:_wb, style:$(elm_img).attr('style'), cls:_cls, uid:$(elm_img).attr('_uid') });
        product_objects.push({uid:_uid, _type:type, def_qty:_def_qty, gst_tb:_gst_tb, left:product_left,top:product_top,style:style,matrix:_matrix,zindex:_zindex,handle:_handle, angle:_angle, opacity:_opacity, text:_text, rgb:_rgb, cls: 'template', spantext:_spantext, img:_img});
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
    for(var key in obj){
        if(obj.hasOwnProperty(key)){
            keys.push(key);
        }
    }
    return keys;
}

function setProductPositions(func) {

    var product_objects = '';
    var embellishment_objects = '';
    var template_objects = '';

    var clonedObject = $('.product.unselected').clone();
    var clonedObject2 = $('.embellishment.unselected').clone();
    var clonedObject3 = $('.template').clone();

    clonedObject.each(function(e){
        $(this).removeClass('selected');
        product_objects += $(this).prop('outerHTML');

    });

    clonedObject2.each(function(e){
        $(this).removeClass('selected');
        embellishment_objects += $(this).prop('outerHTML');

    });

    clonedObject3.each(function(e){
        template_objects += $(this).prop('outerHTML');

    });    

    var cloned_table = $('.table').clone();

    $('.dynamic_qty').each(function(e){

        var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
        cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

    });

    $.ajax({
        url: SET_PRODUCT_POSITION_URL,
        type: "POST",
        data: { guests: $('#guests').val(),tables: $('#tables').val(), buy_table_html: cloned_table.html(),action_url: action_url, total: total, quantity: quantity, selected_prev_prod_qty: selected_prev_prod_qty, obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects, template_objects: template_objects },
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
        $('#canvas').append(PRODUCT_POSITIONS['template_objects'])

        $('.table').html(PRODUCT_POSITIONS['buy_table_html']);
        $('#tables').val(PRODUCT_POSITIONS['tables']);
        $('#guests').val(PRODUCT_POSITIONS['guests']);

        attachEventToQty();
        manage_subtotal();
        manage_total();
    }

    var product_objects = '';
    var embellishment_objects = '';
    var template_objects = '';
    var clonedObject = $('.product.unselected').clone();
    var clonedObject2 = $('.embellishment.unselected').clone();
    var clonedObject3 = $('.template').clone();

    clonedObject.each(function(e){
        $(this).removeClass('selected');
        product_objects += $(this).prop('outerHTML');

    });

    clonedObject2.each(function(e){
        $(this).removeClass('selected');
        embellishment_objects += $(this).prop('outerHTML');

    });

    clonedObject3.each(function(e){
        template_objects += $(this).prop('outerHTML');

    });

    var cloned_table = $('.table').clone();

    $('.dynamic_qty').each(function(e){

        var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
        cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

    });

    changesArray.push({ guests: $('#guests').val(),tables: $('#tables').val(), buy_table_html: cloned_table.html(),action_url: action_url, total: total, quantity: quantity, selected_prev_prod_qty: selected_prev_prod_qty, obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects, template_objects: template_objects });
    
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
    $('.template').remove();
    $('#canvas').append(pos['product_objects']);
    $('#canvas').append(pos['embellishment_objects']);
    $('#canvas').append(pos['template_objects']);
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

        if($('.template').length > 0) {
            box_droppable();
        }
        
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

        if($('.template').length > 0) {
            box_droppable();
        }

        eventTracker($('#canvas'),'redo');
    }
}

function change_cursor(option){
    
    var type = $.parseJSON($('.selected').attr('_matrix'));
    var handles = [];
    if($.isArray(option)){
        handles = option;
    }else{
        var options = option.split(',');
        handles = options;
    }
    
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
    var warning = 'Warning! Canvas reached its 50-item limit. No additional items can be added.';
    if(objCounter < 1){
        $('.nwMenus').hide();
        $('#canvas').css('background-image','url(/media/images/canvasbg.jpg)');
    }else if(objCounter > 49){
        if($('#canvas').hasClass('ui-droppable')){
            $("#canvas").droppable('destroy');
            $('#clone-btn').addClass('cloneFalse');
        }
        $('#canvas').css('background-image','none');
        $('#object-counter').text(warning).show();
        $('.nwMenus').show();
        //$('#save').unbind('click');
    }else{
        droppable_all();
        $('#clone-btn').removeClass('cloneFalse');
        $('#canvas').css('background-image','none');
        $('#object-counter').hide();
        $('.nwMenus').show();
    }
}

function getUrlVars(strURL) {
    var vars = {};
    
    var parts = strURL.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });

    return vars;
}

//centering droped template

function make_center_template(){
    var percent         = 100;
    var box             = computeBboxDimension_template();
    var canvas_Width    = $('#canvas').width();
    var canvas_Height   = $('#canvas').height();
    var box_Height      = box.height;
    var box_Width       = box.width;
    var box_lowestLeft  = box.lowestLeft;
    var box_lowestTop   = box.lowestTop;
    var new_box_width   = canvas_Width;
    var new_box_height  = canvas_Height;
    var plus_top        = 0;
    var plus_left       = 0;

    if((canvas_Width < box_Width) || (canvas_Height < box_Height)){
        var width_diff      = box_Width-canvas_Width;
        var height_diff     = box_Height-canvas_Height;
        var ratio           = box_Width/box_Height;//aspect ratio of bounding box
        
        if(width_diff >= height_diff){
            new_box_width   = canvas_Width;
            new_box_height  = new_box_width/ratio;
            percent         = new_box_width/box_Width;
            plus_top        = (canvas_Height/2)-(new_box_height/2);
        }else{
            new_box_height  = canvas_Height;
            new_box_width   = new_box_height*ratio;
            percent         = new_box_width/box_Width;
            plus_left       = (canvas_Width/2)-(new_box_width/2);
        }

        $('#canvas .template').each(function(){
            var each_aspect         = do_aspectratio_wRespect_template($(this).width(),$(this).height(),percent);
            var present_top         = parseFloat($(this).css('top'));
            var present_left        = parseFloat($(this).css('left'));

            var at_zeroX_axis       = present_left-box_lowestLeft;
            var old_width           = box_Width;
            var new_width           = new_box_width;
            var each_percentX       = at_zeroX_axis/old_width;
            var at_zeroY_axis       = present_top-box_lowestTop;
            var old_height          = box_Height;
            var new_height          = new_box_height;
            var each_percentY       = at_zeroY_axis/old_height;

            $(this).css({
                width:each_aspect.width,
                height:each_aspect.height,
                top: (new_height*each_percentY)+plus_top,
                left:(new_width*each_percentX)+plus_left
            });
        });

    }else{
        var ctr_diff = canvas_bb_ctr_diff_template(box.centerY,box.centerX);

        $('#canvas .template').each(function(){
            $(this).css({
                top:parseFloat($(this).css('top'))+ctr_diff.y,
                left:parseFloat($(this).css('left'))+ctr_diff.x
            });
        });
    }

}

function canvas_bb_ctr_diff_template(box_centerY, box_centerX){
    var ctr_diff    = {};
    ctr_diff['x']   = $('#canvas').width()/2 - box_centerX;
    ctr_diff['y']   = $('#canvas').height()/2 - box_centerY;

    return ctr_diff;
}

function do_aspectratio_wRespect_template(width, height, percent){
    
    var dimension = {};
    var aspectRatio = height/width;
    dimension['width'] = width*percent;
    dimension['height'] = aspectRatio*dimension['width'];

    return dimension;
}

function computeBboxDimension_template() {

    var lowestTop = 0;
    var highestTop = 0;
    var lowestLeft = 0;
    var highestLeft = 0;
    var finalWidth = 0;
    var finalHeight = 0;

    $('#canvas .template').each(function(e){
            
        if(lowestTop == 0) {
            lowestTop = parseFloat($(this).css('top').replace('px',''));
        } else {
            if(parseFloat($(this).css('top').replace('px','')) < lowestTop) {
                lowestTop = parseFloat($(this).css('top').replace('px',''));
            }
        }
        
        if(highestTop == 0) {
            highestTop = parseFloat($(this).css('top').replace('px','')) + parseFloat($(this).css('height').replace('px',''));
        } else {
            if((parseFloat($(this).css('top').replace('px','')) + parseFloat($(this).css('height').replace('px',''))) > highestTop) {
                highestTop = parseFloat($(this).css('top').replace('px','')) + parseFloat($(this).css('height').replace('px',''));
            }
        }

        if(lowestLeft == 0) {
            lowestLeft = parseFloat($(this).css('left').replace('px',''));
        } else {
            if(parseFloat($(this).css('left').replace('px','')) < lowestLeft) {
                lowestLeft = parseFloat($(this).css('left').replace('px',''));
            }
        }

        if(highestLeft == 0) {
            highestLeft = parseFloat($(this).css('left').replace('px','')) + parseFloat($(this).css('width').replace('px',''));
        } else {
            if((parseFloat($(this).css('left').replace('px','')) + parseFloat($(this).css('width').replace('px',''))) > highestLeft) {
                highestLeft = parseFloat($(this).css('left').replace('px','')) + parseFloat($(this).css('width').replace('px',''));
            }
        }
            
            
    });
    
    finalWidth = highestLeft - lowestLeft;
    finalHeight = highestTop - lowestTop;
    
    return {
        'width':finalWidth,
        'height':finalHeight,
        'centerX':finalWidth / 2 + lowestLeft,
        'centerY':finalHeight / 2 + lowestTop,
        'lowestLeft':lowestLeft,
        'lowestTop':lowestTop
    };

}

// Rotate Element to the Given Degree
rotate_global = function(degree) {
    var cos = parseFloat(parseFloat(Math.cos(degToRad_global(-degree)))),
        sin = parseFloat(parseFloat(Math.sin(degToRad_global(-degree)))),
        mtx = {a:cos, b:sin, c:(-sin), d:cos};
        
    return mtx;
};

degToRad_global = function(d) {
    return (d * (Math.PI / 180));
};

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
