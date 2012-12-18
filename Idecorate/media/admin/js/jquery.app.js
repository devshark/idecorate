$handles   = $('.handles');
$img_menus = $('.neMenus');
objCounter = 0;
uniqueIdentifier = 1;
changesCounter = 0;
changesArray = [];
changesCurrentPosition = 0;
var handles = 'ne,se,nw,sw,n,e,s,w';
var aspectR = true;
var slideValue = 0;
DEFAULT_TEXT_E = "I Love iDecorate";

$(document).ready(function () {

    if($.browser.msie && $.browser.version == 7.0) {

        $(".draggable").liveDraggable({
            revert: true,
            helper: function(e) {
                active_object = $(this).clone();
                return $(active_object).find('img').attr('id','');
            },
            containment: 'body'

        });

    } else {

        $(".draggable").liveDraggable({
            revert:true, 
            helper: 'clone',
            containment: 'body'
        });

    }

    $("#canvas").droppable({

        drop: function (e, ui) {


            if ($(ui.draggable)[0].id != "") {

                ui.helper.remove();
                //recreate an object based on dropped object
                var Obj = $(ui.draggable)[0];

                //set this oject to jquery
                Obj = $(Obj);

                if(Obj.hasClass('em')){

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
            }else if($(this).hasClass('box')){
                update_menu($(this), true);
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
            }else if($(this).hasClass('box')){
                update_menu($(this), true);
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

    //initialize object saved on session
    initProductPositions();

    //hide handles and menus
    $(document).click(function(e){
        var click =  $.contains($('#canvas .handles, #canvas .handles .handle')[0],e.target) ? true : e.target == $('#canvas .handles');
        
        if(!click){
            remove_handles(e);
            eventTracker(e.target, 'unselect');
        }

    }).keydown(function(e){
        
        if(!$.browser.mozilla) {
            if((e.keyCode == 8 || e.keyCode == 46) && $('.selected').length > 0 && e.target.type != 'textarea' && e.target.type != 'text') {
                e.preventDefault();
                $('#remove-btn').trigger('click');
            }
        }
    });

    //REMOVE PRODUCT IN FIREFOX
    $('html').keypress(function(e){

        if($.browser.mozilla) {
            if((e.keyCode == 8 || e.keyCode == 46) && $('.selected').length > 0 && e.target.type != 'textarea' && e.target.type != 'text') {
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

    $('#new').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        new_canvas($(this).attr('href'));
    });

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

    $("#text-change-template").on('click mousedown',function(e){
        cancelBubble(e);
    });

    $("#canvas").on('click mousedown','.box',function(e){
        cancelBubble(e);
        update_text_template($(this).find('span').text());
    });

    $('#text-update-template').click(function(e){
        cancelBubble(e);
        update_text_on_box($('#text-change-template').val());
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

    $('#text-change, #text-update, #text-update-template').click(function(e){
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

        $('#canvas').on('click mousedown', '.embellishment.shape,.embellishment.pattern,.embellishment.text,.embellishment.texture, .unselected.box', function(e){
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

            $('#canvas').on('click mousedown', '.embellishment.shape,.embellishment.pattern,.embellishment.text,.embellishment.texture, .unselected.box', function(e){
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

    if($.browser.msie && $.browser.version < 9.0){
        setTimeout('ie_message()',2500);
    }

    $('#createBox').click(function(e){
        e.preventDefault();
        cancelBubble(e);
        //crete container for as product placeholder on template
        create_box();
    });

});

function update_text_template(text){
    $('#text-change-template').val(text);
}

function update_text_on_box(text_value){
    $('.selected').find('span').html(text_value);
    eventTracker($('.selected'),'update_text_box');
}

function create_box(){
    var object      = $('<div/>');
    var appendObj   = $('<span/>');
    var attribute   = {'class':'unselected box'};
    var style       = {zIndex:objCounter+1,width:120, height:120,position:'absolute',top:'40%',left:'40%'};

    appendObj.text('add text here.');
    object.attr(attribute).css(style).append(appendObj);
    if($.browser.msie){
        object.append('<img src="/media/admin/img/fake_BG.png" width="100%">');
    }
    object.appendTo('#canvas');

    if(!object.hasClass('selected')){
        object.addClass('selected').siblings('.unselected').removeClass('selected');
        object.attr('_matrix', '{"a":1, "b":0, "c":0, "d":1,"e":false,"f":false}');
        object.attr('_handle', ['nw','sw','se','ne','w','s','e','n']);
        
        //set handles direction 
        change_cursor(['nw','sw','se','ne','w','s','e','n']);

        set_ctr_attr(object);
        transform(object);
        embellishment_handle_set(100);
    }
    update_menu(object,true);
    hide_canvas_menu();

    $('#text-change-template').val('add text here.');

    objCounter++;

    eventTracker(object,'create_box');

    return object;
}

//message in ie
function ie_message() {
    //view message if ie version < 9
    alert('Sorry! Your browser does not support the following functionalities:  rotate, flip, flop, transparency changes, and personalizing style boards.\nPlease use one of the following browsers: Chrome, Firefox, Safari, or try upgrading your Internet Explorer to version 9.');
}

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
        'src': '/media/embellishments/template/'+fname
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
    if($('.selected').hasClass('shape') || $('.selected').hasClass('texture') || $('.selected').hasClass('pattern') || $('.selected').hasClass('box')){
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

function new_canvas(url){
    var r = confirm("Are you sure you want to discard your changes?");
    if (r){
        window.location = url;
    }else{
        return false;
    }
}

//embelishments functions end
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

function update_menu(obj,img_menu){

    img_menu = img_menu ? img_menu : false;
    
    $img_menus.show();

    if(img_menu){
        $('.imgBgControlWrap').hide();
        if(obj.hasClass('image') || obj.parent().hasClass('image') || obj.parent().hasClass('border') || obj.hasClass('border')){
            $('.colorAdjustment').hide();
        }else if(obj.hasClass('box')){
            $('.colorAdjustment').show();
            $('#text-change-template-wrap').show().siblings().hide();
        }else{
            $('.colorAdjustment').show();
            $('#text-change-template-wrap').hide().siblings().show();
            if(obj.hasClass('text') || obj.parent().hasClass('text')){
                $('#text-change-wrap').show();
                $('#opacity-control-wrap').css({'width':'184px'});
            }else{
                $('#text-change-wrap').hide();
                $('#opacity-control-wrap').css({'width':'334px'});
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

function aspectratio(width, height, percent){

    var dimension = new Array();
    var aspectRatio = height/width;
    dimension['width'] = width*percent;
    dimension['height'] = aspectRatio*dimension['width'];

    return dimension;
}

function hide_canvas_menu(){
    var warning = 'WARNING!!! Object inside the canvas exceed the 50 item limit: '+objCounter+' items.';
    if(objCounter < 1){
        $('.nwMenus').hide();
        //$('#canvas').css('background-image','url(/media/images/canvasbg.jpg)');
    }else if(objCounter > 50){
        $('#canvas').css('background-image','none');
        $('#object-counter').text(warning).show();
        $('.nwMenus').show();
        $('#save').unbind('click');
    }else{
        $('#canvas').css('background-image','none');
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

function set_ctr_attr(obj){

    x = parseFloat(parseFloat(obj.offset().left + obj.width() * 0.5));
    y = parseFloat(parseFloat(obj.offset().top + obj.height() * 0.5));
    if($.browser.msie && $.browser.version < 9.0){

    }
    $handles.attr({'ctr':'{"x":'+x+',"y":'+y+'}'});
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

function eventTracker(currentObject, eventType) {
    //console.log(eventType);
    if(eventType != 'unselect' && eventType != 'undo' && eventType != 'redo') {

        var product_objects = '';
        var embellishment_objects = '';
        var box_objects = '';

        var clonedObject = $('.product.unselected').clone();
        var clonedObject2 = $('.embellishment.unselected').clone();
        var clonedObject3 = $('.box.unselected').clone();

        clonedObject.each(function(e){
            $(this).removeClass('selected');
            product_objects += $(this).prop('outerHTML');

        });

        clonedObject2.each(function(e){
            $(this).removeClass('selected');
            embellishment_objects += $(this).prop('outerHTML');

        });

        clonedObject3.each(function(e){
            $(this).removeClass('selected');
            box_objects += $(this).prop('outerHTML');

        });

        //var cloned_table = $('.table').clone();
        /**
        $('.dynamic_qty').each(function(e){

            var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
            cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

        });
        **/

        if(changesCounter != (changesArray.length - 1)) {
            changesArray.splice(changesCounter + 1, changesArray.length - changesCounter);
        }

        changesArray.push({ obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects, box_objects: box_objects });
        changesCounter++;
    }

    setProductPositions();
}

function setProductPositions(func) {

    var product_objects = '';
    var embellishment_objects = '';
    var box_objects = '';

    var clonedObject = $('.product.unselected').clone();
    var clonedObject2 = $('.embellishment.unselected').clone();
    var clonedObject3 = $('.box.unselected').clone();


    clonedObject.each(function(e){
        $(this).removeClass('selected');
        product_objects += $(this).prop('outerHTML');

    });

    clonedObject2.each(function(e){
        $(this).removeClass('selected');
        embellishment_objects += $(this).prop('outerHTML');

    });


    clonedObject3.each(function(e){
        $(this).removeClass('selected');
        box_objects += $(this).prop('outerHTML');

    });

    /**
    var cloned_table = $('.table').clone();

    $('.dynamic_qty').each(function(e){

        var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
        cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

    });
    **/

    $.ajax({
        url: SET_TEMPLATE_POSITION_URL,
        type: "POST",
        data: { obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects,box_objects: box_objects },
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

function cancelBubble(e) {
    var evt = e ? e:window.event;
    if (evt.stopPropagation)    evt.stopPropagation();
    if (evt.cancelBubble!=null) evt.cancelBubble = true;
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

function updateZIndex(obj) {

    var currentZIndex = parseInt(obj.css('z-index'));

    $('.unselected').each(function(e){
        if(parseInt($(this).css('z-index')) > currentZIndex) {
            $(this).css('z-index', (parseInt($(this).css('z-index')) - 1));
        }
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

function initProductPositions() {
    if(TEMPLATE_POSITIONS != '') {
        uniqueIdentifier = parseInt(TEMPLATE_POSITIONS['unique_identifier']);
        objCounter = parseInt(TEMPLATE_POSITIONS['obj_counter']);
        changesCounter = parseInt(TEMPLATE_POSITIONS['changes_counter']);

        $('#canvas').append(TEMPLATE_POSITIONS['product_objects']);
        $('#canvas').append(TEMPLATE_POSITIONS['embellishment_objects']);
        $('#canvas').append(TEMPLATE_POSITIONS['box_objects']);

    }

    var product_objects = '';
    var embellishment_objects = '';
    var box_objects = '';
    var clonedObject = $('.product.unselected').clone();
    var clonedObject2 = $('.embellishment.unselected').clone();
    var clonedObject3 = $('.box.unselected').clone();

    clonedObject.each(function(e){
        $(this).removeClass('selected');
        product_objects += $(this).prop('outerHTML');

    });

    clonedObject2.each(function(e){
        $(this).removeClass('selected');
        embellishment_objects += $(this).prop('outerHTML');

    });

    clonedObject3.each(function(e){
        $(this).removeClass('selected');
        box_objects += $(this).prop('outerHTML');

    });

    changesArray.push({ obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: 0, product_objects: product_objects, embellishment_objects: embellishment_objects, box_objects: box_objects });
    
}

function changeProductPositions(pos) {

    remove_handles($.event);

    uniqueIdentifier = parseInt(pos['unique_identifier']);
    objCounter = parseInt(pos['obj_counter']);
    //changesCounter = parseInt(pos['changes_counter']);

    $('.product.unselected').remove();
    $('.embellishment.unselected').remove();
    $('.box.unselected').remove();
    $('#canvas').append(pos['product_objects']);
    $('#canvas').append(pos['embellishment_objects']);
    $('#canvas').append(pos['box_objects']);

}

function undo_styleboard() {
    if(changesCounter > 0) {
        changesCounter--;
        changeProductPositions(changesArray[changesCounter]);

        //styleboardH();
        
        eventTracker($('#canvas'),'undo');
    }
}

function redo_styleboard() {
    if(changesCounter < (changesArray.length - 1)) {
        changesCounter++;
        changeProductPositions(changesArray[changesCounter]);

        //styleboardH();

        eventTracker($('#canvas'),'redo');
    }
}

function closed_modal(){
    $('#page-mask').hide();
    $('#modal-save-styleboard-window').hide();
}

function get_template_object_json(){
    var template_objects = [];
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
        var _angle = $(this).attr('_angle')?$(this).attr('_angle'):0;
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
        template_objects.push({uid:_uid, _type:type, def_qty:_def_qty, gst_tb:_gst_tb, left:product_left,top:product_top,style:style,matrix:_matrix,zindex:_zindex,handle:_handle, angle:_angle, opacity:_opacity, text:_text, rgb:_rgb, img:_img});
    });
    var product_array = new Array();
    for (var i in template_objects){
        var x = template_objects[i].zindex;
        product_array[x-1] = template_objects[i];
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

function saved_template(){
    closed_modal();
    alert('Template saved.');
    $('.unselected').each(function(){
        $(this).remove();
    });
}

//extending default jquery
(function ($) {
    //makes dynamic element draggable
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