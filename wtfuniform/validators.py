#!/usr/bin/env python
# coding=utf8

import json
import re

import wtforms.validators
from wtforms.validators import *

_validator_prefix = 'wtfuf_'

def _python_to_js_regex(regex):
	flags = []
	if regex.flags | re.I: flags.append('i')
	if regex.flags | re.M: flags.append('m')

	return 'new RegExp(%s, %s)' % (json.dumps(regex.pattern), json.dumps(''.join(flags)))


class JSValidatorMixin(object):
	def js_validator_name(self, field):
		return _validator_prefix + self.__class__.__name__


class RegexJavascriptMixin(JSValidatorMixin):
	def js_validator(self, form, field):
		return """function(field, caption) {
			var re = %s;
			if (field.val().match(re) || field.val() == '') {
				return true;
			}
			return %s;
		}""" % (_python_to_js_regex(self.regex), json.dumps(field.gettext(self.message or getattr(self, 'js_message', 'Invalid input.'))))



class EqualTo(wtforms.validators.EqualTo, JSValidatorMixin):
	def js_validator(self, form, field):
		other = form[self.fieldname]

		return """function(field, caption) {
			var other = $('#%s');
			if (field.val() == other.val() || field.val() == '') {
				return true;
			}
			return %s;
		}""" % (other.id, json.dumps(field.gettext(self.message or '%s must match %s.' % (other.label.text, field.label.text))))


class Email(wtforms.validators.Email, RegexJavascriptMixin):
	js_message = 'Invalid email address.'


class IPAddress(wtforms.validators.IPAddress, RegexJavascriptMixin):
	js_message = 'Invalid IP address.'


# length is handled natively by uni-form
# number range is handled natively by uni-form as well
# support for Optional is missing


class URL(wtforms.validators.URL, RegexJavascriptMixin):
	js_message = 'Invalid URL.'


class AnyOf(wtforms.validators.AnyOf, JSValidatorMixin):
	def js_validator(self, form, field):
		msg = field.gettext(self.message or 'Invalid value, must be one of: %(values)s.') % {'values': self.values_formatter(self.values)}

		return """function(field, caption) {
			var validValues = %s;

			if ($.inArray(field.val(), validValues) > -1 || field.val() == '') {
				return true;
			}
			return %s;
		}""" % (json.dumps(self.values), json.dumps(msg))


class NoneOf(wtforms.validators.AnyOf, JSValidatorMixin):
	def js_validator(self, form, field):
		msg = field.gettext(self.message or 'Invalid value, can\'t be any of: %(values)s.') % {'values': self.values_formatter(self.values)}

		return """function(field, caption) {
			var validValues = %s;

			if ($.inArray(field.val(), validValues) == -1 || field.val() == '') {
				return true;
			}
			return %s;
		}""" % (json.dumps(self.values), json.dumps(msg))


class Regexp(wtforms.validators.Regexp, RegexJavascriptMixin):
	pass
