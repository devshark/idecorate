function pannelResize(elements){

    list = elements.split(',');

    $.each(list, function(index, element){

        $(element).height($(element).parents('.cell').outerHeight(true)-$(element).siblings().outerHeight(true)-2);

    });
}
