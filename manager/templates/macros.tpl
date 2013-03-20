{% macro manager_nav(request) %}
<ul>
	<li {% if req.path == manager_url %}class="active"{% endif %}><a href="{{ manager_url }}">Dashboard</a></li>
  <li {% if req.path == manager_url + "settings/" %}class="active"{% endif %}><a href="{{ manager_url }}settings/">Settings</a></li>
  <li {% if req.path == manager_url + "pages/" %}class="active"{% endif %}><a href="{{ manager_url }}pages/">Pages</a></li>
	<li {% if req.path == manager_url + "nav/" %}class="active"{% endif %}><a href="{{ manager_url }}nav/">Navigation</a></li>
	<li {% if req.path == manager_url + "catalog/" %}class="active"{% endif %}><a href="{{ manager_url }}catalog/">Catalog</a></li>
	<li><a href="{{ manager_url }}logout/">Logout</a></li>
</ul>
{% endmacro %}

{% macro static_page_layouts(items, columns) %}
<div class="columnwrapper block">
  {% for column in items|slice(columns) %}
    <ul class="column">
    {% for item in column %}
      <li>
      	<div class="layout_name">{{ item.keys()[0] }}</div>
      	<div class="layout_img">{{ item.values()[0] }}</div>
      </li>
    {% endfor %}
    </ul>
  {% endfor %}
</div>
{% endmacro %}

{% macro property_types_select() %}
<select name="container" class="property_container">
  <option value="S">Single line</option>
  <option value="M">Multiple lines</option>
  <option value="B">Yes / No</option>
</select>
{% endmacro %}

{% macro category_row(category) %}
<td class="first">
  <input type="hidden" name="pk" value="{{ category.0 }}" />
  <div>
    <span class="category_name">{{ category.1 }}</span>
    <ul><li>Items: <span>{{ category.2 }}</span></li></ul>
  </div>
</td>
<td class="last"><div>
  <ul class="category_meta block">
    <li class="view">Browse</li>
    <li class="add">+ item</li>
    <li class="rename">Rename</li>
    <li class="delete">Delete</li>
  </ul>
</div></td>
{% endmacro %}

{% macro item_row(item) %}
  <td class="first"><div>{{ item[0] }}</div></td>
  <td class="img70_cell"><div><img src="{{ item[1]|get_mini_image }}" alt="" title="" /></div></td>
  <td><div>{{ item[3] }}</div></td>
  <td class="last"><div>
    <ul class="item_meta block">
      <li class="view">View</li>
      <li class="edit">Edit</li>
      <li class="activate">Hide</li>
      <li class="delete">Delete</li>
    </ul>
  </div></td>
{% endmacro %}

{% macro catalog_navigation(catalog, current_page) %}
<div class="catalog-nav">
  <input type="hidden" name="page" value="{{ current_page }}" />
  <input type="hidden" name="category" value="{{ catalog.PARENT }}" />
  <input type="button" name="catalog_prev" class="form-submit" value="Prev" />
  <input type="text" name="catalog_page" class="form-text" value="{{ current_page }}" size="3" />
  <input type="button" name="go" class="form-submit" value="Go" />
  <input type="button" name="catalog_next" class="form-submit" value="Next" />
</div>
{% endmacro %}

{% macro categories_table(catalog, page) %}
<table>
  <thead><tr><th class="first">Category</th><th class="last">Actions</th></tr></thead>
  <tbody>
  {% if catalog.0|length %}
  {% for category in catalog.0 %}
    <tr class="{{ loop.cycle('odd', 'even') }}">
      <td class="first"><input type="hidden" name="pk" value="{{ category.0 }}" />
        <div>
          <span class="category_name">{{ category.1 }}</span>
          <ul>
            <li>Items: <span>{{ category.2 }}</span></li>
          </ul>
        </div>
      </td>
      <td class="last"><div>
        <ul class="category_meta block">
          <li class="view">Browse</li>
          <li class="add">+ item</li>
          <li class="rename">Rename</li>
          <li class="delete">Delete</li>
        </ul>
      </div></td>
    </tr>
  {% endfor %}
  {% else %}
    <tr><td colspan="2" class="center first last done">There are no categories</td></tr>
  {% endif %}
  </tbody>
</table>
{% endmacro %}

{% macro items_table(catalog, page) %}
<table>
  <thead><tr><th class="first">№</th><th>Image</th><th>Item</th><th class="last">Actions</th></tr></thead>
  <tbody>
  {% if catalog.1|length %}
  {% for item in catalog.1 %}
    <tr class="{{ loop.cycle('odd', 'even') }}{% if item[item|length-1] == 0 %} h{% endif %}">
      <td class="first"><div>{{ item[0] }}</div></td>
      <td class="img70_cell"><div><img src="{{ item[2]|get_main_mini_image }}" alt="" title="" /></div></td>
      <td><div>{{ item[3] }}</div></td>
      <td class="last"><div>
        <ul class="item_meta block">
          <li class="view">View</li>
          <li class="edit">Edit</li>
          <li class="activate">{% if item[item|length-1] == 0 %}Show{% else %}Hide{% endif %}</li>
          <li class="delete">Delete</li>
        </ul>
      </div></td>
    </tr>
  {% endfor %}
  {% else %}
    <tr><td colspan="4" class="center first last done">There are no items</td></tr>
  {% endif %}
  </tbody>
</table>
{% endmacro %}

{% macro empty_table() %}
<table>
  <thead><tr><th class="first last"></th></tr></thead>
  <tbody>
    <tr><td class="center first last done">There are no items</td></tr>
  </tbody>
</table>
{% endmacro %}