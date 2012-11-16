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

            _rotator.draggable({
                helper: 'clone',
                revert: false,
                start: function(e,ui){
                    cancelBubble(e);

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

                },
                drag: function(e,ui){
                    cancelBubble(e);
                    // Mouse Coords
                    mouse_coords = {
                        'x': e.pageX,
                        'y': e.pageY
                    };  
                    
                    angle = _this.getAngle(mouse_coords, center_coords)-90;
                    
                    if($.browser.msie && $.browser.version < 9.0) {
                        angle = -angle;
                    }

                    return _this.rotate(angle);

                },
                stop: function(e,ui){
                    cancelBubble(e);
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
        	var cos = parseFloat(parseFloat(Math.cos(_this.degToRad(-degree)))),
        	    sin = parseFloat(parseFloat(Math.sin(_this.degToRad(-degree)))),
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


            if($('.selected').attr('_matrix')){
                flipflap = $.parseJSON($('.selected').attr('_matrix'));
                var a = flipflap.a,
                    b = flipflap.b,
                    c = flipflap.c,
                    d = flipflap.d,
                    e = flipflap.e; 
                    f = flipflap.f; 

                if(e){
                    m[0] = (m[0]*-1);
                    m[1] = c<0 || c>0 ? (m[1]*-1) : m[2];
                }
                if(f){
                    m[0] = a<0 || a>0 ? (m[0]*-1) : m[0];
                    m[1] = (m[1]*-1);
                }
            }

        	var matrix = 'matrix('+ m[0] +', '+ m[1] +', '+ m[2] +', '+ m[3] +', 0, 0)',
        	    ie_matrix = "progid:DXImageTransform.Microsoft.Matrix(M11='"+m[0]+"', M12='"+m[1]+"', M21='"+m[2]+"', M22='"+m[3]+"', sizingMethod='auto expand')";        	
            if($.browser.msie && $.browser.version == 9.0) {
                _this.css({
                    '-ms-transform'    : matrix
                });

                if(opts.rotateAlso != ''){
                    $(opts.rotateAlso).css({
                        '-ms-transform'    : matrix
                    });
                }
            }else if($.browser.msie && $.browser.version < 9.0){
                _this.css({
                    'filter'           : ie_matrix,
                    '-ms-filter'       : '"' + ie_matrix + '"'
                });

                if(opts.rotateAlso != ''){
                    $(opts.rotateAlso).css({
                        'filter'           : ie_matrix,
                        '-ms-filter'       : '"' + ie_matrix + '"'
                    });
                }
            }else{
                _this.css({
                    '-moz-transform'   : matrix,
                    '-o-transform'     : matrix,
                    '-webkit-transform': matrix,
                    'transform'        : matrix
                });

                if(opts.rotateAlso != ''){
                    $(opts.rotateAlso).css({
                    '-moz-transform'   : matrix,
                    '-o-transform'     : matrix,
                    '-webkit-transform': matrix,
                    'transform'        : matrix
                    });
                }
            }

            if($('.selected').attr('_matrix')){
        	   $(opts.rotateAlso).attr('_matrix','{"a":'+m[0]+',"b":'+m[1]+',"c":'+m[2]+',"d":'+m[3]+',"e":'+e+',"f":'+f+'}');
            }
        };

        return this.intialize();  		
	}
})(jQuery);

