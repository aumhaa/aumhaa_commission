# by amounra 0319 : http://www.aumhaa.com
# written against Live 10.0.6

from __future__ import absolute_import, print_function
import Live
import time
import math
import sys
from itertools import count
import logging
logger = logging.getLogger(__name__)

from ableton.v2.base import inject, listens, listens_group, inject, nop
from ableton.v2.control_surface import ControlSurface, ControlElement, Layer, Skin, PrioritizedResource, Component, ClipCreator, DeviceBankRegistry
from ableton.v2.control_surface.elements import ButtonMatrixElement, DoublePressElement, MultiElement, DisplayDataSource, SysexElement
from ableton.v2.control_surface.components import ClipSlotComponent, SceneComponent, SessionComponent, TransportComponent, BackgroundComponent, ViewControlComponent, SessionRingComponent, SessionRecordingComponent, SessionNavigationComponent, SessionOverviewComponent, MixerComponent, PlayableComponent
from ableton.v2.control_surface.mode import AddLayerMode, ModesComponent, DelayMode, CompoundMode, _ModeEntry, tomode
from ableton.v2.control_surface.elements.physical_display import PhysicalDisplayElement
from ableton.v2.control_surface.components.session_recording import *
from ableton.v2.control_surface.control import PlayableControl, ButtonControl, control_matrix
from ableton.v2.control_surface.components.scroll import ScrollComponent, Scrollable
from ableton.v2.control_surface.components.view_control import BasicSceneScroller
from ableton.v2.control_surface.percussion_instrument_finder import PercussionInstrumentFinder, find_drum_group_device
from ableton.v2.control_surface.elements import PlayheadElement
from ableton.v2.control_surface.components.mixer import SimpleTrackAssigner

from aumhaa.v2.base import initialize_debug
from aumhaa.v2.control_surface import SendLividSysexMode, MomentaryBehaviour, ExcludingMomentaryBehaviour, DelayedExcludingMomentaryBehaviour, ShiftedBehaviour, LatchingShiftedBehaviour, FlashingBehaviour
from aumhaa.v2.control_surface.mod_devices import *
from aumhaa.v2.control_surface.mod import *
from aumhaa.v2.control_surface.elements import MonoEncoderElement, MonoBridgeElement, generate_strip_string, CodecEncoderElement
from aumhaa.v2.control_surface.elements.mono_button import *
from aumhaa.v2.control_surface.components import DeviceNavigator, TranslationComponent, MonoMixerComponent, ResetSendsComponent, DeviceSelectorComponent, MonoMixerComponent
from aumhaa.v2.control_surface.components.device import DeviceComponent
from aumhaa.v2.control_surface.components.mono_instrument import *
from aumhaa.v2.control_surface.mono_modes import SendLividSysexMode, SendSysexMode, CancellableBehaviourWithRelease, ColoredCancellableBehaviourWithRelease, MomentaryBehaviour, BicoloredMomentaryBehaviour, DefaultedBehaviour
from aumhaa.v2.livid import LividControlSurface, LividSettings, LividRGB
from aumhaa.v2.control_surface.components.fixed_length_recorder import FixedLengthSessionRecordingComponent
from aumhaa.v2.control_surface.components.m4l_interface import M4LInterfaceComponent

from pushbase.auto_arm_component import AutoArmComponent
from pushbase.grid_resolution import GridResolution
from pushbase.drum_group_component import DrumGroupComponent

"""Custom files, overrides, and files from other scripts"""
from _Generic.Devices import *
from .ModDevices import *
from .Map import *

from Livid_CNTRLR_v2.Cntrlr import Cntrlr as Base_Cntrlr, CntrlrSessionNavigationComponent, CntrlrViewControlComponent, CntrlrResetSendsComponent, CntrlrSessionNavigationComponent, CntrlrMonoInstrumentComponent, CntrlrAutoArmComponent, CntrlrDeviceComponent

class SpecialCntrlrMonoInstrumentComponent(CntrlrMonoInstrumentComponent):

	def update(self):
		super(MonoInstrumentComponent, self).update()
		self._main_modes.selected_mode = 'disabled'
		if self.is_enabled():
			new_mode = 'disabled'
			drum_device = find_drum_group_device(self.song.view.selected_track)
			self._drumpad._drumgroup.set_drum_group_device(drum_device)
			cur_track = self.song.view.selected_track
			if cur_track.has_audio_input and cur_track in self.song.visible_tracks:
				new_mode = 'audioloop'
				if self._shifted:
					new_mode += '_shifted'
			elif cur_track.has_midi_input:
				scale, mode = self._scale_offset_component.value, self._mode_component.value
				new_mode = get_instrument_type(cur_track, scale, self._settings)
				if mode is 'split':
					new_mode += '_split'
				elif mode is 'seq':
					new_mode +=  '_sequencer'
				if self._shifted:
					new_mode += '_shifted'
				if self._matrix_modes.selected_mode is 'enabled':
					new_mode += '_session'
				self._script.set_feedback_channels([self._scale_offset_component.channel])
				self._script.set_controlled_track(self.song.view.selected_track)
			if new_mode in self._main_modes._mode_map or new_mode is None:
				self._main_modes.selected_mode = new_mode
				#self._script.set_controlled_track(None)  //commented this to get note feedback working in sequencer drumpad component
			else:
				self._main_modes.selected_mode = 'disabled'
				self._script.set_controlled_track(None)
			debug('monoInstrument mode is:', self._main_modes.selected_mode, '  inst:', self.is_enabled(), '  modes:', self._main_modes.is_enabled(), '   key:', self._keypad.is_enabled(), '   drum:', self._drumpad.is_enabled())





"""
Some wierd hacks that had to happen:

	Set the feedback channels via a ControlSurfaceComponent override (top level)
	 	because note feedback wasn't working
	Also added a listener for view.detail_clip @ _on_detail_clip_changed() to keep
		refreshing the task in LoopSelector so that it will keep following (wasn't
		working in the original script)
	Encoder buttons are still not quite right, they need the correct sysex call
		to happen in _define_sysex()

Other general work that happened in here:
	Added 2nd Translation layer to catch all Controls
	Created SpecialSessionComponent to deal with scene launch(in case it turns out
		that client wants to launch the NEXT scene instead of the current one) and
		to override stop_all_clips_button coloring.
	Added some custom coloring to Map file for encoder_buttons, step sequencer, etc.
"""

#debug = initialize_debug()

def log_flattened_arguments(*a, **k):
	args = ''
	for item in a:
		args = args + str(item) + ' '
	logger.info(args)


debug = log_flattened_arguments


def enumerate_track_device(track):
	devices = []
	if hasattr(track, 'devices'):
		for device in track.devices:
			devices.append(device)
			if device.can_have_chains:
				for chain in device.chains:
					for chain_device in enumerate_track_device(chain):
						devices.append(chain_device)
	return devices




class SpecialSessionComponent(SessionComponent):

	fire_scene_button = ButtonControl()

	def _update_stop_all_clips_button(self):
		if self.is_enabled():
			button = self._stop_all_button
			if button:
				button.set_light('Session.StopClipTriggered' if button.is_pressed() else 'Session.StopClip')

	@fire_scene_button.pressed
	def fire_scene_button(self, button):
		debug('fire_scene_button.value:', button)
		#self._selected_scene.


class SelectedSceneScroller(Scrollable):

	def __init__(self, song = None, *a, **k):
		self.song = song
		super(SelectedSceneScroller, self).__init__(*a, **k)

	def can_scroll_up(self):
		view = self.song.view
		scene = view.selected_scene
		scenes = list(self.song.scenes)
		scene_index = scenes.index(scene)
		return scene_index < (len(scenes) - 1)

	def can_scroll_down(self):
		view = self.song.view
		scene = view.selected_scene
		scenes = list(self.song.scenes)
		scene_index = scenes.index(scene)
		return scene_index > 0

	def scroll_up(self):
		view = self.song.view
		scene = view.selected_scene
		scenes = list(self.song.scenes)
		scene_index = scenes.index(scene)
		if self.can_scroll_up():
			try:
				view.selected_scene = scenes[scene_index + 1]
			except:
				debug('couldnt scroll up')

	def scroll_down(self):
		view = self.song.view
		scene = view.selected_scene
		scenes = list(self.song.scenes)
		scene_index = scenes.index(scene)
		if self.can_scroll_down:
			try:
				view.selected_scene = scenes[scene_index - 1]
			except:
				debug('couldnt scroll down')




class Cntrlr(Base_Cntrlr):


	def __init__(self, *a, **k):
		super(Cntrlr, self).__init__(*a, **k)
		self._skin = Skin(CntrlrColors)
		for button in self._grid:
			button._skin = self._skin
		for button in self._button:
			button._skin = self._skin
		for button in self._encoder_button:
			button._skin = self._skin
		self._main_modes.selected_mode = 'FrederikMode'
		self._on_detail_clip_changed.subject = self.song.view
		self.set_feedback_channels(range(0, 15))
		#self.schedule_message(10, self.initialize_frederik_mode)

	def initialize_frederik_mode(self):
		self._main_modes.selected_mode = "FrederikMode"

	def _open_log(self):
		self.log_message("<<<<<<<<<<<<<<<<<<<<= " + str(self._host_name) + " for Frederik Poisquet " + str(self._version_check) + " log opened =>>>>>>>>>>>>>>>>>>>")
		self.show_message(str(self._host_name) + ' Control Surface Loaded')

	def _initialize_script(self):
		super(Cntrlr, self)._initialize_script()
		self._connected = True
		self._main_modes.selected_mode = 'FrederikMode'
		self._main_modes.set_enabled(True)
		self._instrument.set_enabled(True)
		self._main_modes.selected_mode = 'disabled'
		self._main_modes.selected_mode = 'FrederikMode'
		#self._session_ring._update_highlight()

	def _define_sysex(self):
		self.encoder_navigation_on = SendLividSysexMode(livid_settings = self._livid_settings, call = 'set_encoder_encosion_mode', message = [0, 0, 0, 0])

	def _setup_session_control(self):
		self._session_ring = SessionRingComponent(num_tracks = 4, num_scenes = 4)
		self._session_ring.set_enabled(False)

		self._session_navigation = CntrlrSessionNavigationComponent(name = 'SessionNavigation', session_ring = self._session_ring)

		self._session_navigation._vertical_banking.scroll_up_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._vertical_banking.scroll_down_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._horizontal_banking.scroll_up_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._horizontal_banking.scroll_down_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._vertical_paginator.scroll_up_button.color = 'Session.PageNavigationButtonOn'
		self._session_navigation._vertical_paginator.scroll_down_button.color = 'Session.PageNavigationButtonOn'
		self._session_navigation._horizontal_paginator.scroll_up_button.color = 'Session.PageNavigationButtonOn'
		self._session_navigation._horizontal_paginator.scroll_down_button.color = 'Session.PageNavigationButtonOn'

		self._session_navigation.bank_dial_layer = AddLayerMode(self._session_navigation, Layer(priority = 5,))
		self._session_navigation.nav_dial_layer = AddLayerMode(self._session_navigation, Layer(priority = 5,))
		self._session_navigation.select_dial_layer = AddLayerMode(self._session_navigation, Layer(priority = 5))
		self._session_navigation.nav_layer = AddLayerMode(self._session_navigation, Layer(priority = 5, ))

		self._session_navigation.set_enabled(False)

		self._session = SessionComponent(session_ring = self._session_ring, auto_name = True)
		hasattr(self._session, '_enable_skinning') and self._session._enable_skinning()
		self._session.clip_launch_layer = LayerMode(self._session, Layer(priority = 5,stop_all_clips_button = self._button[29]))
		self._session.stop_all_clips_layer = AddLayerMode(self._session, Layer(priority = 6, stop_all_clips_button = self._button[29]))
		self._session.scene_launch_layer = AddLayerMode(self._session._selected_scene, Layer(priority = 5,stop_all_clips_button = self._button[29]))
		self._session.set_enabled(False)

		self._session_zoom = SessionOverviewComponent(name = 'SessionZoom', session_ring = self._session_ring, enable_skinning = True)
		self._session_zoom.layer = Layer(priority = 5,)
		self._session_zoom.set_enabled(False)

		self._session_ring2 = SessionRingComponent(num_tracks = 4, num_scenes = 1, set_session_highlight = nop)
		self._session_ring2.set_enabled(False)

		self._session2 = SpecialSessionComponent(session_ring = self._session_ring2, auto_name = True)
		self._session2._selected_scene.layer = Layer(priority = 5, launch_button = self._button[28])
		self._session2.layer = Layer(priority = 5, stop_all_clips_button = self._button[29]) #, fire_scene_button = self._button[28])

		self._scene_scroller = ScrollComponent(scrollable = SelectedSceneScroller(song = self.song))
		self._scene_scroller.layer = Layer(priority = 5, scroll_up_button = self._button[31], scroll_down_button = self._button[30])
		self._scene_scroller.set_enabled(False)

	def _setup_mixer_control(self):
		super(Cntrlr, self)._setup_mixer_control()
		self._mixer.main_faders_layer = AddLayerMode(self._mixer, Layer(priority = 5,))
		self._mixer.main_buttons_layer = AddLayerMode(self._mixer, Layer(priority = 5,))
		self._mixer.solo_buttons_layer = AddLayerMode(self._mixer, Layer(priority = 5,))
		self._mixer.shifted_buttons_layer = AddLayerMode(self._mixer, Layer(priority = 5,))
		self._mixer.main_knobs_layer = AddLayerMode(self._mixer, Layer(priority = 5,))
		self._mixer.master_fader_layer = AddLayerMode(self._mixer.master_strip(), Layer(priority = 5,))
		self._mixer.instrument_buttons_layer = AddLayerMode(self._mixer, Layer(priority = 5,))
		self._mixer.stop_layer = AddLayerMode(self._mixer, Layer(priority = 5,))
		self._mixer.set_enabled(False)

	def _setup_transport_control(self):
		super(Cntrlr, self)._setup_transport_control()
		self._transport.layer = Layer(priority = 5,)

	def _setup_session_recording_component(self):
		super(Cntrlr, self)._setup_session_recording_component()
		self._recorder.main_layer = AddLayerMode(self._recorder, Layer(priority = 5,))
		self._recorder.shift_layer = AddLayerMode(self._recorder, Layer(priority = 5,))
		self._recorder.set_enabled(False)

	def _setup_device_control(self):
		super(Cntrlr, self)._setup_device_control()
		self._device.dial_layer = AddLayerMode(self._device, Layer(priority = 5,))
		self._device.button_layer = AddLayerMode(self._device, Layer(priority = 5,))
		self._device_navigator.select_dial_layer = AddLayerMode(self._device_navigator, Layer(priority = 5,))
		self._device_navigator.main_layer = AddLayerMode(self._device_navigator, Layer(priority = 5,))

	def _setup_device_selector(self):
		super(Cntrlr, self)._setup_device_selector()
		self._device_selector.select_layer = AddLayerMode(self._device_selector, Layer(priority = 6,))
		self._device_selector.assign_layer = AddLayerMode(self._device_selector, Layer(priority = 7,))

	def _setup_viewcontrol(self):
		super(Cntrlr, self)._setup_viewcontrol()
		self._view_control.main_layer = AddLayerMode(self._view_control, Layer(priority = 6,))

	def _update_modswitcher(self):
		debug('update modswitcher', self.modhandler.active_mod())
		self._modswitcher.selected_mode = 'instrument'

	def _setup_translations(self):
		super(Cntrlr, self)._setup_translations()
		self._setup_translations2()

	def _setup_translations2(self):
		self._translated_controls2 = self._knobs + self._button[16:28] + self._fader + self._encoder + self._encoder_button

		self._translations2 = TranslationComponent(self._translated_controls2, user_channel_offset = 15, channel = 15)
		self._translations2.name = 'TranslationComponent'
		self._translations2.layer = Layer(priority = 10,)
		self._translations2.set_enabled(True)

	def _setup_instrument(self):
		super(Cntrlr, self)._setup_instrument()
		self._instrument._main_modes._mode_map['audioloop'] = _ModeEntry(mode=tomode(self._audioloop_pass), cycle_mode_button_color=None, behaviour=self._instrument._main_modes.default_behaviour, groups=set())
		self._instrument.shift_button_layer = AddLayerMode(self._instrument, Layer(priority = 5,))
		self._instrument._drumpad._step_sequencer._loop_selector._follow_task.restart()
		self._instrument._drumpad._step_sequencer._playhead_component._feedback_channels = range(16)

	def _setup_instrument(self):
		self._grid_resolution = self.register_disconnectable(GridResolution())
		self._c_instance.playhead.enabled = True
		self._playhead_element = PlayheadElement(self._c_instance.playhead)

		self._drum_group_finder = PercussionInstrumentFinder(device_parent=self.song.view.selected_track)

		self._instrument = SpecialCntrlrMonoInstrumentComponent(name = 'InstrumentComponent', is_enabled = True, script = self, skin = self._skin, grid_resolution = self._grid_resolution, drum_group_finder = self._drum_group_finder, parent_task_group = self._task_group, settings = DEFAULT_INSTRUMENT_SETTINGS, device_provider = self._device_provider)
		self._instrument.shift_button_layer = AddLayerMode(self._instrument, Layer(priority = 5,))
		self._instrument.audioloop_layer = AddLayerMode(self._instrument, Layer(priority = 5, loop_selector_matrix = self._key_matrix.submatrix[:, 0]))

		self._instrument.keypad_shift_layer = AddLayerMode(self._instrument, Layer(priority = 5,
									scale_up_button = self._button[13],
									scale_down_button = self._button[12],
									offset_up_button = self._button[11],
									offset_down_button = self._button[10],
									vertical_offset_up_button = self._button[9],
									vertical_offset_down_button = self._button[8],
									split_button = self._button[14],
									sequencer_button = self._button[15]))

		self._instrument.drumpad_shift_layer = AddLayerMode(self._instrument, Layer(priority = 5,
									scale_up_button = self._button[13],
									scale_down_button = self._button[12],
									drum_offset_up_button = self._button[11],
									drum_offset_down_button = self._button[10],
									drumpad_mute_button = self._button[9],
									drumpad_solo_button = self._button[8],
									split_button = self._button[14],
									sequencer_button = self._button[15]))

		self._instrument._keypad.sequencer_layer = LayerMode(self._instrument._keypad, Layer(priority = 5,
																										playhead = self._playhead_element,
		 																								keypad_matrix = self._matrix.submatrix[:,:],
																										sequencer_matrix = self._key_matrix.submatrix[:,0]))
		self._instrument._keypad.split_layer = LayerMode(self._instrument._keypad, Layer(priority = 5,
																										keypad_matrix = self._matrix.submatrix[:,:],
																										split_matrix = self._key_matrix.submatrix[:14,0]))
		self._instrument._keypad.sequencer_shift_layer = LayerMode(self._instrument._keypad, Layer(priority = 5,
																										keypad_select_matrix = self._matrix.submatrix[:,:],
																										loop_selector_matrix = self._key_matrix.submatrix[:8, 0],
																										quantization_buttons = self._key_matrix.submatrix[:8, 1],))
																										#follow_button = self._button[23]))
		self._instrument._keypad.sequencer_session_layer = LayerMode(self._instrument._keypad, Layer(priority = 5,
																										playhead = self._playhead_element,
																										sequencer_matrix = self._key_matrix.submatrix[:,:1]))
		self._instrument._keypad.split_session_layer = LayerMode(self._instrument._keypad, Layer(priority = 5,
																										split_matrix = self._key_matrix.submatrix[:16,:1]))
		self._instrument._keypad.sequencer_session_shift_layer = LayerMode(self._instrument._keypad, Layer(priority = 5,
																										loop_selector_matrix = self._key_matrix.submatrix[:8, :1],
																										quantization_buttons = self._key_matrix.submatrix[:7, 1:],))
																										#follow_button = self._button[23]))

		self._instrument._drumpad.sequencer_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5,
																										playhead = self._playhead_element,
																										drumpad_matrix = self._matrix.submatrix[:,:],
																										sequencer_matrix = self._key_matrix.submatrix[:,:1]))
		self._instrument._drumpad.split_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5,
																										drumpad_matrix = self._matrix.submatrix[:,:],
																										split_matrix = self._key_matrix.submatrix[:16,:1]))
		self._instrument._drumpad.sequencer_shift_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5,
																										drumpad_select_matrix = self._matrix.submatrix[:,:],
																										loop_selector_matrix = self._key_matrix.submatrix[:8, :1],
																										quantization_buttons = self._key_matrix.submatrix[:7, 1:],))
																										#follow_button = self._button[23]))
		self._instrument._drumpad.sequencer_session_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5,
																										playhead = self._playhead_element,
																										sequencer_matrix = self._key_matrix.submatrix[:,:1]))
		self._instrument._drumpad.split_session_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5,
																										split_matrix = self._key_matrix.submatrix[:16,:1]))
		self._instrument._drumpad.sequencer_session_shift_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5,
																										loop_selector_matrix = self._key_matrix.submatrix[:8, :1],
																										quantization_buttons = self._key_matrix.submatrix[:8, 1:],))
																										#follow_button = self._button[23]))

		#self._instrument.set_session_mode_button(self._button[30])

	"""
	def _setup_modes(self):
		super(Cntrlr, self)._setup_modes()
		self._main_modes.add_mode('FrederikMode', [self._instrument,
													self._scene_scroller,
													self._session2,])
		self._main_modes.layer = Layer(priority = 5)
		self._main_modes.selected_mode = 'FrederikMode'
		self._main_modes.set_enabled(True)

		self._test.subject = self._instrument._main_modes
	"""

	def _setup_modes(self):

		common = CompoundMode(self._mixer,
									self._session_ring)
		main_buttons=CompoundMode(self._mixer.main_buttons_layer,
									self._transport,
									self._recorder,
									self._recorder.main_layer,
									self._device,
									self._device.button_layer)
		shifted_main_buttons=CompoundMode(self._mixer.solo_buttons_layer,
									self._recorder,
									self._recorder.shift_layer,
									self._session,
									self._session.scene_launch_layer,
									self._device,
									self._device.button_layer)
		main_faders=CompoundMode(self._mixer.main_faders_layer,
									self._mixer.master_fader_layer)
		main_dials=CompoundMode(self._view_control,
									self._view_control.main_layer,
									self._device,
									self._device.dial_layer,
									self._device_navigator.select_dial_layer,
									self.encoder_navigation_on)
		shifted_dials=CompoundMode(self._session_navigation,
									self._session_navigation.nav_dial_layer,
									self._device,
									self._device.dial_layer,
									self._device_navigator.select_dial_layer,
									self.encoder_navigation_on)

		self._modalt_mode = ModesComponent(name = 'ModAltMode')
		self._modalt_mode.add_mode('disabled', None)
		self._modalt_mode.add_mode('enabled', [tuple([self._enable_mod_alt, self._disable_mod_alt])], behaviour = CancellableBehaviourWithRelease(), cycle_mode_button_color = 'Mod.AltOn')
		self._modalt_mode.selected_mode = 'disabled'
		self._modalt_mode.set_enabled(False)
		self._modalt_mode.layer = Layer(priority = 5, enabled_button = self._encoder_button[1])

		self._modswitcher = ModesComponent(name = 'ModSwitcher')
		self._modswitcher.add_mode('mod', [self.modhandler, self._modalt_mode, main_faders, self._mixer.main_knobs_layer, self._device, self._device.dial_layer, self._device_navigator.main_layer,	main_dials, DelayMode(self.modhandler.update, delay = .5, parent_task_group = self._task_group)])
		self._modswitcher.add_mode('instrument', [self._instrument, self._instrument.shift_button_layer, main_buttons, main_faders, self._mixer.main_knobs_layer, self._device, self._device.dial_layer, self._device.button_layer, self._device_navigator.main_layer,]) #self._instrument.shift_button_layer, self._optional_translations])
		self._modswitcher.selected_mode = 'instrument'
		self._modswitcher.set_enabled(False)

		self._instrument._main_modes = ModesComponent(parent = self._instrument, name = 'InstrumentModes')
		self._instrument._main_modes.add_mode('disabled', [])
		self._instrument._main_modes.add_mode('drumpad', [self._instrument._drumpad.sequencer_layer,
																					main_buttons,
																					main_dials])
		self._instrument._main_modes.add_mode('drumpad_split', [self._instrument._drumpad.split_layer,
																					self._instrument._selected_session,
																					main_buttons,
																					main_dials])
		self._instrument._main_modes.add_mode('drumpad_sequencer', [self._instrument._drumpad.sequencer_layer,
																					main_buttons,
																					main_dials])
		self._instrument._main_modes.add_mode('drumpad_shifted', [])
		self._instrument._main_modes.add_mode('drumpad_split_shifted', [])
		self._instrument._main_modes.add_mode('drumpad_sequencer_shifted', [])
		self._instrument._main_modes.add_mode('keypad', [self._instrument._keypad.sequencer_layer,
																					main_buttons,
																					main_dials])
		self._instrument._main_modes.add_mode('keypad_split', [self._instrument._keypad.split_layer,
																					self._instrument._selected_session,
																					main_buttons,
																					main_dials])
		self._instrument._main_modes.add_mode('keypad_sequencer', [self._instrument._keypad.sequencer_layer,
																					main_buttons,
																					main_dials])
		self._instrument._main_modes.add_mode('keypad_shifted', [])
		self._instrument._main_modes.add_mode('keypad_split_shifted', [])
		self._instrument._main_modes.add_mode('keypad_sequencer_shifted', [])
		self._instrument._main_modes.add_mode('drumpad_session', [])
		self._instrument._main_modes.add_mode('drumpad_split_session', [])
		self._instrument._main_modes.add_mode('drumpad_sequencer_session', [])
		self._instrument._main_modes.add_mode('drumpad_shifted_session', [])
		self._instrument._main_modes.add_mode('drumpad_split_shifted_session', [])
		self._instrument._main_modes.add_mode('drumpad_sequencer_shifted_session', [])
		self._instrument._main_modes.add_mode('keypad_session', [])
		self._instrument._main_modes.add_mode('keypad_split_session', [])
		self._instrument._main_modes.add_mode('keypad_sequencer_session', [])
		self._instrument._main_modes.add_mode('keypad_shifted_session', [])
		self._instrument._main_modes.add_mode('keypad_split_shifted_session', [])
		self._instrument._main_modes.add_mode('keypad_sequencer_shifted_session', [])

		self._instrument._main_modes.add_mode('audioloop', [self._instrument.audioloop_layer,])
		self._instrument._main_modes.add_mode('audioloop_shifted', [self._instrument.audioloop_layer,])

		self._instrument._main_modes.selected_mode = 'disabled'
		self._instrument.set_enabled(True)

		self._main_modes = ModesComponent(name = 'MainModes')
		self._main_modes.add_mode('disabled', [self._background])
		self._main_modes.add_mode('MixMode', [common,
													self._instrument,
													self._instrument.shift_button_layer,
													self._mixer,
													main_faders,
													self._mixer.main_knobs_layer,
													self._device,
													self._device_navigator,
													self._device_navigator.main_layer,])
		self._main_modes.add_mode('ModSwitcher', [common,
													main_faders,
													main_dials,
													self._mixer.main_knobs_layer,
													self._session_navigation.select_dial_layer,
													self._view_control,
													self._view_control.main_layer,
													self._device_navigator.select_dial_layer,
													self.encoder_navigation_on, self._modswitcher,
													DelayMode(self._update_modswitcher, delay = .1)],
													behaviour = ColoredCancellableBehaviourWithRelease(color = 'ModeButtons.ModSwitcher', off_color = 'ModeButtons.ModSwitcherDisabled'))
		self._main_modes.add_mode('Translations', [common,
													main_faders,
													main_dials,
													self._mixer.main_knobs_layer,
													DelayMode(self._translations, delay = .1),
													DelayMode(self._translations.selector_layer, delay = .3)],
													behaviour = DefaultedBehaviour(default_mode = 'MixMode', color = 'ModeButtons.Translations', off_color = 'ModeButtons.TranslationsDisabled'))
		self._main_modes.add_mode('DeviceSelector', [common,
													self._device_selector,
													DelayMode(self._device_selector.select_layer, delay = .1),
													DelayMode(self.modhandler.lock_layer, delay = .1),
													DelayMode(self._device_selector.assign_layer, delay = .5),
													main_buttons,
													main_dials,
													main_faders,
													self._mixer.main_knobs_layer,
													self._device,
													self._device_navigator],
													behaviour = ColoredCancellableBehaviourWithRelease(color = 'ModeButtons.DeviceSelector', off_color = 'ModeButtons.DeviceSelectorDisabled'))
		self._main_modes.add_mode('FrederikMode', [self._instrument,
													self._scene_scroller,
													self._session2,
													self._translations2])
		self._main_modes.layer = Layer(priority = 5)
		self._main_modes.selected_mode = 'FrederikMode'
		self._main_modes.set_enabled(True)

		#self._test.subject = self._instrument._main_modes


	@listens(u'detail_clip')
	def _on_detail_clip_changed(self):
		self._instrument._drumpad._step_sequencer._loop_selector._follow_task.restart()


	def set_feedback_channels(self, channels):
		debug('set_feedback_channels:', channels)
		super(Cntrlr, self).set_feedback_channels(range(15))



#	a
