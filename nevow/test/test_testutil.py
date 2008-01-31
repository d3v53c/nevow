"""
Tests for L{nevow.testutil} -- a module of utilities for testing Nevow
applications.
"""

from unittest import TestResult

from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase, SkipTest
from twisted.web.http import OK, BAD_REQUEST

from nevow.testutil import FakeRequest, renderPage, JavaScriptTestCase
from nevow.testutil import NotSupported
from nevow.url import root
from nevow.rend import Page
from nevow.loaders import stan


class TestFakeRequest(TestCase):
    """
    Bad tests for L{FakeRequest}.

    These tests verify that L{FakeRequest} has some behavior, but not that
    that behavior is the same as the behavior of an actual request object. 
    In other words, these tests do not actually verify the fake.  They
    should be replaced with something which verifies that L{FakeRequest} and
    L{NevowRequest} actually have the same behavior.
    """
    def test_fields(self):
        """
        L{FakeRequest.fields} is C{None} for all fake requests.
        """
        self.assertIdentical(FakeRequest().fields, None)


    def test_prePathURL(self):
        """
        Verify that L{FakeRequest.prePathURL} returns the prepath of the
        requested URL.
        """
        req = FakeRequest(currentSegments=['a'], uri='/a/b')
        self.assertEqual(req.prePathURL(), 'http://localhost/a')


    def test_prePathURLHost(self):
        """
        Verify that L{FakeRequest.prePathURL} will turn the C{Host} header of
        the request into the netloc of the returned URL, if it's present.
        """
        req = FakeRequest(currentSegments=['a', 'b'], uri='/a/b/c/')
        req.setHeader('host', 'foo.bar')
        self.assertEqual(req.prePathURL(), 'http://foo.bar/a/b')


    def test_headers(self):
        """
        Check that one can get headers from L{FakeRequest} after they
        have been set with L{FakeRequest.setHeader}.
        """
        host = 'divmod.com'
        req = FakeRequest()
        req.setHeader('host', host)
        self.assertEqual(req.getHeader('host'), host)

    def test_urls(self):
        """
        Check that rendering URLs via L{renderPage} actually works.
        """
        class _URLPage(Page):
            docFactory = stan(
                root.child('foo'))

        def _checkForUrl(result):
            return self.assertEquals('http://localhost/foo', result)

        return renderPage(_URLPage()).addCallback(_checkForUrl)


    def test_defaultResponseCode(self):
        """
        Test that the default response code of a fake request is success.
        """
        self.assertEqual(FakeRequest().code, OK)


    def test_setResponseCode(self):
        """
        Test that the response code of a fake request can be set.
        """
        req = FakeRequest()
        req.setResponseCode(BAD_REQUEST)
        self.assertEqual(req.code, BAD_REQUEST)


class JavaScriptTests(TestCase):
    """
    Tests for the JavaScript UnitTest runner, L{JavaScriptTestCase}.
    """
    def setUp(self):
        """
        Create a L{JavaScriptTestCase} and verify that its dependencies are
        present (otherwise, skip the test).
        """
        self.case = JavaScriptTestCase()
        try:
            self.case.checkDependencies()
        except NotSupported:
            raise SkipTest("Missing JS dependencies")


    def test_unsuccessfulExit(self):
        """
        Verify that an unsuccessful exit status results in an error.
        """
        result = TestResult()
        self.case.createSource = lambda testMethod: "throw new TypeError();"
        self.case.run(result)
        self.assertEqual(len(result.errors), 1)


    def test_signalledExit(self):
        """
        An error should be reported if the JavaScript interpreter exits because
        it received a signal.
        """
        def stubFinder():
            return FilePath(__file__).sibling('segfault.py').path
        self.case.findJavascriptInterpreter = stubFinder
        self.case.createSource = lambda testMethod: ""
        result = TestResult()
        self.case.run(result)
        self.assertEqual(len(result.errors), 1)
