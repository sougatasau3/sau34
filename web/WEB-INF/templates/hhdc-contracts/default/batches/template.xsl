<?xml version="1.0" encoding="us-ascii"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="US-ASCII"
		doctype-public="-//W3C//DTD HTML 4.01//EN" doctype-system="http://www.w3.org/TR/html4/strict.dtd"
		indent="yes" />
	<xsl:template match="/">
		<html>
			<head>
				<link rel="stylesheet" type="text/css"
					href="{/source/request/@context-path}/reports/19/output/" />
				<title>
					Chellow &gt; HHDC Contracts &gt;
					<xsl:value-of select="/source/batches/hhdc-contract/@name" />
					&gt;
					<xsl:value-of select="'Batches'" />
				</title>
			</head>
			<body>
				<p>
					<a href="{/source/request/@context-path}/reports/1/output/">
						<xsl:value-of select="'Chellow'" />
					</a>
					&gt;
					<a href="{/source/request/@context-path}/reports/113/output/">
						<xsl:value-of select="'HHDC Contracts'" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/reports/115/output/?hhdc-contract-id={/source/batches/hhdc-contract/@id}">
						<xsl:value-of select="/source/batches/hhdc-contract/@name" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/reports/93/output/?hhdc-contract-id={/source/batches/hhdc-contract/@id}">
						<xsl:value-of select="'Batches'" />
					</a>
					&gt; Edit
				</p>
				<br />
				<xsl:if test="//message">
					<ul>
						<xsl:for-each select="//message">
							<li>
								<xsl:value-of select="@description" />
							</li>
						</xsl:for-each>
					</ul>
				</xsl:if>
				<form action="." method="post">
					<fieldset>
						<legend>Add a batch</legend>
						<br />
						<label>
							<xsl:value-of select="'Reference '" />
							<input name="reference"
								value="{/source/request/parameter[@name = 'reference']/value}" />
						</label>
						<br />
						<label>
							<xsl:value-of select="'Description '" />
							<input name="description"
								value="{/source/request/parameter[@name = 'description']/value}" />
						</label>
						<br />
						<br />
						<input type="submit" value="Add" />
						<input type="reset" value="Reset" />
					</fieldset>
				</form>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>