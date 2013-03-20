/**
 * jQuery eComboBox - An editable Combo Box Plugin - http://www.reckdesign.de/eComboBox
 * 
 * @author  Recep Karadas
 * @version 1.0
 *
 * jQuery eComboBox generates editable Combo Boxes.
 *
 * Licensed under The MIT License
 *
 * @version			1.0
 * @since			22.05.2011
 * @author			Recep Karadas
 * @documentation	http://www.reckdesign.de/eComboBox
 * @license			http://opensource.org/licenses/mit-license.php
 *
 * Usage with default values:
 * ---------------------------------------------------------------------------------
 * $('#eComboBox').eComboBox();
 *
 * <select id="eComboBox">
 * 	<option>Value 1</option>
 * 	<option>Value 2</option>
 * 	<option>Value 3</option>
 * 	<option>Value 4</option>
 * </select>
 *
 */

(function( $ ){
  
  var methods = {
     init : function( options ) {

		var settings = {
			'allowNewElements' : true,
			'editableElements' : false
		};

		return this.each(function() { 

			var wrapperElement = null;
			var selectElement = null;  
			selectElement = $(this);
			var selected = "";
			// If options exist, lets merge them
			// with our default settings
			if ( options ) { 
				$.extend( settings, options );
			}

			$(this).data("settings", settings);

			if (settings.allowNewElements){
				selectElement.append('<option>Enter custom URL...</option>');
			}

			// Create Wrapper Element 
			var wrapperEl = document.createElement('span');
			wrapperElement = jQuery(wrapperEl);

			// Create Input Element
			var inputEl = document.createElement('input');
			var inputElement = jQuery(inputEl);

			// put input and select element in wrapper element
			selectElement.before(wrapperElement);
			wrapperElement.append(inputElement).append(selectElement);

			inputElement.css({
				"display" : "none"
			});

			inputElement.addClass("form-text");

			selectElement.keydown( function(e){
				if(e.keyCode >= 37 && e.keyCode <=40  || e.keyCode == 13) // arrow buttons or enter button
					return ;

				selected = $(this).val();

				if(e.keyCode == "46"){ // del-button
					return;
				}

				if( selected=="Enter custom URL..." || settings['editableElements'] ) {
					inputElement.css({"display":"inline"});
					inputElement.after('<div class="help">After press "Enter"</div>');
					if(selected=="Enter custom URL..."){
						inputElement.val( "" ).focus();
					}else if(settings['editableElements']){
						inputElement.val( $(this).val() ).focus();
					}
				}
			});

			selectElement.change( function(e){
				if($(this).val()=="Enter custom URL..."){
					selected = $(this).val();
					$(this).hide();
					inputElement.css({"display":"inline"});
					inputElement.after('<div class="help">After press "Enter"</div>');
					inputElement.val( "" ).focus();
				}
			});

			inputElement.keyup(function(e){
				if(e.keyCode == 13){ //enter
					if(selected=="Enter custom URL..." ){
						if ($(this).val() != ""){
							selectElement.children('option:last').before('<option>'+$.trim($(this).val())+'</option>');
							selectElement.val($(this).val());
						}
						else{
							selectElement.children('option:first').attr('selected','selected');
						}
					}else{
						if( $(this).val() == "" ) {
							selectElement.children('option:selected').remove();
						}else{
							selectElement.children('option:selected').text($(this).val());
						}
					}
					$(this).hide();
					$(this).next().remove();
					selectElement.show();
					selectElement.focus();
				}
			});
		});
	 },
     destroy : function( ) {
		$(this).parent().remove();
	 },
	 disableAddingNewElements: function(){
		var fChild = $(this).children().first();
		if(fChild.text() == "Enter custom URL..."){
			fChild.remove();
		}
	 },
	 enableAddingNewElements: function(){
		var fChild = $(this).children().first();
		if(fChild.text() != "Enter custom URL..."){
			$(this).prepend('<option>Enter custom URL...</option>');
		}
	 },
	 disableEditingElements: function(){
		$(this).data('settings').editableElements = false;
	 },
	 enableEditingElements: function(){
		$(this).data('settings').editableElements = true;
	 }
  };

  
  $.fn.eComboBox = function( method ) {
    
    if ( methods[method] ) {
      return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
      return methods.init.apply( this, arguments );
    } else {
      $.error( 'Method ' +  method + ' does not exist on jQuery.eComboBox' );
    }    
  
  };

})( jQuery );