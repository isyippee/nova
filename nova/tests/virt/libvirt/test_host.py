#    Copyright 2010 OpenStack Foundation
#    Copyright 2012 University Of Minho
#    Copyright 2014 Red Hat, Inc
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from nova import test
from nova.virt.libvirt import host
from nova.tests.virt.libvirt import fakelibvirt
from nova.virt.libvirt import driver as libvirt_driver

try:
    import libvirt
except ImportError:
    libvirt = fakelibvirt
host.libvirt = libvirt
libvirt_driver.libvirt = libvirt


class FakeVirtDomain(object):

    def __init__(self):
        pass

    def jobInfo(self):
        return []

    def jobStats(self, flags=0):
        return {}


class DomainJobInfoTestCase(test.NoDBTestCase):

    def setUp(self):
        super(DomainJobInfoTestCase, self).setUp()

        self.dom = FakeVirtDomain()
        host.DomainJobInfo._have_job_stats = True

    @mock.patch.object(FakeVirtDomain, "jobInfo")
    @mock.patch.object(FakeVirtDomain, "jobStats")
    def test_job_stats(self, mock_stats, mock_info):
        mock_stats.return_value = {
            "type": libvirt.VIR_DOMAIN_JOB_UNBOUNDED,
            "memory_total": 75,
            "memory_processed": 50,
            "memory_remaining": 33,
            "some_new_libvirt_stat_we_dont_know_about": 83
        }

        info = host.DomainJobInfo.for_domain(self.dom)

        self.assertIsInstance(info, host.DomainJobInfo)
        self.assertEqual(libvirt.VIR_DOMAIN_JOB_UNBOUNDED, info.type)
        self.assertEqual(75, info.memory_total)
        self.assertEqual(50, info.memory_processed)
        self.assertEqual(33, info.memory_remaining)
        self.assertEqual(0, info.disk_total)
        self.assertEqual(0, info.disk_processed)
        self.assertEqual(0, info.disk_remaining)

        mock_stats.assert_called_once_with()
        self.assertFalse(mock_info.called)

    @mock.patch.object(FakeVirtDomain, "jobInfo")
    @mock.patch.object(FakeVirtDomain, "jobStats")
    def test_job_info_no_support(self, mock_stats, mock_info):
        mock_stats.side_effect = fakelibvirt.make_libvirtError(
            libvirt.libvirtError,
            "virDomainGetJobStats not implemented",
            libvirt.VIR_ERR_NO_SUPPORT)

        mock_info.return_value = [
            libvirt.VIR_DOMAIN_JOB_UNBOUNDED,
            100, 99, 10, 11, 12, 75, 50, 33, 1, 2, 3]

        info = host.DomainJobInfo.for_domain(self.dom)

        self.assertIsInstance(info, host.DomainJobInfo)
        self.assertEqual(libvirt.VIR_DOMAIN_JOB_UNBOUNDED, info.type)
        self.assertEqual(100, info.time_elapsed)
        self.assertEqual(99, info.time_remaining)
        self.assertEqual(10, info.data_total)
        self.assertEqual(11, info.data_processed)
        self.assertEqual(12, info.data_remaining)
        self.assertEqual(75, info.memory_total)
        self.assertEqual(50, info.memory_processed)
        self.assertEqual(33, info.memory_remaining)
        self.assertEqual(1, info.disk_total)
        self.assertEqual(2, info.disk_processed)
        self.assertEqual(3, info.disk_remaining)

        mock_stats.assert_called_once_with()
        mock_info.assert_called_once_with()

    @mock.patch.object(FakeVirtDomain, "jobInfo")
    @mock.patch.object(FakeVirtDomain, "jobStats")
    def test_job_info_attr_error(self, mock_stats, mock_info):
        mock_stats.side_effect = AttributeError("No such API")

        mock_info.return_value = [
            libvirt.VIR_DOMAIN_JOB_UNBOUNDED,
            100, 99, 10, 11, 12, 75, 50, 33, 1, 2, 3]

        info = host.DomainJobInfo.for_domain(self.dom)

        self.assertIsInstance(info, host.DomainJobInfo)
        self.assertEqual(libvirt.VIR_DOMAIN_JOB_UNBOUNDED, info.type)
        self.assertEqual(100, info.time_elapsed)
        self.assertEqual(99, info.time_remaining)
        self.assertEqual(10, info.data_total)
        self.assertEqual(11, info.data_processed)
        self.assertEqual(12, info.data_remaining)
        self.assertEqual(75, info.memory_total)
        self.assertEqual(50, info.memory_processed)
        self.assertEqual(33, info.memory_remaining)
        self.assertEqual(1, info.disk_total)
        self.assertEqual(2, info.disk_processed)
        self.assertEqual(3, info.disk_remaining)

        mock_stats.assert_called_once_with()
        mock_info.assert_called_once_with()

    @mock.patch.object(FakeVirtDomain, "jobInfo")
    @mock.patch.object(FakeVirtDomain, "jobStats")
    def test_job_stats_no_domain(self, mock_stats, mock_info):
        mock_stats.side_effect = fakelibvirt.make_libvirtError(
            libvirt.libvirtError,
            "No such domain with UUID blah",
            libvirt.VIR_ERR_NO_DOMAIN)

        info = host.DomainJobInfo.for_domain(self.dom)

        self.assertIsInstance(info, host.DomainJobInfo)
        self.assertEqual(libvirt.VIR_DOMAIN_JOB_COMPLETED, info.type)
        self.assertEqual(0, info.time_elapsed)
        self.assertEqual(0, info.time_remaining)
        self.assertEqual(0, info.memory_total)
        self.assertEqual(0, info.memory_processed)
        self.assertEqual(0, info.memory_remaining)

        mock_stats.assert_called_once_with()
        self.assertFalse(mock_info.called)

    @mock.patch.object(FakeVirtDomain, "jobInfo")
    @mock.patch.object(FakeVirtDomain, "jobStats")
    def test_job_info_no_domain(self, mock_stats, mock_info):
        mock_stats.side_effect = fakelibvirt.make_libvirtError(
            libvirt.libvirtError,
            "virDomainGetJobStats not implemented",
            libvirt.VIR_ERR_NO_SUPPORT)

        mock_info.side_effect = fakelibvirt.make_libvirtError(
            libvirt.libvirtError,
            "No such domain with UUID blah",
            libvirt.VIR_ERR_NO_DOMAIN)

        info = host.DomainJobInfo.for_domain(self.dom)

        self.assertIsInstance(info, host.DomainJobInfo)
        self.assertEqual(libvirt.VIR_DOMAIN_JOB_COMPLETED, info.type)
        self.assertEqual(0, info.time_elapsed)
        self.assertEqual(0, info.time_remaining)
        self.assertEqual(0, info.memory_total)
        self.assertEqual(0, info.memory_processed)
        self.assertEqual(0, info.memory_remaining)

        mock_stats.assert_called_once_with()
        mock_info.assert_called_once_with()

    @mock.patch.object(FakeVirtDomain, "jobInfo")
    @mock.patch.object(FakeVirtDomain, "jobStats")
    def test_job_stats_operation_invalid(self, mock_stats, mock_info):
        mock_stats.side_effect = fakelibvirt.make_libvirtError(
            libvirt.libvirtError,
            "Domain is not running",
            libvirt.VIR_ERR_OPERATION_INVALID)

        info = host.DomainJobInfo.for_domain(self.dom)

        self.assertIsInstance(info, host.DomainJobInfo)
        self.assertEqual(libvirt.VIR_DOMAIN_JOB_COMPLETED, info.type)
        self.assertEqual(0, info.time_elapsed)
        self.assertEqual(0, info.time_remaining)
        self.assertEqual(0, info.memory_total)
        self.assertEqual(0, info.memory_processed)
        self.assertEqual(0, info.memory_remaining)

        mock_stats.assert_called_once_with()
        self.assertFalse(mock_info.called)

    @mock.patch.object(FakeVirtDomain, "jobInfo")
    @mock.patch.object(FakeVirtDomain, "jobStats")
    def test_job_info_operation_invalid(self, mock_stats, mock_info):
        mock_stats.side_effect = fakelibvirt.make_libvirtError(
            libvirt.libvirtError,
            "virDomainGetJobStats not implemented",
            libvirt.VIR_ERR_NO_SUPPORT)

        mock_info.side_effect = fakelibvirt.make_libvirtError(
            libvirt.libvirtError,
            "Domain is not running",
            libvirt.VIR_ERR_OPERATION_INVALID)

        info = host.DomainJobInfo.for_domain(self.dom)

        self.assertIsInstance(info, host.DomainJobInfo)
        self.assertEqual(libvirt.VIR_DOMAIN_JOB_COMPLETED, info.type)
        self.assertEqual(0, info.time_elapsed)
        self.assertEqual(0, info.time_remaining)
        self.assertEqual(0, info.memory_total)
        self.assertEqual(0, info.memory_processed)
        self.assertEqual(0, info.memory_remaining)

        mock_stats.assert_called_once_with()
        mock_info.assert_called_once_with()
