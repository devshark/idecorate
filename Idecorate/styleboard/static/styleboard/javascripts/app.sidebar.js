/*================================================
   - global variables
=================================================*/
var categoryContainer = $('.pannel.category');
var productContainer = $('.pannel.product');
var total_product_page = 0;
var product_page = 0;
var category_id = 0;
var categories = {};
var products = {}
var	page_products = [];
var product_keyword = null;
var keyword_textbox = $('#keyword_textbox');

/*================================================
   - start
   - Category Objects and functions
=================================================*/
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

				$('#load_all').remove();
				object.ele.parent().addClass('active').siblings().removeClass('active');
				categoryList.prepend('<li id="load_all"><a href="#">all</a></li>');
				event.preventDefault();
				category_id = object.__id;
				product_page = 0;
				generateProducts();

			});

			item.html(categories[key].__loadItem(key));
			categoryList.append(item);

		}
	}

	$('#load_all').live('click', 'a', function(event){

		event.preventDefault();
		product_page = 0;
		category_id = 0;
		generateProducts();
		$(this).siblings().removeClass('active');
		$(this).remove();

	});

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
/*================================================
   - Category Objects and functions
   - end
=================================================*/

/*================================================
   - start
   - Product Objects and functions
=================================================*/
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
		},
		info_btn : {
			value : $('<a class="btn info"><img src="/static/images/img_trans.gif"><h4>Info</h4></a>')
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

			image.attr('src', MEDIA_URL + 'products/' + this.__thumb);
			productImage.append(image);

			productInfo.append('<h4>'+ this.__name +'</h4>');
			productInfo.append('<h3>$'+ parseFloat(this.__unit_price).toFixed(2) +'</h3>');
			productInfo.append('<h5>'+ this.__default_quantity + ' per ' + this.__default_quantity_unit +'</h5>');

			itemOperation.append('<span class="btn"><img src="/static/images/img_trans.gif"><h4>Drag To<span>Styleboard</span></h4></span>');
			itemOperation.append(this.info_btn.attr('href', PRODUCT_PAGE + this.__id + '/'));

			elementItem.addClass(this.__class).attr('object-id',uuid);
			elementItem.append([productImage, productInfo, itemOperation]);

			return elementItem
		}
	}
});
var clearProducts = function(){

	productContainer.find('.mCSB_container').children('.productItem').remove();
	products = {};

};
var displayProducts = function(){

	$.each(page_products, function(index, value){

		if(products.hasOwnProperty(value)){

			var product = products[value].__loadItem(value);
			var product_info = products[value].info_btn;
			productContainer.find('.mCSB_container').append(product);

			product.draggable({
	            revert:true,
    			appendTo: "body",
    			cursor : "move",
    			containment: "body", 
	            helper: function(){

	            	var cloned = $(this).clone();
            	 	var productName = products[value].__name;
            	 	cloned.find('.productInfo, .itemOperation').remove();
            	 	cloned.append('<h3>'+ productName +'</h3>');
	            	return cloned;

	            }
	        });

	        product_info.click(function(e){
	        	productInfo.openPannel();
	        	e.preventDefault();
	        });

		}

	});

    productContainer.mCustomScrollbar("update");

	if(product_page == 0) {
		
    	productContainer.mCustomScrollbar("scrollTo", "top");

	}
};
var generateProducts = function(){

	if(product_page == 0) {

		clearProducts();
	}

	page_products = []

	var postData = {category_id: category_id, product_page: product_page, product_keyword: product_keyword};
	serverRequest(postData, REQUEST_PRODUCTS, function(response){

		total_product_page = response.total_page;
		var data = $.parseJSON(response.products);
    	
    	$.each(data,function(index, value){

    		productData = {
    			product : value.fields.product,
    			unit_price : value.fields._unit_price
    		}
 
			var uuid = Math.uuid(12, 62);
    		products[uuid] = new Product(productData);
    		page_products.push(uuid); 

		});

		displayProducts();
	});
};

/*================================================
   - Product Objects and functions
   - end
=================================================*/

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

$(function(){

    productContainer.mCustomScrollbar({
        scrollInertia:200,
        scrollButtons:{
            enable:false
        },
        theme: 'dark-thick',
        callbacks:{
            onTotalScrollOffset : 50,
            onTotalScroll:function(){

            	if(product_page <= total_product_page ){
	                ++product_page;
	                generateProducts();
            	}
            	
            }
        }
    });
    generateCategories();
    generateProducts();

    keyword_textbox.keypress(function(e) {
    	code = e.which;
    	if(code==13) {
    		product_keyword = $(this).val();
    		generateProducts();
    	}
    });
});
