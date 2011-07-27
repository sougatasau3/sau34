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
					href="{/source/request/@context-path}/reports/19/output/" />
				<title>
					Chellow &gt; Reports &gt;
					<xsl:value-of
						select="/source/report-output/report/@name" />
					&gt; Output
				</title>
			</head>
			<body>
				<p>
					<a href="{/source/request/@context-path}/reports/1/output/">
						<xsl:value-of select="'Chellow'" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/reports/">
						<xsl:value-of select="'Reports'" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/reports/{/source/report-output/report/@id}/">
						<xsl:value-of
							select="/source/report-output/report/@name" />
					</a>
					&gt; Output
				</p>
				<br />
				<xsl:if test="//message">
					<ul>
						<xsl:for-each select="//message">
							<li>
								<pre>
									<xsl:value-of select="@description" />
								</pre>
							</li>
						</xsl:for-each>
					</ul>
				</xsl:if>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>