{% extends "manager/templates/base.tpl" %}

{% block title %}THEMES{% endblock %}

{% block content %}
<ul class="settings">
{% for theme in themes %}
	<li class="theme">{{ theme_description(theme) }}</li>
{% endfor %}
</ul>
{% endblock %}