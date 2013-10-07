/*================================================
   - global variables
=================================================*/
var category_container = $('.pannel.category');
var product_container = $('.pannel.product');
var total_product_page = 0;
var product_page = 0;
var category_id = 0;
var categories = {};
var products = {};
var	page_products = [];
var product_keyword = null;
var keyword_textbox = $('#keyword_textbox');
var keyword_search_btn = $('#keyword_search_btn');
var embellishment_category_container = $('.pannel.embellishmentCategory');
var embellishment_container = $('.pannel.embellishment');
var embellishment_category_id = 0;
var embellishment_categories = {};
var embellishments = {};
var	page_embellishments = [];
var total_embellishment_page = 0;
var embellishment_page = 0;
var wishlist = {};
var templates = {};

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

	category_container.children('.categoryList').remove();
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

	category_container.append(categoryList);

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

	product_container.find('.mCSB_container').children('.productItem').remove();
	products = {};

};
var displayProducts = function(){

	$.each(page_products, function(index, value){

		if(products.hasOwnProperty(value)){

			var product = products[value].__loadItem(value);
			var product_info = products[value].info_btn;
			product_container.find('.mCSB_container').append(product);

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
	        	productInfo.openPannel(products[value].__id);
	        	e.preventDefault();
	        });

		}

	});

    product_container.mCustomScrollbar("update");

	if(product_page == 0) {
		
    	product_container.mCustomScrollbar("scrollTo", "top");

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



/*================================================
   - start
   - Embellishment Category Objects and functions
=================================================*/
var EmbellishmentCategory = function(data){

	Object.defineProperties(this,{
		ele:{
			value : $('<a href="#"/>'),
			writable : true,
			enumerable : true
		},
		__id : {
			value : data.id
		},
		__title : {
			value : data.title
		},
		__description : {
			value : data.description
		},
		__class : {
			value : 'embellishmentsCategories'
		}
	});

};
Object.defineProperties(EmbellishmentCategory.prototype, {
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

			return this.ele.addClass(this.__class).text(this.__title).attr('object-id',uuid);

		}
	}
});
var clearEmbellishmentCategories = function(){

	embellishment_category_container.children('.embellishmentCategoryList').remove();
	embellishment_categories = {};

};
var displayEmbellishmentCategories = function(){

	var categoryList = $('<ul class="embellishmentCategoryList" />');

	for(var key in embellishment_categories){

		if(embellishment_categories.hasOwnProperty(key)){

			var item = $('<li/>');

			embellishment_categories[key].click(function(object,event){

				$('#load_all_embellishments').remove();
				object.ele.parent().addClass('active').siblings().removeClass('active');
				categoryList.prepend('<li id="load_all_embellishments"><a href="#">all</a></li>');
				event.preventDefault();
				embellishment_category_id = object.__id;
				embellishment_page = 0;
				generateEmbellishments();

			});

			item.html(embellishment_categories[key].__loadItem(key));
			categoryList.append(item);

		}
	}

	$('#load_all_embellishments').live('click', 'a', function(event){

		event.preventDefault();
		embellishment_category_id = 0;
		embellishment_page = 0;
		generateEmbellishments();
		$(this).siblings().removeClass('active');
		$(this).remove();

	});
	embellishment_category_container.append(categoryList);

};
var generateEmbellishmentCategories = function(){

	clearEmbellishmentCategories();

	serverRequest({}, REQUEST_EMBELLISHMENT_CATEGORIES, function(response){

		var data = $.parseJSON(response.embellishment_categories);
    	
    	$.each(data,function(index, value){

    		categoryData = {
    			id : value.pk,
    			title : value.fields.name,
    			description : value.fields.name
    		}
 
			var uuid = Math.uuid(12, 62);
    		embellishment_categories[uuid] = new EmbellishmentCategory(categoryData);

		});
		var uuid = Math.uuid(12, 62);
    		embellishment_categories[uuid] = new EmbellishmentCategory({id:6, title: "Text", description : "Text embellishment"});

		displayEmbellishmentCategories();
	});

};
/*================================================
   - Embellishment Category Objects and functions
   - end
=================================================*/

/*================================================
   - start
   - Embellishment Objects and functions
=================================================*/
var Embellishment = function(data){

	var get_embellishment_type  = function(value){
		for(var key in embellishment_categories){
			var category = embellishment_categories[key];
			if(category.__id == value){
				return key
			}
		}
	};

	Object.defineProperties(this,{
		ele:{
			value : $('<div/>'),
			writable : true,
			enumerable : true
		},
		__id : {
			value : data.id
		},
		__description : {
			value : data.description
		},
		__image : {
			value : data.image
		},
		__thumb : {
			value : data.thumb
		},
		__font : {
			value : data.font
		},
		__type:{
			value : get_embellishment_type(data.type)
		},
		__class : {
			value : 'embellishmentItem'
		}
	});

};
Object.defineProperties(Embellishment.prototype, {
	__loadItem : {
		value : function(uuid){

			var elementItem = this.ele;
			var embellishmentImage = $('<span class="embellishmentImage" />');
			var image = $('<img alt="'+this.__type+'" />');
			var itemOperation = $('<div class="itemOperation"/>');
			var embellishment_category = embellishment_categories[this.__type]
			if(embellishment_category.__id == 6){
				image.attr('src', '/generate_text/?font_size=100&amp;font_text=Abc&amp;font_color=000000000&amp;font_id='+ this.__id +'&amp;font_thumbnail=1');
			}else{
				image.attr('src', '/generate_embellishment/?embellishment_id='+ this.__id +'&amp;embellishment_color=000000000&amp;embellishment_thumbnail=1&amp;embellishment_size=100');
			}
			embellishmentImage.append(image);

			itemOperation.append('<span class="btn"><img src="/static/images/img_trans.gif"><h4>Drag To<span>Styleboard</span></h4></span>');
			
			elementItem.addClass(this.__class + " " + embellishment_category.__title.toLowerCase()).attr('object-id',uuid);
			elementItem.append([embellishmentImage, itemOperation]);

			return elementItem
		}
	}
});
var clearEmbellishments = function(){

	embellishment_container.find('.mCSB_container').children('.embellishmentItem').remove();
	embellishments = {};

};
var displayEmbellishments = function(){

	$.each(page_embellishments, function(index, value){

		if(embellishments.hasOwnProperty(value)){

			var embellishment = embellishments[value].__loadItem(value);
			embellishment_container.find('.mCSB_container').append(embellishment);

			embellishment.draggable({
	            revert:true,
    			appendTo: "body",
    			cursor : "move",
    			containment: "body", 
	            helper: function(){

	            	var cloned = $(this).clone();
	            	cloned.find('.itemOperation').remove();
	            	return cloned;

	            }
	        });
		}

	});

	embellishment_container.find('img').load(function(){
    	embellishment_container.mCustomScrollbar("update");
	});

	if(embellishment_page == 0) {
    	embellishment_container.mCustomScrollbar("scrollTo", "top");
	}
};
var generateEmbellishments = function(){

	if(embellishment_page == 0) {
		clearEmbellishments();
	}

	page_embellishments = []

	var postData = {embellishment_category_id: embellishment_category_id, embellishment_page: embellishment_page};
	serverRequest(postData, REQUEST_EMBELLISHMENT, function(response){

		total_embellishment_page = response.total_page;
		console.log(total_embellishment_page)
		var data = $.parseJSON(response.embellishments);
    	
    	$.each(data,function(index, value){

    		embellishmentData = {
    			id : value.pk,
    			description : value.fields.description,
    			image : value.fields.image,
    			thumb : value.fields.image_thumb,
    			font : value.fields.font,
    			type : (value.fields.e_type === undefined) ? 6 : value.fields.e_type
    		}
			var uuid = Math.uuid(12, 62);
    		embellishments[uuid] = new Embellishment(embellishmentData);
    		page_embellishments.push(uuid); 

		});

		displayEmbellishments();
	});
};

/*================================================
   - Embellishment Objects and functions
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

var pannels = {
	'#products' : {
		element : $('#products'),
		is_empty: function(){
			return ($.isEmptyObject(categories) && $.isEmptyObject(products)) ? true : false;
		},
		action : function(){
			product_container.mCustomScrollbar({
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
		}
	},
	'#embellishments' : {
		element : $('#embellishments'),
		is_empty: function(){
			return ($.isEmptyObject(embellishment_categories) && $.isEmptyObject(embellishments)) ? true : false;
		},
		action : function(){
			embellishment_container.mCustomScrollbar({
		        scrollInertia:200,
		        scrollButtons:{
		            enable:false
		        },
		        theme: 'dark-thick',
		        callbacks:{
		            onTotalScrollOffset : 50,
		            onTotalScroll:function(){

		            	if(embellishment_page <= total_embellishment_page ){
			                ++embellishment_page;
			                generateEmbellishments();
		            	}
		            	
		            }
		        }
		    });
		    generateEmbellishmentCategories();
			generateEmbellishments();
		}
	},
	'#templates' : {
		element : $('#templates'),
		is_empty: function(){
			return $.isEmptyObject(templates);
		},
		action : function(){
			console.log('load templates functions here');
		}
	},
	'#wishlist' : {
		element : $('#wishlist'),
		is_empty: function(){
			return $.isEmptyObject(wishlist);
		},
		action : function(){
			console.log('load wishlist functions here');
		}
	}
};

$(function(){

    var product_pannel = pannels['#products'];
	if(product_pannel.is_empty()){
		product_pannel.action();
	}

    keyword_textbox.keypress(function(e) {
    	code = e.which;
    	if(code==13) {
    		keyword_search_btn.click();
    	}
    });

    
    keyword_search_btn.click(function() {
    	if(keyword_textbox.val() != '' && product_keyword != keyword_textbox.val()) {
    		product_keyword = keyword_textbox.val();
    		generateProducts();
    		$('.clearSearch').removeClass('hidden');
    	}
    });

    $('.clearSearch').click(function(e){
    	e.preventDefault();
    	product_keyword = '';
		product_page = 0;
		category_id = 0;
		keyword_textbox.val('');
		generateProducts();
		$('.clearSearch').addClass('hidden');
    });

    $('.sideBarMenu a').click(function(e){

    	e.preventDefault();
    	var link = $(this);
    	var pannel = pannels[link.attr('href')];
    	if(pannel.is_empty()){
    		pannel.action();
    	}

    	link.addClass('tabActive')
    		.parent()
    		.siblings()
    		.children('a')
    		.removeClass('tabActive');
    	pannel.element.show()
			.addClass('pannelActive')
    		.siblings('.tabs').hide()
    		.removeClass('pannelActive');

    });
});
