package net.sf.chellow.physical;

import java.util.HashSet;
import java.util.Set;

import net.sf.chellow.monad.DeployerException;
import net.sf.chellow.monad.DesignerException;
import net.sf.chellow.monad.Hiber;
import net.sf.chellow.monad.Invocation;
import net.sf.chellow.monad.ProgrammerException;
import net.sf.chellow.monad.Urlable;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.monad.types.MonadUri;
import net.sf.chellow.monad.types.UriPathElement;

public class Ssc extends PersistentEntity {
	public static Ssc insertSsc(int code, String tprs)
			throws ProgrammerException, UserException {
		Ssc ssc = new Ssc(code, tprs);
		Hiber.session().save(ssc);
		Hiber.flush();
		return ssc;
	}

	static public Ssc getSsc(String code) throws UserException,
			ProgrammerException {
		try {
			return getSsc(Integer.parseInt(code.trim()));
		} catch (NumberFormatException e) {
			throw UserException.newInvalidParameter("Problem parsing code: "
					+ e.getMessage());
		}
	}

	public static Ssc getSsc(int code) throws UserException,
			ProgrammerException {
		Ssc ssc = (Ssc) Hiber.session().createQuery(
				"from Ssc ssc where ssc.code = :code").setInteger("code", code)
				.uniqueResult();
		if (ssc == null) {
			throw UserException
					.newInvalidParameter("There isn't an SSC with code: "
							+ code + ".");
		}
		return ssc;
	}

	public static Ssc getSsc(long id) throws UserException, ProgrammerException {
		Ssc ssc = (Ssc) Hiber.session().get(Ssc.class, id);
		if (ssc == null) {
			throw UserException
					.newInvalidParameter("There isn't an SSC with id: " + id
							+ ".");
		}
		return ssc;
	}

	private SscCode code;

	private Set<MpanTop> mpanTops;

	private Set<Tpr> tprs;

	public Ssc() {
		setTypeName("ssc");
	}

	public Ssc(int code, String tprString) throws ProgrammerException,
			UserException {
		setCode(new SscCode(code));
		setTprs(new HashSet<Tpr>());
		if (tprString != null && tprString.trim().length() > 0) {
			for (String tprCode : tprString.split(",")) {
				Tpr tpr = Tpr.getTpr(tprCode);
				tprs.add(tpr);
			}
		}
	}

	public SscCode getCode() {
		return code;
	}

	void setCode(SscCode code) {
		this.code = code;
	}

	public Set<MpanTop> getMpanTops() {
		return mpanTops;
	}

	void setMpanTops(Set<MpanTop> mpanTops) {
		this.mpanTops = mpanTops;
	}

	public Set<Tpr> getTprs() {
		return tprs;
	}

	void setTprs(Set<Tpr> tprs) {
		this.tprs = tprs;
	}

	public Urlable getChild(UriPathElement uriId) throws ProgrammerException,
			UserException {
		return null;
	}

	public MonadUri getUri() throws ProgrammerException, UserException {
		// TODO Auto-generated method stub
		return null;
	}

	public void httpDelete(Invocation inv) throws ProgrammerException,
			DesignerException, UserException, DeployerException {
		// TODO Auto-generated method stub

	}

	public void httpGet(Invocation inv) throws DesignerException,
			ProgrammerException, UserException, DeployerException {
		// TODO Auto-generated method stub

	}

	public void httpPost(Invocation inv) throws ProgrammerException,
			UserException, DesignerException, DeployerException {
		// TODO Auto-generated method stub

	}

}
