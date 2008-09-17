package net.sf.chellow.physical;

import net.sf.chellow.billing.DayFinishDate;
import net.sf.chellow.billing.Invoice;
import net.sf.chellow.data08.MpanCoreRaw;
import net.sf.chellow.monad.Hiber;
import net.sf.chellow.monad.HttpException;
import net.sf.chellow.monad.InternalException;
import net.sf.chellow.monad.Invocation;
import net.sf.chellow.monad.MonadMessage;
import net.sf.chellow.monad.MonadUtils;
import net.sf.chellow.monad.Urlable;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.monad.XmlTree;
import net.sf.chellow.monad.types.MonadDate;
import net.sf.chellow.monad.types.MonadUri;
import net.sf.chellow.monad.types.UriPathElement;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

public class RegisterRead extends PersistentEntity {
	private Mpan mpan;

	private Invoice invoice;

	private float coefficient;

	private Units units;

	private Tpr tpr;

	private DayFinishDate previousDate;

	private float previousValue;

	private ReadType previousType;

	private DayFinishDate presentDate;

	private float presentValue;

	private ReadType presentType;

	RegisterRead() {
	}

	public RegisterRead(Invoice invoice, RegisterReadRaw rawRead)
			throws HttpException {
		if (invoice == null) {
			throw new InternalException("The invoice must not be null.");
		}
		setInvoice(invoice);
		setTpr(Tpr.getTpr(rawRead.getTpr()));
		setCoefficient(rawRead.getCoefficient());
		setUnits(rawRead.getUnits());
		setPreviousDate(rawRead.getPreviousDate());
		setPreviousValue(rawRead.getPreviousValue());
		setPreviousType(rawRead.getPreviousType());
		setPresentDate(rawRead.getPresentDate());
		setpresentValue(rawRead.getPresentValue());
		setpresentType(rawRead.getPresentType());

		MpanCoreRaw mpanCoreRaw = rawRead.getMpanRaw().getMpanCoreRaw();
		Organization org = invoice.getBatch().getContract().getOrganization();
		MpanCore mpanCore = org.getMpanCore(mpanCoreRaw);
		Supply supply = mpanCore.getSupply();
		SupplyGeneration supplyGeneration = supply.getGeneration(rawRead
				.getPresentDate());
		Mpan importMpan = supplyGeneration.getImportMpan();
		Mpan exportMpan = supplyGeneration.getExportMpan();
		if (importMpan != null
				&& importMpan.getMpanRaw().equals(rawRead.getMpanRaw())) {
			setMpan(importMpan);
		} else if (exportMpan != null
				&& exportMpan.getMpanRaw().equals(rawRead.getMpanRaw())) {
			setMpan(exportMpan);
		} else {
			throw new UserException("For the supply " + getId()
					+ " neither the import MPAN " + importMpan
					+ " or the export MPAN " + exportMpan
					+ " match the register read MPAN " + rawRead.getMpanRaw()
					+ ".");
		}
		precedingRead();
	}

	public Mpan getMpan() {
		return mpan;
	}

	void setMpan(Mpan mpan) {
		this.mpan = mpan;
	}

	public Invoice getInvoice() {
		return invoice;
	}

	void setInvoice(Invoice invoice) {
		this.invoice = invoice;
	}

	float getCoefficient() {
		return coefficient;
	}

	void setCoefficient(float coefficient) {
		this.coefficient = coefficient;
	}

	Units getUnits() {
		return units;
	}

	void setUnits(Units units) {
		this.units = units;
	}

	public Tpr getTpr() {
		return tpr;
	}

	void setTpr(Tpr tpr) {
		this.tpr = tpr;
	}

	DayFinishDate getPreviousDate() {
		return previousDate;
	}

	void setPreviousDate(DayFinishDate previousDate) {
		this.previousDate = previousDate;
	}

	float getPreviousValue() {
		return previousValue;
	}

	void setPreviousValue(float previousValue) {
		this.previousValue = previousValue;
	}

	public ReadType getPreviousType() {
		return previousType;
	}

	void setPreviousType(ReadType previousType) {
		this.previousType = previousType;
	}

	public DayFinishDate getPresentDate() {
		return presentDate;
	}

	void setPresentDate(DayFinishDate presentDate) {
		this.presentDate = presentDate;
	}

	public float getpresentValue() {
		return presentValue;
	}

	void setpresentValue(float presentValue) {
		this.presentValue = presentValue;
	}

	public ReadType getpresentType() {
		return presentType;
	}

	void setpresentType(ReadType presentType) {
		this.presentType = presentType;
	}

	public Urlable getChild(UriPathElement uriId) throws HttpException {
		return null;
	}

	public MonadUri getUri() throws InternalException, HttpException {
		// TODO Auto-generated method stub
		return null;
	}

	public void httpGet(Invocation inv) throws HttpException {
		inv.sendOk(document());
	}

	public void httpPost(Invocation inv) throws HttpException {
		if (inv.hasParameter("delete")) {
			delete();
			Hiber.commit();
			Document doc = document();
			Element source = doc.getDocumentElement();
			source.appendChild(new MonadMessage(
					"This register read has been successfully deleted.")
					.toXml(doc));
			inv.sendOk(doc);
		}
	}

	public void delete() {
		Hiber.session().delete(this);
	}

	@SuppressWarnings("unchecked")
	private Document document() throws HttpException {
		Document doc = MonadUtils.newSourceDocument();
		Element source = doc.getDocumentElement();
		source.appendChild(toXml(doc, new XmlTree("invoice", new XmlTree(
				"batch", new XmlTree("contract", new XmlTree("provider")
						.put("organization")))).put(
				"mpan",
				new XmlTree("supplyGeneration", new XmlTree("supply"))
						.put("mpanRaw")).put("tpr")));
		source.appendChild(MonadDate.getMonthsXml(doc));
		source.appendChild(MonadDate.getDaysXml(doc));
		return doc;
	}

	public Node toXml(Document doc) throws HttpException {
		Element element = super.toXml(doc, "register-read");
		element.setAttribute("coefficient", Float.toString(coefficient));
		element.setAttribute("units", units.toString());
		previousDate.setLabel("previous");
		element.appendChild(previousDate.toXml(doc));
		element.setAttribute("previous-value", Float.toString(previousValue));
		previousType.setLabel("previous");
		element.appendChild(previousType.toXml(doc));
		presentDate.setLabel("present");
		element.appendChild(presentDate.toXml(doc));
		element.setAttribute("present-value", Float.toString(presentValue));
		presentType.setLabel("present");
		element.appendChild(presentType.toXml(doc));
		return element;
	}

	public void attach() {
	}

	private RegisterRead precedingRead() throws HttpException {
		if (previousType.getCode() == ReadType.TYPE_INITIAL) {
			return null;
		}
		RegisterRead read = (RegisterRead) Hiber
				.session()
				.createQuery(
						"from RegisterRead read where read.mpan.mpanCore = :mpanCore and read.presentDate.date = :readDate")
				.setEntity("mpanCore", getMpan().getMpanCore()).setDate(
						"readDate", getPreviousDate().getDate()).uniqueResult();
		if (read == null) {
			throw new UserException(
					"There isn't a preceding read for this read.");
		}
		return read;
	}
}