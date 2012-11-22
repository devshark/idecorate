var emb_current_page = 1;
var emb_total_product_count;
var emb_page_number;
var emb_num_pages;
var emb_next_page = 1;            
var emb_product_per_page;
var emb_page_scroll_process = false;
var emb_offset = 25;
var emb_withloading = false;
var emb_total_pages;
var emb_mode_type;
var emb_search_keyword = '';
var emb_ie8_last_action_id;
var emb_ie8_current_page = 1;

$(document).ready(function(){
	$('#embelishments-list-wrap .emCat a').click(function(e){
        var url = $(this).attr('href');
        $('#embellishments .breadcrumb-wrap').html('<ul class="breadcrumb"><li><a href="#">All</a></a></li><li>></li><li>'+$(this).find('span').text()+'</li></ul>');
        $.post(url,{type:$(this).attr('rel')},function(response_data){
        	var data = $.parseJSON(response_data.data);
	        emb_total_product_count = response_data.product_counts;
	        emb_num_pages = response_data.page_number;
	        emb_num_pages = response_data.num_pages;	        
            $.each(data,function(i,v){
            	var id = v.pk;
             	var img_src_url = v.model == 'admin.embellishments'?EMB_IMG_GEN_URL+'?embellishment_id='+id+'&embellishment_color=000000000&embellishment_thumbnail=1&embellishment_size=100':TEXT_IMG_GEN_URL+'?font_size=100&font_text=Abc&font_color=000000000&font_id='+id+'&font_thumbnail=1';
                var a = $('<a />');
                a.attr('id','emb-'+id);
                a.addClass('thumb');
                a.addClass('draggable');
                a.addClass('em');
                var img = $('<img />');
                img.attr('src',img_src_url);
                img.appendTo(a);
                a.appendTo('#embelishments-list-wrap .emItem');
            });
            $('#embelishments-list-wrap .emCat').hide();
        });
        $('#embellishments .breadcrumb-wrap a').bind('click',function(){
            $('#embelishments-list-wrap .emCat').show();
            $('#embelishments-list-wrap .emItem a').each(function(){
                $(this).remove();
            });
            $('#embellishments .breadcrumb-wrap').html('');
        });
        e.preventDefault();
    });
});

function manage_embellishment_pagination(){
    $('.product-list a:first img').each(function(){
        getHeight($(this),function(h){
            var elm = $('.product-list a:first');            

            var prod_width = $('.product-list').width();                     
            var prod_item_width = $(elm).outerWidth(true);            
            var count_by_width = Math.round(prod_width/prod_item_width);
            var prod_per_width = prod_item_width*count_by_width;
            if (prod_per_width > prod_width)
                count_by_width = count_by_width - 1;

            var prod_height = $('.product-list').height();
            var prod_item_height = $(elm).outerHeight(true);

            if (prod_item_height > prod_height){
                //prod_height = prod_item_height+20;
                //$('.product-list').css('min-height',prod_height);
            }

            var count_by_height = Math.round(prod_height/prod_item_height);
            var prod_per_height = prod_item_height*count_by_height;
            if($.browser.msie && $.browser.version == 7.0)
                prod_height = prod_height - 5;

            if (prod_per_height > prod_height)
                count_by_height = count_by_height - 1;

            product_per_page = count_by_width*count_by_height;
            var page = 1;            
            var counter = 1;
            $('.product-list a').each(function(i, val){
                if ( counter <= product_per_page ){                    
                    $(this).removeClass('hidden');
                }
                if (counter > product_per_page){
                    //$(this).remove();
                }
                    
                counter++;
            });

            total_pages = Math.ceil(parseInt(total_product_count)/product_per_page);

            $('.product-list').on('mousewheel', function(event, delta) {
                  
                mode = 1;
                page_scroll_process = true;
                offset = product_per_page;
                if (delta > 0){
                    if (current_page != 1){
                        current_page = current_page-1;
                        next_page = current_page;
                        withloading = true;
                        populate_product_by_page()
                    }
                } else {
                    if(current_page != total_pages){
                        current_page = current_page+1;
                        next_page = current_page;
                        withloading = true;
                        populate_product_by_page();                        
                    }
                }
                $('.cur-page').removeClass('cur-page');
                $('#page-number-' + current_page).addClass('cur-page');
                generate_pagenation();
                return false;
            });

            generate_pagenation();
        });
    });
    if($.browser.msie && $.browser.version == 7.0){
        setTimeout(reset_product,0);
    }
}