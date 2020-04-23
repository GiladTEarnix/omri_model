# custom service file

# model_handler.py

"""
ModelHandler defines a base model handler.
"""
import logging
import json
import numpy as np
from collections import OrderedDict

class ModelHandler(object):
	"""
	A base Model handler implementation.
	"""
	import numpy as np
	import json
	def preprocess(self, batch):
		body = json.loads(batch)
		features_dict = OrderedDict(body)
		return features_dict

	def inference(self, model_input):
		return np.asarray(predict(model_input))

	def postprocess(self, inference_output):
		return inference_output

	def handle(self, data, context):
		model_input = self.preprocess(data)
		model_out = self.inference(model_input)
		return self.postprocess(model_out)

	def __init__(self):
		self.error = None
		self._context = None
		self._batch_size = 0
		self.initialized = False

	def initialize(self, context):
		"""
		Initialize model. This will be called during model loading time
		:param context: Initial context contains model server system properties.
		:return:
		"""
		self._context = context
		self._batch_size = context.system_properties["batch_size"]
		self.initialized = True

	def handle(self, data, context):
		"""
		Call preprocess, inference and post-process functions
		:param data: input data
		:param context: mms context
		"""

		model_input = self.preprocess(data)
		model_out = self.inference(model_input)
		return self.postprocess(model_out)

_service = ModelHandler()


def handle(data, context):
	if not _service.initialized:
		_service.initialize(context)

	if data is None:
		return None

	return _service.handle(data, context)