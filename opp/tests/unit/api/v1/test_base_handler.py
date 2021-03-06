import mock
import unittest

from opp.api.v1 import base_handler as bh


class TestBaseResponseHandler(unittest.TestCase):

    @mock.patch('flask.request')
    def test_check_payload_missing(self, request):
        request.get_json.return_value = {'key': "value"}
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error, {'result': "error",
                                 'message': "Payload missing!"})

    @mock.patch('flask.request')
    def test_check_payload_none(self, request):
        request.get_json.return_value = {'payload': None}
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error, {'result': "error",
                                 'message': "Empty payload!"})

    @mock.patch('flask.request')
    def test_check_payload_empty(self, request):
        request.get_json.return_value = {'payload': ""}
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error, {'result': "error",
                                 'message': "Empty payload!"})

    @mock.patch('flask.request')
    def test_check_payload_list(self, request):
        request.get_json.return_value = {'payload': ["blah", "blah"]}
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertNotEqual(payload, None)
        self.assertIsNone(error)

    @mock.patch('flask.request')
    def test_check_payload_not_list(self, request):
        request.get_json.return_value = {'payload': {"blah": "blah"}}
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=True)
        self.assertEqual(payload, None)
        self.assertEqual(error,
                         {'result': "error",
                          'message': "Payload should be in list form!"})

    @mock.patch('flask.request')
    def test_check_payload_obj(self, request):
        request.get_json.return_value = {'payload': {"blah": "blah"}}
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=False)
        self.assertNotEqual(payload, None)
        self.assertIsNone(error)

    @mock.patch('flask.request')
    def test_check_payload_not_obj(self, request):
        request.get_json.return_value = {'payload': ["blah", "blah"]}
        handler = bh.BaseResponseHandler(request)
        payload, error = handler._check_payload(expect_list=False)
        self.assertEqual(payload, None)
        self.assertEqual(error,
                         {'result': "error",
                          'message': "Payload should not be in list form!"})

    @mock.patch('flask.request')
    def test_respond_missing_phrase(self, request):
        request.headers = {}
        handler = bh.BaseResponseHandler(request)
        self.assertEqual(handler.respond(),
                         {'result': "error",
                         'message': "Passphrase header missing!"})

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_get')
    def test_respond_get(self, func, get_session, request):
        request.method = "GET"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_put')
    def test_respond_put(self, func, get_session, request):
        request.method = "PUT"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_post')
    def test_respond_post(self, func, mock_get_session, request):
        request.method = "POST"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_delete')
    def test_respond_delete(self, func, mock_get_session, request):
        request.method = "DELETE"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request)
        handler.respond()
        self._check_called(func)

    @mock.patch('flask.request')
    @mock.patch('opp.db.api.get_session')
    def test_respond_bad_verb(self, mock_get_session, request):
        request.method = "BAD"
        handler = bh.BaseResponseHandler(request)
        response = handler.respond(require_phrase=False)
        expected = {'result': "error", 'message': "Method not supported!"}
        self.assertEqual(response, expected)


class TestErrorResponseHandler(unittest.TestCase):

    def test_respond(self):
        handler = bh.ErrorResponseHandler("some error msg")
        response = handler.respond()
        expected = {'message': 'some error msg', 'result': 'error'}
        self.assertEqual(response, expected)
