{% extends "manager/templates/base.tpl" %}

{% block title %}DASHBOARD PAGE{% endblock %}

{% block content %}
<h1>Menu items</h1>
<table id="menu_items">
<tr>
	<td id="nav_list">{% include "manager/templates/menu_list.tpl" %}</td>

	<td colspan="2" id="nav_new">
		<table>
			<tr><td colspan="2" class="msg"></td></tr>
			<tr><th>Menu name</th><td><select class="new_menu" name="new_menu" />{% for menu in menu_list %}<option value="{{ menu.0 }}">{{ menu.1 }}</option>{% endfor %}</select></td></tr>
			<tr><th>Title</th><td><input class="form-text new_title" type="text" name="new_title" /></td></tr>
			<tr><th>URL</th><td>
				<select class="form-text new_url" name="new_url">
					{% for o in options %}
					<option value="{{ o.0 }}">{{ o.1 }}</option>
					{% endfor %}
				</select>
			</td></tr>
			<tr><td colspan="2">
				<input class="new_order" type="hidden" name="new_order" value="0" />
				<input class="form-submit" type="button" name="submit" value="Add" />
			</td></tr>
			</tr>
		</table>
	</td>
</tr>
</table>
{% endblock %}