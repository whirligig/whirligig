{% extends "manager/templates/base.tpl" %}

{% block title %}Add items{% endblock %}

{% block content %}
<h1>Catalog</h1>
{% if added %}
<script type="text/javascript">
$(function(){
	$("#notificator").notification({
		{% if item|get_field_value:3|is_true_or_empty %}
		text: 'Item \'{{ item|custom_fields|get_field_value:0|escape }}\' has been created',
		{% endif %}
		{% if item|get_field_value:3|is_not_true_or_empty %}
		text: 'Item has not been created',
		{% endif %}
		type : {% if item|get_field_value:3|is_true_or_empty %}'info'{% endif %}{% if item|get_field_value:3|is_not_true_or_empty %}'error'{% endif %},
		onOK: false,
		onCancel: true
	});
});
</script>
{% endif %}
<table id="catalog">
<tr>
	<td class="images_add">
	<div class="wrap">
		<div id="image_preview">
			{% if item|main_image %}<img src="{{ item|main_image|get_small_image }}" alt="" title="" />{% endif %}
			{% if item|main_image|is_none %}<img src="{{ MANAGER_URL }}static/no-image-150.png" alt="No image" title="No image" />{% endif %}
		</div>
		{% if item|extra_images|length %}
		<table class="extra_images">
			{% for i in range(0,item|extra_images|length,3) %}
			<tr>
				<td>
					<div class="frame">
						{% if item.2.1.extra.i %}
						<div class="crop"><img src="{{ item|extra_images:i|get_mini_image }}" alt="" title="" /></div><span class="remove">&#10006;</span>
						{% endif %}
					</div>
				</td>
				<td>
					<div class="frame">
						{% if item|extra_images:inc(i) %}
						<div class="crop"><img src="{{ item|extra_images:inc(i)|get_mini_image }}" alt="" title="" /></div><span class="remove">&#10006;</span>
						{% endif %}
					</div>
				</td>
				<td>
					<div class="frame">
						{% if item|extra_images:inc(i,2) %}
						<div class="crop"><img src="{{ item|extra_images:inc(i,2)|get_mini_image }}" alt="" title="" /></div><span class="remove">&#10006;</span>
						{% endif %}
					</div>
				</td>
			</tr>
			{% endfor %}
		</table>
		{% endif %}
		<div class="add_image"><input type="button" class="form-submit" value="Add image" /></div>

		<div id="image_result">
			<div>
			<table id="image_insert">
				<tr>
					<td>
						<div id="ci_image_upload">
							<form action="{{ MANAGER_URL }}catalog/upload/" method="post" enctype="multipart/form-data">
								<div class="top-text">
									<div class="upload_msg">Upload image from your computer</div>
									<div class="err_msg">Choose image</div>
									<input type="file" id="file_upload" name="image">
								</div>
								<div id="upload_btn_wrap"><input type="button" value="Upload" id="img_upload_btn" class="form-submit"></div>
								<div id="upload_result">
									<div class="bar">
										<div class="progress"></div>
										<div class="percent"></div>
									</div>
								</div>
							</form>
						</div>
					</td>
					<td>
						<div class="top-text">Choose an image from already uploaded</div>
						<div id="image_browse">
							<div id="browse_btn_wrap"><input type="button" class="form-submit" id="ci_img_browse_btn" value="Browse"></div>
						</div>
					</td>
				</tr>
			</table>
		</div>
		</div>

	</div>
	</td>
	<td class="data_add">
	<form action="" method="post">
	<div class="wrap">
		<input type="hidden" name="images" value="" />
		<table>
			{% for p in properties %}
			<tr>
				<td class="vt">{{ p.0 }}:</td>
				<td>
					{% if p.1|length != 2 %}{{ p.1 }}{% endif %}
					{% if p.1|length == 2 %}<table><tr><td><label for="radio_yes">Yes</label>{{ p.1.0 }}</td><td><label for="radio_no">No</label>{{ p.1.1 }}</td></tr></table>{% endif %}
				</td>
			</tr>
			{% if loop == 1 %}
			<tr>
				<td>Category:</td>
				<td>
					<select name="category">
						<option value="0">no selected</option>
						{% for c in categories %}
						<option value="{{ c.0 }}" {% if equal(item.1.1,c.1) or equal(c.0,category) %}selected="selected"{% endif %}>{{ c.1 }}</option>
						{% endfor %}
					</select>
				</td>
			</tr>
			{% endif %}
			{% endfor %}
		</table>
	</div>
	<div class="wrap"><input type="submit" class="form-submit" value="Save and add other" /></div>
	</form>
	</td>
</tr>
</table>
{% endblock %}