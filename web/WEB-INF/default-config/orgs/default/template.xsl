<?xml version="1.0" encoding="us-ascii"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="US-ASCII"
		doctype-public="-//W3C//DTD HTML 4.01//EN"
		doctype-system="http://www.w3.org/TR/html4/strict.dtd" indent="yes" />

	<xsl:template match="/">
		<html>
			<head>
				<link rel="stylesheet" type="text/css"
					href="{/source/request/@context-path}/style/" />

				<title>
					Chellow &gt; Organizations &gt;
					<xsl:value-of select="/source/organization/@name" />
				</title>

			</head>

			<body>
				<p>
					<a href="{/source/request/@context-path}/">
						<img
							src="{/source/request/@context-path}/logo/" />
						<span class="logo">Chellow</span>
					</a>
					&gt;
					<a href="{/source/request/@context-path}/orgs/">
						<xsl:value-of select="'Organizations'" />
					</a>
					&gt;
					<xsl:value-of select="/source/organization/@name" />
				</p>
				<xsl:if test="//message">
					<ul>
						<xsl:for-each select="//message">
							<li class="error">
								<xsl:value-of select="@description" />
							</li>
						</xsl:for-each>
					</ul>
				</xsl:if>
				<xsl:choose>
					<xsl:when
						test="/source/request/@method='get' and /source/request/parameter[@name='view']/value='confirm-delete'">
						<form method="post" action=".">
							<fieldset>
								<legend>
									Are you sure you want to delete this
									service?
								</legend>
								<input type="submit" name="delete"
									value="Delete" />
							</fieldset>
						</form>
						<p>
							<a href=".">Cancel</a>
						</p>
					</xsl:when>
					<xsl:otherwise>
						<form method="post" action=".">
							<fieldset>
								<legend>Update details</legend>
								<br />
								<label>
									Name
									<input name="name">
										<xsl:attribute name="value">
											<xsl:choose>
												<xsl:when
													test="/source/request/parameter[@name='name']">
													<xsl:value-of
														select="/source/request/parameter[@name='name']/value" />
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of
														select="/source/organization/@name" />
												</xsl:otherwise>
											</xsl:choose>
										</xsl:attribute>
									</input>
								</label>
								<br />
								<br />
								<input type="submit" value="Update" />
								<input type="reset" value="Reset" />
							</fieldset>
						</form>
						<form action=".">
							<fieldset>
								<input type="hidden" name="view"
									value="confirm-delete" />
								<legend>
									Delete this organization
								</legend>
								<input type="submit" value="Delete" />
							</fieldset>
						</form>
						<ul>
							<li>
								<a href="sites/">Sites</a>
							</li>
							<li>
								<a href="mpan-cores/">MPANs</a>
							</li>
							<li>
								<a href="header-data-imports/">
									Header Data Imports
								</a>
							</li>
							<li>
								<a href="reports/">Reports</a>
							</li>
						</ul>

						<h2>Providers</h2>

						<ul>
							<li>
								<a href="suppliers/">Suppliers</a>
							</li>
							<li>
								<a href="dcss/">
									Data Collectors for Settlement
								</a>
							</li>
							<li>
								<a href="dces/">
									Data Collectors for Energy
									Management
								</a>
							</li>
							<li>
								<a href="mops/">Meter Operators</a>
							</li>
						</ul>
					</xsl:otherwise>
				</xsl:choose>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>

