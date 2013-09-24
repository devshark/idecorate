var categories = [];

var ProductCategory = function(data){

	Object.defineProperties(this,{
		ele:{
			value : $('<a href="#"/>'),
			writable : true,
			enumerable : true
		},
		__id : {
			value : data.id
		},
		__thumb : {
			value : data.thumbnail
		},
		__name : {
			value : data.name
		},
		__parent : {
			value : data.parent
		},
		__class : {
			value : 'categories'
		}
	});

};

Object.defineProperties(ProductCategory.prototype, {
	click :{
		value : function(callback){

			var self = this;

			self.ele.click(function(event){

				if($.isFunction(callback)){

					callback.apply(null,[event])

				}
			});

		},
		enumerable : true
	},
	loadItem : {
		value : function(){

			return this.ele.addClass(this.__class).text(this.__name);

		},
		enumerable : true
	},
	appendTo : {
		value : function(element){

			this.loadItem().appendTo(element);
		},
		enumerable : true
	}
});

var clearCategories = function(){

	$('.pannel.category').children(':not(h3)').remove();
	categories = [];

};

var generateCategories = function(){

	clearCategories();

	serverRequest({}, REQUEST_CATEGORIES, function(response){

		var data = $.parseJSON(response.categories);
    	
    	$.each(data,function(index, value){

    		categoryData = {
    			id : value.pk,
    			thumbnail : value.fields.thumbnail,
    			name : value.fields.name,
    			parent : value.fields.parent
    		}

    		category = new ProductCategory(categoryData);
    		categories.push(category);

		});

		$.each(categories, displayCategory);

	});

};

var displayCategory = function(index, category){

	category.click(function(event){

		event.preventDefault();
		generateCategories();

	});

	category.appendTo('.pannel.category');

};

var generateProducts = function(){
	
};

var serverRequest = function(data, url, success, fail){

	var request;
	request = $.ajax({
        url: url,
        type: "POST",
        data: data,
        async: true
    });

    request.done(function (response, textStatus, jqXHR){

    	if($.isFunction(success)){

    		success.apply(null, [response]);

		}
    	
    });

    request.fail(function (jqXHR, textStatus, errorThrown){
        
    	if($.isFunction(fail)){

    		fail.apply(null, [textStatus, errorThrown]);

		}

    });

    request.always(function(){

    });

    return request;
};

generateCategories();