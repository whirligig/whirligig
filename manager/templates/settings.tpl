{% extends "manager/templates/base.tpl" %}

{% block title %}SETTINGS PAGE{% endblock %}

{% block content %}
<form action="" method="post" enctype="multipart/form-data">
	<table class="settings">
		<tr>
			<td class="vt">Sitename:</td>
			<td>
				<input class="form-text" type="text" name="sitename" value="{{ config.sitename }}" />
				<div class="help">Will be displayed in header</div>
			</td>
		</tr>
		{% if LOGO_USED %}
		<tr>
			<td class="vt">Logo: </td>
			<td>
				<table>
					<tr>
						<td class="vt">
							<input type="file" name="logo" />
							<div class="help">Will be displayed according to your theme</div>
						</td>
						<td id="settings_logo">
							<div class="frame">
								<div class="crop"><img src="{{ LOGO|get_mini_image }}" alt="Logo" title="Logo" /></div>
								<span class="remove">&#10006;</span>
							</div>
						</td>
					</tr>
				</table>
			</td>
		</tr>
		{% endif %}
		<tr>
			<td class="vt">Short description:</td>
			<td>
				<input class="form-text" type="text" name="short_description" value="{{ config.short_description }}" />
				<div class="help">Will be displayed as page title</div>
			</td>
		</tr>
		<tr>
			<td class="vt">Description:</td>
			<td>
				<textarea name="description">{{ config.description }}</textarea>
				<div class="help">May be used by search engines - Bing, Yahoo, Google, etc. (Meta description tag) </div>
			</td>
		</tr>
		<tr>
			<td class="vt">Keywords:</td>
			<td>
				<textarea name="keywords">{{ config.keywords }}</textarea>
				<div class="help">May be used by search engines - Bing, Yahoo, Google, etc. (Meta keywords tag) </div>
			</td>
		</tr>
		<tr class="translator">
			<td class="vt">Microsoft Translator</td>
			<td>
				<div>
					<div>Client ID:</div>
					<input class="form-text" type="text" name="translator_cid" value="{{ config.translator_cid }}" />
				</div>
				<div>
					<div>Client Secret:</div>
					<input class="form-text" type="text" name="translator_secret" value="{{ config.translator_secret }}" />
					<div class="help">
					Needed if you want translated to English title of static page as it URL.<br />
					<a target="_blank" href="http://go.microsoft.com/?linkid=9782667">Get from here</a>
					</div>
				</div>
			</td>
		</tr>
		<tr class="catalog">
			<td class="vt">Enable catalog:</td>
			<td>
				<table>
				<tr>
					<td>
						<label for="catalog_yes">Yes</label>
						<input id="catalog_yes" type="radio" name="catalog_enabled" value="on" {% if config.catalog_enabled %}checked{% endif %} />
					</td>
					<td>
						<label for="catalog_no">No</label>
						<input id="catalog_no" type="radio" name="catalog_enabled" value="off" {% if config.catalog_enabled|is_none %}checked{% endif %}/>
					</td>
				</tr>
				</table>
				<div class="help">Check this if you want the catalog on your site</div>
			</td>
		</tr>
		<tr class="connect">
			<td class="vt">Enable connect page:</td>
			<td>
				<table>
					<tr>
						<td>
							<label for="connect_yes">Yes</label><input id="connect_yes" type="radio" name="connect_enabled" value="on" {% if config.connect_enabled %}checked{% endif %} />
						</td>
						<td>
							<label for="connect_no">No</label><input id="connect_no" type="radio" name="connect_enabled" value="off" {% if config.connect_enabled|is_none %}checked{% endif %}/>
						</td>
					</tr>
				</table>
				<div class="help">Check this if you want recieve messages on your site</div>
			</td>
		</tr>
		<tr class="connect_email{% if config.connect_enabled|is_none %} hide{% endif %}">
			<td class="vt">Contact e-mail:</td>
			<td>
				<input class="form-text" type="text" name="connect_email" value="{{ config.connect_email }}" />
				<div class="help">E-mail for feedback</div>
			</td>
		</tr>
		<tr class="connect_host{% if config.connect_enabled|is_none %} hide{% endif %}">
			<td class="vt">SMTP settings</td>
			<td>
				<div>Host:</div>
				<div><input class="form-text" type="text" name="smtp_host" value="{{ config.smtp_host }}" /></div>
				<div>Port:</div>
				<div><input class="form-text" type="text" name="smtp_port" value="{{ config.smtp_port }}" /></div>
				<div>Username:</div>
				<div><input class="form-text" type="text" name="smtp_login" value="{{ config.smtp_login }}" /></div>
				<div>Password:</div>
				<div><input class="form-text" type="password" name="smtp_password" value="{{ config.smtp_password }}" /></div>
			</td>
		</tr>
		<tr><td></td><td><input class="form-submit" type="submit" name="submit" value="Save" /></td></tr>
	</table>
</form>
{% endblock %}