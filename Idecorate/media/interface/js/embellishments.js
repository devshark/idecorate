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

$(document).ready(function(){
	$('#embelishments-list-wrap .emCat a').click(function(e){
        emb_current_page = 1;
        emb_offset = 25;
        $('#embellishments .pagination').show();
        emb_item_url = $(this).attr('href');
        $('#embellishments .breadcrumb-wrap').html('<ul class="breadcrumb"><li><a href="#">All</a></a></li><li>></li><li>'+$(this).find('span').text()+'</li></ul>');
        $('#embellishments .breadcrumb-wrap a').bind('click',function(e){
            $('#embelishments-list-wrap .emCat').show();
            $('#embelishments-list-wrap .emItem a').each(function(){
                $(this).remove();
            });
            $('#embellishments .breadcrumb-wrap').html('');
            $('#embellishments .pagination').hide();
            e.preventDefault();
        });
        emb_type = $(this).attr('rel');
        get_embellishment_items();
        e.preventDefault();
    });
    $(window).resize(function(){
        if($.browser.msie && $.browser.version == 8.0){
            if ( $(window).height() != window_height && $(window).width() != window_width ) {
                window_height = $(window).height();
                window_width = $(window).width();
                manage_embellishment_resize();
            }
        } else {
            manage_embellishment_resize();
        }
    });
    $('#embellishments #embelishments-list-wrap .emItem').on('mousewheel',function(event,delta){
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
        $('#embellishments .pagination .cur-page').removeClass('cur-page');
        $('#emb-page-number-' + emb_current_page).addClass('cur-page');
        generate_embellishment_pagination();
    });
});

function manage_embellishment_pagination(){
    $('#embelishments-list-wrap .emItem a:first img').each(function(){
        getHeight($(this),function(h){
            var elm = $('#embelishments-list-wrap .emItem a:first');            

            var _width = $('#embelishments-list-wrap').width();                     
            var _item_width = $(elm).outerWidth(true);            
            var count_by_width = Math.round(_width/_item_width);
            var item_per_width = _item_width*count_by_width;
            if (item_per_width > _width)
                count_by_width = count_by_width - 1;

            var _height = $('#embellishments').height();
            var _formWrap_height = $('#embellishments .formWrap').outerHeight(true);
            var _breadcrumb_wrap_height = $('#embellishments .breadcrumb-wrap').outerHeight(true);
            var _pagination_height = $('#embellishments .pagination').outerHeight(true);
            _height = _height-_formWrap_height;            
            _height = _height-_breadcrumb_wrap_height;
            _height = _height-_pagination_height;
            var _item_height = $(elm).outerHeight(true);
            if (_height<_item_height)
                _height = _item_height;
            else
                _height = _height-5;

            var count_by_height = Math.round(_height/_item_height);            
            var item_per_height = _item_height*count_by_height;            
            $('#embellishments #embelishments-list-wrap .emItem').height(_height);            

            if (item_per_height>_height)
                count_by_height = count_by_height-1;

            emb_item_per_page = count_by_width*count_by_height;
            emb_offset = emb_item_per_page;
            
            $('#embelishments-list-wrap .emItem a').each(function(i,v){
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

    $('#embellishments .pagination').html(paginator);

    $('#embellishments .pagination span').on('click', function(){                    
        emb_current_page = parseInt($(this).text());
        emb_offset = emb_item_per_page;
        emb_next_page = emb_current_page;
        emb_withloading = true;
        populate_embellishment_by_page();
        $('#embellishments .pagination .cur-page').removeClass('cur-page');
        $('#emb-page-number-' + emb_current_page).addClass('cur-page');
        generate_embellishment_pagination();
    });
}

function populate_embellishment_by_page(){
    get_embellishment_items();
    generate_embellishment_pagination();
}

function get_embellishment_items(){
    $('#embelishments-list-wrap .emItem a').each(function(){
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

                var t = $('#create-tab').offset().top;
                var l = $('#create-tab').offset().left;
                elm_overlay.css({ 'position':'absolute', 'background':'transparent', 'top':(t)+'px', 'left':l+'px', 'width': $('#create-tab').width()+'px', 'height':($('#create-tab').height())+'px' });
                elm_overlay.appendTo('#create-tab');
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
                a.appendTo('#embelishments-list-wrap .emItem');
            });
            manage_embellishment_pagination();
            $('#embelishments-list-wrap .emCat').hide();
            setTimeout(emb_remove_overlay,0);
        },
        error: function(msg) {
        }
    });
}

function manage_embellishment_resize(){
    $('#embelishments-list-wrap .emItem a:first img').each(function(){
        getHeight($(this),function(h){
            var elm = $('#embelishments-list-wrap .emItem a:first');            

            var _width = $('#embelishments-list-wrap').width();                     
            var _item_width = $(elm).outerWidth(true);            
            var count_by_width = Math.round(_width/_item_width);
            var item_per_width = _item_width*count_by_width;
            if (item_per_width > _width)
                count_by_width = count_by_width - 1;

            var _height = $('#embellishments').height();
            var _formWrap_height = $('#embellishments .formWrap').outerHeight(true);
            var _breadcrumb_wrap_height = $('#embellishments .breadcrumb-wrap').outerHeight(true);
            var _pagination_height = $('#embellishments .pagination').outerHeight(true);
            _height = _height-_formWrap_height;            
            _height = _height-_breadcrumb_wrap_height;
            _height = _height-_pagination_height;
            var _item_height = $(elm).outerHeight(true);
            if (_height<_item_height)
                _height = _item_height;
            else
                _height = _height-5;

            var count_by_height = Math.round(_height/_item_height);            
            var item_per_height = _item_height*count_by_height;            
            $('#embellishments #embelishments-list-wrap .emItem').height(_height);            

            if (item_per_height>_height)
                count_by_height = count_by_height-1;

            emb_item_per_page = count_by_width*count_by_height;

            emb_offset = emb_item_per_page;
            
            $('#embelishments-list-wrap .emItem a').each(function(i,v){
                if ((i+1)>emb_item_per_page){
                    $(this).remove();
                }
            });

            emb_total_pages = Math.ceil(parseInt(emb_total_item_count)/emb_item_per_page);

            if ( emb_total_pages < emb_current_page ){
                emb_current_page = emb_total_pages;        
            }
            
            //if ( emb_total_item_count > emb_item_per_page ){
                if ( $('#embelishments-list-wrap .emItem a').length < emb_item_per_page ){
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

                            var t = $('#create-tab').offset().top;
                            var l = $('#create-tab').offset().left;
                            elm_overlay.css({ 'position':'absolute', 'background':'transparent', 'top':(t)+'px', 'left':l+'px', 'width': $('#create-tab').width()+'px', 'height':($('#create-tab').height())+'px' });
                            elm_overlay.appendTo('#create-tab');
                            elm_overlay.html('<div class="loading"></div>');
                        },
                        success: function(response_data){
                            var data = $.parseJSON(response_data.data);
                            emb_total_item_count = response_data.product_counts;
                            emb_page_number = response_data.page_number;
                            emb_num_pages = response_data.num_pages;
                            var item_count = $('#embelishments-list-wrap .emItem a').length;
                            $.each(data,function(i,v){
                                var id = v.pk;                                
                                if(item_count<emb_item_per_page){                                        
                                    if ($('#emb-'+id).length==0){
                                        var img_src_url = v.model == 'admin.embellishments'?EMB_IMG_GEN_URL+'?embellishment_id='+id+'&embellishment_color=000000000&embellishment_thumbnail=1&embellishment_size=100':TEXT_IMG_GEN_URL+'?font_size=100&font_text=Abc&font_color=000000000&font_id='+id+'&font_thumbnail=1';
                                        var a = $('<a />');
                                        a.attr('id','emb-'+id);
                                        a.addClass('thumb');
                                        a.addClass('draggable');
                                        a.addClass('hidden');
                                        a.addClass('em');
                                        var img = $('<img />');
                                        img.attr('src',img_src_url);
                                        img.appendTo(a);
                                        a.appendTo('#embelishments-list-wrap .emItem');
                                        item_count++;
                                    }
                                }
                                
                            });
                            manage_embellishment_pagination();
                            $('#embelishments-list-wrap .emCat').hide();
                            setTimeout(emb_remove_overlay,0);
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