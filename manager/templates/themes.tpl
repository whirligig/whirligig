{% extends "manager/templates/base.tpl" %}

{% block title %}THEMES{% endblock %}

{% block content %}
<ul>
{% for theme in themes %}
	<li>{{ theme_description(theme) }}</li>
{% endfor %}
</ul>
{% endblock %}