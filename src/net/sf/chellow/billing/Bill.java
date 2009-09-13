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

import java.math.BigDecimal;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Map.Entry;

import net.sf.chellow.monad.Hiber;
import net.sf.chellow.monad.HttpException;
import net.sf.chellow.monad.Invocation;
import net.sf.chellow.monad.MonadUtils;
import net.sf.chellow.monad.NotFoundException;
import net.sf.chellow.monad.Urlable;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.monad.XmlTree;
import net.sf.chellow.monad.types.MonadDate;
import net.sf.chellow.monad.types.MonadUri;
import net.sf.chellow.monad.types.UriPathElement;
import net.sf.chellow.physical.HhEndDate;
import net.sf.chellow.physical.PersistentEntity;
import net.sf.chellow.physical.RegisterRead;
import net.sf.chellow.physical.RegisterReadRaw;
import net.sf.chellow.physical.RegisterReads;
import net.sf.chellow.physical.Supply;
import net.sf.chellow.physical.SupplySnag;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

public class Bill extends PersistentEntity implements Urlable {
	public static Bill getBill(Long id) throws HttpException {
		Bill bill = (Bill) Hiber.session().get(Bill.class, id);
		if (bill == null) {
			throw new UserException("There isn't a bill with that id.");
		}
		return bill;
	}

	private Batch batch;

	private Supply supply;

	private DayStartDate issueDate;

	private DayStartDate startDate;

	private DayFinishDate finishDate;

	private BigDecimal net;

	private BigDecimal vat;

	private String reference;

	private Boolean isPaid; // Null is pending, false is rejected.

	private BillType type;

	private boolean isCancelledOut;

	private Set<RegisterRead> reads;

	public Bill() {
	}

	public Bill(Batch batch, Supply supply, RawBill invoiceRaw)
			throws HttpException {
		setBatch(batch);
		setSupply(supply);
		update(invoiceRaw.getIssueDate(), invoiceRaw.getStartDate(), invoiceRaw
				.getFinishDate(), invoiceRaw.getNet(), invoiceRaw.getVat(),
				null, false);
		setReference(invoiceRaw.getReference());
		for (RegisterReadRaw rawRead : invoiceRaw.getRegisterReads()) {
			insertRead(rawRead);
		}
	}

	public Batch getBatch() {
		return batch;
	}

	public void setBatch(Batch batch) {
		this.batch = batch;
	}

	public Supply getSupply() {
		return supply;
	}

	public void setSupply(Supply supply) {
		this.supply = supply;
	}

	public DayStartDate getIssueDate() {
		return issueDate;
	}

	protected void setIssueDate(DayStartDate issueDate) {
		this.issueDate = issueDate;
	}

	public DayStartDate getStartDate() {
		return startDate;
	}

	protected void setStartDate(DayStartDate startDate) {
		this.startDate = startDate;
	}

	public DayFinishDate getFinishDate() {
		return finishDate;
	}

	protected void setFinishDate(DayFinishDate finishDate) {
		this.finishDate = finishDate;
	}

	public BigDecimal getNet() {
		return net;
	}

	void setNet(BigDecimal net) {
		this.net = net;
	}

	public BigDecimal getVat() {
		return vat;
	}

	void setVat(BigDecimal vat) {
		this.vat = vat;
	}

	public String getReference() {
		return reference;
	}

	public void setReference(String reference) {
		this.reference = reference;
	}

	public Boolean getIsPaid() {
		return isPaid;
	}

	public void setIsPaid(Boolean isPaid) {
		this.isPaid = isPaid;
	}

	public BillType getType() {
		return type;
	}

	public void setType(BillType type) {
		this.type = type;
	}

	public boolean getIsCancelledOut() {
		return isCancelledOut;
	}

	public void setIsCancelledOut(boolean isCancelledOut) {
		this.isCancelledOut = isCancelledOut;
	}

	void setReads(Set<RegisterRead> reads) {
		this.reads = reads;
	}

	public Set<RegisterRead> getReads() {
		return reads;
	}

	public void update(DayStartDate issueDate, DayStartDate startDate,
			DayFinishDate finishDate, BigDecimal net, BigDecimal vat,
			Boolean isPaid, boolean isCancelledOut) throws HttpException {
		setIssueDate(issueDate);
		if (startDate.getDate().after(finishDate.getDate())) {
			throw new UserException(
					"The bill start date can't be after the finish date.");
		}
		setStartDate(startDate);
		setFinishDate(finishDate);
		setNet(net);
		setVat(vat);
		setIsPaid(isPaid);
		setIsCancelledOut(isCancelledOut);
		virtualEqualsActual();
	}

	public Element toXml(Document doc) throws HttpException {
		Element element = super.toXml(doc, "invoice");
		issueDate.setLabel("issue");
		element.appendChild(issueDate.toXml(doc));
		startDate.setLabel("start");
		element.appendChild(startDate.toXml(doc));
		finishDate.setLabel("finish");
		element.appendChild(finishDate.toXml(doc));
		element.setAttribute("net", net.toString());
		element.setAttribute("vat", vat.toString());
		element.setAttribute("reference", reference);
		if (isPaid != null) {
			element.setAttribute("is-paid", Boolean.toString(isPaid));
		}
		element.setAttribute("is-cancelled-out", Boolean
				.toString(isCancelledOut));
		return element;
	}

	public void httpPost(Invocation inv) throws HttpException {
		if (inv.hasParameter("delete")) {
			delete();
			Hiber.commit();
			inv.sendSeeOther(batch.billsInstance().getUri());
		} else {
			// String accountReference = inv.getString("account-reference");
			Date issueDate = inv.getDate("issue-date");
			Date startDate = inv.getDate("start-date");
			Date finishDate = inv.getDate("finish-date");
			BigDecimal net = inv.getBigDecimal("net");
			BigDecimal vat = inv.getBigDecimal("vat");
			Boolean isPaid = inv.getBoolean("isPaid");
			Boolean isCancelledOut = inv.getBoolean("isCancelledOut");

			if (!inv.isValid()) {
				throw new UserException(document());
			}
			update(new DayStartDate(issueDate), new DayStartDate(startDate)
					.getNext(), new DayFinishDate(finishDate), net, vat,
					isPaid, isCancelledOut);
			Hiber.commit();
			inv.sendOk(document());
		}
	}

	private Document document() throws HttpException {
		Document doc = MonadUtils.newSourceDocument();
		Element source = doc.getDocumentElement();
		Element invoiceElement = (Element) toXml(doc, new XmlTree("batch",
				new XmlTree("contract", new XmlTree("party"))).put("bill",
				new XmlTree("account")));
		source.appendChild(invoiceElement);
		source.appendChild(MonadDate.getMonthsXml(doc));
		source.appendChild(MonadDate.getDaysXml(doc));
		for (RegisterRead read : reads) {
			invoiceElement.appendChild(read.toXml(doc, new XmlTree("mpan",
					new XmlTree("core").put("supplyGeneration", new XmlTree(
							"supply")))));
		}
		return doc;
	}

	public void httpGet(Invocation inv) throws HttpException {
		inv.sendOk(document());
	}

	public MonadUri getUri() throws HttpException {
		return batch.billsInstance().getUri().resolve(getUriId()).append("/");
	}

	public Urlable getChild(UriPathElement uriId) throws HttpException {
		if (RegisterReads.URI_ID.equals(uriId)) {
			return registerReadsInstance();
		} else {
			throw new NotFoundException();
		}
	}

	public RegisterReads registerReadsInstance() {
		return new RegisterReads(this);
	}

	public RegisterRead insertRead(RegisterReadRaw rawRead)
			throws HttpException {
		RegisterRead read = new RegisterRead(this, rawRead);
		if (reads == null) {
			reads = new HashSet<RegisterRead>();
		}
		reads.add(read);
		Hiber.flush();
		read.attach();
		return read;
	}

	@SuppressWarnings("unchecked")
	public void delete() throws HttpException {
		// Check missing bills...
		HhEndDate snagStart = startDate;
		if (!isCancelledOut) {
			for (Bill bill : (List<Bill>) Hiber
					.session()
					.createQuery(
							"from Bill bill where bill.batch.contract.id = :contractId and bill.isCancelledOut is false and bill.startDate.date <= :finishDate and bill.finishDate.date >= :startDate order by bill.startDate.date")
					.setLong("contractId", batch.getContract().getId())
					.setTimestamp("startDate", startDate.getDate())
					.setTimestamp("finishDate", finishDate.getDate()).list()) {
				if (bill.getStartDate().after(snagStart)) {
					supply.addSnag(batch.getContract(),
							SupplySnag.MISSING_BILL, startDate, finishDate);
					snagStart = bill.getFinishDate().getNext();
				}
			}
			if (!snagStart.after(getFinishDate())) {
				supply.addSnag(batch.getContract(), SupplySnag.MISSING_BILL,
						startDate, finishDate);
			}
		}
		reads.clear();
		Hiber.flush();
		Hiber.session().delete(this);
		Hiber.flush();
	}

	public BillSnag addSnag(String description) throws HttpException {
		BillSnag snag = (BillSnag) Hiber
				.session()
				.createQuery(
						"from BillSnag snag where snag.bill = :bill and snag.description = :description")
				.setEntity("bill", this).setString("description", description)
				.uniqueResult();
		if (snag == null) {
			snag = new BillSnag(description, this);
			Hiber.session().save(snag);
		}
		return snag;
	}

	@SuppressWarnings("unchecked")
	public Map<String, ?> virtualBill() throws HttpException {
		return (Map<String, ?>) batch.getContract().callFunction(
				"virtual_bill", new Object[] { supply, startDate, finishDate });
	}

	public void virtualEqualsActual() throws HttpException {
		Map<String, ?> vBill = virtualBill();
		Double vNet = (Double) vBill.get("net-gbp");
		Double vGross = (Double) vBill.get("gross-gbp");
		if (!vNet.equals(net.doubleValue())
				|| !vGross.equals(vat.doubleValue())) {
			addSnag(BillSnag.INCORRECT_BILL);
		}
	}

	public Element virtualBillXml(Document doc) throws HttpException {
		Element vElement = doc.createElement("virtual-bill");
		for (Entry<String, ?> entry : virtualBill().entrySet()) {
			vElement.setAttribute(entry.getKey(), entry.getValue().toString());
		}
		return vElement;
	}
}