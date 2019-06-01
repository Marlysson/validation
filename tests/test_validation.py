
import json
import unittest

import pendulum

from masonite.app import App
from masonite.providers import ValidationProvider
from masonite.validation import RuleEnclosure
from masonite.validation.Validator import (ValidationFactory, Validator,
                                           accepted, active_domain,
                                           after_today, before_today, contains,
                                           date, email, equals, exists,
                                           greater_than, in_range, ip,
                                           is_future, is_in, is_past, isnt)
from masonite.validation.Validator import json as vjson
from masonite.validation.Validator import (length, less_than, none, numeric,
                                           phone, required, string, timezone,
                                           truthy, when)
from masonite.managers import SessionManager
from masonite.drivers import SessionCookieDriver
from masonite.testsuite import generate_wsgi


class TestValidation(unittest.TestCase):

    def setUp(self):
        pass

    def test_required(self):
        validate = Validator().validate({
            'test': 1
        }, required(['user', 'email']))

        self.assertEqual(validate['user'], ['user is required'])
        self.assertEqual(validate['email'], ['email is required'])

        validate = Validator().validate({
            'test': 1
        }, required(['test']))

        self.assertEqual(len(validate), 0)

    def test_extendable(self):
        v = Validator()
        v.extend('numeric', numeric)

        validate = v.validate({
            'test': 1
        }, v.numeric(['test']))

        self.assertEqual(len(validate), 0)

    def test_email(self):
        validate = Validator().validate({
            'email': 'user@example.com'
        }, email(['email']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'email': 'user'
        }, email(['email']))

        self.assertEqual(
            validate, {'email': ['email must be a valid email address']})

    def test_active_domain(self):
        validate = Validator().validate({
            'domain1': 'google.com',
            'domain2': 'http://google.com',
            'domain3': 'https://www.google.com',
            'email': 'admin@gmail.com'
        }, active_domain(['domain1', 'domain2', 'domain3', 'email']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'domain1': 'domain',
        }, active_domain(['domain1']))

        self.assertEqual(
            validate, {'domain1': ['domain1 must be an active domain name']})

    def test_phone(self):
        validate = Validator().validate({
            'phone': '876-182-1921'
        }, phone('phone', pattern='123-456-7890'))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'phone': '(876)182-1921'
        }, phone('phone', pattern='123-456-7890'))

        self.assertEqual(
            validate, {'phone': ['phone must be in the format XXX-XXX-XXXX']})

    def test_accepted(self):
        validate = Validator().validate({
            'terms': 'on'
        }, accepted(['terms']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'terms': 'test'
        }, accepted(['terms']))

        self.assertEqual(
            validate, {'terms': ['terms must be yes, on, 1 or true']})

    def test_ip(self):
        validate = Validator().validate({
            'ip': '192.168.1.1'
        }, ip(['ip']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'ip': 'test'
        }, ip(['ip']))

        self.assertEqual(validate, {'ip': ['ip must be a valid ipv4 address']})

    def test_timezone(self):
        validate = Validator().validate({
            'timezone': 'America/New_York'
        }, timezone(['timezone']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'timezone': 'test'
        }, timezone(['timezone']))

        self.assertEqual(
            validate, {'timezone': ['timezone must be a valid timezone']})

    def test_exists(self):
        validate = Validator().validate({
            'terms': 'on',
            'user': 'here',
        }, exists(['user']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'terms': 'test'
        }, exists(['user']))

        self.assertEqual(validate, {'user': ['user must exist']})

    def test_date(self):
        validate = Validator().validate({
            'date': '1975-05-21T22:00:00',
        }, date(['date']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': 'woop',
        }, date(['date']))

        self.assertEqual(validate, {'date': ['date must be a valid date']})

    def test_before_today(self):
        validate = Validator().validate({
            'date': '1975-05-21T22:00:00',
        }, before_today(['date']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': pendulum.yesterday().to_datetime_string(),
        }, before_today(['date']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': '2020-05-21T22:00:00',
        }, before_today(['date']))

        self.assertEqual(
            validate, {'date': ['date must be a date before today']})

    def test_after_today(self):
        validate = Validator().validate({
            'date': '2020-05-21T22:00:00',
        }, after_today(['date']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': pendulum.tomorrow().to_datetime_string(),
        }, after_today(['date']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': '1975-05-21T22:00:00',
        }, after_today(['date']))

        self.assertEqual(
            validate, {'date': ['date must be a date after today']})

    def test_is_past(self):
        validate = Validator().validate({
            'date': '1950-05-21T22:00:00',
        }, is_past(['date']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': pendulum.yesterday().to_datetime_string(),
        }, is_past(['date'], tz='America/New_York'))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': pendulum.tomorrow().to_datetime_string(),
        }, is_past('date', tz='America/New_York'))

        self.assertEqual(
            validate, {'date': ['date must be a time in the past']})

    def test_is_future(self):
        validate = Validator().validate({
            'date': '2020-05-21T22:00:00',
        }, is_future(['date']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': pendulum.tomorrow().to_datetime_string(),
        }, is_future(['date'], tz='America/New_York'))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'date': pendulum.yesterday().to_datetime_string(),
        }, is_future(['date']))

        self.assertEqual(
            validate, {'date': ['date must be a time in the past']})

    def test_exception(self):
        with self.assertRaises(AttributeError) as e:
            validate = Validator().validate({
                'terms': 'on',
            }, required(['user'], raises={
                'user': AttributeError
            }))

        try:
            validate = Validator().validate({
                'terms': 'on',
            }, required(['user'], raises={
                'user': AttributeError
            }))
        except AttributeError as e:
            self.assertEqual(str(e), 'user is required')

        try:
            validate = Validator().validate({
                'terms': 'on',
            }, required(['user'], raises=True))
        except ValueError as e:
            self.assertEqual(str(e), 'user is required')

    def test_conditional(self):
        validate = Validator().validate({
            'terms': 'on'
        }, when(accepted(['terms'])).then(
            required(['user'])
        ))

        self.assertEqual(validate, {'user': ['user is required']})

        validate = Validator().validate({
            'terms': 'test'
        }, accepted(['terms']))

        self.assertEqual(
            validate, {'terms': ['terms must be yes, on, 1 or true']})

    def test_error_message_required(self):
        validate = Validator().validate({
            'test': 1
        }, required(['user', 'email'], messages={
            'user': 'there must be a user value'
        }))

        self.assertEqual(validate['user'], ['there must be a user value'])
        self.assertEqual(validate['email'], ['email is required'])

        validate = Validator().validate({
            'test': 1
        }, required(['user', 'email'], messages={
            'email': 'there must be an email value'
        }))

        self.assertEqual(validate['user'], ['user is required'])
        self.assertEqual(validate['email'], ['there must be an email value'])

    def test_numeric(self):
        validate = Validator().validate({
            'test': 1
        }, numeric(['test']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'test': 'hey'
        }, numeric(['test']))

        self.assertEqual(validate, {'test': ['test must be a numeric']})

    def test_several_tests(self):
        validate = Validator().validate({
            'test': 'hey'
        }, required(['notin']), numeric(['notin']))

        self.assertEqual(
            validate, {'notin': ['notin is required', 'notin must be a numeric']})

    def test_json(self):
        validate = Validator().validate({
            'json': 'hey'
        }, vjson(['json']))

        self.assertEqual(validate, {'json': ['json must be json']})

        validate = Validator().validate({
            'json': json.dumps({'test': 'key'})
        }, vjson(['json']))

        self.assertEqual(len(validate), 0)

    def test_length(self):
        validate = Validator().validate({
            'json': 'hey'
        }, length(['json'], min=1, max=10))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'json': 'hey'
        }, length(['json'], '1..10'))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'json': 'this is a really long string'
        }, length(['json'], min=1, max=10))

        self.assertEqual(
            validate, {'json': ['json length must be between 1 and 10']})

    def test_string(self):
        validate = Validator().validate({
            'text': 'hey'
        }, string(['text']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': 1
        }, string(['text']))

        self.assertEqual(validate, {'text': ['text must be a string']})

    def test_none(self):
        validate = Validator().validate({
            'text': None
        }, none(['text']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': 1
        }, none(['text']))

        self.assertEqual(validate, {'text': ['text must be None']})

    def test_equals(self):
        validate = Validator().validate({
            'text': 'test1'
        }, equals(['text'], 'test1'))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': 'test2'
        }, equals(['text'], 'test1'))

        self.assertEqual(validate, {'text': ['text must be equal to test1']})

    def test_truthy(self):
        validate = Validator().validate({
            'text': 'value'
        }, truthy(['text']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': 1
        }, truthy(['text']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': False
        }, truthy(['text']))

        self.assertEqual(validate, {'text': ['text must be a truthy value']})

    def test_in_range(self):
        validate = Validator().validate({
            'text': 52
        }, in_range(['text'], min=25, max=72))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': 101
        }, in_range(['text'], min=25, max=72))

        self.assertEqual(
            validate, {'text': ['text must be between 25 and 72']})

    def test_greater_than(self):
        validate = Validator().validate({
            'text': 52
        }, greater_than(['text'], 25))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': 101
        }, greater_than(['text'], 150))

        self.assertEqual(validate, {'text': ['text must be greater than 150']})

    def test_less_than(self):
        validate = Validator().validate({
            'text': 10
        }, less_than(['text'], 25))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'text': 101
        }, less_than(['text'], 75))

        self.assertEqual(validate, {'text': ['text must be less than 75']})

    def test_isnt(self):
        validate = Validator().validate({
            'test': 50
        }, isnt(
            in_range(['test'], min=10, max=20)
        )
        )

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'test': 15
        }, isnt(
            in_range(['test'], min=10, max=20))
        )

        self.assertEqual(
            validate, {'test': ['test must not be between 10 and 20']})

    def test_isnt_equals(self):
        validate = Validator().validate({
            'test': 'test'
        }, isnt(
            equals(['test'], 'test'),
            length(['test'], min=10, max=20)
        )
        )

        self.assertEqual(
            validate, {'test': ['test must not be equal to test']})

    def test_contains(self):
        validate = Validator().validate({
            'test': 'this is a sentence'
        }, contains(['test'], 'this'))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'test': 'this is a not sentence'
        }, contains(['test'], 'test'))

        self.assertEqual(validate, {'test': ['test must contain test']})

    def test_is_in(self):
        validate = Validator().validate({
            'test': 1
        }, is_in(['test'], [1, 2, 3]))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'test': 1
        }, is_in(['test'], [4, 2, 3]))

        self.assertEqual(
            validate, {'test': ['test must contain an element in [4, 2, 3]']})


class TestDotNotationValidation(unittest.TestCase):

    def setUp(self):
        pass

    def test_dot_required(self):
        validate = Validator().validate({
            'user': {
                'email': 'user@example.com'
            }
        }, required(['user.id']))

        self.assertEqual(validate, {'user.id': ['user.id is required']})

        validate = Validator().validate({
            'user': {
                'id': 1
            }
        }, required(['user.id']))

        self.assertEqual(len(validate), 0)

    def test_dot_numeric(self):
        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com'
            }
        }, numeric(['user.id']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com'
            }
        }, numeric(['user.email']))

        self.assertEqual(
            validate, {'user.email': ['user.email must be a numeric']})

    def test_dot_several_tests(self):
        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com'
            }
        }, required(['user.id', 'user.email']), numeric(['user.id']))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com'
            }
        }, required(['user.id', 'user.email']), numeric(['user.email']))

        self.assertEqual(
            validate, {'user.email': ['user.email must be a numeric']})

    def test_dot_json(self):
        validate = Validator().validate({
            'user': {
                'id': 'hey',
                'email': 'user@example.com'
            }
        }, vjson(['user.id']))

        self.assertEqual(validate, {'user.id': ['user.id must be json']})

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'payload': json.dumps({'test': 'key'})
            }
        }, vjson(['user.payload']))

        self.assertEqual(len(validate), 0)

    def test_dot_length(self):
        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com'
            }
        }, length(['user.id'], min=1, max=10))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'description': 'this is a really long description'
            }
        }, length(['user.id'], '1..10'))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'description': 'this is a really long description'
            }
        }, length(['user.description'], min=1, max=10))

        self.assertEqual(validate, {'user.description': [
                         'user.description length must be between 1 and 10']})

    def test_dot_in_range(self):
        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'age': 25
            }
        }, in_range(['user.age'], min=25, max=72))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'age': 25
            }
        }, in_range(['user.age'], min=27, max=72))

        self.assertEqual(
            validate, {'user.age': ['user.age must be between 27 and 72']})

    def test_dot_equals(self):
        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'age': 25
            }
        }, equals(['user.age'], 25))

        self.assertEqual(len(validate), 0)

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'age': 25
            }
        }, equals(['user.age'], 'test1'))

        self.assertEqual(
            validate, {'user.age': ['user.age must be equal to test1']})

    def test_dot_error_message_required(self):
        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com',
                'age': 25
            }
        }, required(['user.description'], messages={
            'user.description': 'You are missing a description'
        }))

        self.assertEqual(validate, {'user.description': [
                         'You are missing a description']})

        validate = Validator().validate({
            'user': {
                'id': 1,
                'email': 'user@example.com'
            }
        }, required(['user.id', 'user.email', 'user.age'], messages={
            'user.age': 'You are missing a user age'
        }))

        self.assertEqual(
            validate, {'user.age': ['You are missing a user age']})


class TestValidationFactory(unittest.TestCase):

    def test_can_register(self):
        factory = ValidationFactory()
        factory.register(required)
        self.assertEqual(factory.registry['required'], required)


class TestValidationProvider(unittest.TestCase):

    def setUp(self):
        from masonite.request import Request
        self.app = App()
        self.app.bind('Request', Request().load_app(self.app))
        self.provider = ValidationProvider().load_app(self.app)
        self.provider.register()
        self.app.resolve(self.provider.boot)

    def test_loaded_validator_class(self):
        self.assertIsInstance(self.app.make(Validator), Validator)

    def test_loaded_registry(self):
        self.assertTrue(self.app.make(Validator).numeric)

    def test_request_validation(self):
        request = self.app.make('Request')
        validate = self.app.make('Validator')
        print('validate is', validate)

        request.request_variables = {
            'id': 1,
            'name': 'Joe'
        }

        validated = request.validate(
            validate.required(['id', 'name'])
        )

        self.assertEqual(len(validated), 0)

        validated = request.validate(
            validate.required(['user'])
        )

        self.assertEqual(validated, {'user': ['user is required']})

    def test_request_validation_redirects_back_with_session(self):
        wsgi = generate_wsgi()
        self.app.bind('Application', self.app)
        self.app.bind('SessionCookieDriver', SessionCookieDriver)
        self.app.bind('Environ', wsgi)

        request = self.app.make('Request')
        request.load_environ(wsgi)

        request.request_variables = {
            'id': 1,
            'name': 'Joe'
        }

        errors = request.validate(
            required('user')
        )

        request.session = SessionManager(self.app).driver('cookie')

        self.assertEqual(request.redirect(
            '/login').with_errors(errors).redirect_url, '/login')
        self.assertEqual(request.redirect(
            '/login').with_errors(errors).session.get('errors'), {'user': ['user is required']})


class MockRuleEnclosure(RuleEnclosure):

    def rules(self):
        return [
            required(['username', 'email']),
            accepted('terms')
        ]


class TestRuleEnclosure(unittest.TestCase):

    def test_enclosure_can_encapsulate_rules(self):
        validate = Validator().validate({
            'username': 'user123',
            'email': 'user@example.com',
            'terms': 'on'
        }, MockRuleEnclosure)

        self.assertEqual(len(validate), 0)
