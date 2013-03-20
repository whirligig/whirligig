{% extends "base.tpl" %}

{% block title %}ERROR PAGE{% endblock %}

{% block content %}
<div id="error_code">{{ code }}</div>
<div id="error_msg">{{ message }}</div>
{% endblock %}