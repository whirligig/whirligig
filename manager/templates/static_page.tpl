{% extends "manager/templates/base.tpl" %}

{# from "manager/templates/inclusions.tpl" import static_page_layouts #}

{% block title %}Page editor{% endblock %}

{% block content %}
<h1>Static page</h1>
<input type="hidden" id="pk" name="pk" value="{{ page.pk }}" />

<table id="page_edit">
<tr>
	<td id="fields">
		<table>
			<tr><td>Title: </td><td><input type="text" class="form-text" id="page-title-form" name="title" value="{{ page.title }}" /></td></tr>
		</table>
	</td>
</tr>
<tr>
	<td id="layouts">
		<div id="layout_title"><span>Layouts</span></div>
		<div class="block">
			<div id="layout_help">You can use existing page structures. Click on the button on the right and select the appropriate layout for you. Note that if you change the layout of your page existing content will be disappear.</div>
			<div id="layout_btn"><input type="button" class="form-submit" value="Change page layout" /></div>
		</div>
		{{ static_page_layouts(layouts) }}
	</td>
</tr>
<tr>
	<td id="editor">
		<textarea name="content">{{ page.content }}</textarea>
	</td>
</tr>
</table>

<table id="status">
<tr>
	<td>
		<input id="active" class="checkbox" type="checkbox" {% if page.status == 'on' %}checked{% endif %}><label id="label" for="active" class="checkbox-label{% if page.status == 'on' %} label-selected{% endif %}">{% if page.status == 'on' %}Page is active{% endif %}{% if page.status != 'on' %}Page is hidden{% endif %}</label>
	</td>
	<td>URL: </td><td><input type="text" class="form-text" id="page-name-form" name="name" value="{{ page.name }}" />.html</td>
	<td class="func-button"><input type="button" id="save" class="form-submit" name="save" value="Save" /></td>
	<td class="func-button"><input type="button" id="preview" class="form-submit" name="preview" value="Preview" /></td>
	<td class="del-button"><form action="{{ MANAGER_URL }}page/delete/" class="delete_form" method="post"><input type="button" class="form-submit" id="delete" name="delete" value="Delete" /></form></td>
</tr>
<tr><td></td><td></td><td><div class="help">If this field is empty, page will be saved as 'page-%d.html'<br />where %d - integer</div></td><td></td><td></td><td></td></tr>
</table>

<div class="images_add">
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

<script type="text/javascript">
	var $editor = $('#editor textarea').wysiwyg({
		css : "/static/{{ THEME }}/style.css",
		iFrameClass : "editor_iframe"
	});
</script>
{% endblock %}