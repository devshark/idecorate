var iDHomeItemize = (function(iDHomeItemize){



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

	var Itemize = function(panelElement){

		var items = panelElement.children();

		Object.defineProperties(this, {
            __el: {
                value: panelElement
            },
            items: {
                value: createPanelItems(items),
                enumerable: true
            }
        });

	};

	iDHomeItemize.createItemize = function(element){

		if(element.length < 1){
			element = $('#itemize');
		}

		var itemize = new Itemize(element);

		return itemize;

	};

	return iDHomeItemize;

}(iDHomeItemize || {}));