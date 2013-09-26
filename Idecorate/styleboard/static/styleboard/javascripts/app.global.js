$(function(){

    /*================================================
        - set heights on page loads
        - set heights on window resize
    =================================================*/
    pannelResize('.sideBarItems, #canvas');
    
});

var resizing;

$(window).resize(function(){

    clearTimeout(resizing);

    resizing = setTimeout(function(){

        pannelResize('.sideBarItems, #canvas');

    }, 100);

});

function pannelResize(elements){

    $(elements).height(0);
    $.each($(elements), function(index, element){
        $(element).height($(element).parents('.cell').outerHeight(true)-$(element).siblings().outerHeight(true)-2);
    });
}
