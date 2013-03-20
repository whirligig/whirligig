{% extends "manager/templates/base.tpl" %}

{% block title %}DASHBOARD PAGE{% endblock %}

{% block content %}
<h1>Static pages</h1>
<table id="static_pages">
<tr>
	<td id="page_list">
	{% if pages.active|length %}
		<div class="page_group">active pages</div>
		<ul class="page-list">
		{% for item in pages.active %}
		<li>
			<div class="block page_head"><div class="page_name">{{ item.2 }}</div>
				<div class="page_meta">
					[<span class="edit page_edit">
						<form action="{{ MANAGER_URL }}page/" method="post"><input type="hidden" name="pk" value="{{ item.0 }}" />edit</form>
					</span>]
					<span class="remove page_delete">
						<form action="{{ MANAGER_URL }}page/delete/" method="post"><input type="hidden" name="pk" value="{{ item.0 }}" />&#10006;</form>
					</span>
				</div>
			</div>
		</li>
		{% endfor %}
		</ul>
	{% endif %}
	{% if pages.hidden|length %}
		<div class="page_group">hidden pages</div>
		<ul class="page-list">
		{% for item in pages.hidden %}
		<li>
			<div class="block page_head">{{ item.1 }}
				<div class="page_meta">
					[<span class="edit page_edit"><form action="{{ MANAGER_URL }}page/" method="post"><input type="hidden" name="pk" value="{{ item.0 }}" />edit</form></span>]
					<span class="remove page_delete"><form action="{{ MANAGER_URL }}page/delete/" method="post"><input type="hidden" name="pk" value="{{ item.0 }}" />&#10006;</form></span>
				</div>
			</div>
		</li>
		{% endfor %}
		</ul>
	{% endif %}
	{% if pages.active|length|is_none and pages.hidden|length|is_none %}
		<div class="empty-list">There are no static pages.<br />To create them, click the right button.</div>
	{% endif %}
	</td>
	<td id="page_create">
		<form action="{{ MANAGER_URL }}page/" method="post"><input type="submit" class="form-submit" value="Create new page" /></form>
	</td>
</tr>
</table>
{% endblock %}