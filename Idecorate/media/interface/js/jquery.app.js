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
                /*
                $.ajax({
                    url : 'class/method/',
                    data: {},
                    dataType: json,
                    type: 'POST',
                    success: function(data){

                    }
                });
                
                product_image = new Image();
                product_image.src = '/media/dummyproduct/large/img_default_'+product_id+'.jpg';
                
                img_wrapped = $(product_image).load(function(){
                    $('<div class="product unselected selected"><img src="' + product_image.src + '" /></div>').appendTo('#canvas-wrap').css({
                        top : e.pageY-$('#canvas-wrap').offset().top-product_image.height/2,
                        left :e.pageX-$('#canvas-wrap').offset().left-product_image.width/2,
                    });
                });
                */
			}
		}
    });

    $('.selected').click(function(){
        console.log('text');
    });

    $('.handles').draggable({
                    helper: 'original',
                    cursor: 'move'
                }).resizable({
                    handles: 'ne,se,nw,sw',
                    aspectRatio: true  
                }).rotatable();
});