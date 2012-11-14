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
             			mtx: [1, 0, 0, 1],
                        rotateAlso : ''
  		                },

        opts        = $.extend(defaults, options),
	    _this       = this,
	    _rotator;      
  		  
  		// Initialization 
  		this.intialize = function() {
        	this.createHandler();
        	this.updateRotationMatrix(opts.mtx);
        };
        
        // Create Rotation Handler
        this.createHandler = function() {
        	_rotator = $('<div class="'+opts.rotatorClass+'-tip"></div>');
            _rotator = $('<div class="'+opts.rotatorClass+'"></div>').append(_rotator);
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

            _rotator.on({
                mousedown:function(e){
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    $rotatable = $(this).addClass('ui-rotating');
                    
                    // TL Corner Coords
                    tl_coords = {
                        'x': parseInt(_this.parent().css('left')),
                        'y': parseInt(_this.parent().css('top'))
                    };
                    
                    // Center Coords
                    center_coords = $.parseJSON(_this.attr('ctr'));
                    // center_coords = {
                    //     'x': raw_ctr.x,
                    //     'y': raw_ctr.y
                    // };

                    $rotatable.parents().on({
                        mousemove:function(e){
                            e.stopPropagation();
                            e.stopImmediatePropagation();

                            // Mouse Coords
                            mouse_coords = {
                                'x': e.pageX,
                                'y': e.pageY
                            };  
                            
                            angle = _this.getAngle(mouse_coords, center_coords)-90;
                            
                            if($.browser.msie) {
                                angle = -angle;
                            }

                            return _this.rotate(angle);
                        },
                        mouseup:function(e){
                            $rotatable.removeClass('ui-rotating');
                            $rotatable.parents().off('mousemove');
                        }
                    });
                },mouseup:function(e){
                    $rotatable.removeClass('ui-rotating');
                }
            });
        };
        
        // Get Angle
        this.getAngle = function(ms, ctr) {
            var x     = ms.x - ctr.x,
                y     = - ms.y + ctr.y,
                rad   = Math.atan(y/x),
                angle = rad * (180 / Math.PI);

                if (x < 0){
                    angle = angle+180;
                }else if(y < 0){
                    angle = angle+360;
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

            if(opts.rotateAlso != ''){
                $(opts.rotateAlso).css({
                    '-moz-transform'   : matrix,
                    '-o-transform'     : matrix,
                    '-webkit-transform': matrix,
                    '-ms-transform'    : matrix,
                    'transform'        : matrix,
                    'filter'           : ie_matrix,
                    '-ms-filter'       : '"' + ie_matrix + '"'
                });
            }
            
        };
        
        return this.intialize();  		
	}
})(jQuery);

