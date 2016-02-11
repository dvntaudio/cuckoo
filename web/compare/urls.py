# Copyright (C) 2010-2013 Claudio Guarnieri.
# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file "docs/LICENSE" for copying permission.

import compare.views

from django.conf.urls import patterns, url

urlpatterns = [
    url(r"^(?P<left_id>\d+)/$", compare.views.left),
    url(r"^(?P<left_id>\d+)/(?P<right_id>\d+)/$", compare.views.both),
    url(r"^(?P<left_id>\d+)/(?P<right_hash>\w+)/$", compare.views.hash),
]
