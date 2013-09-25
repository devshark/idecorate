var categories = {};
var categoryContainer = $('.pannel.category');
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

					callback.apply(null,[self, event])

				}
			});

		},
		enumerable : true
	},
	__loadItem : {
		value : function(uuid){

			return this.ele.addClass(this.__class).text(this.__name).attr('object-id',uuid);

		}
	}
});
var clearCategories = function(){

	categoryContainer.children('.categoryList').remove();
	categories = {};

};
var displayCategories = function(){

	var categoryList = $('<ul class="categoryList" />');

	for(var key in categories){

		if(categories.hasOwnProperty(key)){

			var item = $('<li/>');
			categories[key].click(function(object,event){

				object.ele.parent().addClass('active').siblings().removeClass('active');
				event.preventDefault();
				generateProducts(object.__id);

			});
			item.html(categories[key].__loadItem(key));
			categoryList.append(item);

		}
	}

	categoryContainer.append(categoryList);

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
 
			var uuid = Math.uuid(12, 62);
    		categories[uuid] = new ProductCategory(categoryData);

		});

		displayCategories();
	});

};


var products = {}
var productContainer = $('.pannel.product');
var Product = function(data){

	Object.defineProperties(this,{
		ele:{
			value : $('<div/>'),
			writable : true,
			enumerable : true
		},
		__id : {
			value : data.product.id
		},
		__name : {
			value : data.product.name
		},
		__description : {
			value : data.product.description
		},
		__thumb : {
			value : data.product.thumb
		},
		__opaque_image : {
			value : data.product.opaque_image
		},
		__transparent_image : {
			value : data.product.transparent_image
		},
		__categories : {
			value : data.product.categories
		},
		__default_quantity : {
			value : data.product.default_quantity
		},
		__default_quantity_unit : {
			value : data.product.default_quantity_unit
		},
		__unit_price : {
			value : data.unit_price
		},
		__class : {
			value : 'productItem products'
		}
	});

};
Object.defineProperties(Product.prototype, {
	__loadItem : {
		value : function(uuid){

			var elementItem = this.ele;
			var productImage = $('<span class="productImage" />');
			var image = $('<img alt="'+this.__name+'" />');
			var productInfo = $('<span class="productInfo"/>'); 
			var itemOperation = $('<div class="itemOperation"/>');

			image.attr('src', MEDIA_URL + '/products/' + this.__thumb);
			productImage.append(image);

			productInfo.append('<h4>'+ this.__name +'</h4>');
			productInfo.append('<h3>$'+ parseFloat(this.__unit_price).toFixed(2) +'</h3>');
			productInfo.append('<h5>'+ this.__default_quantity + ' per ' + this.__default_quantity_unit +'</h5>');

			itemOperation.append('<span class="btn"><img src="/static/images/img_trans.gif"><h4>Drag To<span>Styleboard</span></h4></span>');
			itemOperation.append('<a class="btn info" href="'+ PRODUCT_PAGE + this.__id +'/"><img src="/static/images/img_trans.gif"><h4>Info</h4></a>');

			elementItem.addClass(this.__class).attr('object-id',uuid);
			elementItem.append([productImage, productInfo, itemOperation]);

			return elementItem
		}
	}
});
var clearProducts = function(){

	productContainer.children('.productItem').remove();
	products = {};

};
var divObjectIdExists = function(key){
	ret = false;
	div = 'div[object-id="' + key + '"]';
	if($(div).hasClass('products')) {
		ret = true;
	}
	return ret
};
var displayProducts = function(){

	for(var key in products){

		if(products.hasOwnProperty(key)){
			if(!divObjectIdExists(key)) {
				productContainer.append(products[key].__loadItem(key));
			}
		}
	}

};
var generateProducts = function(category_id, product_page){

	if(product_page === undefined) {
		clearProducts();
	} 

	var postData = {category_id: (category_id === undefined) ? 0 : category_id,
					product_page: (product_page === undefined) ? 0: product_page};
	serverRequest(postData, REQUEST_PRODUCTS, function(response){

		var data = $.parseJSON(response.products);
    	
    	$.each(data,function(index, value){

    		productData = {
    			product : value.fields.product,
    			unit_price : value.fields._unit_price
    		}
 
			var uuid = Math.uuid(12, 62);
    		products[uuid] = new Product(productData);

		});

		displayProducts();
	});
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
generateProducts();