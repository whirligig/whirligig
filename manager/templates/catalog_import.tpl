{% extends "manager/templates/base.tpl" %}

{% block title %}Import items{% endblock %}

{% block content %}
<h1>Catalog</h1>
<table id="catalog">
<tr>
	<td class="catalog_wizard">
		<div class="block">
		<div class="import_type">
			<div>Select type of your file with catalog data (images in file will not be imported):</div>
			<ul>
				<li><label for="xls">Excel file (95-2007)</label><input id="xls" type="radio" name="import_type" value="xls" /></li>
				<li><label for="csv">CSV file</label><input id="csv" type="radio" name="import_type" value="csv" /></li>
			</ul>
			<div class="import_file">
				<input type="file" name="import_file" />
				<input class="form-submit" type="button" value="Import" />
			</div>
		</div>
		</div>
		<div><input class="form-submit" type="submit" name="submit" value="Next" </div>
	</td>
</tr>
</table>
{% endblock %}