# by amounra 0320 : http://www.aumhaa.com
# written against Live 10.1.9 on 0320

from __future__ import absolute_import, print_function
import Live
import math
import sys
from re import *
from itertools import imap, chain, starmap

from ableton.v2.base import inject, listenable_property, listens, listens_group
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
#from aumhaa.v2.control_surface.components.mono_instrument import *
from aumhaa.v2.livid import LividControlSurface, LividSettings, LividRGB
from aumhaa.v2.control_surface.components.fixed_length_recorder import FixedLengthSessionRecordingComponent
from aumhaa.v2.control_surface.components.device import DeviceComponent
from aumhaa.v2.control_surface.components.m4l_interface import M4LInterfaceComponent

from pushbase.auto_arm_component import AutoArmComponent
from pushbase.grid_resolution import GridResolution
from pushbase.drum_group_component import DrumGroupComponent
from pushbase.step_seq_component import StepSeqComponent
from pushbase.note_editor_component import NoteEditorComponent
from pushbase.loop_selector_component import LoopSelectorComponent
from pushbase.playhead_component import PlayheadComponent
from pushbase.grid_resolution import GridResolution
from pushbase.pad_control import PadControl
from pushbase.instrument_component import SelectedNotesInstrumentComponent

from .mono_instrument import *

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


class SpecialStepSeqComponent(StepSeqComponent):

	def __init__(self, *a, **k):
		super(SpecialStepSeqComponent, self).__init__(*a, **k)
		self._playhead_component = SpecialPlayheadComponent(parent=self, grid_resolution=self._grid_resolution, paginator=self.paginator, follower=self._loop_selector, notes=chain(*starmap(range, ((0, 16),
		 (16, 32),
		 (32, 48),
		 (48, 64),
		 (64, 80),
		 (80, 96),
		 (96, 112),
		 (112, 128)))), triplet_notes=chain(*starmap(range, ((0, 12),
		 (16, 28),
		 (32, 44),
		 (48, 60),
		 (64, 76),
		 (80, 92),
		 (96, 108),
		 (112, 124)))), feedback_channels=range(0,1))
		self._loop_selector.follow_detail_clip = True
		self._loop_selector._on_detail_clip_changed.subject = self.song.view
		self._update_delay_task = self._tasks.add(task.sequence(task.wait(1), task.run(self._update_delayed)))
		self._update_delay_task.kill()


	def update(self):
		"""We need to delay the update task, as on_detail_clip_changed (triggering set_detail_clip() in loopselector) causes all stored sequencer states to zero out while modes are switching"""
		super(SpecialStepSeqComponent, self).update()
		self._update_delay_task.restart()
		debug('stepseq.update, playhead:', self._playhead_component._clip, self._playhead_component._feedback_channels, self._playhead_component._playhead )


	def _update_delayed(self):
		self._on_detail_clip_changed()
		self._update_playhead_color()
		self._update_delay_task.kill()


class SpecialNoteEditorComponent(NoteEditorComponent):


	"""Custom function for displaying triplets for different grid sizes, called by _visible steps"""
	_visible_steps_model = lambda self, indices: filter(lambda k: k % 4 != 3, indices)
	matrix = control_matrix(PadControl, channel=0, sensitivity_profile=u'loop', mode=PlayableControl.Mode.listenable)

	@matrix.pressed
	def matrix(self, button):
		super(SpecialNoteEditorComponent, self)._on_pad_pressed(button.coordinate)

	@matrix.released
	def matrix(self, button):
		super(SpecialNoteEditorComponent, self)._on_pad_released(button.coordinate)

	def _on_pad_pressed(self, coordinate):
		y, x = coordinate
		debug('SpecialNoteEditorComponent._on_pad_pressed:', y, x)
		super(SpecialNoteEditorComponent, self)._on_pad_pressed(coordinate)

	def _visible_steps(self):
		first_time = self.page_length * self._page_index
		steps_per_page = self._get_step_count()
		step_length = self._get_step_length()
		indices = range(steps_per_page)
		if is_triplet_quantization(self._triplet_factor):
			indices = self._visible_steps_model(indices)
		return [ (self._time_step(first_time + k * step_length), index) for k, index in enumerate(indices) ]


class SpecialLoopSelectorComponent(LoopSelectorComponent):

	def __init__(self, *a, **k):
		self._playhead_page_index = 0
		super(SpecialLoopSelectorComponent, self).__init__(*a, **k)

	# def _update_page_and_playhead_leds(self):
	# 	super(SpecialLoopSelectorComponent, self)._update_page_and_playhead_leds()
	# 	if self.is_enabled() and self._has_running_clip():
	# 		position = self._sequencer_clip.playing_position
	# 		visible_page = int(position / self._page_length_in_beats) - self.page_offset
	#
	# 		#new_playhead_page = int(position / self.)
	# 		if visible_page != self._playhead_page_index:
	# 			self._playhead_page_index = visible_page
	# 			self.notify_playhead_page_index(self._playhead_page_index)
	# 			#debug('page:', visible_page)


	@listenable_property
	def playhead_page_index(self):
		return self._playhead_page_index


class STEPSEQMonoInstrumentComponent(MonoInstrumentComponent):


	def __init__(self, *a, **k):
		#self._matrix_modes = ModesComponent(name = 'MatrixModes')
		super(STEPSEQMonoInstrumentComponent, self).__init__(*a, **k)
		# self._keypad._note_sequencer._playhead_component._notes=tuple(range(32))
		# self._keypad._note_sequencer._playhead_component._triplet_notes=tuple(range(32))
		self._keypad._note_sequencer._playhead_component.set_note_banks(NOTEBANKS)
		self._keypad._note_sequencer._playhead_component.set_triplet_note_banks(TRIPLET_NOTEBANKS)
		# self._keypad._note_sequencer._note_editor._visible_steps_model = lambda indices: filter(lambda k: k % 16 not in (13, 14, 15, 16), indices)
		# self._keypad._note_sequencer._loop_selector = SpecialLoopSelectorComponent(parent=self, clip_creator=ClipCreator(), default_size=4, measure_length = 4.0)
		# self._keypad._note_sequencer._playhead_component.set_follower(self._keypad._note_sequencer._loop_selector)

		# self._drumpad._step_sequencer._playhead_component._notes=tuple(range(32))
		# self._drumpad._step_sequencer._playhead_component._triplet_notes=tuple(range(32))
		# self._drumpad._step_sequencer._playhead_component.set_note_banks(NOTEBANKS)
		# self._drumpad._step_sequencer._note_editor._visible_steps_model = lambda indices: filter(lambda k: k % 16 not in (13, 14, 15, 16), indices)
		# self._drumpad._step_sequencer._loop_selector = SpecialLoopSelectorComponent(parent=self, clip_creator=ClipCreator(), default_size=4, measure_length = 4.0)




class STEPSEQ(ControlSurface):

	device_provider_class = ModDeviceProvider

	def __init__(self, *a, **k):
		super(STEPSEQ, self).__init__(*a, **k)
		self._skin = Skin(STEPSEQColors)
		with self._component_guard():
			self._setup_controls()
			self._setup_autoarm()
			self._setup_mixer_control()
			self._setup_device_control()
			self._setup_stepsequencer()
			self._setup_background()
			self._setup_main_modes()
		self._on_device_changed.subject = self._device_provider
		self._on_selected_track_changed.subject = self.song.view
		self._on_detail_clip_changed.subject = self.song.view
		# self.set_feedback_channels(range(0, 15))
		self._main_modes.selected_mode = 'Main'
		# self.introspect_playhead()


	# def set_feedback_channels(self, channels, *a, **k):
	# 	super(STEPSEQ, self).set_feedback_channels(channels, *a, **k)


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
		self._pad_matrix = ButtonMatrixElement(name = 'PadMatrix', rows = [self._pad[0:16],
																			self._pad[16:32],
																			self._pad[32:48],
																			self._pad[48:64],
																			self._pad[64:80],
																			self._pad[80:96],
																			self._pad[96:112],
																			self._pad[112:128]])

		self._select_multi = MultiElement(self._button[0], self._button[1], self._button[2], self._button[3], self._button[4], self._button[5], self._button[6], self._button[7],)


	def _setup_background(self):
		self._background = BackgroundComponent(name = 'Background')
		self._background.layer = Layer(priority = 5, matrix = self._pad_matrix, playhead = self._playhead_element)
		self._background.set_enabled(False)


	def _setup_autoarm(self):
		self._auto_arm = AutoArmComponent(name='Auto_Arm')
		self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
		self._auto_arm._update_notification = lambda: None


	def _setup_mixer_control(self):
		self._session_ring = SessionRingComponent(name = 'Session_Ring', num_tracks = 8, num_scenes = 1)
		self._mixer = MonoMixerComponent(name = 'Mixer', num_returns = 4,tracks_provider = self._session_ring, track_assigner = SimpleTrackAssigner(), invert_mute_feedback = True, auto_name = True, enable_skinning = True, channel_strip_component_type = MonoChannelStripComponent)
		self._mixer.layer = Layer(priority = 5, track_select_buttons = self._select_button_matrix)
		self._mixer.set_enabled(False)


	def _setup_device_control(self):
		self._device_selection_follows_track_selection = True
		self._device = DeviceComponent(name = 'Device_Component', device_bank_registry = DeviceBankRegistry(), device_provider = self._device_provider)
		self._device.layer = Layer(priority = 5, parameter_controls = self._encoder_matrix)
		self._device.set_enabled(False)


	# def _setup_stepsequencer(self):
	# 	self._grid_resolution = GridResolution()
	# 	self._c_instance.playhead.enabled = True
	# 	self._playhead_element = PlayheadElement(playhead = self._c_instance.playhead)
	#
	# 	self._clip_creator = ClipCreator()
	# 	self._note_editor = SpecialNoteEditorComponent(clip_creator = self._clip_creator, grid_resolution = self._grid_resolution)
	# 	#self._note_editor.set_enabled(False)
	# 	self._instrument = MonoKeyGroupComponent()
	# 	#self._instrument.set_enabled(False)
	# 	self._stepsequencer = SpecialStepSeqComponent(clip_creator = self._clip_creator, skin = self._skin, grid_resolution = self._grid_resolution, name = 'Note_Sequencer', note_editor_component= self._note_editor, instrument_component = self._instrument)
	# 	self._stepsequencer.layer = Layer(priority = 5, button_matrix = self._pad_matrix, playhead = self._playhead_element)
	# 	self._stepsequencer.set_enabled(False)


	def _setup_stepsequencer(self):
		self._grid_resolution = GridResolution()

		self._c_instance.playhead.enabled = True
		self._playhead_element = PlayheadElement(self._c_instance.playhead)
		#self._playhead_element.reset()

		self._drum_group_finder = PercussionInstrumentFinder(device_parent=self.song.view.selected_track)

		self._instrument = STEPSEQMonoInstrumentComponent(name = 'InstrumentModes', script = self, skin = self._skin, drum_group_finder = self._drum_group_finder, grid_resolution = self._grid_resolution, settings = DEFAULT_INSTRUMENT_SETTINGS, device_provider = self._device_provider, parent_task_group = self._task_group)
		#self._instrument.layer = Layer(priority = 6)

		self._instrument._keypad.main_layer = LayerMode(self._instrument._keypad, Layer(priority = 5, keypad_matrix = self._pad_matrix.submatrix[:,:]))

		self._instrument._keypad.sequencer_layer = AddLayerMode(self._instrument._keypad, Layer(priority = 5, playhead = self._playhead_element, sequencer_matrix = self._pad_matrix.submatrix[:, :])) # loop_selector_matrix = self._pad_matrix.submatrix[:, 4:6], quantization_buttons = self._pad_matrix.submatrix[8:15, 6:]))
		self._instrument._keypad.sequencer_shift_layer = AddLayerMode(self._instrument._keypad, Layer(priority = 5, sequencer_matrix = self._pad_matrix.submatrix[:, :4], loop_selector_matrix = self._pad_matrix.submatrix[:, 6:7], quantization_buttons = self._pad_matrix.submatrix[9:, 7:8],)) #follow_button = self._pad[15]))

		self._instrument._drumpad.main_layer = LayerMode(self._instrument._drumpad, Layer(priority = 5, drumpad_matrix = self._pad_matrix.submatrix[:,:]))

		self._instrument._drumpad.sequencer_layer = AddLayerMode(self._instrument._drumpad, Layer(priority = 5, playhead = self._playhead_element, sequencer_matrix = self._pad_matrix.submatrix[:, :])) # loop_selector_matrix = self._pad_matrix.submatrix[:, 4:6], quantization_buttons = self._pad_matrix.submatrix[8:15, 6:]))
		self._instrument._drumpad.sequencer_shift_layer = AddLayerMode(self._instrument._drumpad, Layer(priority = 5, sequencer_matrix = self._pad_matrix.submatrix[:, :4], loop_selector_matrix = self._pad_matrix.submatrix[:, 6:7], quantization_buttons = self._pad_matrix.submatrix[9:, 7:8],)) #follow_button = self._pad[15]))

		self._instrument.audioloop_layer = LayerMode(self._instrument, Layer(priority = 6, loop_selector_matrix = self._pad_matrix.submatrix[:,:]))

		self._instrument._main_modes = ModesComponent(parent = self._instrument, name = 'InstrumentModes')
		self._instrument._main_modes.add_mode('disabled', [])
		self._instrument._main_modes.add_mode('drumpad', [self._instrument._drumpad, self._instrument._drumpad.sequencer_layer])
		self._instrument._main_modes.add_mode('drumpad_split', [self._instrument._drumpad, self._instrument._drumpad.sequencer_layer])
		self._instrument._main_modes.add_mode('drumpad_sequencer', [self._instrument._drumpad, self._instrument._drumpad.sequencer_layer])
		self._instrument._main_modes.add_mode('drumpad_shifted', [self._instrument._drumpad, self._instrument._drumpad.sequencer_shift_layer])
		self._instrument._main_modes.add_mode('drumpad_split_shifted', [self._instrument._drumpad, self._instrument._drumpad.sequencer_shift_layer])
		self._instrument._main_modes.add_mode('drumpad_sequencer_shifted', [self._instrument._drumpad, self._instrument._drumpad.sequencer_shift_layer])
		self._instrument._main_modes.add_mode('keypad', [self._instrument._keypad, self._instrument._keypad.sequencer_layer])
		self._instrument._main_modes.add_mode('keypad_split', [self._instrument._keypad, self._instrument._keypad.sequencer_layer])
		self._instrument._main_modes.add_mode('keypad_sequencer', [self._instrument._keypad, self._instrument._keypad.sequencer_layer] )
		self._instrument._main_modes.add_mode('keypad_shifted', [self._instrument._keypad, self._instrument._keypad.sequencer_shift_layer])
		self._instrument._main_modes.add_mode('keypad_split_shifted', [self._instrument._keypad, self._instrument._keypad.sequencer_shift_layer])
		self._instrument._main_modes.add_mode('keypad_sequencer_shifted', [self._instrument._keypad, self._instrument._keypad.sequencer_shift_layer])
		self._instrument._main_modes.add_mode('audioloop', [self._instrument.audioloop_layer])
		self._instrument.set_enabled(False)


	def _setup_main_modes(self):
		self._main_modes = ModesComponent(name = 'MainModes')
		self._main_modes.add_mode('disabled', [self._background])
		#self._main_modes.add_mode('Main', [self._mixer, self._device, self._instrument, self._stepsequencer])
		self._main_modes.add_mode('Main', [self._mixer, self._device, self._instrument])
		self._main_modes.add_mode('Select', [self._device, self._instrument, tuple([self._send_instrument_shifted, self._send_instrument_unshifted])], behaviour = DelayedExcludingMomentaryBehaviour(excluded_groups = ['shifted']) )
		self._main_modes.selected_mode = 'disabled'
		self._main_modes.layer = Layer(priority = 5, Select_button=self._select_multi)
		self._main_modes.set_enabled(True)


	def _send_instrument_shifted(self):
		self._instrument.is_enabled() and self._instrument._on_shift_value(1)


	def _send_instrument_unshifted(self):
		self._instrument.is_enabled() and self._instrument._on_shift_value(0)


	"""general functionality"""
	def disconnect(self):
		super(STEPSEQ, self).disconnect()


	def _can_auto_arm_track(self, track):
		# routing = track.current_input_routing
		# return routing == 'Ext: All Ins' or routing == 'All Ins' or routing.startswith('S Input')
		return False


	@listens(u'device')
	def _on_device_changed(self):
		pass


	@listens(u'selected_track')
	def _on_selected_track_changed(self):
		#super(STEPSEQ, self)._on_selected_track_changed()
		# self._drum_group_finder.device_parent = self.song.veiw.selected_track
		# self._stepsequencer.update()
		# self._playhead_element.track = self.song.view.selected_track
		# self.set_feedback_channels([15])
		# self.set_controlled_track(self.song.view.selected_track)
		pass


	@listens(u'detail_clip')
	def _on_detail_clip_changed(self):
		# debug('_on_detail_clip_changed')
		# self._main_modes.selected_mode = 'disabled'
		# self._main_modes.selected_mode = 'Main'
		# self._c_instance.playhead.enabled = True
		# self._playhead_element.proxied_object = self._c_instance.playhead
		# self._stepsequencer.set_playhead(self._playhead_element)
		# self._stepsequencer.update()
		# debug('MODE:', self._main_modes.selected_mode)
		pass

	def introspect_playhead(self):
		debug('playhead dir:', dir(self._c_instance.playhead))



#	a
