# by amounra 0216 : http://www.aumhaa.com
# written against Live 10.0.5 on 102318

from __future__ import absolute_import, print_function
import Live
import math
import sys
from re import *
from itertools import imap, chain, starmap

from ableton.v2.base import inject, listens, listens_group
from ableton.v2.control_surface import ControlSurface, ControlElement, Layer, Skin, PrioritizedResource, Component, ClipCreator, DeviceBankRegistry
from ableton.v2.control_surface.elements import ButtonMatrixElement, DoublePressElement, MultiElement, DisplayDataSource, SysexElement
from ableton.v2.control_surface.components import ClipSlotComponent, SceneComponent, SessionComponent, TransportComponent, BackgroundComponent, ViewControlComponent, SessionRingComponent, SessionRecordingComponent, SessionNavigationComponent, MixerComponent, PlayableComponent
from ableton.v2.control_surface.components.mixer import SimpleTrackAssigner
from ableton.v2.control_surface.mode import AddLayerMode, ModesComponent, DelayMode
from ableton.v2.control_surface.elements.physical_display import PhysicalDisplayElement
from ableton.v2.control_surface.components.session_recording import *
from ableton.v2.control_surface.percussion_instrument_finder import PercussionInstrumentFinder, find_drum_group_device
from ableton.v2.control_surface.control import PlayableControl, ButtonControl, control_matrix
from ableton.v2.control_surface.elements import PlayheadElement

from aumhaa.v2.base import initialize_debug
from aumhaa.v2.control_surface import SendLividSysexMode, MomentaryBehaviour, ExcludingMomentaryBehaviour, DelayedExcludingMomentaryBehaviour, ShiftedBehaviour, LatchingShiftedBehaviour, FlashingBehaviour
from aumhaa.v2.control_surface.mod_devices import *
from aumhaa.v2.control_surface.mod import *
from aumhaa.v2.control_surface.elements import MonoEncoderElement, MonoBridgeElement, generate_strip_string
from aumhaa.v2.control_surface.elements.mono_button import *
from aumhaa.v2.control_surface.components import MonoDeviceComponent, DeviceNavigator, TranslationComponent, MonoMixerComponent, MonoChannelStripComponent
from aumhaa.v2.control_surface.components.device import DeviceComponent
from aumhaa.v2.control_surface.components.mono_instrument import *
from aumhaa.v2.livid import LividControlSurface, LividSettings, LividRGB
from aumhaa.v2.control_surface.components.fixed_length_recorder import FixedLengthSessionRecordingComponent
from aumhaa.v2.control_surface.components.device import DeviceComponent
from aumhaa.v2.control_surface.components.m4l_interface import M4LInterfaceComponent

from pushbase.auto_arm_component import AutoArmComponent
from pushbase.grid_resolution import GridResolution
from pushbase.drum_group_component import DrumGroupComponent

debug = initialize_debug()

from .Map import *

MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224


def is_device(device):
	return (not device is None and isinstance(device, Live.Device.Device) and hasattr(device, 'name'))


def make_pad_translations(chan):
	return tuple((x%4, int(x/4), x+16, chan) for x in range(16))


def return_empty():
	return []


def make_default_skin():
	return Skin(STEPSEQColors)




class STEPSEQ(ControlSurface):


	_sysex_id = 12
	_alt_sysex_id = 17
	_model_name = 'STEPSEQ'
	_host_name = 'STEPSEQ'
	_version_check = 'b996'
	monomodular = None
	device_provider_class = ModDeviceProvider

	def __init__(self, *a, **k):
		super(STEPSEQ, self).__init__(*a, **k)
		self._skin = Skin(STEPSEQColors)
		with self._component_guard():
			self._setup_controls()
			self._setup_background()
			self._setup_autoarm()
			self._setup_mixer_control()
			self._setup_device_control()
			self._setup_stepsequencer()
			self._setup_main_modes()
		self._on_device_changed.subject = self._device_provider
		self.set_feedback_channels(range(14, 15))
		self._main_modes.selected_mode = 'Main'


	def set_feedback_channels(self, channels, *a, **k):
		super(STEPSEQ, self).set_feedback_channels(channels, *a, **k)


	def _setup_controls(self):
		is_momentary = True
		optimized = True
		resource = PrioritizedResource
		self._encoder = [MonoEncoderElement(msg_type = MIDI_CC_TYPE, channel = ENCODER_CHANNEL, identifier = STEPSEQ_ENCODERS[index], name = 'Encoder_' + str(index), num = index, script = self, mapping_feedback_delay = -1, optimized_send_midi = optimized, resource_type = resource) for index in range(4)]
		self._encoder_button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = ENCODER_CHANNEL, identifier = STEPSEQ_ENCODER_BUTTONS[index], name = 'Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(4)]
		self._encoder_matrix = ButtonMatrixElement(name = 'EncoderMatrix', rows = [self._encoder])
		self._button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = BUTTON_CHANNEL, identifier = STEPSEQ_BUTTONS[index], name = 'Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(8)]
		self._select_button_matrix = ButtonMatrixElement(name = 'SelectButtonMatrix', rows = [self._button])
		self._pad = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = PAD_CHANNEL, identifier = STEPSEQ_PADS[index], name = 'Pad_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(128)]


	def _setup_background(self):
		self._background = BackgroundComponent(name = 'Background')
		#self._background.layer = Layer(priority = 5, matrix = self._base_grid, matrix_CC = self._base_grid_CC, touchpads = self._touchpad_matrix, faders = self._fader_matrix, runners = self._runner_matrix)
		self._background.set_enabled(True)


	def _setup_autoarm(self):
		self._auto_arm = AutoArmComponent(name='Auto_Arm')
		self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
		self._auto_arm._update_notification = lambda: None


	def _setup_mixer_control(self):
		self._session_ring = SessionRingComponent(name = 'Session_Ring', num_tracks = 8, num_scenes = 1)
		self._mixer = MonoMixerComponent(name = 'Mixer', num_returns = 4,tracks_provider = self._session_ring, track_assigner = SimpleTrackAssigner(), invert_mute_feedback = True, auto_name = True, enable_skinning = True, channel_strip_component_type = MonoChannelStripComponent)
		self._mixer.layer = Layer(track_select_buttons = self._select_button_matrix)
		self._mixer.set_enabled(False)


	def _setup_device_control(self):
		self._device_selection_follows_track_selection = True
		self._device = DeviceComponent(name = 'Device_Component', device_bank_registry = DeviceBankRegistry(), device_provider = self._device_provider)
		self._device.layer = Layer(parameter_controls = self._encoder_matrix)
		self._device.set_enabled(False)


	def _setup_stepsequencer(self):
		self._grid_resolution = GridResolution()
		self._c_instance.playhead.enabled = True
		self._playhead_element = PlayheadElement(self._c_instance.playhead)


	def _setup_main_modes(self):
		self._main_modes = ModesComponent(name = 'MainModes')
		self._main_modes.add_mode('disabled', [self._background])
		self._main_modes.add_mode('Main', [self._mixer, self._device])
		self._main_modes.selected_mode = 'disabled'
		self._main_modes.set_enabled(True)


	"""general functionality"""
	def disconnect(self):
		super(STEPSEQ, self).disconnect()


	def _can_auto_arm_track(self, track):
		# routing = track.current_input_routing
		# return routing == 'Ext: All Ins' or routing == 'All Ins' or routing.startswith('S Input')
		return False


	@listens('device')
	def _on_device_changed(self):
		pass


	def _on_selected_track_changed(self):
		super(STEPSEQ, self)._on_selected_track_changed()
		#self._drum_group_finder.device_parent = self.song.veiw.selected_track


	def reset_controlled_track(self, track = None, *a):
		if not track:
			track = self.song.view.selected_track
		self.set_controlled_track(track)


	def set_controlled_track(self, track = None, *a):
		dtrack = track.name if track and hasattr(track, 'name') else track
		#debug('set_controlled_track:', dtrack)
		if isinstance(track, Live.Track.Track):
			super(STEPSEQ, self).set_controlled_track(track)
		else:
			self.release_controlled_track()



#	a
