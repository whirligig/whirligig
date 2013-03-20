{% extends "base.tpl" %}

{% from "inclusions.tpl" import connect_form %}

{% block title %}CONNECT PAGE{% endblock %}

{% block content %}
<h1>Connect with us</h1>
{% if success %}
	<div>Thank you! Message has been sent.</div>
{% else %}
	{% if error %}<div>{{ error }}</div>{% endif %}
	{{ connect_form() }}
{% endif %}

{% endblock %}