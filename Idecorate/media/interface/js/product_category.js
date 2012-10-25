var current_page = 1;
var total_product_count;
var page_number;
var num_pages;
var next_page = 1;            
var product_per_page;
var page_scroll_process = false;
var offset = 25;
var withloading = false;
var total_pages;
$(document).ready( function() {
    $('.categories').click(function(){
        browse_categories(this.id);
        return false;
    });
    $('.breadcrumb a').click(function(){
        browse_categories(this.rel);
        return false;
    });

    $(window).resize(manage_product_resize);
});

function browse_categories(elm_id){
    var type;
    $.ajax({
        url: STYLEBOARD_AJAX_URL,
        type: "POST",
        dataType: 'json',
        data: { cat_id: elm_id, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() },
        async:   false,
        success: function(response_data){
            var items = '';
            var breadcrumb = '';
            //$(".draggable").draggable("destroy");
            var data = $.parseJSON(response_data.data);                                            
            $.each(data,function(i, val){                            
                var id = val.pk;
                type = val.model == 'category.categories' ? 'categories' : 'products';
                var thumb = val.fields.thumbnail;
                var name = val.fields.name;
                if(type =='products'){
                    thumb = val.fields.original_image_thumbnail;
                    thumb = 'products/' + thumb;
                    items += '<a _uid="'+id+'" class="hidden thumb draggable ' + type + '" id="'+id+'" href="#">' +
                            '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
                        '</a>';
                }else{
                    items += '<div id="' + id + '" class="thumb ' + type + '">' +
                            '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
                            '<span>' + name + '</span>' +
                        '</div>';
                }
            });

            if(type =='products'){
                category_id = elm_id;
                total_product_count = response_data.product_counts;
                items = '<div class="product-list">' + items + '</div>';
            }

            var breadcrumb_tree = '';
            $.ajax({
                url: CATEGORY_TREE_AJAX_URL,
                type: "POST",
                data: { cat_id: elm_id, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() },
                async:   false,
                success: function(breadcrumb_data){
                    if (breadcrumb_data){
                        arr = breadcrumb_data.split('|');
                        breadcrumb += '<ul class="breadcrumb">'
                        breadcrumb += '<li><a href="#">All</a></li>';
                        i = arr.length;
                        while (i!=0){
                            cc = arr[i-1].split(':');
                            if (i==1)
                                breadcrumb += '<li> > </li><li class="active">' + cc[1] + '</li>';
                            else
                                breadcrumb += '<li> > </li><li><a rel="' + cc[0] + '" href="#">' + cc[1] + '</a></li>';
                            i = i-1
                        }
                        breadcrumb += '</ul>'
                    }
                },
                error: function(msg) {
            
                }
            });            
            $('.breadcrumb-wrap').html(breadcrumb);
            $('.product-list-wrap').html(items);
            $('.breadcrumb a').each(function(){
                $(this).bind('click',function(e){
                    e.preventDefault();
                    browse_categories(this.rel);
                });
            });
            $('.categories').each(function(){
                $(this).bind('click',function(e){
                    e.preventDefault();
                    browse_categories(this.id);
                });
            });

            if(type =='products'){
                manage_product_pagination();
            }
        },
        error: function(msg) {
        }
    });
}

function get_products(){
    var data;
    $.ajax({
        url: STYLEBOARD_PRODUCT_AJAX_URL + '?page=' + next_page + '&offset=' + offset,
        type: "POST",
        dataType: 'json',
        data: { cat_id: category_id, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() },
        async:   false,
        beforeSend : function(a){
            if ( withloading ){
                var elm_overlay = $('<div />');
                elm_overlay.attr('class','product-overlay');

                var t = $('#create-tab').offset().top;
                var l = $('#create-tab').offset().left;
                elm_overlay.css({ 'position':'absolute', 'background':'transparent', 'top':(t)+'px', 'left':l+'px', 'width': $('#create-tab').width()+'px', 'height':($('#create-tab').height())+'px' });
                elm_overlay.appendTo('#create-tab');
                elm_overlay.html('<div class="loading"></div>');
            }
        },
        success: function(response_data){
            data = response_data;
            if( $('.product-overlay').length > 0 )
                $('.product-overlay').remove();
        },
        error: function(msg) {
        }
    });

    return data;
}

function populate_products(){
    var response_data = get_products();
    var items = '';
    var breadcrumb = '';
    //$(".draggable").draggable("destroy");
    var data = $.parseJSON(response_data.data);
    total_product_count = response_data.product_counts;
    page_number = response_data.page_number;
    num_pages = response_data.num_pages;
    $.each(data,function(i, val){                            
        var id = val.pk;
        type = val.model == 'category.categories' ? 'categories' : 'products';
        var name = val.fields.name;
        var thumb = val.fields.original_image_thumbnail;
        thumb = 'products/' + thumb;
        items += '<a _uid="'+id+'" class="hidden thumb draggable ' + type + '" id="'+id+'" href="#">' +
                '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
            '</a>';
    });

    items = '<div class="product-list">' + items + '</div>';
    $('.product-list-wrap').after(items);
    manage_product_pagination();
}

function manage_product_pagination(){
    console.log($('#create-tab').height(),$('#create-tab-nav').height(), $('.breadcrumb-wrap').height())
    var computed_height = $('#create-tab').outerHeight(true)-$('#create-tab-nav').outerHeight(true)-$('.breadcrumb-wrap').outerHeight(true)-40;
    $('.product-list').css('height',computed_height+'px');
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
                prod_height = prod_item_height+20;
                $('.product-list').css('min-height',prod_height);
            }

            var count_by_height = Math.round(prod_height/prod_item_height);
            var prod_per_height = prod_item_height*count_by_height;
            //if($.browser.chrome)
            prod_height = prod_height + 5;

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
                    $(this).remove();
                }
                    
                counter++;
            });

            total_pages = Math.ceil(parseInt(total_product_count)/product_per_page);

            $('.product-list').bind('mousewheel', function(event, delta) {
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
                generate_pagenation()
                return false;
            });

            generate_pagenation();
        });
    });
}

function generate_pagenation(){

    total_pages = Math.ceil(parseInt(total_product_count)/product_per_page);
    var left = 1, right = 5;
    if ( total_pages <= 5 ){
        right = total_pages;
    } else {
        var range = 5;
        left = (current_page-2), right = (current_page+2);    

        if ( right < range )
            right = range;
        
        if ( right > total_pages )
            right = total_pages;

        if ( left < 1){
            left = 1;
        }

        var dif = right - left;

        if ( dif < 4 ){
            left = right-4;
        }
    }
    
    var i = left;
    var paginator = '';
    while(i<=right){
        var page_selected_cls = '';
        if (current_page == i){
            page_selected_cls = 'cur-page';
        }
        paginator += '<span class="inline-block ' + page_selected_cls + '" id="page-number-' + i + '">' + i + '</span>';
        i++;
    }
    $('.pagination').remove();
    var pagination = '<div class="pagination">' + paginator + '</div>';
    $('.product-list').after(pagination);

    $('.pagination span').each(function(){
        $(this).bind('click', function(){                    
            current_page = parseInt($(this).text());
            offset = product_per_page;
            next_page = current_page;
            withloading = true;
            populate_product_by_page()

            $('.cur-page').removeClass('cur-page');
            $(this).addClass('cur-page');
            generate_pagenation();
        });
    });
}

function getHeight(el,fn) {
    var img = new Image();
    img.onload = function() { fn(img.height); };
    img.src = el.attr("src");
}

function clear_products(){
    $('.product-list a').each(function(){
        $(this).remove();
    });
}

function populate_product_by_page(){
    var response_data = get_products();
    var data = $.parseJSON(response_data.data);
    total_product_count = response_data.product_counts;
    page_number = response_data.page_number;
    num_pages = response_data.num_pages;

    clear_products();
    
    $.each(data,function(i, val){
        var id = val.pk;
        var name = val.fields.name;
        var thumb = val.fields.original_image_thumbnail;
        thumb = 'products/' + thumb;
        var items = '<a _uid="'+id+'"  class="thumb draggable products" id="'+id+'" href="#">' +
                '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
            '</a>';
        $('.product-list').append(items);
    });    
}

function manage_product_resize(){
    $('.draggable').draggable('destroy');
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
        $('.product-list').css('min-height',prod_item_height+20);
    }

    var count_by_height = Math.round(prod_height/prod_item_height);
    var prod_per_height = prod_item_height*count_by_height;
    //if($.browser.chrome)
    prod_height = prod_height + 5;

    if (prod_per_height > prod_height)
        count_by_height = count_by_height - 1;

    product_per_page = count_by_width*count_by_height;

    var page = 1;
    $(".draggable").draggable("destroy");
    var counter = 1;
    $('.product-list a').each(function(i, val){                
        if (counter > product_per_page){
            $('#remove_products_container').append(this);
        }
        counter++;
    });

    if ( $('.product-list a').length < product_per_page ){
        var x = $('.product-list a').length;        
        $('#remove_products_container a').each(function(){
            $('.product-list').append(this);
            if ( x == product_per_page )
                return false;
            x++;            
        });
    }

    total_pages = Math.ceil(parseInt(total_product_count)/product_per_page);
    if ( total_pages < current_page ){
        current_page = total_pages;        
    }
    if ( total_product_count > product_per_page ){
        if ( $('.product-list a').length < product_per_page ){
            next_page = current_page;
            offset = product_per_page;
            var response_data = get_products();

            var data = $.parseJSON(response_data.data);
            var y = $('.product-list a').length;
            $.each(data,function(i, val){            
                var id = val.pk;
                if ( $('#'+id).length == 0 ){
                    type = 'products';
                    var name = val.fields.name;
                    var thumb = val.fields.original_image_thumbnail;
                    thumb = 'products/' + thumb;
                    item = '<a _uid="'+id+'" class="thumb draggable ' + type + '" id="'+id+'" href="#">' +
                            '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
                        '</a>';

                    $('.product-list').append(item);
                    if ( y ==  product_per_page)
                        return false;
                    y++;
                }
            });

        }
    }    
    generate_pagenation();
    $('.draggable').draggable({
        revert:true,
        helper:'clone'
    });
    sort_remove_prod();
}

function sort_remove_prod(){
    $('#remove_products_container a').each(function(){
        $(this).index(this.id);
    });
}