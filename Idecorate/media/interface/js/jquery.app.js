$(document).ready(function () {

    //set dropable area for the dragable obj
    $("#canvas-wrap").droppable({

        drop: function (e, ui) {
            if ($(ui.draggable)[0].id != "") {

                dropedObj = ui.helper.clone();
                ui.helper.remove();

                product_id = $(ui.draggable)[0].id;
                product_image_src = '/media/products/';

                //get image filename from DB using product_id via ajax
                $.ajax({
                    url: PRODUCT_IMAGE_URL,
                    type: "POST",
                    data: { product_id: product_id},
                    async:   false,
                    success: function(data){
                        product_image_src = product_image_src+data;
                        
                    },
                    error: function(msg) {
                    }
                });

                product_image = new Image();
                product_image.src = product_image_src;

                new_image = $('<img src="'+product_image_src+'" />');
                    
                new_image.width(200);

                dropedObj = $('<div class="product" />');

                dropedObj.html('');

                new_image.appendTo(dropedObj);

                dropedObj.appendTo('#canvas-wrap');

                dropedObj.css({
                    top : e.pageY-$('#canvas-wrap').offset().top-dropedObj.height()/2,
                    left: e.pageX-$('#canvas-wrap').offset().left-dropedObj.width()/2
                });

                dropedObj.find('img').resizable({
                            handles: 'ne,se,nw,sw',
                            aspectRatio: true  
                        });

                dropedObj.draggable({
                            helper: 'original',
                            cursor: 'move'
                        });

                dropedObj.find('img').parent().rotatable();


                /*$(product_image).load(function(){

                    new_image = $('<img src="'+product_image_src+'" />');
                    
                    new_image.width(product_image.width*.40);

                    dropedObj = $('<div class="product" />');

                    dropedObj.html('');

                    new_image.appendTo(dropedObj);

                    dropedObj.appendTo('#canvas-wrap');

                    dropedObj.css({
                        top : e.pageY-$('#canvas-wrap').offset().top-dropedObj.height()/2,
                        left: e.pageX-$('#canvas-wrap').offset().left-dropedObj.width()/2
                    });

                    dropedObj.find('img').resizable({
                                handles: 'ne,se,nw,sw',
                                aspectRatio: true  
                            });

                    dropedObj.draggable({
                                helper: 'original',
                                cursor: 'move'
                            });

                    dropedObj.find('img').parent().rotatable();


                });*/


                /*product_image = new Image();
                product_image.src = '/media/products/' + data;
                
                img_wrapped = $(product_image).load(function(){
                    $('<div class="product unselected selected"><img src="' + product_image.src + '" /></div>').appendTo('#canvas-wrap').css({
                        top : e.pageY-$('#canvas-wrap').offset().top-product_image.height/2,
                        left :e.pageX-$('#canvas-wrap').offset().left-product_image.width/2,
                    });

                    $('.handles').css({display: 'block'});
                });*/
			}
		}
    });

    /*$('.handles').draggable({
                    helper: 'original',
                    cursor: 'move'
                }).resizable({
                    handles: 'ne,se,nw,sw',
                    aspectRatio: true  
                }).rotatable();*/
});