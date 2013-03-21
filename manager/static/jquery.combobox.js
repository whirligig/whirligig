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

(function(e){var t={init:function(t){var n={allowNewElements:true,editableElements:false};return this.each(function(){var r=null;var i=null;i=e(this);var s="";if(t){e.extend(n,t)}e(this).data("settings",n);if(n.allowNewElements){i.append("<option>Enter custom URL...</option>")}var o=document.createElement("span");r=jQuery(o);var u=document.createElement("input");var a=jQuery(u);i.before(r);r.append(a).append(i);a.css({display:"none"});a.addClass("form-text");i.keydown(function(t){if(t.keyCode>=37&&t.keyCode<=40||t.keyCode==13)return;s=e(this).val();if(t.keyCode=="46"){return}if(s=="Enter custom URL..."||n["editableElements"]){a.css({display:"inline"});a.after('<div class="help">After press "Enter"</div>');if(s=="Enter custom URL..."){a.val("").focus()}else if(n["editableElements"]){a.val(e(this).val()).focus()}}});i.change(function(t){if(e(this).val()=="Enter custom URL..."){s=e(this).val();e(this).hide();a.css({display:"inline"});a.after('<div class="help">After press "Enter"</div>');a.val("").focus()}});a.keyup(function(t){if(t.keyCode==13){if(s=="Enter custom URL..."){if(e(this).val()!=""){i.children("option:last").before("<option>"+e.trim(e(this).val())+"</option>");i.val(e(this).val())}else{i.children("option:first").attr("selected","selected")}}else{if(e(this).val()==""){i.children("option:selected").remove()}else{i.children("option:selected").text(e(this).val())}}e(this).hide();e(this).next().remove();i.show();i.focus()}})})},destroy:function(){e(this).parent().remove()},disableAddingNewElements:function(){var t=e(this).children().first();if(t.text()=="Enter custom URL..."){t.remove()}},enableAddingNewElements:function(){var t=e(this).children().first();if(t.text()!="Enter custom URL..."){e(this).prepend("<option>Enter custom URL...</option>")}},disableEditingElements:function(){e(this).data("settings").editableElements=false},enableEditingElements:function(){e(this).data("settings").editableElements=true}};e.fn.eComboBox=function(n){if(t[n]){return t[n].apply(this,Array.prototype.slice.call(arguments,1))}else if(typeof n==="object"||!n){return t.init.apply(this,arguments)}else{e.error("Method "+n+" does not exist on jQuery.eComboBox")}}})(jQuery)