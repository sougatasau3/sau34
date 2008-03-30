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

package net.sf.chellow.physical;



import net.sf.chellow.monad.ProgrammerException;
import net.sf.chellow.monad.UserException;
import net.sf.chellow.monad.types.MonadString;

public class Password extends MonadString {
	public Password() {
		setTypeName("password");
		setMinimumLength(6);
		setMaximumLength(250);
	}
	
	public Password(String name) throws UserException, ProgrammerException  {
		this(null, name);
	}

	public Password(String label, String name) throws UserException, ProgrammerException {
		this();
		setLabel(label);
			update(name);
	}
	
	public boolean equals(Object obj) {
		boolean isEqual = false;
		if (obj instanceof Password) {
			isEqual = getString().equals(((Password) obj).getString());
		}
		return isEqual;
	}
}