{% extends "base.tpl" %}

{% block title %}CATALOG CATEGORY PAGE{% endblock %}

{% block content %}

{% for item in catalog.1 %}
<div>{{ item }}</div>
{% endfor %}


{% endblock %}