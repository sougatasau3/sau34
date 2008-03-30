/*
 
 Copyright 2005-2008 Meniscus Systems Ltd
 
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

package net.sf.chellow.physical;

import java.text.DecimalFormat;
import java.text.NumberFormat;
import java.util.Locale;

import net.sf.chellow.monad.ProgrammerException;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.monad.types.MonadInteger;

public class MeterTimeswitchCode extends MonadInteger {
	public MeterTimeswitchCode() {
		setTypeName("code");
		setMinimum(0);
		setMaximum(999);
	}

	public MeterTimeswitchCode(String code) throws UserException,
			ProgrammerException {
		this(null, code);
	}

	public MeterTimeswitchCode(String label, String code) throws UserException,
			ProgrammerException {
		this();
		setLabel(label);
		update(code);
	}

	public void update(String code) throws UserException, ProgrammerException {
		NumberFormat profileClassCodeFormat = NumberFormat
				.getIntegerInstance(Locale.UK);
		int mtc = Integer.parseInt(code.trim());
		if (mtc < 0) {
			throw UserException
					.newInvalidParameter("The MTC can't be negative.");
		}
		profileClassCodeFormat.setMinimumIntegerDigits(3);
		super.update(profileClassCodeFormat.format(mtc));
	}

	public boolean hasDso() {
		return !((getInteger() > 499 && getInteger() < 510) || (getInteger() > 799 && getInteger() < 1000));
	}

	public String toString() {
		DecimalFormat mtcFormat = new DecimalFormat("000");
		return mtcFormat.format(getInteger());
	}
}