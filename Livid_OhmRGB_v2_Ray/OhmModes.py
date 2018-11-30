# by amounra 1216 : http://www.aumhaa.com
# written against Live 10.0.5 on 112718

from __future__ import absolute_import, print_function
import Live
import math
import sys
from re import *
from itertools import imap, chain, starmap, izip, izip_longest

from ableton.v2.base import inject, listens, listens_group
from ableton.v2.control_surface import ControlSurface, ControlElement, Layer, Skin, PrioritizedResource, Component, ClipCreator, DeviceBankRegistry
from ableton.v2.control_surface.elements import EncoderElement, ButtonMatrixElement, DoublePressElement, MultiElement, DisplayDataSource, SysexElement
from ableton.v2.control_surface.components import DrumGroupComponent, SessionOverviewComponent, ClipSlotComponent, SceneComponent, SessionComponent, TransportComponent, BackgroundComponent, ViewControlComponent, SessionRingComponent, SessionRecordingComponent, SessionNavigationComponent, MixerComponent, PlayableComponent
from ableton.v2.control_surface.components.mixer import SimpleTrackAssigner
from ableton.v2.control_surface.mode import AddLayerMode, ModesComponent, DelayMode
from ableton.v2.control_surface.elements.physical_display import PhysicalDisplayElement
from ableton.v2.control_surface.components.session_recording import *

from ableton.v2.control_surface.control import PlayableControl, ButtonControl, control_matrix
from ableton.v2.control_surface.percussion_instrument_finder import PercussionInstrumentFinder, find_drum_group_device
from ableton.v2.control_surface.elements import PlayheadElement

from aumhaa.v2.base import initialize_debug
from aumhaa.v2.control_surface import SendLividSysexMode, MomentaryBehaviour, ExcludingMomentaryBehaviour, DelayedExcludingMomentaryBehaviour, ShiftedBehaviour, LatchingShiftedBehaviour, FlashingBehaviour, DefaultedBehaviour, CancellableBehaviourWithRelease
from aumhaa.v2.control_surface.mod_devices import *
from aumhaa.v2.control_surface.mod import *
from aumhaa.v2.control_surface.elements import MonoEncoderElement, MonoBridgeElement, generate_strip_string
from aumhaa.v2.control_surface.elements.mono_button import *
from aumhaa.v2.control_surface.components import MonoKeyGroupComponent, MonoDrumGroupComponent, MonoDeviceComponent, DeviceNavigator, TranslationComponent, MonoMixerComponent
from aumhaa.v2.control_surface.components.device import DeviceComponent
from aumhaa.v2.control_surface.components.mono_instrument import *
from aumhaa.v2.livid import LividControlSurface, LividSettings, LividRGB
from aumhaa.v2.control_surface.components.fixed_length_recorder import FixedLengthSessionRecordingComponent
from aumhaa.v2.control_surface.components.device import DeviceComponent

from Livid_OhmModes_v2.OhmModes import *

from .Map import *


from pushbase.grid_resolution import GridResolution
from Push2.drum_group_component import DrumGroupComponent

debug = initialize_debug()


_NOTENAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTENAMES = [(_NOTENAMES[index%12] + ' ' + str(int(index/12))) for index in range(128)]

TEMPO_TOP = 200.0
TEMPO_BOTTOM = 60.0
MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224



class SpecialOhmSessionComponent(OhmSessionComponent):


	def _update_stop_clips_led(self, index):
		tracks_to_use = self._session_ring.tracks_to_use()
		track_index = index + self._session_ring.track_offset
		if self.is_enabled() and self._stop_track_clip_buttons != None and index < len(self._stop_track_clip_buttons):
			button = self._stop_track_clip_buttons[index]
			if button != None:
				value_to_send = None
				if track_index < len(tracks_to_use) and tracks_to_use[track_index].clip_slots:
					track = tracks_to_use[track_index]
					if track.fired_slot_index == -2:
						value_to_send = self._stop_clip_triggered_value
					elif track.playing_slot_index >= 0:
						value_to_send = self._stop_clip_value
				if value_to_send == None:
					button.set_light('Session.StopClip')
				elif in_range(value_to_send, 0, 128):
					button.send_value(value_to_send)
				else:
					button.set_light(value_to_send)


	def _update_stop_all_clips_button(self):
		if self.is_enabled():
			button = self._stop_all_button
			if button:
				button.set_light('Session.StopClipTriggered' if button.is_pressed() else 'Session.StopClip')


"""We need to add an extra mode to the instrument to deal with session shifting, thus the _matrix_modes and extra functions."""
"""We also set up the id's for the note_editor here"""
"""We also make use of a shift_mode instead of the original shift mode included in the MonoInstrument so that we can add a custom behaviour locking behaviour to it"""

GRID_IDS = [0,8,16,24,32,40,48,56,1,9,17,25,33,41,49,57,2,10,18,26,34,42,50,58,3,11,19,27,35,43,51,59]

#[(column*8) + (row) for row in range(8) for row in range(8)]

class OhmMonoInstrumentComponent(MonoInstrumentComponent):


	def __init__(self, *a, **k):
		#self._matrix_modes = ModesComponent(name = 'MatrixModes')
		super(OhmMonoInstrumentComponent, self).__init__(*a, **k)
		self._keypad._note_sequencer._playhead_component._notes=tuple([GRID_IDS[index] for index in range(16)])
		self._keypad._note_sequencer._playhead_component._triplet_notes=tuple([GRID_IDS[index] for index in range(12)])
		self._keypad._note_sequencer._note_editor._visible_steps_model = lambda indices: filter(lambda k: k % 16 not in (13, 14, 15, 16), indices)
		self._drumpad._step_sequencer._playhead_component._notes=tuple([GRID_IDS[index] for index in range(16)])
		self._drumpad._step_sequencer._playhead_component._triplet_notes=tuple([GRID_IDS[index] for index in range(12)])
		self._drumpad._step_sequencer._note_editor._visible_steps_model = lambda indices: filter(lambda k: k % 16 not in (13, 14, 15, 16), indices)
		#self._matrix_modes.add_mode('disabled', [DelayMode(self.update, delay = .1, parent_task_group = self._parent_task_group)])
		#self._matrix_modes.add_mode('enabled', [DelayMode(self.update, delay = .1, parent_task_group = self._parent_task_group)], behaviour = DefaultedBehaviour())
		#self._matrix_modes._last_selected_mode = 'enabled'
		#self._matrix_modes.selected_mode = 'disabled'

		#self.set_session_mode_button = self._matrix_modes.enabled_button.set_control_element


	"""
	def _setup_shift_mode(self):
		self._shifted = False
		self._shift_mode = ModesComponent()
		self._shift_mode.add_mode('shift', tuple([lambda: self._on_shift_value(True), lambda: self._on_shift_value(False)]), behaviour = ColoredCancellableBehaviourWithRelease(color = 'MonoInstrument.ShiftOn', off_color = 'MonoInstrument.ShiftOff') if SHIFT_LOCK else BicoloredMomentaryBehaviour(color = 'MonoInstrument.ShiftOn', off_color = 'MonoInstrument.ShiftOff'))
		self._shift_mode.add_mode('disabled', None)
		self._shift_mode.selected_mode = 'disabled'


	def update(self):
		super(OhmMonoInstrumentComponent, self).update()
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
				self._script.set_controlled_track(None)
			else:
				self._main_modes.selected_mode = 'disabled'
				self._script.set_controlled_track(None)
			debug('monoInstrument mode is:', self._main_modes.selected_mode, '  inst:', self.is_enabled(), '  modes:', self._main_modes.is_enabled(), '   key:', self._keypad.is_enabled(), '   drum:', self._drumpad.is_enabled())
		"""

FEEDBACK_CHANNELS = range(14,15)

class OhmModesRay(OhmModes):


	_sysex_id = 2
	_alt_sysex_id = 7
	_model_name = 'Ohm'
	_version_check = 'b996'
	_host_name = 'Ohm'
	device_provider_class = ModDeviceProvider

	def __init__(self, c_instance):
		super(OhmModes, self).__init__(c_instance)
		self._skin = Skin(OhmColors)
		with self.component_guard():
			self._define_sysex()
			self._setup_controls()
			self._setup_background()
			self._setup_m4l_interface()
			#self._setup_translations()
			self._setup_session_control()
			self._setup_mixer_control()
			self._setup_instrument()
			#self._setup_device_control()
			#self._setup_transport_control()
			#self._setup_drumgroup()
			#self._setup_keygroup()
			#self._setup_bassgroup()
			#self._setup_mod()
			#self._setup_modswitcher()
			self._setup_modes()
		self._on_device_changed.subject = self._device_provider
		self.set_feedback_channels(FEEDBACK_CHANNELS)
		self._session_ring._update_highlight()


	def set_feedback_channels(self, channels, *a, **k):
		super(OhmModes, self).set_feedback_channels(channels, *a, **k)



	def _setup_session_control(self):
		self._session_ring = SessionRingComponent(num_tracks = 7, num_scenes = 7)
		self._session_ring.set_enabled(True)

		self._session_navigation = SessionNavigationComponent(session_ring = self._session_ring)
		self._session_navigation.scroll_navigation_layer = AddLayerMode(self._session_navigation, Layer(priority = 5, up_button = self._menu[1], down_button = self._menu[4], left_button = self._menu[3], right_button = self._menu[5]))
		self._session_navigation.page_navigation_layer = AddLayerMode(self._session_navigation, Layer(priority = 5, page_up_button = self._menu[2], page_down_button = self._menu[5], page_left_button = self._menu[3], page_right_button = self._menu[4]))
		self._session_navigation._vertical_banking.scroll_up_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._vertical_banking.scroll_down_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._horizontal_banking.scroll_up_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._horizontal_banking.scroll_down_button.color = 'Session.NavigationButtonOn'
		self._session_navigation._vertical_paginator.scroll_up_button.color = 'Session.PageNavigationButtonOn'
		self._session_navigation._vertical_paginator.scroll_down_button.color = 'Session.PageNavigationButtonOn'
		self._session_navigation._horizontal_paginator.scroll_up_button.color = 'Session.PageNavigationButtonOn'
		self._session_navigation._horizontal_paginator.scroll_down_button.color = 'Session.PageNavigationButtonOn'
		self._session_navigation.set_enabled(False)

		self._session = SpecialOhmSessionComponent(name = 'Session', session_ring = self._session_ring, auto_name = True)
		self._session.set_enabled(False)
		self._session.clip_launch_layer = AddLayerMode(self._session, Layer(priority = 5,  clip_launch_buttons = self._matrix.submatrix[:7,:7]))
		self._session.scene_launch_layer = AddLayerMode(self._session, Layer(priority = 5,  scene_launch_buttons = self._matrix.submatrix[7,:7]))
		self._session.stop_clips_layer = AddLayerMode(self._session, Layer(priority = 5,  stop_track_clip_buttons = self._matrix.submatrix[:7,7], stop_all_clips_button = self._grid[7][7]))

		"""self._session_zoom = SessionOverviewComponent(name = 'Session_Overview', session_ring = self._session_ring, enable_skinning = True)
		self._session_zoom.layer = Layer(priority = 5, button_matrix = self._matrix.submatrix[:7,:7])
		self._session_zoom.set_enabled(False)

		self._session_modes = ModesComponent(name = 'Session_Modes')
		self._session_modes.add_mode('disabled', [self._session,
														self._session.clip_launch_layer,
														self._session.scene_launch_layer,
														self._session_navigation,
														self._session_navigation.scroll_navigation_layer])
		self._session_modes.add_mode('enabled', [self._session,
														self._session.scene_launch_layer,
														self._session_zoom,
														self._session_navigation,
														self._session_navigation.page_navigation_layer],
														behaviour = DefaultedBehaviour())
		self._session_modes.layer = Layer(priority = 5, enabled_button = self._grid[7][7])
		self._session_modes.selected_mode = 'disabled'
		self._session_modes.set_enabled(False)"""



	def _setup_mixer_control(self):
		self._mixer = OhmMixerComponent(name = 'Mixer', tracks_provider = self._session_ring, track_assigner = SimpleTrackAssigner(), invert_mute_feedback = True, auto_name = True, enable_skinning = True)
		#self._mixer.layer = Layer(priority = 5, volume_controls = self._fader_matrix.submatrix[:7, :], prehear_volume_control = self._dial[15], crossfader_control = self._crossfader)
		self._mixer.layer = Layer(priority = 5, solo_buttons = self._button_matrix.submatrix[:7,:])
		"""self._mixer.master_strip().layer = Layer(priority = 5, volume_control = self._fader[7], select_button = self._button[7])
		self._mixer.mix_layer = AddLayerMode(self._mixer, Layer(priority = 5, mute_buttons = self._matrix.submatrix[:7,5],
													solo_buttons = self._matrix.submatrix[:7,6],
													arm_buttons = self._matrix.submatrix[:7,7],
													send_controls = self._dial_matrix.submatrix[:,:2],
													pan_controls = self._dial_matrix.submatrix[:7,2:],
													track_select_buttons = self._button_matrix.submatrix[:7,:],))
		self._mixer.dj_layer = AddLayerMode(self._mixer, Layer(priority = 5, mute_buttons = self._matrix.submatrix[:7,5],
													crossfade_toggles = self._matrix.submatrix[:7,6],
													end_pan_controls = self._dial_matrix.submatrix[:3,3],
													eq_gain_controls = self._dial_matrix.submatrix[:,:3],
													track_select_buttons = self._button_matrix.submatrix[:7,:],))
		self._mixer.instrument_layer = AddLayerMode(self._mixer, Layer(priority = 5,
													instrument_send_controls = self._dial_matrix.submatrix[:,2:],
													arming_track_select_buttons = self._button_matrix.submatrix[:7,:]))
		"""


	def _setup_instrument(self):
		self._grid_resolution = GridResolution()

		self._c_instance.playhead.enabled = True
		self._playhead_element = PlayheadElement(self._c_instance.playhead)
		#self._playhead_element.reset()

		#quantgrid = ButtonMatrixElement([self._base_grid._orig_buttons[2][4:8], self._base_grid._orig_buttons[3][4:7]])

		self._drum_group_finder = PercussionInstrumentFinder(device_parent=self.song.view.selected_track)

		self._instrument = OhmMonoInstrumentComponent(name = 'InstrumentModes', script = self, skin = self._skin, drum_group_finder = self._drum_group_finder, grid_resolution = self._grid_resolution, settings = DEFAULT_INSTRUMENT_SETTINGS, device_provider = self._device_provider, parent_task_group = self._task_group)
		self._instrument.layer = Layer(priority = 5, shift_button = self._livid)
		self._instrument.audioloop_layer = LayerMode(self._instrument, Layer(priority = 5, loop_selector_matrix = self._matrix))

		self._instrument.keypad_options_layer = AddLayerMode(self._instrument, Layer(priority = 5,
									scale_up_button = self._menu[0],
									scale_down_button = self._menu[3],
									offset_up_button = self._menu[1],
									offset_down_button = self._menu[4],
									vertical_offset_up_button = self._menu[2],
									vertical_offset_down_button = self._menu[5],))
		self._instrument.drumpad_options_layer = AddLayerMode(self._instrument, Layer(priority = 5,
									scale_up_button = self._menu[0],
									scale_down_button = self._menu[3],
									drum_offset_up_button = self._menu[1],
									drum_offset_down_button = self._menu[4],
									drumpad_mute_button = self._menu[2],
									drumpad_solo_button = self._menu[5],))

		self._instrument._keypad.octave_toggle_layer = AddLayerMode(self._instrument._keypad, Layer(priority = 5)) #, offset_shift_toggle = self._livid))
		self._instrument._drumpad.octave_toggle_layer = AddLayerMode(self._instrument._drumpad, Layer(priority = 5)) #, offset_shift_toggle = self._livid))

		self._instrument._keypad.main_layer = LayerMode(self._instrument._keypad, Layer(priority = 5, keypad_matrix = self._matrix.submatrix[:,:]))
		self._instrument._keypad.select_layer = LayerMode(self._instrument._keypad, Layer(priority = 5, keypad_select_matrix = self._matrix.submatrix[:, :]))
		self._instrument._keypad.split_layer = LayerMode(self._instrument._keypad, Layer(priority = 5, keypad_matrix = self._matrix.submatrix[:, 2:4]))
		self._instrument._keypad.split_select_layer = LayerMode(self._instrument._keypad, Layer(priority = 5, keypad_select_matrix = self._matrix.submatrix[:, 2:4]))

		self._instrument._keypad.sequencer_layer = AddLayerMode(self._instrument._keypad, Layer(priority = 5, playhead = self._playhead_element, sequencer_matrix = self._matrix.submatrix[:, :4]))
		self._instrument._keypad.sequencer_shift_layer = AddLayerMode(self._instrument._keypad, Layer(priority = 5, loop_selector_matrix = self._matrix.submatrix[:, :4], quantization_buttons = self._matrix.submatrix[:8, 1:2],)) #follow_button = self._pad[15]))

		self._instrument._drumpad.main_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5, drumpad_matrix = self._matrix.submatrix[:,4:], sequencer_matrix = self._matrix.submatrix[:, :2], loop_selector_matrix = self._matrix.submatrix[:, 3:4], playhead = self._playhead_element, quantization_buttons = self._matrix.submatrix[:, 2:3]))
		self._instrument._drumpad.select_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5, drumpad_select_matrix = self._matrix.submatrix[:,4:],  sequencer_matrix = self._matrix.submatrix[:, :2], loop_selector_matrix = self._matrix.submatrix[:, 3:4], playhead = self._playhead_element, quantization_buttons = self._matrix.submatrix[:, 2:3]))
		self._instrument._drumpad.split_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5, drumpad_matrix = self._matrix.submatrix[:4, 4:],))
		self._instrument._drumpad.split_select_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5, drumpad_select_matrix = self._matrix.submatrix[:4,4:]))

		self._instrument._drumpad.sequencer_layer = AddLayerMode(self._instrument._drumpad, Layer(priority = 5, playhead = self._playhead_element, sequencer_matrix = self._matrix.submatrix[:, :4]))
		self._instrument._drumpad.sequencer_shift_layer = AddLayerMode(self._instrument._drumpad, Layer(priority = 5, loop_selector_matrix = self._matrix.submatrix[4:8, :2], quantization_buttons = self._matrix.submatrix[4:8, 2:],)) #follow_button = self._pad[31]))

		self._instrument._selected_session._keys_layer = LayerMode(self._instrument._selected_session, Layer(priority = 5, clip_launch_buttons = self._matrix.submatrix[:, :2]))
		self._instrument._selected_session._drum_layer = LayerMode(self._instrument._selected_session, Layer(priority = 5, clip_launch_buttons = self._matrix.submatrix[4:8, :]))

		self._instrument._main_modes = ModesComponent(parent = self._instrument, name = 'InstrumentModes')
		self._instrument._main_modes.add_mode('disabled', [])
		self._instrument._main_modes.add_mode('drumpad', [self._instrument._drumpad, self._instrument._drumpad.main_layer, self._instrument.drumpad_options_layer])
		self._instrument._main_modes.add_mode('drumpad_split', [self._instrument._drumpad, self._instrument._drumpad.split_layer, self._instrument._selected_session, self._instrument._selected_session._drum_layer])
		self._instrument._main_modes.add_mode('drumpad_sequencer', [self._instrument._drumpad, self._instrument._drumpad.sequencer_layer, self._instrument._drumpad.split_layer])
		self._instrument._main_modes.add_mode('drumpad_shifted', [self._instrument._drumpad, self._instrument._drumpad.select_layer, self._instrument.drumpad_options_layer, self._instrument._drumpad.octave_toggle_layer])
		self._instrument._main_modes.add_mode('drumpad_split_shifted', [ self._instrument._drumpad, self._instrument._drumpad.split_select_layer, self._instrument.drumpad_options_layer, self._instrument._drumpad.octave_toggle_layer, self._instrument._selected_session, self._instrument._selected_session._drum_layer])
		self._instrument._main_modes.add_mode('drumpad_sequencer_shifted', [self._instrument._drumpad, self._instrument._drumpad.split_select_layer, self._instrument._drumpad.sequencer_shift_layer, self._instrument.drumpad_options_layer, self._instrument._drumpad.octave_toggle_layer])
		self._instrument._main_modes.add_mode('keypad', [self._instrument._keypad, self._instrument._keypad.main_layer, self._instrument.keypad_options_layer])
		self._instrument._main_modes.add_mode('keypad_split', [self._instrument._keypad, self._instrument._keypad.split_layer, self._instrument._selected_session, self._instrument._selected_session._keys_layer])
		self._instrument._main_modes.add_mode('keypad_sequencer', [self._instrument._keypad, self._instrument._keypad.sequencer_layer, self._instrument._keypad.split_layer], )
		self._instrument._main_modes.add_mode('keypad_shifted', [self._instrument._keypad, self._instrument._keypad.select_layer, self._instrument.keypad_options_layer, self._instrument._keypad.octave_toggle_layer])
		self._instrument._main_modes.add_mode('keypad_split_shifted', [self._instrument._keypad, self._instrument._keypad.split_select_layer, self._instrument.keypad_options_layer, self._instrument._keypad.octave_toggle_layer, self._instrument._selected_session, self._instrument._selected_session._keys_layer])
		self._instrument._main_modes.add_mode('keypad_sequencer_shifted', [self._instrument._keypad, self._instrument._keypad.split_select_layer, self._instrument._keypad.sequencer_shift_layer, self._instrument.keypad_options_layer, self._instrument._keypad.octave_toggle_layer])
		self._instrument._main_modes.add_mode('audioloop', [self._instrument.audioloop_layer])
		#self._instrument.register_component(self._instrument._main_modes)
		self._instrument.set_enabled(False)




	def _setup_modes(self):

		self._main_modes = ModesComponent(name = 'MainModes')
		self._main_modes.add_mode('disabled', [self._background])
		self._main_modes.add_mode('Mix', [self._mixer, self._session, self._session.stop_clips_layer, self._session.clip_launch_layer, self._session.scene_launch_layer, self._session_navigation, self._session_navigation.scroll_navigation_layer])
		self._main_modes.add_mode('Instrument', [self._instrument])
		self._main_modes.selected_mode = 'disabled'
		self._main_modes.layer = Layer(priority = 5, Mix_button = self._shift_l, Instrument_button = self._shift_r)
		self._main_modes.set_enabled(True)


	def reset_controlled_track(self, track = None, *a):
		if not track:
			track = self.song.view.selected_track
		self.set_controlled_track(track)


	def set_controlled_track(self, track = None, *a):
		if isinstance(track, Live.Track.Track):
			super(OhmModes, self).set_controlled_track(track)
		else:
			self.release_controlled_track()

	@listens('device')
	def _on_device_changed(self):
		debug('_on_device_changed')
		self.update()

	def update(self):
		self.reset_controlled_track()
		self.set_feedback_channels(FEEDBACK_CHANNELS)
		super(OhmModes, self).update()







#a
