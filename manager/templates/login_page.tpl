{% extends "manager/templates/base.tpl" %}
{# import manager_nav #}

{% block title %}LOGIN PAGE{% endblock %}

{% block content %}
{% if error %}ERROR{% endif %}
<form action="{{ MANAGER_URL }}login/" method="post">
    {{ print_time_token() }}
	<table>
		<tr><td>username:</td><td><input type="text" class="form-text" name="username" /></td></tr>
		<tr><td>password:</td><td><input type="password" class="form-text" name="password" /></td></tr>
		<tr><td colspan="2"><input type="submit" class="form-submit" name="submit" value="submit" /></td></tr>
	</table>
</form>
{% endblock %}