{% if url %}
<table>
<tr>
	<td id="uploaded"><div><image src="{{ url }}" alt="Preview" title="Preview" /></div></td>
	<td>
		<ul class="image_size block">
			<li><label for="img_mini"><input id="img_mini" type="radio" name="float"> mini (70 px)</label></li>
			<li><label for="img_small"><input id="img_small" type="radio" name="float" checked> small (150 px)</label></li>
			<li><label for="img_medium"><input id="img_medium" type="radio" name="float"> medium (500 px)</label></li>
			<li><label for="img_big"><input id="img_big" type="radio" name="float"> big (900 px)</label></li>
		</ul>
		<ul class="image_float block">
			<li class="img_float_none float-selected"><div>float none</div></li>
			<li class="img_float_left"><div>float left</div></li>
			<li class="img_float_right"><div>float right</div></li>
		</ul>
		<div id="image_insert_btn"><input type="button" class="form-submit" value="Insert image" /></div>
		<input type="hidden" name="img_url" id="img_url" value="" />
		<input type="hidden" name="img_float" id="img_float" value="" />
	</td>
</tr>
</table>
{% endif %}

{% if url|is_none %}
{% if images|length %}
<table class="thumb_browse">
	{% for column in do_batch(images,6,'') %}
	<tr>{% for item in column %}<td>
		<div class="frame">
			<div class="crop"><img src="{{ item }}" alt="" title="" /></div>
			{% if item|length %}<span class="remove">&#10006;</span>{% endif %}
		</div>
	</td>{% endfor %}</tr>
	{% endfor %}
</table>
{% endif %}
<input type="hidden" name="page" value="{{ page }}" />

<div class="browse_nav block">
	<span class="upload"><input type="button" class="form-submit" value="upload new image" /></span>
	<span class="nav">
	<input type="button" class="form-submit prev {% if prev|is_none %}disabled{% endif %}" value="< back" {% if prev|is_none %}disabled="disabled"{% endif %} />
	<input type="button" class="form-submit next {% if next|is_none %}disabled{% endif %}" value="forward >" {% if next|is_none %}disabled="disabled"{% endif %} />
	</span>
</div>
{% endif %}