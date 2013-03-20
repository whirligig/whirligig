{% extends "manager/templates/base.tpl" %}

{% block title %}Catalog wizard{% endblock %}

{% block content %}
<h1>Catalog wizard</h1>
<table id="catalog">
<tr>
	<td id="item_pic"></td>
	<td class="catalog_wizard">
		<div class="center">We have prepared some catalog item properties for you.<br />Delete all you don't need and add new:</div>
		<form id="properties_form" action="{{ MANAGER_URL }}catalog/create/" method="post">
			<ul class="property_list">
				<li class="block"><div>Property</div><div>Container</div><div></div></li>
				<li class="sort block"><div>Name</div><div>( Single line )</div><div class="remove">&#10006;</div></li>
				<li class="sort block"><div>Price</div><div>( Single line )</div><div class="remove">&#10006;</div></li>
				<li class="sort block"><div>In stock</div><div>( Yes / No )</div><div class="remove">&#10006;</div></li>
				<li class="sort block"><div>Description</div><div>( Multiple lines )</div><div class="remove">&#10006;</div></li>
				<li class="block">
					<div id="add_property">
						<div>If you need other properties, add them below:</div>
						<table>
							<tr>
								<td><input type="text" class="form-text" name="property" /></td>
								<td>{{ property_types_select() }}</td>
								<td><input type="button" class="form-submit" value="Add" /></td>
							</tr>
							<tr>
								<td class="help">Allowed digits, alphabetical characters, spaces and hyphens</td>
								<td></td>
								<td></td>
							</tr>
						</table>
					</div>
				</li>
			</ul>
			<input type="button" class="form-submit next" value="Next" />
		</form>
	</td>
</tr>
</table>
{% endblock %}