/*!
 * jQuery Element Rotation Plugin
 *
 * Requires jQueryUI 
 *
 * Copyright (c) 2010 Pavel Markovnin
 * Dual licensed under the MIT and GPL licenses.
 *
 * http://vremenno.net
 */

(function($) {
	$.fn.rotatable = function(options) {
	
		// Default Values
		var defaults = {
 			rotatorClass: 'ui-rotatable-handle',
 			mtx:          [1, 0, 0, 1]
  		},  opts        = $.extend(defaults, options),
  		    _this       = this,
  		    _rotator;      
  		  
  		// Initialization 
  		this.intialize = function() {
        	this.createHandler();
        	
        	dims = {
				'w': _this.width(),
				'h': _this.height()
			};
        	this.updateRotationMatrix(opts.mtx);
        };
        
        // Create Rotation Handler
        this.createHandler = function() {
        	_rotator = $('<div class="'+ opts.rotatorClass+ '"></div>');
  			_this.append(_rotator);
  			
  			this.bindRotation();
        };
                
        // Bind Rotation to Handler
        this.bindRotation = function() {
        
        	// IE Fix
        	if($.browser.msie) {
	        	_rotator.mousedown(function(e) {
	        		e.stopPropagation();
	        	});
	        
	        	_rotator.mouseup(function(e) {
	        		e.stopPropagation();
	        	});
	        }
			
        	_rotator.draggable({
                opacity: 0.001,
				handle: _rotator.wrap('<div class="ui-rotatable-handle-wrap" />'),
				helper: 'clone',
				revert: false,
				start:  function(e) {
        			e.stopPropagation();
        			e.stopImmediatePropagation();
        			
        			// TL Corner Coords
        			tl_coords = {
        				'x': parseInt(_this.parent().css('left')),
						'y': parseInt(_this.parent().css('top'))
        			};
        			
        			// Element Width & Height()
        			dims = {
        				'w': _this.width(),
        				'h': _this.height()
        			};
					
					// Center Coords
					center_coords = {
						'x': _this.offset().left + _this.width()  * 0.5,
						'y': _this.offset().top  + _this.height() * 0.5
					};
				},
				drag:  function(e) {
        			e.stopPropagation();
        			e.stopImmediatePropagation();
        			
					// Mouse Coords
					mouse_coords = {
						'x': e.pageX,
						'y': e.pageY
					};	
					
					angle = _this.radToDeg(_this.getAngle(mouse_coords, center_coords)) - 90;
                    

                    // setting handles cursor depending on angle.

                    
                    cursoring = angle+90;
                    if (cursoring >= 67.5 && cursoring <= 112.5) {
                        //console.log('nw = nw,ne = ne, se = se,sw = sw');
                        $('.ui-resizable-nw').css({cursor: 'nw-resize'});
                        $('.ui-resizable-ne').css({cursor: 'ne-resize'});
                        $('.ui-resizable-se').css({cursor: 'se-resize'});
                        $('.ui-resizable-sw').css({cursor: 'sw-resize'});
                    }else if(cursoring >= 112.5 && cursoring <= 157.5){
                        //console.log('nw = w, ne = n, se = e, sw = s');
                        $('.ui-resizable-nw').css({cursor: 'w-resize'});
                        $('.ui-resizable-ne').css({cursor: 'n-resize'});
                        $('.ui-resizable-se').css({cursor: 'e-resize'});
                        $('.ui-resizable-sw').css({cursor: 's-resize'});
                    }else if(cursoring >= 157.5 && cursoring <= 202.5){
                        //console.log('nw = sw, ne = nw, se = ne, sw = se');
                        $('.ui-resizable-nw').css({cursor: 'sw-resize'});
                        $('.ui-resizable-ne').css({cursor: 'nw-resize'});
                        $('.ui-resizable-se').css({cursor: 'ne-resize'});
                        $('.ui-resizable-sw').css({cursor: 'se-resize'});
                    }else if(cursoring >= 202.5 && cursoring <= 247.5){
                        //console.log('nw = s, ne = w, se = n, sw = e');
                        $('.ui-resizable-nw').css({cursor: 's-resize'});
                        $('.ui-resizable-ne').css({cursor: 'w-resize'});
                        $('.ui-resizable-se').css({cursor: 'n-resize'});
                        $('.ui-resizable-sw').css({cursor: 'e-resize'});
                    }else if(cursoring >= 247.5 && cursoring <= 292.5){
                        //console.log('nw = se, ne = sw, se = nw, sw = ne');
                        $('.ui-resizable-nw').css({cursor: 'se-resize'});
                        $('.ui-resizable-ne').css({cursor: 'sw-resize'});
                        $('.ui-resizable-se').css({cursor: 'nw-resize'});
                        $('.ui-resizable-sw').css({cursor: 'ne-resize'});
                    }else if(cursoring >= 292.5 && cursoring <= 337.5){
                        //console.log('nw = e, ne = s, se = w, sw = n');
                        $('.ui-resizable-nw').css({cursor: 'e-resize'});
                        $('.ui-resizable-ne').css({cursor: 's-resize'});
                        $('.ui-resizable-se').css({cursor: 'w-resize'});
                        $('.ui-resizable-sw').css({cursor: 'n-resize'});
                    }else if(cursoring >= 337.5 && cursoring >= 360 || cursoring >= 0 && cursoring <= 22.5){
                        //console.log('nw = ne, ne = se, se = sw, sw = nw');
                        $('.ui-resizable-nw').css({cursor: 'ne-resize'});
                        $('.ui-resizable-ne').css({cursor: 'se-resize'});
                        $('.ui-resizable-se').css({cursor: 'sw-resize'});
                        $('.ui-resizable-sw').css({cursor: 'nw-resize'});
                    }else if(cursoring >= 22.5 && cursoring <= 67.5){
                        //console.log('nw = n, ne = e, se = s, sw = w');
                        $('.ui-resizable-nw').css({cursor: 'n-resize'});
                        $('.ui-resizable-ne').css({cursor: 'e-resize'});
                        $('.ui-resizable-se').css({cursor: 's-resize'});
                        $('.ui-resizable-sw').css({cursor: 'w-resize'});
                    }


                    if($.browser.msie)
						angle = - angle;
					
					return _this.rotate(angle);
				}
        	});
        };
        
        // Get Angle
        this.getAngle = function(ms, ctr) {
        	var x     = ms.x - ctr.x,
        	    y     = - ms.y + ctr.y,
        	    hyp   = Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2)),
        	    angle = Math.acos(x / hyp);
        	
        	if (y < 0) {    
        		angle = 2 * Math.PI - angle;
        	}
        	
		    return angle;
        };
        
        // Convert from Degrees to Radians
        this.degToRad = function(d) {
        	return (d * (Math.PI / 180));
        };
        
        // Convert from Radians to Degrees
        this.radToDeg = function(r) {
        	return (r * (180 / Math.PI));
        };
        
        // Rotate Element to the Given Degree
        this.rotate = function(degree) {
        	var cos = Math.cos(_this.degToRad(-degree)),
        	    sin = Math.sin(_this.degToRad(-degree)),
        	    mtx = [cos, sin, (-sin), cos];
        	    
        	this.updateRotationMatrix(mtx);
        };
        
        // Get CSS Transform Matrix (transform: matrix)
        this.getRotationMatrix = function() {
        	var _matrix = _this.css('transform') ? _this.css('transform') : 'matrix(1, 0, 0, 1, 0, 0)';
			    _m      = _matrix.split(','),
        	    m       = [];
        	    
        	for (i = 0; i < 4; i++) {
        		m[i] = parseFloat(_m[i].replace('matrix(', ''));
        	}
        	        	
        	return m;
        };
        
        // Update CSS Transform Matrix (transform: matrix)
        this.updateRotationMatrix = function(m) {
        	var matrix = 'matrix('+ m[0] +', '+ m[1] +', '+ m[2] +', '+ m[3] +', 0, 0)',
        	    ie_matrix = "progid:DXImageTransform.Microsoft.Matrix(M11='"+m[0]+"', M12='"+m[1]+"', M21='"+m[2]+"', M22='"+m[3]+"', sizingMethod='auto expand')";        	
        	  
        	_this.css({
				'-moz-transform'   : matrix,
				'-o-transform'     : matrix,
        		'-webkit-transform': matrix,
        		'-ms-transform'    : matrix,
				'transform'        : matrix,
				'filter'           : ie_matrix,
				'-ms-filter'       : '"' + ie_matrix + '"'
			});
        	
        	// IE Fix
        	if($.browser.msie) {
        		var	coef    = dims.w / dims.h,
	        	    _height = _this.parent().parent().height()
	        	    _width  = coef * _height,
	        	    _top    = (dims.h - _height) / 2,
	        	    _left   = (dims.w - _width) / 2;
	        	
	        	_this.parent().parent().css({
	        		'width'      : _width
	        	});
	        	
	        	_this.parent().css({
	        		'left': _left,
	        		'top' : _top
	        	});
        	}
        };
        
        return this.intialize();  		
	}
})(jQuery);