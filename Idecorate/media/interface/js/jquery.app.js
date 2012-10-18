$handles   = $('.handles');
$img_menus = $('.neMenus');
objCounter = 0;

$(document).ready(function () {

    //draggable sidebar obj to canvas
    $(".draggable").draggable({
        revert:true, 
        helper: 'clone'
    }).click(function(e){
        e.preventDefault();
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

                var img_src = '/media/products/';

                //get image filename from DB using product_id via ajax
                $.ajax({
                    url: PRODUCT_IMAGE_URL,
                    type: "POST",
                    data: { product_id: uid},
                    async:   false,
                    success: function(data){
                        img_src = img_src+data;
                        
                    },
                    error: function(msg) {
                    }
                });

                //create new image using image object
                var Obj_img = $('<img />').attr('src',img_src+ "?" + new Date().getTime()).hide().load(function () {
                    
                    var imgWidth    = this.width;
                    var imgHeight   = this.height;
                    var dimentions  = aspectratio(imgWidth, imgHeight, .60);
                    var imgTop      = e.pageY-$('#canvas').offset().top-dimentions['height']/2;
                    var imgLeft     = e.pageX-$('#canvas').offset().left-dimentions['width']/2;

                    //create instance of this object
                    object = create_new_instance({
                            id          : uid,
                            img         : this,
                            imgW        : dimentions['width'],
                            imgH        : dimentions['height'],
                            container   : $('<div />'),
                            addclass    : 'product unselected'
                        });

                    //show menus
                    update_menu();

                    //display handles based on the dropped position of created instance
                    update_ui({
                        styles:{
                            display: 'block',
                            top: imgTop,
                            left: imgLeft,
                            width: dimentions['width'],
                            height: dimentions['height']
                        }
                    });
                    
                    //append to canvas the newly created instance
                    setTimeout(function(){
                        append_to_canvas(e,object,objCounter);
                    },500);

                    //GLOBAL var objCounter is for setting z-index for each created instance
                    objCounter++;

                }).fadeIn(1000);
            }
        }
    });
        
    //display menus and handles onmousedown 
    //need more research on trigering draggable on mousedown using .live
    $('.product').live('mousedown',function(e){

        disableEventPropagation(e);

        update_menu();


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

        // IE related catch
        if($.browser.msie){

            $(document).unbind("click");//unbind click event

            setTimeout(function(){//bind click in document after click
                $(document).click(function(e){;

                    remove_handles(e);

                });
            },300);
        
        }
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

            update_menu();
            if($.browser.msie){//it appears that this event is not supported by IE
                $(document).unbind("click");
            }

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

            if($.browser.msie){//bind click in document after resize
                setTimeout(function(){
                    $(document).click(function(e){;
        
                        remove_handles(e);

                    });
                },300);
            }

        }
    }).resizable({

        handles: 'ne,se,nw,sw',
        minWidth: 50,
        aspectRatio: true,
        start : function(e, ui){
            if($.browser.msie){//it appears that this event is not supported by IE
                $(document).unbind("click");
            }
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
            if($.browser.msie){//bind click in document after resize
                setTimeout(function(){
                    $(document).click(function(e){;
        
                        remove_handles(e);

                    });
                },300);
            }
        }
    });

    //hide handles and menus
    $(document).click(function(e){;
        remove_handles(e);
    });

    //remove selected obj
    $('#remove-btn').click(function(e){
        e.preventDefault();
        objCounter--;
        updateZIndex($('.selected'));
        $('.selected').remove();
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
});

function create_new_instance(options){

    object = options.container;
    object.addClass(options.addclass);
    object.attr('_uid', options.id);
    object.append(options.img).width(options.imgW).height(options.imgH);
    object.find('img').width('100%').height('auto');

    if(!object.hasClass('selected')){object.addClass('selected');}
    
    return object;
}

function append_to_canvas(event, obj, index){

    obj.appendTo('#canvas');
    obj_top = event.pageY-$('#canvas').offset().top-obj.height()/2;
    obj_left = event.pageX-$('#canvas').offset().left-obj.width()/2;
    obj.css({top : obj_top, left: obj_left, zIndex: index });
    if(obj.hasClass('selected')){obj.siblings('.unselected').removeClass('selected');}

    return obj;
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

function update_menu(){
    
    update_ui({
        styles : {
            display : 'block',
        },
        update_obj : $img_menus
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
    //console.log(defaults.styles);
    //console.log(defaults.update_obj);
}

function disableEventPropagation(event) {

    if (event.stopPropagation) {
    // this code is for Mozilla and Opera
        event.stopPropagation();
    } else if (window.event) {
    // this code is for IE
        window.event.cancelBubble = true;
    }
}

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
    objCounter++;
    var cloned_obj = obj.clone().appendTo('#canvas');

    cloned_obj.siblings('.product').removeClass('selected');
    cloned_obj.css({
        zIndex : objCounter,
        top : parseInt(obj.css('top'),10)+20,
        left : parseInt(obj.css('left'),10)+20
    });

    update_menu();

    update_ui({
        styles:{
            display: 'block',
            top: cloned_obj.css('top'),
            left: cloned_obj.css('left'),
            width: cloned_obj.css('width'),
            height: cloned_obj.css('height')
        }
    });
}
