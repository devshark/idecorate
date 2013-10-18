(function( $, undefined ) {

    $.widget("ui.rotatable", $.ui.mouse, {
    options: {
        handle: false,
        matrix : false,
        // callbacks
        start: null,
        rotate: null,
        stop: null
    },
    handle: function(handle) {
        if (handle === undefined) {
            return this.options.handle;
        }
        this.options.handle = handle;
    },
    _create: function() {
        if (!this.options.handle) {
            this.options.handle = $(document.createElement('div'));
        }

        this.listeners = {
        rotateElement: $.proxy(this.rotateElement, this),
        startRotate: $.proxy(this.startRotate, this),
        stopRotate: $.proxy(this.stopRotate, this),
        };

        var handle = this.options.handle;
        handle.addClass('ui-rotatable-handle');
        handle.draggable({ helper: 'clone', start: this.dragStart });
        handle.bind('mousedown', this.listeners.startRotate);
        handle.appendTo(this.element);
        this.element.attr('rotation',0);
        this.elementCurrentAngle = parseFloat(this.element.attr('rotation'));
    },
    performRotation: function(angle) {
        this.element.attr('rotation', angle);
        if(this.options.matrix){
            var angle = this.radianToDegree(angle);
            var matrix = this.generateMatrix(angle);
            this.performRotationByMatrix(matrix);
        }else{
            this.element.css('transform','rotate(' + angle + 'rad)');
            this.element.css('-moz-transform','rotate(' + angle + 'rad)');
            this.element.css('-webkit-transform','rotate(' + angle + 'rad)');
            this.element.css('-o-transform','rotate(' + angle + 'rad)');
        }
    },
    performRotationByMatrix : function(matrix){
        var matrix = 'matrix('+ matrix[0] +', '+ matrix[1] +', '+ matrix[2] +', '+ matrix[3] +', 0, 0)';
        this.element.css({
            '-moz-transform'   : matrix,
            '-o-transform'     : matrix,
            '-webkit-transform': matrix,
            '-ms-transform'    : matrix,
            'transform'        : matrix
        });
    },
    degreeToRadian : function(degree) {
        return (degree * (Math.PI / 180));
    },
    radianToDegree : function(radian) {
        return (radian * (180 / Math.PI));
    },
    generateMatrix : function(degree) {
        var cos = Math.cos(this.degreeToRadian(degree)),
            sin = Math.sin(this.degreeToRadian(degree)),
            matrix = [cos, sin, (-sin), cos];
        return matrix;
    },
    getElementOffset: function() {
        this.performRotation(0);
        var offset = this.element.offset();
        this.performRotation(this.elementCurrentAngle);
        return offset;
    },
    getElementCenter: function() {
        var elementOffset = this.getElementOffset();
        var elementCentreX = elementOffset.left + this.element.width() / 2;
        var elementCentreY = elementOffset.top + this.element.height() / 2;
        return Array(elementCentreX, elementCentreY);
    },
    dragStart: function(event) {
        if (this.element) {
            return false;
        }
    },
    startRotate: function(event) {
        this.elementCurrentAngle = parseFloat(this.element.attr('rotation'));
        var center = this.getElementCenter();
        var startXFromCenter = event.pageX - center[0];
        var startYFromCenter = event.pageY - center[1];
        this.mouseStartAngle = Math.atan2(startYFromCenter, startXFromCenter);
        this.elementStartAngle = this.elementCurrentAngle;
        this.hasRotated = false;

        this._propagate("start", event);

        $(document).bind('mousemove', this.listeners.rotateElement);
        $(document).bind('mouseup', this.listeners.stopRotate);

        return false;
    },
    rotateElement: function(event) {
        if (!this.element) {
            return false;
        }

        var center = this.getElementCenter();
        var xFromCenter = event.pageX - center[0];
        var yFromCenter = event.pageY - center[1];
        var mouseAngle = Math.atan2(yFromCenter, xFromCenter);
        var rotateAngle = mouseAngle - this.mouseStartAngle + this.elementStartAngle;

        this.performRotation(rotateAngle);
        var previousRotateAngle = this.elementCurrentAngle;
        this.elementCurrentAngle = rotateAngle;

        // Plugins callbacks need to be called first.
        this._propagate("rotate", event);

        if (previousRotateAngle != rotateAngle) {
            this._trigger("rotate", event, this.ui());
            this.hasRotated = true;
        }

        return false;
    },
    stopRotate: function(event) {
        if (!this.element) {
            return;
        }

        $(document).unbind('mousemove', this.listeners.rotateElement);
        $(document).unbind('mouseup', this.listeners.stopRotate);

        this.elementStopAngle = this.elementCurrentAngle;
        if (this.hasRotated) {
            this._propagate("stop", event);
        }

        setTimeout( function() { this.element = false; }, 10 );
        return false;
    },
    _propagate: function(n, event) {
        $.ui.plugin.call(this, n, [event, this.ui()]);
        (n !== "rotate" && this._trigger(n, event, this.ui()));
    },
    plugins: {},

    ui: function() {
        return {
            element: this.element,
            radian: {
                start: this.elementStartAngle,
                current: this.elementCurrentAngle,
                stop: this.elementStopAngle
            },
            degree:{
                start: this.radianToDegree(this.elementStartAngle),
                current: this.radianToDegree(this.elementCurrentAngle),
                stop: this.radianToDegree(this.elementStopAngle)
            },
            matrix:{
                start: this.generateMatrix(this.radianToDegree(this.elementStartAngle)),
                current: this.generateMatrix(this.radianToDegree(this.elementCurrentAngle)),
                stop: this.generateMatrix(this.radianToDegree(this.elementStopAngle))
            }
        };
    },

    });

})(jQuery);
