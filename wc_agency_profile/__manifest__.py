# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Raya Agency Profile',
    'summary': 'Raya Agency profile from Backend',
    'version': '14.0.0.1.0',
    'category': 'HR',
    'author': 'White Code Company.',
    'maintainer': 'White Code Company.',
    'live_test_url': 'http://white-code.co.uk/',
    'contributors': ['Ahmad Nabeel <anabil@white-code.co.uk>'],
    'website': 'http://white-code.co.uk/',
    'depends': ['base','hr_recruitment','hr','wc_hiring_request','wc_raya_updates2'],
    'data': [
        #'views/update_profile_template.xml',
        'views/views.xml',
        #'views/warning_wizard.xml',
        'ir.model.access.csv'

    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'images': ['static/description/poster_image.png'],
}
