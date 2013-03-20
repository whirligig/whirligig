{% extends "manager/templates/base.tpl" %}

{# from "manager/templates/inclusions.tpl" import categories_table, items_table #}

{% block title %}DASHBOARD PAGE{% endblock %}

{% block content %}
<h1>Catalog</h1>
{% if exist|is_none %}
<table id="catalog">
<tr>
	<td class="catalog_create">
		To create your catalog use our wizard:
		<form action="{{ MANAGER_URL }}catalog/prepare/" method="post">
			<input type="submit" class="form-submit" value="Create catelog" />
		</form>
	</td>
</tr>
</table>
{% endif %}
{% if exist|is_some %}
<table id="catalog">
<tr>
	<td id="category_list">
		<div class="wrapper">
			<div class="category_create">
				<table><tr>
					<td>
						<div>Add new catalog item:</div>
						<a href="{{ MANAGER_URL }}catalog/add/"><input type="button" class="form-submit" value="Add" /></a>
					</td>
					<td>
						<div>Create new catalog category:</div>
						<input type="text" name="category_name" id="category_name" class="form-text" value="" />
						<input type="button" name="category_add" id="category_add" class="form-submit" value="Create" />
					</td>
				</tr></table>
			</div>
			<div class="category_table">
				{% include "manager/templates/catalog_rows.tpl" %}
			</div>
		</div>
	</td>
</tr>
</table>
{% endif %}
{% endblock %}