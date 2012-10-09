$(document).ready(function () {
	
	$(".draggable").draggable({
        helper: 'clone',
        cursor: 'move'
    });

    //set dropable area for the dragable obj
    $("#canvas-wrap").droppable({

        drop: function (e, ui) {
            if ($(ui.draggable)[0].id != "") {

                dropedObj = ui.helper.clone();
                ui.helper.remove();

                product_id = $(ui.draggable)[0].id;

                //get image filename from DB using product_id via ajax

                $.ajax({
                    url: PRODUCT_IMAGE_URL,
                    type: "POST",
                    data: { product_id: product_id},
                    async:   false,
                    success: function(data){

                        product_image = new Image();
                        product_image.src = '/media/products/' + data;
                        
                        img_wrapped = $(product_image).load(function(){
                            $('<div class="product unselected selected"><img src="' + product_image.src + '" /></div>').appendTo('#canvas-wrap').css({
                                top : e.pageY-$('#canvas-wrap').offset().top-product_image.height/2,
                                left :e.pageX-$('#canvas-wrap').offset().left-product_image.width/2,
                            });

                            $('.handles').css({display: 'block'});
                        });

                    },
                    error: function(msg) {
                            
                    }
                });
                
			}
		}
    });

    $('.handles').draggable({
                    helper: 'original',
                    cursor: 'move'
                }).resizable({
                    handles: 'ne,se,nw,sw',
                    aspectRatio: true  
                }).rotatable();
});