var pannelResize = function(elements){

    $(elements).height(0);
    $.each($(elements), function(index, element){

        $(element).height($(element).parents('.cell').outerHeight(true)-$(element).siblings().outerHeight(true)-2);

    });
};

var StyleboardIntro = function(){
    
}

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
        productPage.pannelResize();

    }, 100);

});