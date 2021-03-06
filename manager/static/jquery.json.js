/**
 * jQuery JSON plugin 2.4-alpha
 *
 * @author Brantley Harris, 2009-2011
 * @author Timo Tijhof, 2011-2012
 * @source This plugin is heavily influenced by MochiKit's serializeJSON, which is
 *         copyrighted 2005 by Bob Ippolito.
 * @source Brantley Harris wrote this plugin. It is based somewhat on the JSON.org
 *         website's http://www.json.org/json2.js, which proclaims:
 *         "NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.", a sentiment that
 *         I uphold.
 * @license MIT License <http://www.opensource.org/licenses/mit-license.php>
 */
(function($){var escape=/["\\\x00-\x1f\x7f-\x9f]/g,meta={"\b":"\\b","   ":"\\t","\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"},hasOwn=Object.prototype.hasOwnProperty;$.toJSON=typeof JSON==="object"&&JSON.stringify?JSON.stringify:function(e){if(e===null){return"null"}var t,n,r,i,s=$.type(e);if(s==="undefined"){return undefined}if(s==="number"||s==="boolean"){return String(e)}if(s==="string"){return $.quoteString(e)}if(typeof e.toJSON==="function"){return $.toJSON(e.toJSON())}if(s==="date"){var o=e.getUTCMonth()+1,u=e.getUTCDate(),a=e.getUTCFullYear(),f=e.getUTCHours(),l=e.getUTCMinutes(),c=e.getUTCSeconds(),h=e.getUTCMilliseconds();if(o<10){o="0"+o}if(u<10){u="0"+u}if(f<10){f="0"+f}if(l<10){l="0"+l}if(c<10){c="0"+c}if(h<100){h="0"+h}if(h<10){h="0"+h}return'"'+a+"-"+o+"-"+u+"T"+f+":"+l+":"+c+"."+h+'Z"'}t=[];if($.isArray(e)){for(n=0;n<e.length;n++){t.push($.toJSON(e[n])||"null")}return"["+t.join(",")+"]"}if(typeof e==="object"){for(n in e){if(hasOwn.call(e,n)){s=typeof n;if(s==="number"){r='"'+n+'"'}else if(s==="string"){r=$.quoteString(n)}else{continue}s=typeof e[n];if(s!=="function"&&s!=="undefined"){i=$.toJSON(e[n]);t.push(r+":"+i)}}}return"{"+t.join(",")+"}"}};$.evalJSON=typeof JSON==="object"&&JSON.parse?JSON.parse:function(str){return eval("("+str+")")};$.secureEvalJSON=typeof JSON==="object"&&JSON.parse?JSON.parse:function(str){var filtered=str.replace(/\\["\\\/bfnrtu]/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,"]").replace(/(?:^|:|,)(?:\s*\[)+/g,"");if(/^[\],:{}\s]*$/.test(filtered)){return eval("("+str+")")}throw new SyntaxError("Error parsing JSON, source is not valid.")};$.quoteString=function(e){if(e.match(escape)){return'"'+e.replace(escape,function(e){var t=meta[e];if(typeof t==="string"){return t}t=e.charCodeAt();return"\\u00"+Math.floor(t/16).toString(16)+(t%16).toString(16)})+'"'}return'"'+e+'"'}})(jQuery)
