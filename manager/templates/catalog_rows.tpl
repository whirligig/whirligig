<div class="list">
{% if catalog|categories %}
	{{ categories_table(catalog,page) }}
{% endif %}
{% if catalog|items %}
	{{ items_table(catalog,page) }}
{% endif %}
{% if catalog|categories|is_none and catalog|items|is_none %}
	{{ empty_table() }}
{% endif %}
{{ catalog_navigation(catalog,page) }}
</div>