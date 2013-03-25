{% extends "manager/templates/base.tpl" %}

{% block title %}THEMES{% endblock %}

{% block content %}
<ul class="settings">
{% for theme in themes %}
	<li class="theme block">
		<div class="theme-name">{{ theme|theme_name }}</div>
		{{ theme_screenshots(theme) }}
		<table class="meta">
			<tr><td>navigation:</td><td>{{ theme|theme_navigations }}</td></tr>
			<tr><td>author:</td><td>{{ theme|theme_author }}</td></tr>
		</table>
		<div class="func block"><input type="button" class="form-submit" name="change" value="Change" /></div>
	</li>
{% endfor %}
</ul>
{% endblock %}
