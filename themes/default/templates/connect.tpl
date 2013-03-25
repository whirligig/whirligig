{% extends "base.tpl" %}

{% from "inclusions.tpl" import connect_form %}

{% block title %}CONNECT PAGE{% endblock %}

{% block content %}
<h1>Connect with us</h1>
{% if success %}
	<div class="connect-message">Thank you! Message has been sent.</div>
{% endif %}
{% if success|is_none %}
	{% if error %}<div class="connect-error">{{ error }}</div>{% endif %}
	{{ connect_form() }}
{% endif %}

{% endblock %}