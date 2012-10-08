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

                //get odometer for thumbnail and set to get large image of the thumbnail
                var thumbImg    = dropedObj.find('img').attr('src');
                var defaultImg  = thumbImg.split('/');
                    defaultImg  = defaultImg[4];
                    defaultImg  = defaultImg.split('_');
                    defaultImg  = '<img id="large_'+defaultImg[2]+'" src="/media/dummyproduct/large/img_default_'+defaultImg[2]+'" />';

                //replace content by large image version of thumbnail
                dropedObj.html(defaultImg);

                //set image to a minimal width and not the default size
                dropedObj.find('img').css({
                    'width': 150
                });

                //prepending dragged obj to canvass
                dropedObj.appendTo('#canvas-wrap').css({
                    top : e.pageY-$('#canvas-wrap').offset().top-dropedObj.height()/2,
                    left :e.pageX-$('#canvas-wrap').offset().left-dropedObj.width()/2
                });

                //resizing active obj inside the canvas
                //**needs improvement after rotate
                dropedObj.find('img').resizable({
                    minWidth: 150,
                    handles: 'ne,se,nw,sw',
                    aspectRatio: true  
                });

                //setting active image to be dragable inside the canvas
                dropedObj.draggable({
                    helper: 'original',
                    cursor: 'move'
                });

                dropedObj.find('img').parent().rotatable(function(){
                    console.log('test');
                });

                
			}
		}
    });
});