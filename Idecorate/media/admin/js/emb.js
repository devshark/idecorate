var emb_current_page = 1;
var emb_total_item_count;
var emb_page_number;
var emb_num_pages;
var emb_next_page = 1;            
var emb_item_per_page;
var emb_page_scroll_process = false;
var emb_offset = 25;
var emb_withloading = false;
var emb_total_pages;
var emb_mode_type;
var emb_search_keyword = '';
var emb_type;
var emb_item_url;
var emb_window_height;
var emb_window_width;
var emb_uploaded_filename;
var emb_error_upload = false;
var is_trigger_change = false;

$(document).ready(function(){
    emb_window_height = $(window).height();
    emb_window_width = $(window).width();
	$('#embellishment-wrap .emCat a').click(function(e){
        emb_current_page = 1;
        emb_offset = 25;
        $('#manage-template-sidebar .pagination').show();
        emb_item_url = $(this).attr('href');
        $('#manage-template-sidebar .breadcrumbWrap').html('<ul class="breadcrumb"><li><a href="#">All</a></a></li><li>></li><li>'+$(this).find('span').text()+'</li></ul>');
        $('#manage-template-sidebar .breadcrumbWrap a').bind('click',function(e){
            $('#embellishment-wrap .emCat').show();
            $('#embellishment-wrap .emItem').hide();
            $('#embellishment-wrap .emItem a').each(function(){
                $(this).remove();
            });
            $('#manage-template-sidebar .breadcrumbWrap').html('');
            $('#manage-template-sidebar .pagination').hide();
            e.preventDefault();
        });
        emb_type = $(this).attr('rel');
        get_embellishment_items();
        e.preventDefault();
        return false;
    });
    $(window).resize(function(){
        _resize_embellisment();
    });

    $('#form_submit_button').click(function(){
        var f = $('#picture').val();
        if (!emb_error_upload && f.length>0){            
            if($('#upload-emb-error').length>0)
                $('#upload-emb-error').remove();            
            var extension = f.substr( (f.lastIndexOf('.') +1) ).toLowerCase();
            if (extension == 'jpg' || extension == 'jpeg' || extension == 'png' || extension == 'gif' || extension == 'tif'){                
                $('#X-Progress-ID').val(gen_uuid());
                var options = {
                    dataType: 'html',
                    url: EMBELLISHMENT_UPLOAD_ACTION + '?X-Progress-ID='+$('#X-Progress-ID').val(), 
                    beforeSubmit:  showRequestEmbellishment,           
                    success: showResponseEmbellishment
                }
                $('#upload-embel').ajaxSubmit(options); 
            } else {
                $('#form_submit_button').after('<span id="upload-emb-error" style="color:#ff0000; font-size:12px;"> File not supported.</span>');
            }           
        }
        return false;
    });    
    
    if($.browser.safari || $.browser.msie){
        $('#btn-from-my-computer').hide();
        $('#uploadImage .file-wrapper input[type=file]').css({
            'opacity': 100,
            'filter': 'alpha(opacity=100)',
            '-ms-filter': "alpha(opacity=0)",
            '-khtml-opacity': 100,
            '-moz-opacity': 100,
            'position':'relative',
            'font-size': 14
        });
        $('#form_submit_button').show();
    } else {
        $('#uploadImage input[type=file]').change(manage_upload);
    }

    $('#manage-template-sidebar #embellishment-wrap .emItem').on('mousewheel',function(event,delta){                
        emb_offset = emb_item_per_page;
        if (delta > 0){
            if (emb_current_page != 1){
                emb_current_page = emb_current_page-1;
                emb_next_page = emb_current_page;
                emb_withloading = true;
                populate_embellishment_by_page()
            }
        } else {
            if(emb_current_page != emb_total_pages){
                emb_current_page = emb_current_page+1;
                emb_next_page = emb_current_page;
                emb_withloading = true;
                populate_embellishment_by_page();                        
            }
        }
        $('#manage-template-sidebar .pagination .cur-page').removeClass('cur-page');
        $('#emb-page-number-' + emb_current_page).addClass('cur-page');
        generate_embellishment_pagination();
    });
});

function manage_upload(e) {
    is_trigger_change  = true;
    if($('#upload-emb-error').length>0)
        $('#upload-emb-error').remove();

    if(!$.browser.msie && !$.browser.safari){
        if (this.files[0].size>MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE){
            $('#form_submit_button').after('<span id="upload-emb-error" style="color:#ff0000; font-size:12px;"> Please keep filesize under 2MB. Current filesize '+ (this.files[0].size/1024/1024).toFixed(2) +'MB</span>');
            emb_error_upload = true;
        } else {
            emb_error_upload = false;
        }
    }

    $('#form_submit_button').show();
    if ($.browser.msie || $.browser.safari){
        $(this).blur();    
    }
    var val = $(this).val(),
    valArray = val.split('\\'),
    newVal = valArray[valArray.length-1],
    button = $('#btn-from-my-computer'),
    fakeFile = $('#manage-template-sidebar .file-wrapper .file-holder');    
    if(newVal !== '') {        
        if($(fakeFile).length === 0) {
            $(button).after('<span class="file-holder">' + newVal + '</span>');
        } else {
            $(fakeFile).text(newVal);
        }
    }
}

function _resize_embellisment(){    
    if($.browser.msie && $.browser.version == 8.0){
        if ( $(window).height() != emb_window_height && $(window).width() != emb_window_width ) {
            emb_window_height = $(window).height();
            emb_window_width = $(window).width();
            manage_embellishment_resize();
        }
    } else {
        manage_embellishment_resize();
    }
}

function get_embellishment_items(){
    $('#embellishment-wrap .emItem a').each(function(){
        $(this).remove();
    });
    var url = emb_item_url + '?page='+emb_next_page+'&offset='+emb_offset;

    $.ajax({
        url: url,
        type: "POST",
        dataType: 'json',
        data: { type:emb_type },
        async:   false,
        beforeSend : function(a){
            if ( emb_withloading ){
                var elm_overlay = $('<div />');
                elm_overlay.attr('class','embellishment-overlay');

                var t = $('#manage-template-sidebar').offset().top;
                var l = $('#manage-template-sidebar').offset().left;
                elm_overlay.css({ 'position':'absolute', 'background':'transparent', 'top':(t)+'px', 'left':l+'px', 'width': $('#manage-template-sidebar').width()+'px', 'height':($('#manage-template-sidebar').height())+'px' });
                elm_overlay.appendTo('#manage-template-sidebar');
                elm_overlay.html('<div class="loading"></div>');
            }
        },
        success: function(response_data){
            var data = $.parseJSON(response_data.data);
            emb_total_item_count = response_data.product_counts;
            emb_page_number = response_data.page_number;
            emb_num_pages = response_data.num_pages; 

            $.each(data,function(i,v){
                var id = v.pk;
                var img_src_url = v.model == 'admin.embellishments'?EMB_IMG_GEN_URL+'?embellishment_id='+id+'&embellishment_color=000000000&embellishment_thumbnail=1&embellishment_size=100':TEXT_IMG_GEN_URL+'?font_size=100&font_text=Abc&font_color=000000000&font_id='+id+'&font_thumbnail=1';
                var a = $('<a />');
                a.attr('id','emb-'+id);
                a.attr('_type',response_data.type);
                a.addClass('thumb');
                a.addClass('draggable');
                a.addClass('hidden');
                a.addClass('em');
                var img = $('<img />');
                img.attr('src',img_src_url);
                img.appendTo(a);
                a.appendTo('#embellishment-wrap .emItem');
            });
            manage_embellishment_pagination();
            $('#embellishment-wrap .emCat').hide();
            setTimeout(emb_remove_overlay,0);
        },
        error: function(msg) {
        }
    });
}

function manage_embellishment_pagination(){
    $('#embellishment-wrap .emItem').show();    
    $('#embellishment-wrap .emItem a:first img').each(function(){
        getHeight($(this),function(h){
            var elm = $('#embellishment-wrap .emItem a:first');            

            var _width = $('#embellishment-wrap').width();                     
            var _item_width = $(elm).outerWidth(true);            
            var count_by_width = Math.round(_width/_item_width);
            var item_per_width = _item_width*count_by_width;
            if (item_per_width > _width)
                count_by_width = count_by_width - 1;

            var _height = $('#canvas').outerHeight(true);
            var _formWrap_height = $('#manage-template-sidebar #uploadImage').outerHeight(true);
            var _breadcrumb_wrap_height = $('#manage-template-sidebar .breadcrumbWrap').outerHeight(true);
            var _pagination_height = $('#manage-template-sidebar .pagination').outerHeight(true);
            var _h2_height = $('#manage-template-sidebar h2').outerHeight(true);
            _height = _height-_formWrap_height;            
            _height = _height-_breadcrumb_wrap_height;
            _height = _height-_pagination_height;
            _height = _height-_h2_height;
            var _item_height = $(elm).outerHeight(true);
            if (_height<_item_height)
                _height = _item_height;
            else
                _height = _height-5;

            var count_by_height = Math.round(_height/_item_height);            
            var item_per_height = _item_height*count_by_height;            
            $('#manage-template-sidebar #embellishment-wrap .emItem').height(_height);            

            if (item_per_height>_height)
                count_by_height = count_by_height-1;

            emb_item_per_page = count_by_width*count_by_height;
            emb_offset = emb_item_per_page;            
            $('#embellishment-wrap .emItem a').each(function(i,v){
                if ((i+1)>emb_item_per_page){
                    $(this).remove();
                } else 
                    $(this).removeClass('hidden');
            });

            emb_total_pages = Math.ceil(parseInt(emb_total_item_count)/emb_item_per_page);
            generate_embellishment_pagination();            
        });
    });
    // if($.browser.msie && $.browser.version == 7.0){
    //     setTimeout(reset_product,0);
    // }
}

function generate_embellishment_pagination(){
    var left = 1, right = 5;
    if ( emb_total_pages <= 5 ){
        right = emb_total_pages;
    } else {
        var range = 5;
        left = (emb_current_page-2), right = (emb_current_page+2); 
        if ( right < range )
            right = range;
        if ( right > emb_total_pages )
            right = emb_total_pages;
        if ( left < 1)
            left = 1;
        var dif = right - left;
        if ( dif < 4 )
            left = right-4;
    }
    
    var i = left;
    var paginator = '';
    while(i<=right){
        var page_selected_cls = '';
        if (emb_current_page == i){
            page_selected_cls = 'cur-page';
        }
        paginator += '<span class="inline-block ' + page_selected_cls + '" id="emb-page-number-' + i + '">' + i + '</span>';
        i++;
    }

    $('#manage-template-sidebar .pagination').html(paginator);

    $('#manage-template-sidebar .pagination span').on('click', function(){                    
        emb_current_page = parseInt($(this).text());
        emb_offset = emb_item_per_page;
        emb_next_page = emb_current_page;
        emb_withloading = true;
        populate_embellishment_by_page();
        $('#manage-template-sidebar .pagination .cur-page').removeClass('cur-page');
        $('#emb-page-number-' + emb_current_page).addClass('cur-page');
        generate_embellishment_pagination();
    });
}

function populate_embellishment_by_page(){
    get_embellishment_items();
    generate_embellishment_pagination();
}

function manage_embellishment_resize(){
    $('#embellishment-wrap .emItem a:first img').each(function(){
        getHeight($(this),function(h){
            var elm = $('#embellishment-wrap .emItem a:first');            

            var _width = $('#embellishment-wrap').width();                     
            var _item_width = $(elm).outerWidth(true);            
            var count_by_width = Math.round(_width/_item_width);
            var item_per_width = _item_width*count_by_width;
            if (item_per_width > _width)
                count_by_width = count_by_width - 1;

            var _height = $('#canvas').outerHeight(true);
            var _formWrap_height = $('#manage-template-sidebar #uploadImage').outerHeight(true);
            var _breadcrumb_wrap_height = $('#manage-template-sidebar .breadcrumbWrap').outerHeight(true);
            var _pagination_height = $('#manage-template-sidebar .pagination').outerHeight(true);
            var _h2_height = $('#manage-template-sidebar h2').outerHeight(true);

            _height = _height-_formWrap_height;            
            _height = _height-_breadcrumb_wrap_height;
            _height = _height-_pagination_height;
            _height = _height-_h2_height;
            var _item_height = $(elm).outerHeight(true);
            if (_height<_item_height)
                _height = _item_height;
            else
                _height = _height-5;

            var count_by_height = Math.round(_height/_item_height);

            var item_per_height = _item_height*count_by_height;            
            $('#manage-template-sidebar #embellishment-wrap .emItem').height(_height);            

            if (item_per_height>_height)
                count_by_height = count_by_height-1;

            emb_item_per_page = count_by_width*count_by_height;

            emb_offset = emb_item_per_page;
            
            $('#embellishment-wrap .emItem a').each(function(i,v){
                if ((i+1)>emb_item_per_page){
                    $(this).remove();
                }
            });

            emb_total_pages = Math.ceil(parseInt(emb_total_item_count)/emb_item_per_page);

            if ( emb_total_pages < emb_current_page ){
                emb_current_page = emb_total_pages;        
            }
            
            //if ( emb_total_item_count > emb_item_per_page ){
                if ( $('#embellishment-wrap .emItem a').length < emb_item_per_page ){
                    emb_next_page = emb_current_page;
                    var url = emb_item_url + '?page='+emb_next_page+'&offset='+emb_offset;
                    $.ajax({
                        url: url,
                        type: "POST",
                        dataType: 'json',
                        data: { type:emb_type },
                        async:   false,
                        beforeSend : function(a){
                            var elm_overlay = $('<div />');
                            elm_overlay.attr('class','embellishment-overlay');

                            var t = $('#manage-template-sidebar').offset().top;
                            var l = $('#manage-template-sidebar').offset().left;
                            elm_overlay.css({ 'position':'absolute', 'background':'transparent', 'top':(t)+'px', 'left':l+'px', 'width': $('#manage-template-sidebar').width()+'px', 'height':($('#manage-template-sidebar').height())+'px' });
                            elm_overlay.appendTo('#manage-template-sidebar');
                            elm_overlay.html('<div class="loading"></div>');
                        },
                        success: function(response_data){
                            var data = $.parseJSON(response_data.data);
                            emb_total_item_count = response_data.product_counts;
                            emb_page_number = response_data.page_number;
                            emb_num_pages = response_data.num_pages;
                            var item_count = $('#embellishment-wrap .emItem a').length;
                            $.each(data,function(i,v){
                                var id = v.pk;                                
                                if(item_count<emb_item_per_page){                                        
                                    if ($('#emb-'+id).length==0){
                                        var img_src_url = v.model == 'admin.manage-template-main'?EMB_IMG_GEN_URL+'?embellishment_id='+id+'&embellishment_color=000000000&embellishment_thumbnail=1&embellishment_size=100':TEXT_IMG_GEN_URL+'?font_size=100&font_text=Abc&font_color=000000000&font_id='+id+'&font_thumbnail=1';
                                        var a = $('<a />');
                                        a.attr('id','emb-'+id);
                                        a.addClass('thumb');
                                        a.addClass('draggable');
                                        a.addClass('hidden');
                                        a.addClass('em');
                                        var img = $('<img />');
                                        img.attr('src',img_src_url);
                                        img.appendTo(a);
                                        a.appendTo('#embellishment-wrap .emItem');
                                        item_count++;
                                    }
                                }
                                
                            });
                            manage_embellishment_pagination();
                            $('#embellishment-wrap .emCat').hide();
                            setTimeout(emb_remove_overlay,1000);
                        },
                        error: function(msg) {
                        }
                    });
                }
            //}
            
            generate_embellishment_pagination();
        });
    });
}
function emb_remove_overlay(){
    if( $('.embellishment-overlay').length > 0 )
        $('.embellishment-overlay').remove();
}
/* embellishment upload */
function gen_uuid() {
    var uuid = ""
    for (var i=0; i < 32; i++) {
        uuid += Math.floor(Math.random() * 16).toString(16); 
    }
    return uuid
}
function showRequestEmbellishment(){
    if($.browser.msie || $.browser.safari){
        $('#upload-embel fieldset').append('<span class="loading"><img src="/media/images/loader.gif" alt="loader" /></span>');
    }
}
function showResponseEmbellishment(responseText, statusText, xhr, $form) {
    $('.loading').remove();
    response = responseText.split('|')
    res_code = response[0]
    res_msg = response[1]
    if (res_code=='f1'){
        $('#form_submit_button').after('<span id="upload-emb-error" style="color:#ff0000; font-size:12px;"> '+res_msg+'</span>');
    } else if (res_code=='f2') {
        $('#form_submit_button').after('<span id="upload-emb-error" style="color:#ff0000; font-size:12px;"> '+res_msg+'</span>');
    } else {
        $('#upload-embel fieldset').append('<span id="uploadprogressbar"></span>');
        emb_uploaded_filename = res_msg;        
        var d = {
            boxImage : '/media/images/progressbar.gif',
            barImage : {
                0:  '/media/images/progressbg_red.gif',
                30: '/media/images/progressbg_orange.gif',
                70: '/media/images/progressbg_green.gif'
            }
        }
        $('#upload-embel').find('#uploadprogressbar').progressBar(d);
        startProgressBarUpdate($('#X-Progress-ID').val());
        hideUploadEmbellishment();
    }    
} 
var g_progress_intv = 1;
function startProgressBarUpdate(upload_id) {
    $("#uploadprogressbar").fadeIn();
    if(g_progress_intv != 0)
        clearInterval(g_progress_intv);
    g_progress_intv = setInterval(function() {
        $.getJSON(UPLOAD_EMBELLISMENT_PROG+"?X-Progress-ID="+ upload_id, function(data) {
            if (data == null) {
                $("#uploadprogressbar").progressBar(100);
                clearInterval(g_progress_intv);
                g_progress_intv = 0;
                setTimeout(showUploadEmbellishment,1000);
                return;
            }
            var percentage = Math.floor(100 * parseInt(data.uploaded) / parseInt(data.length));
            $("#uploadprogressbar").progressBar(percentage);
        });
    }, 1000);
}
function hideUploadEmbellishment(){
    $('.file-wrapper input[type="button"]').hide();
    $('#form_submit_button').hide();
}
function showUploadEmbellishment(){
    if ($.browser.msie){
        $('#picture').replaceWith($('#picture').clone());
    } else {
        $('#picture').val('');
    }
    
    if (!$.browser.safari && !$.browser.msie){
        $('.file-wrapper input[type="button"]').show();
        $('#form_submit_button').hide();
    } else {
        $('#form_submit_button').show();
    }
    $("#uploadprogressbar").remove();
    $('.file-wrapper .file-holder').remove();
    create_instance_embellishment_upload(emb_uploaded_filename);
}
function getHeight(el,fn) {
    var img = new Image();
    img.onload = function() { fn(img.height); };
    img.src = el.attr("src");
}