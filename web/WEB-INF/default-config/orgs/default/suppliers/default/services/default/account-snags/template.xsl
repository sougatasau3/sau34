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
					<xsl:value-of
						select="/source/account-snags/supplier-service/supplier/organization/@name" />
					&gt; Suppliers &gt;
					<xsl:value-of
						select="/source/account-snags/supplier-service/supplier/@name" />
					&gt; Services &gt;
					<xsl:value-of
						select="/source/account-snags/supplier-service/@name" />
					&gt; Account Snags
				</title>
			</head>

			<body>
				<xsl:if test="//message">
					<ul>
						<xsl:for-each select="//message">
							<li>
								<xsl:value-of select="@description" />
							</li>
						</xsl:for-each>
					</ul>
				</xsl:if>

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
					<a
						href="{/source/request/@context-path}/orgs/{/source/account-snags/supplier-service/supplier/organization/@id}/">
						<xsl:value-of
							select="/source/account-snags/supplier-service/supplier/organization/@name" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/orgs/{/source/account-snags/supplier-service/supplier/organization/@id}/suppliers/">
						<xsl:value-of select="'Suppliers'" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/orgs/{/source/account-snags/supplier-service/supplier/organization/@id}/suppliers/{/source/account-snags/supplier-service/supplier/@id}/">
						<xsl:value-of
							select="/source/account-snags/supplier-service/supplier/@name" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/orgs/{/source/account-snags/supplier-service/supplier/organization/@id}/suppliers/{/source/account-snags/supplier-service/supplier/@id}/services/">
						<xsl:value-of select="'Services'" />
					</a>
					&gt;
					<a
						href="{/source/request/@context-path}/orgs/{/source/account-snags/supplier-service/supplier/organization/@id}/suppliers/{/source/account-snags/supplier-service/supplier/@id}/services/{/source/account-snags/supplier-service/@id}/">
						<xsl:value-of
							select="/source/account-snags/supplier-service/@name" />
					</a>
					&gt; Account Snags
				</p>
				<br />
				<xsl:choose>
					<xsl:when
						test="/source/response/@status-code = '201'">
						<p>
							The
							<a
								href="{/source/response/header[@name = 'Location']/@value}">
								<xsl:value-of
									select="'new account snag'" />
							</a>
							has been successfully created.
						</p>
					</xsl:when>
					<xsl:otherwise>
						<table>
							<caption>Account Snags</caption>
							<thead>
								<tr>
									<th>Id</th>
									<th>Account</th>
									<th>Start Date</th>
									<th>Finish Date</th>
									<th>Date Created</th>
									<th>Date Resolved</th>
									<th>Is Ignored?</th>
									<th>Description</th>
								</tr>
							</thead>
							<tbody>
								<xsl:for-each
									select="/source/account-snags/account-snag">
									<tr>
										<td>
											<a href="{@id}/">
												<xsl:value-of
													select="@id" />
											</a>
										</td>
										<td>
											<a
												href="{/source/request/@context-path}/orgs/{/source/account-snags/supplier-service/supplier/organization/@id}/suppliers/{/source/account-snags/supplier-service/supplier/@id}/accounts/{account/@id}/">
												<xsl:value-of
													select="account/@reference" />
											</a>
										</td>
										<td>
											<xsl:value-of
												select="concat(hh-end-date[@label='start']/@year, '-', hh-end-date[@label='start']/@month, '-', hh-end-date[@label='start']/@day)" />
										</td>
										<td>
											<xsl:value-of
												select="concat(hh-end-date[@label='finish']/@year, '-', hh-end-date[@label='finish']/@month, '-', hh-end-date[@label='finish']/@day)" />
										</td>
										<td>
											<xsl:value-of
												select="concat(date[@label='created']/@year, '-', date[@label='created']/@month, '-', date[@label='created']/@day)" />
										</td>
										<td>
											<xsl:choose>
												<xsl:when
													test="hh-end-date[@label='resolved']">
													<xsl:value-of
														select="concat(hh-end-date[@label='resolved']/@year, '-', hh-end-date[@label='resolved']/@month, '-', hh-end-date[@label='resolved']/@day)" />
												</xsl:when>
												<xsl:otherwise>
													Unresolved
												</xsl:otherwise>
											</xsl:choose>
										</td>
										<td>
											<xsl:choose>
												<xsl:when
													test="@is-ignored = 'true'">
													Yes
												</xsl:when>
												<xsl:otherwise>
													No
												</xsl:otherwise>
											</xsl:choose>
										</td>
										<td>
											<xsl:value-of
												select="@description" />
										</td>
									</tr>
								</xsl:for-each>
							</tbody>
						</table>
						<br />
						<hr />
						<form action="." method="post">
							<fieldset>
								<legend>Add an account snag</legend>
								<label>
									<xsl:value-of select="'Reference '" />
									<input name="reference"
										value="{/source/request/parameter[@name = 'reference']/value}" />
								</label>
								<br />
								<br />
								<input type="submit" value="Add" />
								<input type="reset" value="Reset" />
							</fieldset>
						</form>
					</xsl:otherwise>
				</xsl:choose>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>