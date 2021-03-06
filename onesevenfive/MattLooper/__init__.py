# by amounra 1020 : http://www.aumhaa.com


from ableton.v2.control_surface.capabilities import *
from .MattLooper import MattLooper

def create_instance(c_instance):
	""" Creates and returns the MonoPedal script """
	return MattLooper(c_instance)


def get_capabilities():
	return {CONTROLLER_ID_KEY: controller_id(vendor_id=2536, product_ids=[115], model_name='aumhaa MattLooper'),
	 PORTS_KEY: [inport(props=[NOTES_CC, SCRIPT, REMOTE]), outport(props=[SCRIPT, REMOTE])]}
