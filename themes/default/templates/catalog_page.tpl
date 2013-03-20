{% extends "base.tpl" %}

{% block title %}CATALOG PAGE{% endblock %}

{% block content %}

{% for category in catalog|categories %}
<div>{{ category }}</div>
{% endfor %}

{% for item in catalog|items %}
<div class="catalog_item">
    <table>
        <tr>
            <td>
                <a href="/catalog/{{ item.0.1 }}/"><img src="{{ item|main_image|get_small_image }}" alt="" title="" /></a>
            </td>
        </tr>
        <tr>
            <td>
                <a href="/catalog/{{ item.0.1 }}/">{{ item|custom_fields|get_field_value:0 }}</a>
            </td>
        </tr>
    </table>
</div>
{% endfor %}


{% endblock %}