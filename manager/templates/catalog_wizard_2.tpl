{% extends "manager/templates/base.tpl" %}

{% block title %}Catalog wizard{% endblock %}

{% block content %}
<h1>Catalog wizard</h1>
<table id="catalog">
<tr>
	<td class="catalog_wizard">
		<div class="center done">Catalog is successful created. You may fill it manually or automatically (import excel or csv file)</div>
		<table class="choice_table">
			<tr>
				<td><a href="{{ MANAGER_URL }}catalog/add/"><input type="button" class="form-submit" value="Add items manually" /></a></td>
				<td>
                    <a href="{{ MANAGER_URL }}catalog/import/"><input type="button" class="form-submit" value="Import from file" /></a>
                    <div class="help">(Not implemented yet)</div>
                </td>
			</tr>
		</table>
	</td>
</tr>
</table>
{% endblock %}