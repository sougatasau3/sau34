/*******************************************************************************
 * 
 *  Copyright (c) 2005, 2009 Wessex Water Services Limited
 *  
 *  This file is part of Chellow.
 * 
 *  Chellow is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 * 
 *  Chellow is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 * 
 *  You should have received a copy of the GNU General Public License
 *  along with Chellow.  If not, see <http://www.gnu.org/licenses/>.
 *  
 *******************************************************************************/

package net.sf.chellow.billing;

import java.util.Date;

import net.sf.chellow.monad.Hiber;
import net.sf.chellow.monad.HttpException;
import net.sf.chellow.monad.Invocation;
import net.sf.chellow.monad.MonadUtils;
import net.sf.chellow.monad.NotFoundException;
import net.sf.chellow.monad.Urlable;
import net.sf.chellow.monad.XmlTree;
import net.sf.chellow.monad.types.MonadDate;
import net.sf.chellow.monad.types.UriPathElement;
import net.sf.chellow.physical.MarketRole;
import net.sf.chellow.physical.Participant;
import net.sf.chellow.physical.PersistentEntity;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

public abstract class Party extends PersistentEntity {
	static public Party getParty(Long id) throws HttpException {
		Party party = (Party) Hiber.session().get(Party.class, id);
		if (party == null) {
			throw new NotFoundException("The Party with id " + id
					+ " could not be found.");
		}
		return party;
	}

	static public Party getParty(String participantCode, char roleCode)
			throws HttpException {
		return getParty(Participant.getParticipant(participantCode), MarketRole
				.getMarketRole(roleCode));
	}

	static public Party getParty(String participantCode, String roleCode)
			throws HttpException {
		return getParty(Participant.getParticipant(participantCode), MarketRole
				.getMarketRole(roleCode));
	}

	static public Party getParty(Participant participant, MarketRole role)
			throws HttpException {
		Party party = (Party) Hiber
				.session()
				.createQuery(
						"from Party party where party.participant = :participant and party.role = :role")
				.setEntity("participant", participant).setEntity("role", role)
				.uniqueResult();
		if (party == null) {
			throw new NotFoundException();
		}
		return party;
	}

	private String name;
	private Participant participant;
	private MarketRole role;
	private Date validFrom;
	private Date validTo;

	public Party() {
	}

	public Party(String name, Participant participant, char role,
			Date validFrom, Date validTo) throws HttpException {
		setName(name);
		setParticipant(participant);
		setRole(MarketRole.getMarketRole(role));
		setValidFrom(validFrom);
		setValidTo(validTo);
	}

	public String getName() {
		return name;
	}

	void setName(String name) {
		this.name = name;
	}

	public Participant getParticipant() {
		return participant;
	}

	void setParticipant(Participant participant) {
		this.participant = participant;
	}

	public MarketRole getRole() {
		return role;
	}

	void setRole(MarketRole role) {
		this.role = role;
	}

	public Date getValidFrom() {
		return validFrom;
	}

	void setValidFrom(Date from) {
		this.validFrom = from;
	}

	public Date getValidTo() {
		return validTo;
	}

	void setValidTo(Date to) {
		this.validTo = to;
	}

	public Element toXml(Document doc, String elementName) throws HttpException {
		Element element = super.toXml(doc, elementName);

		element.setAttribute("name", name);
		element.appendChild(MonadDate.toXML(validFrom, "from", doc));
		if (validTo != null) {
			element.appendChild(MonadDate.toXML(validTo, "to", doc));
		}
		return element;
	}

	public Element toXml(Document doc) throws HttpException {
		return toXml(doc, "party");
	}

	/*
	 * public Account getAccount(String accountText) throws HttpException {
	 * Account account = (Account) Hiber .session() .createQuery( "from Account
	 * account where account.provider = :provider and account.reference =
	 * :accountReference") .setEntity("provider",
	 * this).setString("accountReference", accountText.trim()).uniqueResult();
	 * if (account == null) { throw new UserException("There isn't an account
	 * for '" + getName() + "' with the reference '" + accountText + "'."); }
	 * return account; }
	 */
	/*
	 * abstract public List<SupplyGeneration> supplyGenerations(Account
	 * account);
	 * 
	 * public abstract Service getService(String name) throws HttpException,
	 * InternalException;
	 */
	@Override
	public Urlable getChild(UriPathElement uriId) throws HttpException {
		throw new NotFoundException();
	}

	@Override
	public void httpGet(Invocation inv) throws HttpException {
		Document doc = MonadUtils.newSourceDocument();
		Element source = doc.getDocumentElement();

		source.appendChild(toXml(doc, new XmlTree("participant").put("role")));
		inv.sendOk(doc);
	}

	@Override
	public void httpPost(Invocation inv) throws HttpException {
		// TODO Auto-generated method stub

	}
}
