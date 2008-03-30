/*
 
 Copyright 2005 Meniscus Systems Ltd
 
 This file is part of Chellow.

 Chellow is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 Chellow is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Chellow; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 */

package net.sf.chellow.billing;

import java.util.List;

import net.sf.chellow.monad.DeployerException;
import net.sf.chellow.monad.DesignerException;
import net.sf.chellow.monad.Hiber;
import net.sf.chellow.monad.Invocation;
import net.sf.chellow.monad.MonadUtils;
import net.sf.chellow.monad.ProgrammerException;
import net.sf.chellow.monad.Urlable;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.monad.types.MonadUri;
import net.sf.chellow.monad.types.UriPathElement;
import net.sf.chellow.physical.HhEndDate;
import net.sf.chellow.physical.SupplyGeneration;
import net.sf.chellow.ui.Chellow;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

public class Government extends Provider {
	public static final UriPathElement URI_ID;

	static {
		try {
			URI_ID = new UriPathElement("government");
		} catch (UserException e) {
			throw new RuntimeException(e);
		} catch (ProgrammerException e) {
			throw new RuntimeException(e);
		}
	}

	public static Government insertGovernment() {
		Government government = new Government("Government");
		Hiber.session().save(government);
		Hiber.flush();
		return government;
	}

	public static Government getGovernment() throws UserException,
			ProgrammerException {
		Government government = findGovernment();
		if (government == null) {
			throw new ProgrammerException("Can't find the government!");
		}
		return government;
	}

	public static Government findGovernment() {
		return (Government) Hiber.session().createQuery(
				"from Government government").uniqueResult();
	}

	public Government() {
		setTypeName("government");
	}

	public Government(String name) {
		super(name);
	}

	public void httpPost(Invocation inv) throws ProgrammerException,
			UserException, DesignerException, DeployerException {
	}

	public void httpGet(Invocation inv) throws DesignerException,
			ProgrammerException, UserException, DeployerException {
		inv.sendOk(document());
	}

	private Document document() throws ProgrammerException, UserException,
			DesignerException {
		Document doc = MonadUtils.newSourceDocument();
		Element source = doc.getDocumentElement();
		source.appendChild(toXML(doc));
		return doc;
	}

	public MonadUri getUri() throws ProgrammerException, UserException {
		return Chellow.getUrlableRoot().getUri().resolve(getUriId())
				.append("/");
	}
	
	public UriPathElement getUriId() {
		return URI_ID;
	}

	public Urlable getChild(UriPathElement uriId) throws ProgrammerException,
			UserException {
		if (GovernmentServices.URI_ID.equals(uriId)) {
			return servicesInstance();
		}
		throw UserException.newNotFound();
	}

	public void httpDelete(Invocation inv) throws ProgrammerException,
			DesignerException, UserException, DeployerException {
	}

	GovernmentServices servicesInstance() {
		return new GovernmentServices(this);
	}

	@Override
	public List<SupplyGeneration> supplyGenerations(Account account) {
		// TODO Auto-generated method stub
		return null;
	}

	public GovernmentService insertService(String name, HhEndDate startDate,
			String chargeScript) throws UserException, ProgrammerException,
			DesignerException {
		GovernmentService service = new GovernmentService(name, startDate,
				chargeScript, this);
		Hiber.session().save(service);
		Hiber.flush();
		return service;
	}

	@Override
	public GovernmentService getService(String name) throws UserException,
			ProgrammerException {
		GovernmentService service = (GovernmentService) Hiber
				.session()
				.createQuery(
						"from GovernmentService service where service.provider = :provider and service.name = :serviceName")
				.setEntity("provider", this).setString("serviceName", name)
				.uniqueResult();
		if (service == null) {
			throw UserException.newInvalidParameter("The government service '"
					+ name + "' doesn't exist.");
		}
		return service;
	}
}