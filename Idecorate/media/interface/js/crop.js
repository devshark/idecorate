	currentLine = null;
	lineRect = {startX: 0, startY: 0, w: 0, h: 0};
	lineEvent = "";
	mouseX = 0;
	mouseY = 0;
	savedCoordinates = [];
	liningStart = true;
	justStarted = true;
	pointCount = 0;
	doneCrop = false;
	rectMouse = {x: 0, y: 0, w: 0, h: 0};
	usePen = true;

	function resetEditing() {
		currentLine = null;
		lineRect = {startX: 0, startY: 0, w: 0, h: 0};
		lineEvent = "";
		mouseX = 0;
		mouseY = 0;
		savedCoordinates = [];
		liningStart = true;
		justStarted = true;
		pointCount = 0;
		doneCrop = false;
		rectMouse = {x: 0, y: 0, w: 0, h: 0};

		var c3 = canvas3.getContext("2d");
		c3.clearRect(0,0, canvas3.width, canvas3.height);
		c3.globalAlpha = 1;

		var c1 = canvas.getContext("2d");
		c1.clearRect(0,0, canvas.width, canvas.height);
	
		$('.crop_handles').remove();
		//setCanvasImage(PIC_FILENAME);

	}

	function createHandle(x,y) {

		var thisId = "";

		if(liningStart) {
			thisId = ' id="startHandle"';
			liningStart = false;
		} else {
			thisId = '';
		}
	
		$('<div class="crop_handles"' + thisId + ' style="position:absolute;"></div>').css({left : (x - (7 / 2)) + 'px', top: (y - (7 / 2)) + 'px'}).appendTo('#canvas_container');
	
	}
	
	function drawLines() {
		var started = false;
		var newLine = canvas3.getContext("2d");
		newLine.beginPath();
		newLine.clearRect(0,0, canvas3.width, canvas3.height);
		//newLine.lineWidth = 1;

		for(x = 0; x < savedCoordinates.length; x++) {
			if(!started) {
				started = true;
				newLine.moveTo(savedCoordinates[x].startX,savedCoordinates[x].startY);
			}
					
			newLine.lineTo(savedCoordinates[x].w, savedCoordinates[x].h);
			newLine.stroke();

		}


		return newLine;
	}
	
	function setCanvasImage(imageSrc) {
		
		var img = canvas2.getContext("2d");
		var imgObj = new Image();

		var context = canvas2.getContext("2d");
		context.clearRect(0,0, canvas2.width, canvas2.height);	
			 
		imgObj.onload = function() {
		
			img.drawImage(imgObj, 0, 0);
		};
			 
		imgObj.src = imageSrc;
			
	}

	function loadCropped() {
		//alert(PRE_TASK);
		if(PRE_TASK == 'rect') {
			doneCrop = true;
			usePen = false;

			var pre_d = PRE_DIMENSIONS.split(',')
			var pre_od = PRE_OTHERDATA.split(',')


			savedCoordinates.push({
				startX: parseInt(pre_d[0]),
				startY: parseInt(pre_d[1]),
				w: parseInt(pre_d[2]),
				h: parseInt(pre_d[3]),
				realW: parseInt(pre_od[0]),
				realH: parseInt(pre_od[1])
			});

			var rect2 = canvas3.getContext("2d");
			rect2.beginPath();
			rect2.rect(parseInt(pre_d[0]), parseInt(pre_d[1]), parseInt(pre_od[0]), parseInt(pre_od[1]));
			rect2.globalAlpha = 0.5;
			rect2.fillStyle = "white";
			rect2.fill();
			rect2.stroke();

		} else if(PRE_TASK == 'poly') {
			doneCrop = true;
			usePen = true;

			var pre_d = PRE_DIMENSIONS.split(',')
			var pre_od = PRE_OTHERDATA.split(',')
			var dCounter = 0;

			for(dCounter = 0; dCounter < pre_d.length; dCounter++) {

				var splitted_d = pre_d[dCounter].split(':');
				var splitted_od = pre_od[dCounter].split(':');

				savedCoordinates.push({
					startX: parseInt(splitted_d[0]),
					startY: parseInt(splitted_d[1]),
					w: parseInt(splitted_od[0]),
					h: parseInt(splitted_od[1])
				});

			}

			var pth = drawLines();
			pth.closePath();
			pth.globalAlpha = 0.5;
			pth.fillStyle = "white";
			//pth.globalCompositeOperation = 'xor';
			pth.fill();

		}
	}
	
	$(function(e){


		$('#pen').click(function(e){
			usePen = true;
			resetEditing();
		});


		$('#rect').click(function(e){
			usePen = false;
			resetEditing();
		});

		$('#cancel_crop').click(function(e){
			parent.closeModalForm();
		});

		$('<canvas id="myCanvas" width="400" height="400" style="position:absolute;z-index: 3;"></canvas>').appendTo('#main');
		$('<canvas id="myCanvas2" width="400" height="400" style="position:absolute;z-index: 1;"></canvas>').appendTo('#main');
		$('<canvas id="myCanvas3" width="400" height="400" style="position:absolute;z-index: 2;"></canvas>').appendTo('#main');
		var posi = $('#main').position();
		
		$('#myCanvas').css({left : posi.left + 'px', top: posi.top + 'px'});
		$('#myCanvas2').css({left : posi.left + 'px', top: posi.top + 'px'});
		$('#myCanvas3').css({left : posi.left + 'px', top: posi.top + 'px'});
		
		canvas = document.getElementById("myCanvas");
		canvas2 = document.getElementById("myCanvas2");
		canvas3 = document.getElementById("myCanvas3");

		try {

			G_vmlCanvasManager.initElement(canvas);
			G_vmlCanvasManager.initElement(canvas2);
			G_vmlCanvasManager.initElement(canvas3);
		} catch(e) {

		}
		
		setCanvasImage(PIC_FILENAME);
		
		$("#myCanvas").click(function(e){

			if(!doneCrop) {

				if(usePen) {

					var x = mouseX;
					var y = mouseY;

					pointCount++;
					currentLine = canvas.getContext("2d");

					if(lineRect.w != 0) {
					
						savedCoordinates.push({startX: lineRect.startX, startY: lineRect.startY, w: lineRect.w, h: lineRect.h});


						var newLine = canvas3.getContext("2d");
						newLine.beginPath();
						//newLine.clearRect(0,0, canvas3.width, canvas3.height);
						//if(justStarted) {
							//justStarted = false;
						//console.log(savedCoordinates);
						newLine.moveTo(savedCoordinates[pointCount - 2].startX,savedCoordinates[pointCount - 2].startY);
						//}
						
						newLine.lineTo(savedCoordinates[pointCount - 2].w, savedCoordinates[pointCount - 2].h);
						newLine.stroke();
						currentLine.clearRect(0,0, canvas.width, canvas.height);
					}
					
					lineEvent = "";

					createHandle(x,y);
					lineRect.startX = (e.pageX - this.offsetLeft);
					lineRect.startY = (e.pageY - this.offsetTop);
					
					lineEvent = "move";
					$('#startHandle').click(function(e){

						doneCrop = true;

						lineEvent = "";
						lineRect.w = savedCoordinates[0].startX;
						lineRect.h = savedCoordinates[0].startY;
						savedCoordinates.push({startX: lineRect.startX, startY: lineRect.startY, w: lineRect.w, h: lineRect.h});
						currentLine.clearRect(0,0, canvas.width, canvas.height);
						//currentLine = null;
						var pth = drawLines();
						pth.closePath();
						pth.globalAlpha = 0.5;
						pth.fillStyle = "white";
						//pth.globalCompositeOperation = 'xor';
			        	pth.fill();
			        	//pth.lineWidth = 1;
					});
				}

			}
		
		}).mousemove(function(e){
			
			if(lineEvent == "move") {
				
				var x = (e.pageX - this.offsetLeft); //- mouseX;
				var y = (e.pageY - this.offsetTop); //- mouseY				
				lineRect.w = x;
				lineRect.h = y;
				currentLine.clearRect(0,0, canvas.width, canvas.height);
				currentLine.beginPath();
				currentLine.moveTo(lineRect.startX,lineRect.startY);
				currentLine.lineTo(lineRect.w, lineRect.h);
				currentLine.stroke();
				//currentLine.closePath();
				//drawLines();
			}

			if(lineEvent == 'drag') {
				var rect = canvas.getContext("2d");
				var x = (e.pageX - this.offsetLeft) - lineRect.startX; //- mouseX;
				var y = (e.pageY - this.offsetTop) - lineRect.startY; //- mouseY				
				lineRect.w = x;
				lineRect.h = y;
				rect.clearRect(0,0, canvas.width, canvas.height);
				rect.beginPath();
				rect.rect(lineRect.startX, lineRect.startY, lineRect.w, lineRect.h);
				rect.stroke();
			}

			if(lineEvent == 'dragCircle') {
				var arc = canvas.getContext("2d");
				var x = (e.pageX - this.offsetLeft) - lineRect.startX; //- mouseX;
				var y = (e.pageY - this.offsetTop) - lineRect.startY; //- mouseY				
				lineRect.w = x;
				lineRect.h = y;
				arc.clearRect(0,0, canvas.width, canvas.height);
				
				arc.beginPath();

				var centerX = lineRect.startX;
				var centerY = lineRect.startY;

				if(lineRect.w < lineRect.startX || lineRect.h < lineRect.startY) {
					var radius = (Math.abs(lineRect.w) > Math.abs(lineRect.h))?Math.abs(lineRect.w):Math.abs(lineRect.h);	
				} else {
					var radius = (lineRect.w > lineRect.h)?lineRect.w:lineRect.h;	
				}
				//console.log('centerX: ' + centerX + ', centerY: ' + centerY + ', radius:' + radius);
				arc.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
				arc.stroke();
			}
			
		}).mousedown(function(e){
			if(!usePen) {
				if(!doneCrop) {
					var x = (e.pageX - this.offsetLeft); //- mouseX;
					var y = (e.pageY - this.offsetTop); //- mouseY

					lineRect.startX = x;
					lineRect.startY = y;
					rectMouse.x = mouseX;
					rectMouse.y = mouseY;
					lineEvent = 'drag';
					liningStart = false;
				}
			}


		}).mouseup(function(e){
			if(!usePen) {
				if(!doneCrop) {
					lineEvent = "";
					doneCrop = true;
					var x = (e.pageX - this.offsetLeft) - lineRect.startX; //- mouseX;
					var y = (e.pageY - this.offsetTop) - lineRect.startY; //- mouseY				
					lineRect.w = x;
					lineRect.h = y;
					rectMouse.w = mouseX;
					rectMouse.h = mouseY;

					var rect = canvas.getContext("2d");
					rect.clearRect(0,0, canvas.width, canvas.height);

					var rect2 = canvas3.getContext("2d");
					rect2.beginPath();
					rect2.rect(lineRect.startX, lineRect.startY, lineRect.w, lineRect.h);
					rect2.globalAlpha = 0.5;
					rect2.fillStyle = "white";
					rect2.fill();
					rect2.stroke();	

					createHandle(rectMouse.x, rectMouse.y);
					createHandle(rectMouse.w,rectMouse.h);
					createHandle(rectMouse.w,rectMouse.y);
					createHandle(rectMouse.x,rectMouse.h);
					savedCoordinates.push({startX: lineRect.startX, startY: lineRect.startY, w: (e.pageX - this.offsetLeft), h: (e.pageY - this.offsetTop), realW: lineRect.w, realH: lineRect.h});
				}
			}

		});
		
		
		$(document).mousemove(function(e){
				mouseX = e.pageX;
				mouseY = e.pageY;
		});

		$('.cstyle').click(function(e){

			resetEditing();

		});

		$('#crop_it').click(function(e){
			if(savedCoordinates.length > 0) {

				var dimen = '';
				var dimen2 = '';
				var task = '';
				var url = '';

				if(usePen) { 
					var val = [];
					var val2 = [];

					for(x=0; x < savedCoordinates.length; x++) {
						val.push(savedCoordinates[x].startX + ':' + savedCoordinates[x].startY);
						val2.push(savedCoordinates[x].w + ':' + savedCoordinates[x].h);
					}

					dimen = val.toString();
					dimen2 = val2.toString();
					task = 'poly';
				} else {
					dimen = savedCoordinates[0].startX + ',' + savedCoordinates[0].startY + ',' + savedCoordinates[0].w + ',' + savedCoordinates[0].h;
					dimen2 = savedCoordinates[0].realW + ',' + savedCoordinates[0].realH;
					task = 'rect';
				}

				url = CROP_URL + '?&task=' + task + '&dimensions=' + escape(dimen) + '&filename=' + escape(BASE_FILENAME) + '&otherdata=' + escape(dimen2);

				parent.setSelectedImage(url);
			}

		});

		loadCropped();

		/**
		$('#frmbutton').click(function(e){

			if(savedCoordinates.length > 0) {

				if(usePen) {
					var val = [];

					for(x=0; x < savedCoordinates.length; x++) {
						val.push(savedCoordinates[x].startX + ':' + savedCoordinates[x].startY);
					}

					$('#dimen').val(val.toString());
				} else if($('input[name="task"]:checked').val() == "rect" || $('input[name="task"]:checked').val() == "circ") {
					$('#dimen').val(savedCoordinates[0].startX + ',' + savedCoordinates[0].startY + ',' + savedCoordinates[0].w + ',' + savedCoordinates[0].h);
				}

				//$('#frm').submit();
				var url = '{% url cropped %}' + '?csrfmiddlewaretoken=' + $('input[name="csrfmiddlewaretoken"]').val() + '&task=' + $('input[name="task"]:checked').val() + '&dimensions=' + escape($('#dimen').val());

				setCanvasImage(url);
				var c3 = canvas3.getContext("2d");
				c3.clearRect(0,0, canvas3.width, canvas3.height);
				var c1 = canvas.getContext("2d");
				c1.clearRect(0,0, canvas.width, canvas.height);
				$('.crop_handles').remove();
			}

		});

		$('#frmreset').click(function(e){

			resetEditing();

			$('.cstyle').each(function(e){
				this.checked = false;
			});

		});
		**/

	});