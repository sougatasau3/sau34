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

package net.sf.chellow.hhimport.stark;

import java.io.IOException;
import java.io.LineNumberReader;
import java.io.Reader;
import java.text.DateFormat;
import java.text.ParseException;
import java.util.Locale;
import java.util.TimeZone;

import net.sf.chellow.data08.HhDatumRaw;
import net.sf.chellow.data08.MpanCoreRaw;
import net.sf.chellow.hhimport.HhConverter;
import net.sf.chellow.monad.ProgrammerException;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.physical.HhDatumStatus;
import net.sf.chellow.physical.HhEndDate;
import net.sf.chellow.physical.IsImport;
import net.sf.chellow.physical.IsKwh;

public class StarkDF2HHConverter implements HhConverter {
	private LineNumberReader reader;

	private MpanCoreRaw core;

	private HhDatumRaw datum = null;

	private HhDatumRaw datumNext = null;

	private IsImport isImport = null;

	private IsKwh isKwh = null;

	private String line;

	private DateFormat dateFormat = DateFormat.getDateTimeInstance(
			DateFormat.SHORT, DateFormat.SHORT, Locale.UK);

	public StarkDF2HHConverter(Reader reader) throws UserException,
			ProgrammerException {
		dateFormat.setTimeZone(TimeZone.getTimeZone("GMT"));
		this.reader = new LineNumberReader(reader);
		try {
			line = this.reader.readLine();
			if (!line.equals("#F2")) {
				throw UserException
						.newInvalidParameter("The first line must be '#F2'.");
			}
			line = this.reader.readLine();
			try {
				next();
			} catch (RuntimeException e) {
				if (e.getCause() != null) {
					Throwable t = e.getCause();
					if (t instanceof UserException) {
						throw (UserException) t;
					} else {
						throw new ProgrammerException(t);
					}
				} else {
					throw e;
				}
			}
		} catch (IOException e) {
			throw UserException.newOk("Can't read Stark DF2 file.");
		}
	}

	public boolean hasNext() {
		return datumNext != null;
	}

	public void remove() {
		throw new UnsupportedOperationException();
	}

	public HhDatumRaw next() {
		HhDatumRaw datum = null;
		this.datum = datumNext;
		try {
			while (datum == null && line != null) {
				if (line.startsWith("#O")) {
					core = new MpanCoreRaw("", line.substring(2));
				} else if (line.startsWith("#S")) {
					int sensor = Integer.parseInt(line.substring(2).trim());
					switch (sensor) {
					case 1:
						isImport = new IsImport(true);
						isKwh = new IsKwh(true);
						break;
					case 2:
						isImport = new IsImport(false);
						isKwh = new IsKwh(true);
						break;
					case 3:
						isImport = new IsImport(true);
						isKwh = new IsKwh(false);
						break;
					case 4:
						isImport = new IsImport(false);
						isKwh = new IsKwh(false);
						break;

					default:
						throw new RuntimeException(
								UserException
										.newOk("The sensor number must be between 1 and 4 inclusive."));
					}
				} else if (line.length() > 0 && !line.equals("#F2")) {
					int datePos = line.indexOf(',');
					if (datePos < 0) {
						throw UserException
								.newInvalidParameter("Problem at line number: "
										+ lastLineNumber() + ". '" + line
										+ "'. Can't find the first comma.");
					}
					datePos = line.indexOf(',', datePos + 1);
					if (datePos < 0) {
						throw UserException
								.newInvalidParameter("Problem at line number: "
										+ lastLineNumber() + ". '" + line
										+ "'. Can't find the second comma.");
					}
					HhEndDate endDate = new HhEndDate(dateFormat.parse(line
							.substring(0, datePos).replace(",", " ")));
					int valuePos = line.indexOf(',', datePos + 1);
					HhDatumStatus status = null;
					Float valueKw = null;
					if (valuePos < 0) {
						valueKw = Float.parseFloat(line.substring(datePos + 1));
					} else {
						valueKw = Float.parseFloat(line.substring(datePos + 1,
								valuePos));
						String trimmedLine = line.trim();
						status = new HhDatumStatus(trimmedLine
								.charAt(trimmedLine.length() - 1));
					}
					if (!core.getDsoCode().getString().equals("99")
							&& valueKw * 10 % 2 == 1) {
						throw UserException
								.newInvalidParameter("Problem at line number: "
										+ lastLineNumber()
										+ ". '"
										+ line
										+ "'. For a settlement MPAN the last digit of the value must be even. If it isn't it means that the data is probably kWh rather than kW.");
					}
					datum = new HhDatumRaw(core, isImport, isKwh, endDate,
							valueKw / 2, status);
				}
				line = reader.readLine();
			}
			datumNext = datum;
			return this.datum;
		} catch (IOException e) {
			RuntimeException rte = new RuntimeException();
			rte.initCause(e);
			throw rte;
		} catch (UserException e) {
			try {
				throw new RuntimeException(UserException
						.newInvalidParameter("Problem at line number: "
								+ lastLineNumber() + ": " + e.getMessage()));
			} catch (ProgrammerException e1) {
				throw new RuntimeException(e1);
			}
		} catch (ParseException e) {
			RuntimeException rte = new RuntimeException();
			try {
				rte.initCause(UserException
						.newInvalidParameter("Problem at line number: "
								+ lastLineNumber() + ". '" + line
								+ "' Can't parse date and time. "
								+ e.getMessage()));
			} catch (ProgrammerException e1) {
				throw new RuntimeException(e1);
			}
			throw rte;
		} catch (ProgrammerException e) {
			RuntimeException rte = new RuntimeException();
			rte.initCause(e);
			throw rte;
		}
	}

	public int lastLineNumber() {
		return reader.getLineNumber();
	}

	public void close() throws ProgrammerException {
		try {
			reader.close();
		} catch (IOException e) {
			throw new ProgrammerException(e);
		}
	}
}
