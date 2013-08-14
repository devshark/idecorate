var iDSidebar = (function(iDSidebar){
	
	var iDSidebarSettings = {};

	var SidebarItem = function(){

		Object.defineProperties(this, {
			__el : {
				value : $('<div class="thumb"/>'),
				writable : true,
				emutable : true
			},
			__img : {
				value : $('<img />')
			},
			__label : {
				value : $('<span/>')
			}
		});

	};

	Object.defineProperties(SidebarItem.prototype, {
		mousedown : {
			value : function(callback){
				this.__el.on('mousedown', function(){
					callback();
				});
			},
			emutable : true
		},
		get_id : {
			get : function(){
				return this.__id;
			},
			emutable : true
		}
	});

	var ProductCategory = function(data){

		SidebarItem.call(this);

		Object.defineProperties(this,{
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

	ProductCategory.prototype = Object.create(SidebarItem.prototype, {

		callback : {
			value : function(){
				iDSidebarSettings.categoryId = this.__id;
				Sidebar.prototype.removeElements('#products');
				Sidebar.prototype.serverRequest(APP_SIDEBAR_ITEMS_URL, iDSidebarSettings);
				Sidebar.prototype.generateItems();
				Sidebar.prototype.removeElements('#breadcrumb_product');
				Sidebar.prototype.generateBreadcrumb();
			},
			emutable : true
		},
		loadItem : {
			value : function(){

				var self = this;

				this.__el.addClass(this.__class);
				this.__img.attr({

					'src' : MEDIA_URL+this.__thumb,
					'alt' : this.__name

				});
				
				this.__label.text(this.__name);

				this.__el.append(this.__img, this.__label);
				this.mousedown(this.callback.bind(this));

				Sidebar.prototype.appendTo('#products', this.__el);

				this.__img.load(function(){

					console.log(self.__name + ' category is loaded');

				});

			}
		}
	});

	var Product = function(data){

		SidebarItem.call(this);

		Object.defineProperties(this,{
			__id : {
				value : data.id
			},
			__name : {
				value : data.name
			},
			__sku : {
				value : data.sku
			},
			__description : {
				value : data.description
			},
			__thumb : {
				value : data.thumbnail
			},
			__image1 : {
				value : data.main_image
			},
			__image2 : {
				value : data.alt_image
			},
			__categories : {
				value : data.categories
			},
			__price : {
				value : data.price
			},
			__defaultQty : {
				value : data.default_quantity
			},
			__group : {
				value : data.group
			},
			__class : {
				value : 'products'
			}
		});

	};

	Product.prototype = Object.create(ProductCategory.prototype, {

		callback : {
			value : function(){
				console.log(this.__name);
			},
			emutable : true
		},
		loadItem : {
			value : function(){

				var self = this;

				this.__el.addClass(this.__class);
				this.__img.attr({

					'src' : MEDIA_URL + 'products/' + this.__thumb,
					'alt' : this.__name

				});

				var name_truncated = truncateStr(this.__name,10);

				this.__label.text(name_truncated);

				this.__el.append(this.__img, this.__label);
				this.mousedown(this.callback.bind(this));

				Sidebar.prototype.appendTo('#products', this.__el);

				this.__img.load(function(){

					console.log(self.__name + ' product is loaded');

				});

			}
		}
	});

	var EmbellishmentCategory = function(data){ };

	var Embellishment = function(data){ };

	var Template = function(data){ };

	var createSidebarItems = function(objectData){

		var generateCategory = function(object){

			var data = {
				'id': object.pk, 
				'name': object.fields.name, 
				'thumbnail': object.fields.thumbnail, 
				'parent' : object.fields.parent
			};

			return new ProductCategory(data)
		};

		var generateProduct = function(object){

			var data = {
				'id': object.pk, 
				'categories': object.fields.categories, 
				'name': object.fields.name, 
				'sku' : object.fields.sku, 
				'description': object.fields.description, 
				'thumbnail': object.fields.original_image_thumbnail, 
				'main_image' : object.fields.original_image, 
				'alt_image': object.fields.no_background, 
				'price': 0, 
				'default_quantity' : object.fields.default_quantity, 
				'group' : object.fields.guest_table
			};

			return new Product(data)
		};

		var items = $.makeArray();

		var rawItems = $.parseJSON(objectData.data);

		$.each(rawItems, function(index, value){

			switch(objectData.type){

				case 'category': 

					var item = generateCategory(value);

					break;

				case 'product':

					var item = generateProduct(value);
					break;

			}

			item.loadItem();

			items.push(item);
		});

		return items;

	};

	var BreadcrumbLink = function(id, name, clickable){

		Object.defineProperties(this, {
			__ele : {
				value : $('<li/>')
			},
			__id : {
				value : id
			},
			__name : {
				value : name
			},
			__clickable : {
				value : typeof clickable === "undefined" ? true : false
			}

		});

	};

	Object.defineProperties(BreadcrumbLink.prototype, {
		callback : {
			value : function(){
				iDSidebarSettings.categoryId = this.__id;
				Sidebar.prototype.removeElements('#products');
				Sidebar.prototype.serverRequest(APP_SIDEBAR_ITEMS_URL, iDSidebarSettings);
				Sidebar.prototype.generateItems();
				Sidebar.prototype.removeElements('#breadcrumb_product');
				Sidebar.prototype.generateBreadcrumb();
			}
		},
		mousedown : {
			value : function(callback){
				if(this.__clickable){
					this.__ele.on('mousedown', function(e){
						e.preventDefault();
						e.stopPropagation();
						callback();
					});
				}
			},
			emutable : true
		},
		loadItem : {
			value : function(){

				var element = this.__clickable ? $('<a />') : $('<span />');
				element.append(this.__name);
				this.__ele.append(element);

				this.mousedown(this.callback.bind(this));

			},	
			emutable : true
		}

	});

	var createBreadcrumb = function(objects){

		var breadcrumb = $('<ul />');
		breadcrumb.addClass('breadcrumb');

		$.each(objects, function(index, value){

			var direction = value.__ele.clone();
			var link = value.__ele;

			direction.append('<span>></span>');
			value.loadItem();

			if(value.__clickable){

				link.find('a').attr('href','#');
			}

			if(index+1 == objects.length){

				breadcrumb.append(link);

			}else{

				breadcrumb.append(link,direction);
			}


		});

		return breadcrumb;
	};

	var createSidebarBreadcrumb = function(objectData){

		var linkArray = $.makeArray();

		if(objectData.length > 0){

			linkArray.push(new BreadcrumbLink(0, 'All'));

			$.each(objectData, function(index,value){

				if (index+1 == objectData.length){

					linkArray.push(new BreadcrumbLink(value[0], value[1], false));

				}else{

					linkArray.push(new BreadcrumbLink(value[0], value[1]));
				}
			});

			linkArray.push(new BreadcrumbLink(objectData.length-2 < 0 ? 0 : objectData[objectData.length-2][0], 'Back'));

		}

		Sidebar.prototype.appendTo('#breadcrumb_product',createBreadcrumb(linkArray));

		return linkArray;

	};

	var requestSidebarItems = function(){

		var request = {};

		Object.defineProperties(request, {
			type : {
				value: "",
				writable : true
			},
			data : {
				value: {},
				writable : true
			},
			loadData : {
				value: function(success, returnData){

					this.breadcrumb = returnData.breadcrumb;

					if ('categories' in returnData){

						this.data = returnData.categories;	
						this.type = 'category';	

					}else if('products' in returnData){

						this.data = returnData.products;	
						this.type = 'product';
						
					}

				},
				emutable: true
			},
			prepareRequest : {
				value: function(url, postData){

					makeRequest(url, postData, this.loadData.bind(this));

				},
				emutable: true
			},
			getData : {
				get : function(){
					return {type : this.type, data : this.data};
				},
				emutable: true
			},
			getBreadcrumb : {
				get : function(){
					return this.breadcrumb;
				},
				emutable: true
			}

		});
		
		return request;

	};

	var Sidebar = function(){};

	Object.defineProperties(Sidebar.prototype, {
		appendTo : {
			value : function(parentElement, element){

				$(parentElement).append(element);
			},
			emutable : true
		},
		removeElements : {
			value : function(element){

				$(element).children().remove();
			},
			emutable : true
		},
		serverRequest : {
			value : function(url, postData){

				var request = requestSidebarItems();
				request.prepareRequest(url, postData);

				this.itemData = request.getData;
				this.breadcrumbData = request.getBreadcrumb;
			}
		},
		generateItems : {
			value : function(){

				this.items = createSidebarItems(this.itemData);

			}
		},
		generateBreadcrumb : {
			value : function(){
				this.breadcrumb = createSidebarBreadcrumb(this.breadcrumbData)
			}
		}
	});

	var initialize = function(){

		iDSidebarSettings = {
			searchKeyword : $('#search').length < 1 ? '' : $('#search').val(),
			categoryId : CATEGORY_ID
		};

	};

	iDSidebar.createSidebar = function(){

		initialize();

		var sidebar = new Sidebar();
		sidebar.serverRequest(APP_SIDEBAR_ITEMS_URL, iDSidebarSettings);

		return sidebar;

	};

	return iDSidebar;

}(iDSidebar || {}));

var makeRequest = function(action, postData, callback){

	var data;
	var success = false;
	var sync = function(value){

		return value;

	};

	var request = $.ajax({
		async:false,
		url: action,
		type: "POST",
		dataType : 'json',
		data: postData
	});

	request.done(function(returnData){

		success = sync(true);
		data = sync(returnData);

	});

	request.fail(function(jqXHR, textStatus){

		data = sync(textStatus);
	
	});

	callback(success, data);

};

sidebar = iDSidebar.createSidebar();
sidebar.generateItems();