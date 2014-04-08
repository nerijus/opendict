# OpenDict
# Copyright (c) 2003-2006 Martynas Jocius <martynas.jocius@idiles.com>
# Copyright (c) 2007 IDILES SYSTEMS, UAB <support@idiles.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your opinion) any later version.
#
# This program is distributed in the hope that will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MECHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more detals.
#
# You shoud have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
#
# Module: history

class History:

    def __init__(self):

        self.pages = []
        self.index = -1

    def add(self, page):

        self.pages.append(page)
        self.index = len(self.pages) - 1

    def clear(self):

        self.pages = []
        self.index = -1

    def back(self):

        if self.index > 0:
            self.index -= 1
            page = self.pages[self.index]
        else:
            page = self.pages[self.index]

        return page

    def forward(self):

        if self.index < len(self.pages) - 1:
            self.index += 1
            page = self.pages[self.index]
        else:
            page = self.pages[self.index]

        return page

    def canBack(self):

        return self.index > 0

    def canForward(self):

        return self.index < len(self.pages) - 1

