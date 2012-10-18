var current_page = 1;
var total_product_count;
var page_number;
var num_pages;
var next_page = 1;            
var product_per_page;
var page_scroll_process = false;
$(document).ready( function() {
    //tableScroll sets the table's tbody to be scrollable leaving the head and foot fixed.
    //$('#buy-table').tableScroll({height:450});

    $('.categories').click(function(){
        browse_categories(this.id);
        return false;
    });

    $('.breadcrumb a').click(function(){
        browse_categories(this.rel);
        return false;
    });  
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
            $(".draggable").draggable("destroy");
            var data = $.parseJSON(response_data.data);                                            
            $.each(data,function(i, val){                            
                var id = val.pk;
                type = val.model == 'category.categories' ? 'categories' : 'products';
                var thumb = val.fields.thumbnail;
                var name = val.fields.name;
                if(type =='products'){
                    thumb = val.fields.original_image_thumbnail;
                    thumb = 'products/' + thumb;
                    items += '<a class="thumb draggable ' + type + '" id="'+id+'" href="#">' +
                            '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
                        '</a>';
                }else{
                    items += '<div  style="cursor: pointer;" id="' + id + '" class="thumb ' + type + '">' +
                            '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
                            '<span>' + name + '</span>' +
                        '</div>';
                }
            });

            if(type =='products'){
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
            var side_content = breadcrumb + items;
            $('#create-tab').html(side_content);
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
        url: STYLEBOARD_PRODUCT_AJAX_URL + '?page=' + next_page,
        type: "POST",
        dataType: 'json',
        data: { cat_id: category_id, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() },
        async:   false,
        success: function(response_data){
            data = response_data;
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
    $(".draggable").draggable("destroy");
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
        items += '<a class="thumb draggable ' + type + '" id="'+id+'" href="#">' +
                '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
            '</a>';
    });

    items = '<div class="product-list">' + items + '</div>';
    $('#create-tab .breadcrumb').after(items);
    manage_product_pagination();
}

function getHeight(el,fn) {
    var img = new Image();
    img.onload = function() { fn(img.height); };
    img.src = el.attr("src");
}

function manage_product_pagination(){
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
            var count_by_height = Math.round(prod_height/prod_item_height);
            var prod_per_height = prod_item_height*count_by_height;

            //if($.browser.chrome)
            prod_height = prod_height + 5;

            if (prod_per_height > prod_height)
                count_by_height = count_by_height - 1;

            product_per_page = count_by_width*count_by_height;
            var page = 1;
            var product_page_cont = $('<div />');
            product_page_cont.attr('id','prod-page-' + page);
            product_page_cont.addClass('product-page-cont');
            product_page_cont.addClass('current-page');
            $(".draggable").draggable("destroy");
            product_page_cont.appendTo('.product-list');
            var counter = 1;
            $('.product-list a').each(function(i, val){                            
                $(this).appendTo(product_page_cont);
                if (counter == product_per_page){
                    page += 1;
                    product_page_cont = $('<div />');
                    product_page_cont.attr('id','prod-page-' + page);
                    product_page_cont.addClass('prduct-page-cont');
                    product_page_cont.css('display','none');
                    product_page_cont.appendTo('.product-list');
                    counter = 0;
                }
                counter++;
            });

            var total_pages = Math.ceil(parseInt(total_product_count)/product_per_page);

            $(".draggable").draggable({ 
                revert:true, 
                helper: 'clone' 
            });

            $('.product-list').bind('mousewheel', function(event, delta) {
                // var elm_overlay = $('<div />');
                // elm_overlay.attr('class','product-overlay');
                // var t = $('#create-tab').offset().top;
                // var l = $('#create-tab').offset().left;
                // elm_overlay.css({ 'position':'absolute', 'background':'transparent', 'top':(t-140)+'px', 'left':0, 'width': $('#create-tab').width()+'px', 'height':($('#create-tab').height()-25)+'px' });
                // elm_overlay.appendTo('#create-tab');
                // if ( page_scroll_process )
                //     return false;
                if (delta > 0){
                    mode = 1;
                    page_scroll_process = true;
                    if (current_page != 1){
                        current_page = current_page-1;
                        $('.current-page').each(function(){
                            $(this).css('display','none');
                            $(this).removeClass('current-page');
                        });
                    }                    
                } else {
                    if(current_page != total_pages){
                        page_scroll_process = true;
                        var prev_page = current_page;
                        current_page = current_page+1;

                        var prev_displayed = prev_page * product_per_page;
                        if ($('#prod-page-' + current_page).length > 0){
                            var current_page_item_count = $('#prod-page-' + current_page + ' a').length;
                            if ( current_page_item_count < product_per_page && (prev_displayed+current_page_item_count) < total_product_count){
                                populate_product_via_paginate('prod-page-' + current_page);                                
                            }
                        } else {
                            if ( prev_displayed < total_product_count ){
                                var product_page_cont = $('<div />');
                                product_page_cont.attr('id','prod-page-' + page);
                                product_page_cont.addClass('product-page-cont');
                                product_page_cont.addClass('current-page');
                                product_page_cont.appendTo('.product-list');
                                populate_product_via_paginate('prod-page-' + current_page);                                            
                            }
                        }                                  
                        $('.current-page').each(function(){
                            $(this).css('display','none');
                            $(this).removeClass('current-page');
                        });
                    }
                }
                // var x = current_page;
                // var ok = true;
                // while ( x!=0 ){
                //     console.log(x)
                //     if ( $('#prod-page-' + x).length == 0 ){                    
                //         console.log($('#prod-page-' + x).length)
                //         ok = false;
                //     }
                //     x = x-1;
                // }
                // if (ok)
                //     $('.product-overlay').remove();
                $('.cur-page').removeClass('cur-page');
                $('#prod-page-' + current_page).css('display','block');
                $('#page-number-' + current_page).addClass('cur-page');
                $('#prod-page-' + current_page).addClass('current-page');
                return false;
            });
            var k=1;
            var paginator = '';
            while(k<=total_pages){
                var page_selected_cls = '';
                if (current_page == k){
                    page_selected_cls = 'cur-page';
                }
                paginator += '<span class="inline-block ' + page_selected_cls + '" id="page-number-' + k + '">' + k + '</span>';
                k++;
            }
            var pagination = '<div class="pagination">' + paginator + '</div>';
            $('.product-list').after(pagination);
            $('.pagination span').each(function(){
                $(this).bind('click', function(){

                    var prev_page = current_page;
                    current_page = parseInt($(this).text());

                    var prev_displayed = prev_page * product_per_page;
                    if ($('#prod-page-' + current_page).length > 0){
                        var current_page_item_count = $('#prod-page-' + current_page + ' a').length;
                        if ( current_page_item_count < product_per_page && (prev_displayed+current_page_item_count) < total_product_count){
                            populate_product_via_paginate('prod-page-' + current_page);
                        }
                    } else {
                        if ( prev_displayed < total_product_count ){
                            var product_page_cont = $('<div />');
                            product_page_cont.attr('id','prod-page-' + page);
                            product_page_cont.addClass('product-page-cont');
                            product_page_cont.addClass('current-page');
                            product_page_cont.appendTo('.product-list');
                            populate_product_via_paginate('prod-page-' + current_page);                                            
                        }
                    }                                  
                    $('.current-page').each(function(){
                        $(this).css('display','none');
                        $(this).removeClass('current-page');
                    });

                    $('.cur-page').removeClass('cur-page');
                    $('#prod-page-' + current_page).css('display','block');
                    $('#page-number-' + current_page).addClass('cur-page');
                    $('#prod-page-' + current_page).addClass('current-page');
                });
            });
        });
    });
}

function populate_product_via_paginate(page_cont_elm){
    next_page = page_number+1;
    var response_data = get_products();
    var data = $.parseJSON(response_data.data);
    total_product_count = response_data.product_counts;
    page_number = response_data.page_number;
    num_pages = response_data.num_pages;                
    var counter = $('#' + page_cont_elm + ' a').length;
    var product_page_cont = $('#' + page_cont_elm);
    var page = current_page;
    
    $.each(data,function(i, val){
        var id = val.pk;
        var name = val.fields.name;
        var thumb = val.fields.original_image_thumbnail;
        thumb = 'products/' + thumb;
        var items = '<a class="thumb draggable products" id="'+id+'" href="#">' +
                '<img src="/' + media_url + thumb + '" alt="' + name + '" />' +
            '</a>';
        if (counter == product_per_page){                        
            page += 1;
            product_page_cont = $('<div />');
            product_page_cont.attr('id','prod-page-' + page);
            product_page_cont.addClass('prduct-page-cont');
            product_page_cont.css('display','none');
            product_page_cont.appendTo('.product-list');
            counter = 0;
        }
        $(product_page_cont).append(items);
        $('#' + id).draggable({ 
            revert:true, 
            helper: 'clone' 
        });
        counter++;
    });    
}