function browse_categories(elm_id){
    $.ajax({
            url: "{% url styleboard_ajax %}",
            type: "POST",
            dataType: 'xml',
            data: { cat_id: elm_id, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val() },
            async:   false,
            success: function(response_data){
                var items = '';
                var breadcrumb = '';
                $(".draggable").draggable("destroy");
                $(response_data).find('object').each(function(){
                    var type = $(this).attr('model') == 'category.categories' ? 'categories' : 'products';                         
                    var id = $(this).attr('pk');
                    var name = $(this).find('field[name="name"]').text();
                    if (name){                                    
                        var thumb = $(this).find('field[name="thumbnail"]').text();
                        if(type =='products'){
                            thumb = $(this).find('field[name="original_image_thumbnail"]').text();
                            thumb = 'products/' + thumb;
                            items += '<a class="thumb draggable ' + type + '" id="'+id+'" href="#">' +
                                        '<img src="/{{ MEDIA_URL }}' + thumb + '" alt="' + name + '" />' +
                                    '</a>';
                        }else{
                            items += '<div  style="cursor: pointer;" id="' + id + '" class="thumb ' + type + '">' +
                                        '<img src="/{{ MEDIA_URL }}' + thumb + '" alt="' + name + '" />' +
                                        '<span>' + name + '</span>' +
                                '</div>';
                        }
                    }

                });

                var breadcrumb_tree = '';
                $.ajax({
                    url: "{% url get_category_tree_ajax %}",
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
                
                $(".draggable").draggable({ 
                    revert:true, 
                    helper: 'clone' 
                });
            },
            error: function(msg) {
            }
        });
}