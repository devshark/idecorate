$handles   = $('.handles');
$img_menus = $('.neMenus');
objCounter = 0;
lassoStart = false;
lassoCoordinate = {startX: 0, startY: 0};
uniqueIdentifier = 1;
changesCounter = 0;

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
    $(".draggable").draggable({
        revert:true, 
        helper: 'clone'
    });

    //set dropable area for the draggable sidebar objects
    $("#canvas").droppable({

        drop: function (e, ui) {

            if ($(ui.draggable)[0].id != "") {

                ui.helper.remove();
                //recreate an object based on dropped object
                var Obj = $(ui.draggable)[0];

                //set this oject to jquery
                Obj = $(Obj);

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
                        // img_wo_bg_w = data.no_background_w;
                        // img_wo_bg_h = data.no_background_h;

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

            }
        }
    }).mousemove(function(e){
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
        //e.preventDefault();
        //remove_handles(e);
        if($('.selected').length == 0) {

            var x = e.pageX - $(this).offset().left;
            var y = e.pageY - $(this).offset().top;
            lassoCoordinate.startX = x;
            lassoCoordinate.startY = y;
            lassoStart = true;   
        }

    }).mouseup(function(e){
        //console.log('up');
        //e.preventDefault();
        lassoStart = false;
        var x = e.pageX - $(this).offset().left;
        var y = e.pageY - $(this).offset().top;
        lassoCoordinate.startX = 0;
        lassoCoordinate.startY = 0;
        $('#lasso').width(0);
        $('#lasso').height(0);
        $('#lasso').css('display', 'none');
    }).change(function(e){
        //console.log('changed');
    });

    //drag the selected product together with its handle on the fly
    $('.product').liveDraggable({
        helper: 'original',
        cursor: 'move',
        start : function(e, ui){
            update_ui({
                styles:{
                    display: 'block',
                    top: $(this).css('top'),
                    left: $(this).css('left'),
                    width: $(this).css('width'),
                    height: $(this).css('height')
                }
            });
        },
        drag : function(e, ui){
            update_ui({
                styles:{
                    display: 'block',
                    top: $(this).css('top'),
                    left: $(this).css('left'),
                    width: $(this).css('width'),
                    height: $(this).css('height')
                }
            });
        },
        stop : function(e, ui){
            update_ui({
                styles:{
                    display: 'block',
                    top: $(this).css('top'),
                    left: $(this).css('left'),
                    width: $(this).css('width'),
                    height: $(this).css('height')
                }
            });


            //track event
            eventTracker($(this),'move');

        }
    });

    //onmouse down show handles for selected product
    $('#canvas').on('mousedown','.product',function(e){

        update_menu($(this).find('img'));

        if(!$(this).hasClass('selected')){

            $(this).addClass('selected').siblings().removeClass('selected');

            update_ui({
                styles:{
                    display: 'block',
                    top: $('.selected').css('top'),
                    left: $('.selected').css('left'),
                    width: $('.selected').css('width'),
                    height: $('.selected').css('height')
                }
            });
        }

        disableEventPropagation(e);
    });

    //draggable handles binds style on selected obj
    $handles.draggable({
        helper: 'original',
        cursor: 'move',
        start: function(e, ui){

            update_ui({
                styles:{
                    display: 'block',
                    top: $(this).css('top'),
                    left: $(this).css('left'),
                    width: $(this).css('width'),
                    height: $(this).css('height')
                },
                update_obj : $('.selected')
            });

        },
        drag: function(e, ui){

            update_ui({
                styles:{
                    display: 'block',
                    top: $(this).css('top'),
                    left: $(this).css('left'),
                    width: $(this).css('width'),
                    height: $(this).css('height')
                },
                update_obj : $('.selected')
            });

        },
        stop: function(e, ui){

            update_ui({
                styles:{
                    display: 'block',
                    top: $(this).css('top'),
                    left: $(this).css('left'),
                    width: $(this).css('width'),
                    height: $(this).css('height')
                },
                update_obj : $('.selected')
            });
            //track event
            eventTracker($('.selected'),'move');

            //track event
            eventTracker($(this),'move');

        }
    }).resizable({

        handles: 'ne,se,nw,sw',
        minWidth: 50,
        aspectRatio: true,
        start : function(e, ui){

            $(".draggable").draggable('destroy');
            $(".draggable").draggable({
                revert:true, 
                helper: 'clone'
            });
        },
        resize: function(e, ui){
            update_ui({
                styles:{
                    top: $(this).css('top'),
                    left: $(this).css('left'),
                    width: $(this).css('width'),
                    height: $(this).css('height')
                },
                update_obj : $('.selected, .selected img')
            });
        },
        stop : function(e, ui){

            $(".draggable").draggable({
                revert:true, 
                helper: 'clone'
            });

            //track event
            eventTracker($('.selected'),'resize');

        }
    });

    //hide handles and menus
    $(document).click(function(e){

        var click =  $.contains($('#canvas .handles')[0],e.target) ? true : e.target == $('#canvas .handles');
        
        if(!click){
            remove_handles(e);
            eventTracker(e.target, 'unselect');
        }

    }).keydown(function(e){
        //console.log(e.keyCode);
        if((e.keyCode == 8 || e.keyCode == 46) && $('.selected').length > 0) {
            //alert('test');
            e.preventDefault();
            $('#remove-btn').trigger('click');
        }
    });

    //remove selected obj
    $('#remove-btn').click(function(e){
        e.preventDefault();
        objCounter--;
        updateZIndex($('.selected'));
        
        var selected_uid = $('.selected').attr('_uid');
        var count = 0;
        $('.unselected').each(function(){
            if (selected_uid == $(this).attr('_uid'))
                count++;
        });
        if (count<=1)
            remove_from_cart(parseInt(selected_uid,10));

        var removedElement = $('.selected');

        $('.selected').remove();

        eventTracker(removedElement,'remove');

    });

    //forward selected obj
    $('#forward-btn').click(function(e){
        e.preventDefault();
        disableEventPropagation(e);
        obj = $('.selected');
        moveNext(obj);
    });

    //backward selected obj
    $('#backward-btn').click(function(e){
        e.preventDefault();
        disableEventPropagation(e);
        obj = $('.selected');
        moveBack(obj);
    });

    //clone selected obj
    $('#clone-btn').click(function(e){
        e.preventDefault();
        disableEventPropagation(e);
        obj = $('.selected');
        cloneObj(obj);
    });

    //make selected product image PNG
    $('#transBg-btn').click(function(e){
        e.preventDefault();
        disableEventPropagation(e);
        if($('.selected').length == 1){change_img($('.selected'),false);}

    });

    //make selected product image JPG
    $('#whiteBg-btn').click(function(e){
        e.preventDefault();
        disableEventPropagation(e);

        if($('.selected').length == 1){change_img($('.selected'),true);}

    });

    // create custom image crop
    $('#customBg-btn').click(function(e){
        e.preventDefault();
        disableEventPropagation(e);
        display_modal(MODAL_SRC.replace('0',$('.selected > img').attr('src').replace('/media/products/','')));
    });

    // close modal
    $('#close-modal').click(function(e){
        e.preventDefault();
        disableEventPropagation(e);
        close_modal();
    });

    //dont remove handles and selected object when modal window is displayed
    $('#modal-window, #page-mask').click(function(e){
        disableEventPropagation(e);
    });

    initProductPositions();

});

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

        //display handles based on the dropped position of created instance
        update_ui({
            styles:{
                display: 'block',
                top: imgTop,
                left: imgLeft,
                width: dimensions['width'],
                height: dimensions['height']
            }
        });

        update_ui({
            styles:{
                width               : dimensions['width'],
                height              : dimensions['height'],
                top                 : '',
                left                : '',
                '-moz-transform'    : '',
                '-o-transform'      : '',
                '-webkit-transform' : '',
                '-ms-transform'     : '',
                'transform'         : '',
                'filter'            : '',
                '-ms-filter'        : ''
            },
            update_obj: $('.fakeHandle')
        });
        
        //append to canvas the newly created instance
        setTimeout(function(){
            append_to_canvas(options._event,object,objCounter);
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

function append_to_canvas(event, obj, index){

    object = obj;
    object.appendTo('#canvas');
    object_top = event.pageY-$('#canvas').offset().top-object.height()/2;
    object_left = event.pageX-$('#canvas').offset().left-object.width()/2;
    object.css({top : object_top, left: object_left, zIndex: index });
    object.attr('object_id',uniqueIdentifier);
    uniqueIdentifier++;
    if(object.hasClass('selected')){object.siblings('.unselected').removeClass('selected');}

    //track event
    //eventTracker(object,'create');

    return object;
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
        if($('.product').hasClass('selected')){
            $('.product').removeClass('selected');
            return true;
        }
    
    }
}

function update_menu(obj){
    
    update_ui({
        styles : {
            display : 'block'
        },
        update_obj : $img_menus
    });

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

function update_ui(options) {

    var defaults = {   
            styles :{
                display: '',
                top : 0,
                left: 0,
                //zIndex: '',
                width: '',
                height: '',
                '-moz-transform'   : 'none',
                '-o-transform'     : 'none',
                '-webkit-transform': 'none',
                '-ms-transform'    : 'none',
                'transform'        : 'none',
                'filter'           : 'none',
                '-ms-filter'       : 'none'

            },
            update_obj : $handles
        }
        for (var key in defaults.styles) {
          if (options.styles.hasOwnProperty(key)) {
            defaults.styles[key] = options.styles[key];
          }
        }

    defaults.update_obj = options.update_obj == null ? defaults.update_obj : options.update_obj;

    defaults.update_obj.css(defaults.styles);

    return defaults.update_obj;
}

// function disableEventPropagation(event) {

//     if (event.stopPropagation) {
//     // this code is for Mozilla and Opera
//         event.stopPropagation();
//     } else if (window.event) {
//     // this code is for IE
//         window.event.cancelBubble = true;
//     }
// }

function moveNext(obj) {
        
    var currentZIndex = parseInt(obj.css('z-index'));
    var nextIndex = currentZIndex + 1;

    if(nextIndex > objCounter) {
        //cannot move
    } else {
        $('.product').each(function(e){
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
        $('.product').each(function(e){
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

    $('.product').each(function(e){
        if(parseInt($(this).css('z-index')) > currentZIndex) {
            $(this).css('z-index', (parseInt($(this).css('z-index')) - 1));
        }
    });
}

function cloneObj(obj) {

    var cloned_obj = obj.clone().appendTo('#canvas');
    objCounter++;

    cloned_obj.siblings('.product').removeClass('selected');
    cloned_obj.css({
        zIndex : objCounter,
        top : parseInt(obj.css('top'),10)+20,
        left : parseInt(obj.css('left'),10)+20
    });

    cloned_obj.attr('object_id',uniqueIdentifier);

    uniqueIdentifier++;

    update_menu(cloned_obj.find('img'));

    update_ui({
        styles:{
            display: 'block',
            top: cloned_obj.css('top'),
            left: cloned_obj.css('left'),
            width: cloned_obj.css('width'),
            height: cloned_obj.css('height')
        }
    });

    //track event
    eventTracker(cloned_obj, 'clone');
}

function eventTracker(currentObject, eventType) {

    changesCounter++;
    //console.log('Count of changes: ' + changesCounter);
    //console.log(currentObject);
    //console.log(eventType);
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

function setProductPositions(func) {

    var product_objects = '';

    var clonedObject = $('.product.unselected').clone();

    //clonedObject.;

    clonedObject.each(function(e){
        $(this).removeClass('selected');
        //$(this).removeClass('selected');
        product_objects += $(this).prop('outerHTML');

    });

    var cloned_table = $('.table').clone();

    $('.dynamic_qty').each(function(e){

        var strInput = '<input class="dynamic_qty" type="text" _pid="' + $(this).attr('_pid') + '" _pr="' + $(this).attr('_pr') + '" _cur="' + $(this).attr('_cur') + '" _gs="' + $(this).attr('_gs') + '" _dq="' + $(this).attr('_dq') + '" max-length="' + $(this).attr('max-length') + '" name="' + $(this).attr('name') + '" value="' + $(this).val() + '" placeholder="' + $(this).attr('placeholder') + '">';
        cloned_table.find('[_pid="' + $(this).attr('_pid') + '"]').replaceWith($(strInput));

    });

    $.ajax({
        url: SET_PRODUCT_POSITION_URL,
        type: "POST",
        data: { guests: $('#guests').val(),tables: $('#tables').val(), buy_table_html: cloned_table.html(),action_url: action_url, total: total, quantity: quantity, selected_prev_prod_qty: selected_prev_prod_qty, obj_counter: objCounter, unique_identifier: uniqueIdentifier, changes_counter: changesCounter, product_objects: product_objects },
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
        $('.table').html(PRODUCT_POSITIONS['buy_table_html']);
        $('#tables').val(PRODUCT_POSITIONS['tables']);
        $('#guests').val(PRODUCT_POSITIONS['guests']);

        attachEventToQty();
        manage_subtotal();
        manage_total();
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
}(jQuery));
