var temp_current_page = 1;
var temp_total_item_count;
var temp_page_number;
var temp_num_pages;
var temp_next_page = 1;            
var temp_item_per_page;
var temp_page_scroll_process = false;
var temp_offset = 25;
var temp_withloading = false;
var temp_total_pages;
var temp_mode_type;
var temp_search_keyword = '';
var temp_type;
var temp_item_url;
var temp_window_height;
var temp_window_width;
var temp_uploaded_filename;
var temp_error_upload = false;

$(document).ready(function(){
	$('a[href="#templates"]').click(function(){
		create_current_tab = 'products';
	});
	$('a[href="#embellishments"]').click(function(){
		create_current_tab = 'embellishments';
	});
	$('a[href="#templates"]').click(function(){
		if(create_current_tab != 'templates'){
			create_current_tab = 'templates';
			populate_template_items();
		}
	});
});

function populate_template_items(){
	$('#templates .template-wrap').html('');
    var url = GET_TEMPLATES_LIST_URL + '?page='+temp_next_page+'&offset='+temp_offset;
    $.ajax({
        url: url,
        type: "POST",
        dataType: 'json',
        async:   false,
        beforeSend : function(a){
            if ( temp_withloading ){
                var elm_overlay = $('<div />');
                elm_overlay.attr('class','template-overlay');

                var t = $('#create-tab').offset().top;
                var l = $('#create-tab').offset().left;
                elm_overlay.css({ 'position':'absolute', 'background':'transparent', 'top':(t)+'px', 'left':l+'px', 'width': $('#create-tab').width()+'px', 'height':($('#create-tab').height())+'px' });
                elm_overlay.appendTo('#create-tab');
                elm_overlay.html('<div class="loading"></div>');
            }
        },
        success: function(response_data){
            var data = $.parseJSON(response_data.data);
            temp_total_item_count = response_data.product_counts;
            temp_page_number = response_data.page_number;
			temp_num_pages = response_data.num_pages;
            $.each(data,function(i,v){
                var id = v.pk;                
                if ($('#temp-'+id).length == 0){                    
                    //var img_src_url = v.model == 'admin.embellishments'?temp_IMG_GEN_URL+'?embellishment_id='+id+'&embellishment_color=000000000&embellishment_thumbnail=1&embellishment_size=100':TEXT_IMG_GEN_URL+'?font_size=100&font_text=Abc&font_color=000000000&font_id='+id+'&font_thumbnail=1';
                    var img_src_url = '/styleboard/generate_styleboard_template_view/' + id + '/139/139/'
                    var a = $('<a />');
                    a.attr('id','temp-'+id);
                    a.attr('_uid',id);
                    a.attr('_type',response_data.type);
                    a.addClass('thumb');
                    a.addClass('draggable');
                    a.addClass('hidden');
                    a.addClass('temp');
                    var img = $('<img />');
                    img.attr('src',img_src_url);
                    img.appendTo(a);
                    a.appendTo('.template-wrap');
                }                
            });
            manage_template_pagination();
            setTimeout(temp_remove_overlay,0);
        },
        error: function(msg) {
        }
    });
}

function manage_template_pagination(){
    $('#templates a:first img').each(function(){
        getHeight($(this),function(h){
            var elm = $('#templates a:first');            

            var _width = $('#templates').width();                     
            var _item_width = $(elm).outerWidth(true);            
            var count_by_width = Math.round(_width/_item_width);
            var item_per_width = _item_width*count_by_width;
            if (item_per_width > _width)
                count_by_width = count_by_width - 1;

            var _height = $('#templates').height();
            var _pagination_height = $('#templates .pagination').outerHeight(true);
            _height = _height-_pagination_height;
            var _item_height = $(elm).outerHeight(true);
            if (_height<_item_height)
                _height = _item_height;
            else
                _height = _height-5;

            var count_by_height = Math.round(_height/_item_height);            
            var item_per_height = _item_height*count_by_height;            
            $('#templates .template-wrap').height(_height);            

            if (item_per_height>_height && count_by_height > 1)
                count_by_height = count_by_height-1;

            if (count_by_height<=0){
                count_by_height = 1;
            }

            temp_item_per_page = count_by_width*count_by_height;
            temp_offset = temp_item_per_page;
            
            $('#templates .template-wrap a').each(function(i,v){
                if ((i+1)>temp_item_per_page){
                    $(this).addClass('invisible');
                } else {
                    $(this).removeClass('hidden');
                }
            });

            temp_total_pages = Math.ceil(parseInt(temp_total_item_count)/temp_item_per_page);
            generate_template_pagination();
        });
    });
    if($.browser.msie && $.browser.version == 7.0){
        setTimeout(reset_template,0);
    }
}

function generate_template_pagination(){
    var left = 1, right = 5;
    if ( temp_total_pages <= 5 ){
        right = temp_total_pages;
    } else {
        var range = 5;
        left = (temp_current_page-2), right = (temp_current_page+2); 
        if ( right < range )
            right = range;
        if ( right > temp_total_pages )
            right = temp_total_pages;
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
        if (temp_current_page == i){
            page_selected_cls = 'cur-page';
        }
        paginator += '<span class="inline-block ' + page_selected_cls + '" id="temp-page-number-' + i + '">' + i + '</span>';
        i++;
    }

    $('#templates .pagination').html(paginator);
    $('#templates .pagination').show();

    $('#templates .pagination span').on('click', function(){                    
        temp_current_page = parseInt($(this).text());
        temp_offset = temp_item_per_page;
        temp_next_page = temp_current_page;
        temp_withloading = true;
        populate_template_by_page();
        $('#templates .pagination .cur-page').removeClass('cur-page');
        $('#temp-page-number-' + temp_current_page).addClass('cur-page');
        //generate_embellishment_pagination();
    });

    //$('#templates .template-wrap').height($('#templates').outerHeight(true)-$('#templates .pagination').outerHeight(true));
    var h = $('#templates .template-wrap').outerHeight(true)+$('#templates .pagination').outerHeight(true);
    //$('#templates').height(h);
    // $('#canvas').height(h);
    // $('#styleboard').height(h);
}

function populate_template_by_page(){
    populate_template_items();
    generate_template_pagination();
}

function reset_template(){
	var items = $('#templates .template-wrap').html();
    clear_template();
    $('#templates .template-wrap').append(items);
}

function clear_template(){
    $('#templates .template-wrap a').each(function(){
        $(this).remove();
    });
}

function temp_remove_overlay(){
	if( $('.template-overlay').length > 0)
		$('.template-overlay').remove();
}