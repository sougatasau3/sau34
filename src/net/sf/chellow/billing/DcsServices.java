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

import java.util.Date;
import java.util.List;

import net.sf.chellow.monad.DeployerException;
import net.sf.chellow.monad.DesignerException;
import net.sf.chellow.monad.Hiber;
import net.sf.chellow.monad.Invocation;
import net.sf.chellow.monad.MonadUtils;
import net.sf.chellow.monad.ProgrammerException;
import net.sf.chellow.monad.Urlable;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.monad.XmlDescriber;
import net.sf.chellow.monad.XmlTree;
import net.sf.chellow.monad.types.MonadUri;
import net.sf.chellow.monad.types.UriPathElement;
import net.sf.chellow.physical.HhEndDate;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;


@SuppressWarnings("serial")
public class DcsServices implements Urlable, XmlDescriber {
	public static final UriPathElement URI_ID;

	static {
		try {
			URI_ID = new UriPathElement("services");
		} catch (UserException e) {
			throw new RuntimeException(e);
		} catch (ProgrammerException e) {
			throw new RuntimeException(e);
		}
	}

	private Dcs dcs;

	public DcsServices(Dcs dcs) {
		this.dcs = dcs;
	}

	public UriPathElement getUrlId() {
		return URI_ID;
	}

	public MonadUri getUri() throws ProgrammerException, UserException {
		return dcs.getUri().resolve(getUrlId()).append("/");
	}

	public void httpPost(Invocation inv) throws ProgrammerException,
			UserException, DesignerException, DeployerException {
		int type = inv.getInteger("type");
		String name = inv.getString("name");
		Date startDate = inv.getDate("start");
		Date finishDate = null;
		boolean hasFinished = inv.getBoolean("hasFinished");
		String chargeScript = inv.getString("charge-script");
		if (!inv.isValid()) {
			throw UserException.newInvalidParameter(document());
		}
		if (hasFinished) {
			finishDate = inv.getDate("finish");
			if (!inv.isValid()) {
				throw UserException.newInvalidParameter(document());
			}
		}
		DcsService contract = dcs.insertContract(type, name, HhEndDate.roundDown(startDate), HhEndDate.roundDown(finishDate), chargeScript);
		Hiber.commit();
		inv.sendCreated(document(), contract.getUri());
	}

	@SuppressWarnings("unchecked")
	private Document document() throws ProgrammerException, UserException, DesignerException {
		Document doc = MonadUtils.newSourceDocument();
		Element source = doc.getDocumentElement();
		Element contractsElement = (Element) toXML(doc);
		source.appendChild(contractsElement);
		contractsElement.appendChild(dcs.toXML(doc));
		for (DceService contract : (List<DceService>) Hiber
				.session()
				.createQuery(
						"from ContractDce contract where contract.dcs = :dcs order by contract.name")
				.setEntity("dcs", dcs).list()) {
			contractsElement.appendChild(contract.toXML(doc));
		}
		return doc;
	}

	public void httpGet(Invocation inv) throws DesignerException,
			ProgrammerException, UserException, DeployerException {
		inv.sendOk(document());
	}

	public Service getChild(UriPathElement uriId) throws UserException,
			ProgrammerException {
		Service contract = (Service) Hiber
				.session()
				.createQuery(
						"from ContractDce contract where contract.dcs = :dcs and contract.id = :contractId")
				.setEntity("dcs", dcs).setLong("contractId",
						Long.parseLong(uriId.getString())).uniqueResult();
		if (contract == null) {
			throw UserException.newNotFound();
		}
		return contract;
	}

	public void httpDelete(Invocation inv) throws ProgrammerException,
			UserException {
		// TODO Auto-generated method stub

	}

	public Node toXML(Document doc) throws ProgrammerException, UserException {
		Element contractsElement = doc.createElement("dcs-services");
		return contractsElement;
	}

	public Node getXML(XmlTree tree, Document doc) throws ProgrammerException,
			UserException {
		// TODO Auto-generated method stub
		return null;
	}
}