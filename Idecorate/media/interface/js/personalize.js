$(document).ready(function(){
	populate_save_styleboard();
});

function populate_save_styleboard(){
	var item = eval(PERSONALIZE_ITEM);	
	$.each(item, function(i,v){
		//console.log(v.img[0].a)
		// var elm = $('<div />');
		// elm.attr('_angle',v.angle);
		// elm.addClass('');
	});
}