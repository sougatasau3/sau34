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
					Chellow &gt; Profile Classes &gt;
					<xsl:value-of select="/source/profile-class/@code" />
				</title>
			</head>

			<body>
				<p>
					<a href="{/source/request/@context-path}/">
						<img
							src="{/source/request/@context-path}/logo/" />
						<span class="logo">Chellow</span>
					</a>
					<xsl:value-of select="' &gt; '" />
					<a
						href="{/source/request/@context-path}/profile-classes/">
						<xsl:value-of select="'Profile Classes'" />
					</a>
					<xsl:value-of
						select="concat(' &gt; ', /source/profile-class/@code)" />
				</p>

				<xsl:if test="//message">
					<ul>
						<xsl:for-each select="//message">
							<li>
								<xsl:value-of select="@description" />
							</li>
						</xsl:for-each>
					</ul>
				</xsl:if>
				<ul>
					<li>
						Code:
						<xsl:value-of
							select="/source/profile-class/@code" />
					</li>
					<li>
						Description:
						<xsl:value-of
							select="/source/profile-class/@description" />
					</li>
				</ul>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>

