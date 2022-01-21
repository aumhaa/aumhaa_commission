# by amounra 0320 : http://www.aumhaa.com
# written against Live 11.0.5 on 0821


import Live
import math
import sys
from re import *
from itertools import chain, starmap
from functools import cmp_to_key, partial, reduce
# from itertools import chain, imap, product

from ableton.v2.base import inject, listenable_property, listens, listens_group, clamp, task, liveobj_valid, nop, first, second, mixin, product, flatten, is_matrix, find_if
from ableton.v2.control_surface import ControlSurface, ControlElement, Layer, Skin, PrioritizedResource, Component, ClipCreator, DeviceBankRegistry, BankingInfo, ParameterInfo
from ableton.v2.control_surface.elements import ButtonMatrixElement, DoublePressElement, MultiElement, DisplayDataSource, SysexElement, EncoderElement, SliderElement
from ableton.v2.control_surface.components import ClipSlotComponent, SceneComponent, SessionComponent, TransportComponent, BackgroundComponent, ViewControlComponent, SessionRingComponent, SessionRecordingComponent, SessionNavigationComponent, MixerComponent, PlayableComponent
from ableton.v2.control_surface.components.mixer import SimpleTrackAssigner
from ableton.v2.control_surface.mode import AddLayerMode, ModesComponent, DelayMode
from ableton.v2.control_surface.elements.physical_display import PhysicalDisplayElement
from ableton.v2.control_surface.components.session_recording import *
from ableton.v2.control_surface.percussion_instrument_finder import PercussionInstrumentFinder, find_drum_group_device
from ableton.v2.control_surface.control import PlayableControl, ButtonControl, control_matrix, EncoderControl, control_list, RadioButtonControl, ToggleButtonControl, control_event, control_color, Control, RadioButtonGroup
from ableton.v2.control_surface.control.control_list import ControlList
from ableton.v2.control_surface.control.control import Connectable
from ableton.v2.control_surface.control.button import ButtonControlBase
from ableton.v2.control_surface.elements import PlayheadElement
from ableton.v2.control_surface.components.device import DeviceComponent
from ableton.v2.control_surface.default_bank_definitions import BANK_DEFINITIONS
from ableton.v2.control_surface.elements.proxy_element import ProxyElement
from ableton.v2.control_surface.components.session import SessionComponent
from ableton.v2.control_surface.components.session_navigation import SessionNavigationComponent

from aumhaa.v2.base import initialize_debug
from aumhaa.v2.control_surface import SendLividSysexMode, MomentaryBehaviour, ExcludingMomentaryBehaviour, DelayedExcludingMomentaryBehaviour, ShiftedBehaviour, LatchingShiftedBehaviour, FlashingBehaviour
from aumhaa.v2.control_surface.mod_devices import *
from aumhaa.v2.control_surface.mod import *
from aumhaa.v2.control_surface.elements import MonoEncoderElement, MonoBridgeElement, generate_strip_string
from aumhaa.v2.control_surface.elements.mono_button import *
from aumhaa.v2.control_surface.components import MonoDeviceComponent, DeviceNavigator, TranslationComponent, MonoMixerComponent, MonoChannelStripComponent
#from aumhaa.v2.control_surface.components.device import DeviceComponent
# from aumhaa.v2.control_surface.components.mono_instrument import *
from aumhaa.v2.livid import LividControlSurface, LividSettings, LividRGB
from aumhaa.v2.control_surface.components.fixed_length_recorder import FixedLengthSessionRecordingComponent
#from aumhaa.v2.control_surface.components.device import DeviceComponent
from aumhaa.v2.control_surface.components.m4l_interface import M4LInterfaceComponent
from aumhaa.v2.control_surface.components.mono_keygroup import MonoKeyGroupComponent
from aumhaa.v2.control_surface.components.mono_mixer import *
from aumhaa.v2.control_surface.components.mono_instrument import *

from pushbase.auto_arm_component import AutoArmComponent
from pushbase.grid_resolution import GridResolution
from pushbase.drum_group_component import DrumGroupComponent
from pushbase.step_seq_component import StepSeqComponent
from pushbase.note_editor_component import *
from pushbase.loop_selector_component import LoopSelectorComponent
from pushbase.playhead_component import PlayheadComponent
from pushbase.grid_resolution import GridResolution
from pushbase.pad_control import PadControl
from pushbase.instrument_component import SelectedNotesInstrumentComponent
from pushbase.note_settings_component import *
from pushbase.automation_component import AutomationComponent
from pushbase.device_parameter_component import DeviceParameterComponent
from pushbase.setting import EnumerableSetting

from pushbase.note_editor_component import NoteEditorComponent

# from .mono_instrument import *


from ableton.v2.control_surface.components.device import DeviceComponent

LOCAL_DEBUG = False

debug = initialize_debug(local_debug = LOCAL_DEBUG)

from .Map import *


MIDI_NOTE_TYPE = 0
MIDI_CC_TYPE = 1
MIDI_PB_TYPE = 2
MIDI_MSG_TYPES = (MIDI_NOTE_TYPE, MIDI_CC_TYPE, MIDI_PB_TYPE)
MIDI_NOTE_ON_STATUS = 144
MIDI_NOTE_OFF_STATUS = 128
MIDI_CC_STATUS = 176
MIDI_PB_STATUS = 224

ONE_YEAR_AT_120BPM_IN_BEATS = 63072000.0

def note_pitch(note):
	return note[0]


def note_start_time(note):
	return note[1]


def note_length(note):
	return note[2]


def note_velocity(note):
	return note[3]


def note_muted(note):
	return note[4]


def is_device(device):
	return (not device is None and isinstance(device, Live.Device.Device) and hasattr(device, 'name'))


def make_pad_translations(chan):
	return tuple((x%4, int(x/4), x+16, chan) for x in range(16))


def return_empty():
	return []


def make_default_skin():
	return Skin(STEPSEQColors)


def tracks_to_use_from_song(song):
	tracks = []
	for track in song.visible_tracks:
		if liveobj_valid(track) and track.name.startswith(u'*SEQ'):
			tracks.append(track)
	name_list = [track.name for track in tracks]
	debug('tracks are:', name_list)
	if len(tracks):
		return tuple(tracks)
	return song.visible_tracks

#these are doing the same job as the c_instance version would, but within Python.
#its important to note that unless the update method of the PlayheadComponent is replaced, there is fuckery
#when working with it this way, since it depends on the _notes and _triplet_notes passed to it as to how it
#makes decisions about how to space its feedback (start_time, step_length)
class SpecialNullPlayhead(object):
	notes = []
	start_time = 0.0
	step_length = 1.0
	velocity = 0.0
	wrap_around = False
	track = None
	clip = None
	set_feedback_channels = nop
	set_buttons = nop
	_last_step_index = 0

class Playhead(Component):

	def __init__(self, *a, **k):
		super(Playhead, self).__init__(*a, **k)
		self._notes = []
		self._start_time = 0.0
		self._step_length = 1.0
		self._velocity = 0.0
		self._wrap_around = False
		self._track = None
		self._clip = None
		self.set_feedback_channels = nop
		self._last_step_index = -1

	@property
	def notes(self):
		return self._notes

	@notes.setter
	def notes(self, val):
		self._notes = val
		# debug('playhead notes are now:', self._notes)

	@property
	def clip(self):
		return self._clip

	@clip.setter
	def clip(self, clip):
		self._clip = clip
		self._on_clip_playing_position_changed.subject = clip
		# debug('playhead clip is now:', self._clip)

	@listens('playing_position')
	def _on_clip_playing_position_changed(self):
		if not self._buttons is None:
			position = liveobj_valid(self._clip) and self._clip.playing_position
			step_index = int((position-self._start_time)/self._step_length)
			buttons_length = len(self._buttons)
			# debug('buttons_length:', buttons_length, 'step_index:', step_index)
			if (step_index != self._last_step_index) and (step_index < buttons_length) and (step_index > 0):
				# debug('start_time:', self._start_time)
				last_button = self._buttons[self._last_step_index] if len(self._buttons) >self._last_step_index else None
				# debug('last_step_index:', self._last_step_index, 'last_button', last_button)
				last_button != None and last_button.unflash_playhead()
				button = None
				if step_index < len(self._buttons):
					button = self._buttons[step_index]
				# button = self._buttons[step_index] if step_index < len(self._buttons) else None
				# debug('step_index:', step_index, 'button', button)
				button != None and button.flash_playhead(self.velocity)
				self._last_step_index = step_index
			# debug('playing position is:', position, step_index)

	@property
	def track(self):
		return self._track

	@track.setter
	def track(self, track):
		self._track = track
		# debug('playhead track is now:', self._track)

	@property
	def start_time(self):
		return self._start_time

	@start_time.setter
	def start_time(self, start_time):
		self._start_time = start_time
		# debug('playhead start_time is now:', self._start_time)

	@property
	def step_length(self):
		return self._step_length

	@step_length.setter
	def step_length(self, step_length):
		self._step_length = step_length
		# debug('playhead step_length is now:', self._step_length)

	@property
	def velocity(self):
		return self._velocity

	@velocity.setter
	def velocity(self, velocity):
		self._velocity = velocity
		# debug('playhead velocity is now:', self._velocity)

	@property
	def wrap_around(self):
		return self._wrap_around

	@wrap_around.setter
	def wrap_around(self, wrap_around):
		self._wrap_around = wrap_around
		# debug('playhead wrap_around is now:', self._wrap_around)

	def set_buttons(self, buttons):
		# if self._buttons:
		# 	self._buttons.reset()
		# debug('set_buttons:', buttons)
		if not buttons is None:
			self._buttons = [button for row in buttons._orig_buttons for button in row]
		else:
			self._buttons = None


#we only override this becxause we need to inject the SpecialNullPlayhead as the proxied interface
class SpecialPlayheadElement(ProxyElement):

	def __init__(self, playhead = None, *a, **k):
		super(SpecialPlayheadElement, self).__init__(proxied_object=playhead, proxied_interface = SpecialNullPlayhead())

	def reset(self):
		self.track = None


# class SpecialPlayheadComponent(PlayheadComponent):
#
# 	def update(self):
# 		super(SpecialPlayheadComponent, self).update()
# 		if self._playhead:
# 			clip = None
# 			if self.is_enabled() and self.song.is_playing and liveobj_valid(self._clip):
# 				if self._clip.is_arrangement_clip or self._clip.is_playing:
# 					clip = self._clip
# 			self._playhead.clip = clip
# 			self._playhead.set_feedback_channels(self._feedback_channels)
# 			if clip:
# 				is_triplet = self._grid_resolution.clip_grid[1]
# 				notes = self._triplet_notes if is_triplet else self._notes
# 				self._playhead.notes = list(notes)
# 				self._playhead.wrap_around = self._follower.is_following and self._paginator.can_change_page
# 				self._playhead.start_time = self._paginator.page_length * self._paginator.page_index
# 				self._playhead.step_length = self._paginator.page_length / len(notes)


class SpecialMonoButtonElement(MonoButtonElement):

	def flash_playhead(self, color):
		data_byte1 = self._original_identifier
		data_byte2 = color
		status_byte = self._original_channel
		status_byte += MIDI_NOTE_ON_STATUS
		self.send_midi((status_byte,
		 data_byte1,
		 data_byte2))

	def unflash_playhead(self):
		data_byte1 = self._original_identifier
		data_byte2 = self._color
		status_byte = self._original_channel
		status_byte += MIDI_NOTE_ON_STATUS
		self.send_midi((status_byte,
		 data_byte1,
		 data_byte2))

#A small tweak to make the EncoderElement (which is expected to be endless) to work as an absolute element.
#The Automation and NoteEditorSettings are expecting an encoder.
class SpecialEncoderElement(EncoderElement):

	def relative_value_to_delta(self, value):
		debug('relative_value_to_delta', value)
		return value

	def normalize_value(self, value):
		# return self.relative_value_to_delta(value) / 64.0 * self.encoder_sensitivity
		return value


#These are taken from ableton.v2 framework, but instead of overriding them I copied all to prevent the need for future updating (hopefully)
#They work as radio buttons, but allow mutliple items to be checked.  One should set up with new_control_list(CheckedRadioButtonControl),
#and then observe the checked_indexes property in the component they belong to.
class CheckedRadioButtonControl(ButtonControlBase):
	checked = control_event(u'checked')

	class State(ButtonControlBase.State):
		unchecked_color = control_color(u'DefaultButton.Off')
		checked_color = control_color(u'DefaultButton.On')

		def __init__(self, unchecked_color = None, checked_color = None, *a, **k):
			super(CheckedRadioButtonControl.State, self).__init__(*a, **k)
			if unchecked_color is not None:
				self.unchecked_color = unchecked_color
			if checked_color is not None:
				self.checked_color = checked_color
			self._checked = False
			self._on_checked = nop

		@property
		def is_checked(self):
			return self._checked

		@is_checked.setter
		def is_checked(self, value):
			if self._checked != value:
				self._checked = value
				if self._checked:
					self._on_checked()
				self._send_current_color()

		def _send_button_color(self):
			self._control_element.set_light(self.checked_color if self._checked else self.unchecked_color)

		def _on_pressed(self):
			super(CheckedRadioButtonControl.State, self)._on_pressed()
			if not self._checked:
				self._checked = True
			self._notify_checked()

		def _notify_checked(self):
			if self._checked:
				self._call_listener(u'checked')
				self._on_checked()


class CheckedRadioButtonGroup(ControlList, CheckedRadioButtonControl):
	checked_indexes = control_event(u'checked_indexes')

	class State(ControlList.State, Connectable):
		requires_listenable_connected_property = True

		def __init__(self, *a, **k):
			self._checked_indexes = [0]
			self._initial_pressed = None
			super(CheckedRadioButtonGroup.State, self).__init__(*a, **k)


		def _on_pressed(self):
			# debug('CheckedRadioButtonGroup._on_pressed:', self._checked_indexes)
			super(CheckedRadioButtonGroup.State, self)._on_pressed()

		@property
		def checked_indexes(self):
			return self._checked_indexes

		@checked_indexes.setter
		def checked_indexes(self, val):
			# assert -1 <= index < self.control_count
			# if index != -1:
			# 	self[index].is_checked = True
			# else:
			# 	checked_control = find_if(lambda c: c.is_checked, self)
			# 	if checked_control is not None:
			# 		checked_control.is_checked = False
			self._checked_indexes = val
			# debug('checked_indexes.setter:', val)

		def connect_property(self, *a):
			super(CheckedRadioButtonGroup.State, self).connect_property(*a)
			self.checked_indexes = self.connected_property_value

		def on_connected_property_changed(self, value):
			# debug('on_connected_property_changed')
			self._checked_indexes.append(value)

		def _create_controls(self, count):
			super(CheckedRadioButtonGroup.State, self)._create_controls(count)
			# self.checked_index = clamp(self._checked_index, -1, count - 1)

		def _make_control(self, index):
			control = super(CheckedRadioButtonGroup.State, self)._make_control(index)
			control_state = control._get_state(self._manager)
			control_state._on_checked = partial(self._on_checked, control_state)
			# control_state._on_checked_indexes = partial(self._on_checked_indexes, control_state)
			control_state.is_checked = index in self._checked_indexes
			return control

		def _on_checked(self, checked_control):

			def control_pressed(val, element):
				control = element._get_state(self._manager)
				if control.is_pressed:
					val.append(control)
				return val

			pressed_buttons = reduce(control_pressed, self._controls, [])
			real_controls = list(control._get_state(self._manager) for control in self._controls)
			if checked_control in real_controls:
				index = real_controls.index(checked_control)
				if len(pressed_buttons) == 1:
					self._initial_pressed = checked_control
					self.checked_indexes = [index]
				elif (checked_control in pressed_buttons) and not (index in self.checked_indexes):
					checked_indexes = self.checked_indexes
					checked_indexes.append(index)
					self.checked_indexes = checked_indexes
				elif index in self.checked_indexes:
					self.checked_indexes = self._checked_indexes.remove(index)
				for control in self._controls:
					control = control._get_state(self._manager)
					index = real_controls.index(control)
					control.is_checked = index in self.checked_indexes
			self.connected_property_value = self._checked_indexes
			self._notify_checked_indexes()

		# def _on_checked_indexes(self, checked_control):
		# 	debug('_on_checked_indexes', checked_control)
			# for control in self._controls:
			# 	control = control._get_state(self._manager)
			# 	control.is_checked = control == checked_control
			#
			# self._checked_indexes.append(checked_control.index)
			# self.connected_property_value = self._checked_indexes

		def _notify_checked_indexes(self):
			# if self._checked:
			self._call_listener(u'checked_indexes')
			# self._on_checked_indexes())


	def __init__(self, *a, **k):
		super(CheckedRadioButtonGroup, self).__init__(CheckedRadioButtonControl, *a, **k)


_control_list_classes = dict()
def new_control_list(control_type, *a, **k):
	if control_type == RadioButtonControl:
		return RadioButtonGroup(*a, **k)
	if control_type == CheckedRadioButtonControl:
		return CheckedRadioButtonGroup(*a, **k)
	c = _control_list_classes.get(control_type, None)
	if not c:
		c = mixin(ControlList, control_type)
		_control_list_classes[control_type] = c
	return c(control_type, *a, **k)



#this needs to be wrapped up into aumhaa.framework, but for now we will just override.
class SpecialMonoChannelStripComponent(MonoChannelStripComponent):

	def _create_device(self, device_provider):
		# self._banking_info = BankingInfo(BANK_DEFINITIONS)
		# self._device_bank_registry = DeviceBankRegistry()
		# self._device_provider = ChannelStripStaticDeviceProvider()
		device_component = SpecialDeviceComponent(device_provider=device_provider, device_bank_registry=DeviceBankRegistry(), banking_info=BankingInfo(BANK_DEFINITIONS))
		device_component._show_msg_callback = lambda message: None
		return device_component

#we need to observe when any track names change we can autodetect the *SEQ tag
class SpecialMonoMixerComponent(MonoMixerComponent):

	def __init__(self, *a, **k):
		super(SpecialMonoMixerComponent, self).__init__(*a, **k)
		self._on_visible_tracks_name_changed.replace_subjects(self.song.visible_tracks)

	@listens_group('name')
	def _on_visible_tracks_name_changed(self, *a, **k):
		debug('visible tracks name changed')
		self._reassign_tracks()


#this needs to be here to accommodate the need for a parameter provider in the other components down the chain
class SpecialDeviceComponent(DeviceComponent):

	def _create_parameter_info(self, parameter, name):
		device_class_name = self.device().class_name
		return ParameterInfo(parameter=parameter, name=name)




DEFAULT_START_NOTE = 60

#This is the main component that encompasses all subcomponents needed for each track sequencer.  It relies on the Channelstrip above.
class TrackStepSequencer(Component):

	def __init__(self, script, skin, grid_resolution, channel_strip, parent_task_group, buttons, encoders, track_index = 0, settings = DEFAULT_INSTRUMENT_SETTINGS, *a, **k):
		super(TrackStepSequencer, self).__init__(*a, **k)
		self._track_index = track_index
		self._channel_strip = channel_strip
		# self._parameter_provider = parameter_provider
		self._parameter_provider = self._channel_strip._device_component
		self._encoders = encoders
		self._buttons = buttons
		self._settings = settings
		self._parent_task_group = parent_task_group
		# self._device_provider = device_provider
		self._script = script
		self._skin = skin
		self._grid_resolution = grid_resolution

		self._instrument = MonoKeyGroupComponent()

		scale_clip_creator = ClipCreator()
		scale_note_editor = SpecialNoteEditorComponent(clip_creator=scale_clip_creator, grid_resolution=grid_resolution)
		self._note_editor = scale_note_editor
		self._note_editor._pitches = [DEFAULT_START_NOTE]

		self._note_sequencer = SpecialStepSeqComponent(parent = self,
			channel_strip = self._channel_strip,
			clip_creator=scale_clip_creator,
			skin=skin,
			grid_resolution=self._grid_resolution,
			name='Note_Sequencer',
			note_editor_component=scale_note_editor,
			instrument_component=self._instrument)
		# self._note_sequencer._playhead_component._notes=tuple(chain(*starmap(range, ((60, 68), (52, 60)))))
		# self._note_sequencer._playhead_component._triplet_notes=tuple(chain(*starmap(range, ((60, 66), (52, 58)))))
		# self._note_sequencer._playhead_component.set_note_banks(NOTEBANKS)
		# self._note_sequencer._playhead_component.set_triplet_note_banks(TRIPLET_NOTEBANKS)
		# self._note_sequencer._playhead_component._feedback_channels = [15]
		self._note_sequencer._note_editor._visible_steps_model = lambda indices: [k for k in indices if k % 8 not in (6, 7)]

		self._note_sequencer._loop_selector.loop_length_radio_buttons._extra_kws = {'checked_color':u'SequenceColors.Sequence'+str(track_index), 'unchecked_color':u'SequenceSelector.Unselected'}

		self._note_editor_settings = SpecialNoteEditorSettingsComponent(channel_strip=self._channel_strip,
			note_settings_component_class = NoteSettingsComponent,
			automation_component_class = SpecialAutomationComponent,
			grid_resolution = self._grid_resolution,
			initial_encoder_layer = Layer(initial_encoders = encoders, priority=5),
			encoder_layer = Layer(encoders=encoders, buttons=buttons, priority = 5))
		self._note_editor_settings.automation.parameter_provider = self._parameter_provider
		self._note_editor_settings.add_editor(scale_note_editor)
		# self._note_editor_settings._settings_modes.selected_mode = u'automation'
		self._note_editor_settings._settings_modes.set_enabled(True)
		self._note_editor_settings.selected_setting = u'automation'
		self._note_editor_settings.set_enabled(True)
		self._note_editor_settings.selected_mode = u'disabled'
		# self._note_editor_settings._automation

		# self.set_playhead_buttons = self._note_sequencer._playhead_component._playhead.set_buttons
		self.set_playhead = self._note_sequencer.set_playhead
		self.set_loop_selector_matrix = self._note_sequencer.set_loop_selector_matrix
		self.set_quantization_buttons = self._note_sequencer.set_quantization_buttons
		self.set_loop_length_buttons = self._note_sequencer._loop_selector.set_loop_length_radio_buttons
		# self.set_follow_button = self._note_sequencer.set_follow_button
		self.set_sequencer_matrix = self._note_sequencer.set_button_matrix



class SpecialStepSeqComponent(MonoStepSeqComponent):

	def __init__(self, channel_strip, *a, **k):
		super(SpecialStepSeqComponent, self).__init__(*a, **k)
		self._loop_selector = SpecialLoopSelectorComponent()
		self._channel_strip = channel_strip
		self._on_playing_clip_changed.subject = channel_strip

	@listens(u'detail_clip')
	def _on_detail_clip_changed(self):
		# debug('detail_clip....')
		# clip = self.song.view.detail_clip
		# clip = clip if liveobj_valid(clip) and clip.is_midi_clip else None
		# self._detail_clip = clip
		# self._note_editor.set_detail_clip(clip)
		# self._loop_selector.set_detail_clip(clip)
		# self._playhead_component.set_clip(self._detail_clip)
		pass

	@listens(u'playing_clip')
	def _on_playing_clip_changed(self, clip):
		debug('SpecialStepSeqComponent._on_playing_clip_changed:', clip)
		# clip = self.song.view.detail_clip
		clip = clip if liveobj_valid(clip) and clip.is_midi_clip else None
		self._detail_clip = clip
		self._note_editor.set_detail_clip(clip)
		self._loop_selector.set_detail_clip(clip)
		self._playhead_component.set_clip(self._detail_clip)


class SpecialNoteEditorComponent(MonoNoteEditorComponent):


	# def _determine_color(self, notes):
	#     return color_for_note(most_significant_note(notes), velocity_range_thresholds=self._velocity_range_thresholds)

	@property
	def can_change_page(self):
		return False

	@property
	def active_note_regions_with_fill(self):
		return map(self._get_time_range_with_fill, chain(self._pressed_steps, self._modified_steps))

	def _next_active_note_start(self, end_time):

		def note_compare(left, right):
			return left.start_time - right.start_time

		notes_sorted = sorted(self._clip_notes, key=cmp_to_key(note_compare))

		if notes_sorted:
			for note in notes_sorted:
				if note.start_time >= end_time:
					return note.start_time
			return self._sequencer_clip.length if liveobj_valid(self._sequencer_clip) else end_time
		else:
			return self._sequencer_clip.length if liveobj_valid(self._sequencer_clip) else end_time

	def _get_time_range_with_fill(self, step):

		def note_compare(left, right):
			return left.start_time - right.start_time

		time = self.get_step_start_time(step)
		notes = self._time_step(time).filter_notes(self._clip_notes)

		if notes:
			beginning_note = first(sorted(notes, key=cmp_to_key(note_compare)))
			start = beginning_note.start_time
			end = self._next_active_note_start(start + beginning_note.duration)
			# end = start + note_length(beginning_note)
			#1 if len(notes) > 1:
			# 	end_note = notes[-1]
			# 	end = note_start_time(end_note) + note_length(end_note)
			return (start, end)
		else:
			# return (time, time + self._get_step_length())
			return (time, self._next_active_note_start(time))

	# def get_row_start_times(self):
	# 	#return [ self.get_step_start_time((0, row)) for row in xrange(self._get_height()) ]
	# 	return [0 for row in range(self._get_height)]
	#
	# def _get_width(self):
	# 	if self.matrix.width:
	# 		debug('width:', self.matrix.width)
	# 		return self.matrix.width
	# 	debug('width def:', 4)
	# 	return 4
	#
	# def _get_height(self):
	# 	if self.matrix.height:
	# 		debug('height:', self.matrix.height)
	# 		return self.matrix.height
	# 	debug('height def:', 4)
	# 	return 4

	# def _get_step_length(self):
	# 	debug('_get_step_length:', self._grid_resolution.step_length)
	# 	return self._grid_resolution.step_length


AutomationState = Live.DeviceParameter.AutomationState

class SpecialAutomationComponent(DeviceParameterComponent):
	ENCODER_SENSITIVITY_FACTOR = 1.0
	_clip = None
	# _held_buttons = []
	encoders = control_list(EncoderControl)
	buttons = control_list(ButtonControl)

	@staticmethod
	def parameter_is_automateable(parameter):
		return liveobj_valid(parameter) and isinstance(parameter, Live.DeviceParameter.DeviceParameter)

	def __init__(self, *a, **k):
		(super(SpecialAutomationComponent, self).__init__)(*a, **k)
		self._selected_time = []
		self._parameter_floats = []
		self._update_parameter_values_task = self._tasks.add(task.run(self._update_parameter_values))
		self._update_parameter_values_task.kill()

	def _get_clip(self):
		return self._clip

	def _set_clip(self, value):
		debug('**************automation._set_clip:', value.name if hasattr(value, 'name') else value)
		self._clip = value
		self._update_parameter_values_task.restart()

	clip = property(_get_clip, _set_clip)

	def _get_selected_time(self):
		return self._selected_time

	def _set_selected_time(self, value):
		# debug('automation._set_selected_time', value)
		self._selected_time = value or []
		self._update_parameter_values()
		self._update_parameter_floats()

	selected_time = property(_get_selected_time, _set_selected_time)

	@property
	def parameters(self):
		return [info.parameter if info else None for info in self._parameter_infos_to_use()]

	@property
	def parameter_infos(self):
		return self._parameter_infos_to_use()

	def _parameter_infos_to_use(self):
		return list(map(lambda info: info if self.parameter_is_automateable(info.parameter if info else None) else None, self._parameter_provider.parameters))

	@property
	def can_automate_parameters(self):
		return self._can_automate_parameters()

	def _can_automate_parameters(self):
		return len(self.parameter_provider.parameters) > 0 and liveobj_valid(self._clip) and not self._clip.is_arrangement_clip

	def set_parameter_controls(self, encoders):
		self.encoders.set_control_element(encoders)

	def set_parameter_control_buttons(self, buttons):
		self.buttons.set_control_element(buttons)

	def _update_parameters(self):
		super(SpecialAutomationComponent, self)._update_parameters()
		self._update_parameter_floats()

	def _connect_parameters(self):
		pass

	def parameter_to_string(self, parameter):
		if not parameter:
			return ''
		if len(self._selected_time) == 0:
			return '-'
		return parameter.str_for_value(self.parameter_to_value(parameter))

	def parameter_to_value(self, parameter):
		if self._clip:
			if len(self.selected_time) > 0:
				if liveobj_valid(parameter):
					envelope = self._clip.automation_envelope(parameter)
					if liveobj_valid(envelope):
						return self._value_at_time(envelope, self.selected_time[0])
					return parameter.value
		return 0.0

	def _value_at_time(self, envelope, time_range):
		return envelope.value_at_time(old_div(time_range[0] + time_range[1], 2))

	def _can_edit_clip_envelope(self, parameter_index):
		parameters = self.parameters
		# debug('parameter_index:', parameter_index, 'parameters:', list(parameters))
		# debug('0 <= parameter_index < len(parameters)', 0 <= parameter_index < len(parameters))
		# debug('self._clip:', self._clip)
		# debug('self._parameter_for_index(parameters, parameter_index)', self._parameter_for_index(parameters, parameter_index))
		return bool((0 <= parameter_index < len(parameters)) and (self._clip) and (self._parameter_for_index(parameters, parameter_index)))

	def _parameter_for_index(self, parameters, index):
		return parameters[index]

	# @buttons.pressed
	# def buttons(self, button):
	# 	debug('buttons.pressed', button, button.index)
	# 	index = button.index
	# 	if not index in self._held_buttons:
	# 		self._held_buttons.append(index)
	#
	# @buttons.released
	# def buttons(self, button):
	# 	debug('buttons.released', button.index)
	# 	index = button.index
	# 	if index in self._held_buttons:
	# 		self._held_buttons.remove(index)

	@encoders.value
	def encoders(self, value, encoder):
		# debug('automation.encoders.value:', value)
		index = encoder.index
		# debug('index is:', index)
		# debug('is pressed:', self.buttons[index].is_pressed)
		# if (index < 3) and self.buttons._control_elements[index].is_pressed():
		# if index in self._held_buttons and index < 3:
		if (index < 3) and self.buttons[index].is_pressed:
			index = int(index + 4)
		# debug('index is now:', index)
		parameters = self.parameters
		# debug('can_edit_clip_envelope:', self._can_edit_clip_envelope(index))
		if self._can_edit_clip_envelope(index):
			param = self._parameter_for_index(parameters, index)
			# debug('param', param)
			envelope = self._clip.automation_envelope(param)
			debug('evelope:', envelope)
			# debug('clip:', self._clip.name if liveobj_valid(self._clip) else 'None')
			debug('param:', param.name)
			if not liveobj_valid(envelope):
				envelope = self._clip.create_automation_envelope(param)
			if liveobj_valid(envelope):
				debug('is valid...')
				if param.automation_state == AutomationState.overridden:
					param.re_enable_automation()
				for time_index, time_range in enumerate(self.selected_time):
					debug('time_index', time_range, time_index, index, envelope, value)
					self._insert_step(time_range, time_index, index, envelope, value)

			self._update_parameter_values()

	@encoders.touched
	def encoders(self, encoder):
		# debug('automation.encoders.touched:', encoder)
		index = encoder.index
		# if index in self._held_buttons and index < 3:
		if (index < 3) and self.buttons[index].is_pressed:
			index = int(index + 4)
		parameters = self.parameters
		if self._can_edit_clip_envelope(index):
			self._clip.view.select_envelope_parameter(self._parameter_for_index(parameters, index))
			self._update_parameter_floats()

	def _update_parameter_floats(self):
		self._parameter_floats = []
		if self._clip:
			if self.is_enabled():
				parameters = self.parameters
				for step in self.selected_time:
					step_parameter_floats = []
					for index, param in enumerate(parameters):
						if param is None:
							value = 0.0
						else:
							parameter = self._parameter_for_index(parameters, index)
							envelope = self._clip.automation_envelope(parameter)
							if liveobj_valid(envelope):
								value = self._value_at_time(envelope, step)
							else:
								value = parameter.value
						step_parameter_floats.append(value)

					self._parameter_floats.append(step_parameter_floats)

	def _insert_step(self, time_range, time_index, param_index, envelope, value):
		param = self._parameter_for_index(self.parameters, param_index)
		envelope_value = self._parameter_floats[time_index][param_index]
		#sensitivity = self.parameter_infos[param_index].default_encoder_sensitivity * self.ENCODER_SENSITIVITY_FACTOR
		sensitivity = 1
		if param.is_quantized:
			value_to_insert = clamp(envelope_value + old_div(value, min(.00001, EnumerableSetting.STEP_SIZE)), param.min, param.max)
		else:
			value_range = param.max - param.min
			#value_to_insert = clamp(envelope_value + (value/127) * value_range * sensitivity, param.min, param.max)
			value_to_insert = clamp((value/127) * value_range * sensitivity, param.min, param.max)
		self._parameter_floats[time_index][param_index] = value_to_insert
		debug('inserting:', time_range[0], time_range[1] - time_range[0], value_to_insert)
		envelope.insert_step(time_range[0], time_range[1] - time_range[0], value_to_insert)


class SpecialNoteEditorSettingsComponent(ModesComponent):
	initial_encoders = control_list(EncoderControl)
	encoders = control_list(EncoderControl)
	buttons = control_list(ButtonControl)

	def __init__(self, channel_strip, note_settings_component_class=None, automation_component_class=None, grid_resolution=None, initial_encoder_layer=None, encoder_layer=None, *a, **k):
		(super(SpecialNoteEditorSettingsComponent, self).__init__)(*a, **k)
		self._channel_strip = channel_strip
		self.settings = note_settings_component_class(grid_resolution=grid_resolution,
		  parent=self,
		  is_enabled=False)
		self.automation = automation_component_class(parent=self, is_enabled=False )
		self._mode_selector = ModeSelector(parent=self, is_enabled=False)
		self._visible_detail_view = 'Detail/DeviceChain'
		self._show_settings_task = self._tasks.add(task.sequence(task.wait(defaults.MOMENTARY_DELAY), task.run(self._show_settings))).kill()
		self._update_infos_task = self._tasks.add(task.run(self._update_note_infos)).kill()
		self._settings_modes = ModesComponent(parent=self)
		self._settings_modes.set_enabled(False)
		self._settings_modes.add_mode('automation', [
		 self.automation,
		 self._mode_selector,
		 partial(self._set_envelope_view_visible, True),
		 partial(show_clip_view, self.application)])
		self._settings_modes.add_mode('note_settings', [
		 self.settings,
		 self._update_note_infos,
		 self._mode_selector,
		 partial(self._set_envelope_view_visible, False),
		 partial(show_clip_view, self.application)])
		self._settings_modes.selected_mode = 'automation'
		self._SpecialNoteEditorSettingsComponent__on_selected_setting_mode_changed.subject = self._settings_modes
		self.add_mode('disabled', [])
		self.add_mode('about_to_show', [
		 AddLayerMode(self, initial_encoder_layer),
		 (
		  self._show_settings_task.restart, self._show_settings_task.kill)])
		self.add_mode('enabled', [
		 DetailViewRestorerMode(self.application),
		 AddLayerMode(self, encoder_layer),
		 self._settings_modes])
		self._editors = []
		self.selected_mode = 'enabled'
		# self._on_detail_clip_changed.subject = self.song.view
		self._on_selected_track_changed.subject = self.song.view
		self._SpecialNoteEditorSettingsComponent__on_full_velocity_changed.subject = self.settings
		self._SpecialNoteEditorSettingsComponent__on_setting_changed.subject = self.settings
		self._on_playing_clip_changed.subject = self._channel_strip
		self._channel_strip._update_playing_clip()

	automation_layer = forward_property('automation')('layer')
	mode_selector_layer = forward_property('_mode_selector')('layer')
	selected_setting = forward_property('_settings_modes')('selected_mode')

	@property
	def step_settings(self):
		return self._settings_modes

	@property
	def editors(self):
		return self._editors

	@listenable_property
	def is_touched(self):
		return any(map(lambda e: e and e.is_touched, filter(lambda e: self._can_notify_is_touched(e), self.encoders)))

	def _is_step_held(self):
		return len(self._active_note_regions()) > 0

	def add_editor(self, editor):
		self._editors.append(editor)
		self._on_active_note_regions_changed.add_subject(editor)
		self._on_notes_changed.replace_subjects(self._editors)
		self._SpecialNoteEditorSettingsComponent__on_modify_all_notes_changed.add_subject(editor)

	def set_encoders(self, encoders):
		# debug('set_encoders:', encoders)
		self.encoders.set_control_element(encoders)
		self.settings.set_encoder_controls(encoders)
		self.automation.set_parameter_controls(encoders)

	def set_buttons(self, buttons):
		# debug('set_encoders:', buttons)
		self.buttons.set_control_element(buttons)
		self.automation.set_parameter_control_buttons(buttons)

	@property
	def parameter_provider(self):
		self.automation.parameter_provider

	@parameter_provider.setter
	def parameter_provider(self, value):
		self.automation.parameter_provider = value

	@listens('selected_mode')
	def __on_selected_setting_mode_changed(self, mode):
		if mode == 'automation':
			self.automation.selected_time = self._active_note_regions()

	def update_view_state_based_on_selected_setting(self, setting):
		if self.selected_mode == 'enabled' and self.is_touched or setting is None:
			self._set_settings_view_enabled(False)
		elif self._is_step_held():
			if self.selected_setting == 'automation' and self.automation.can_automate_parameters or self.selected_setting == 'note_settings':
				self._show_settings()

	@listens('full_velocity')
	def __on_full_velocity_changed(self):
		for editor in self._editors:
			editor.set_full_velocity()

	@listens('setting_changed')
	def __on_setting_changed(self, index, value):
		for editor in self._editors:
			self._modify_note_property_offset(editor, index, value)

	def _modify_note_property_offset(self, editor, index, value):
		if index == 1:
			editor.set_nudge_offset(value)
		elif index == 2:
			editor.set_length_offset(value)
		elif index == 3:
			editor.set_velocity_offset(value)
		elif index == 4:
			editor.set_velocity_deviation_offset(value)
		elif index == 5:
			editor.set_probability_offset(value)

	def _set_envelope_view_visible(self, visible):
		clip = self.song.view.detail_clip
		if liveobj_valid(clip):
			if visible:
				clip.view.show_envelope()
			else:
				clip.view.hide_envelope()

	def _set_settings_view_enabled(self, should_show_view):
		really_show_view = should_show_view and self.automation.can_automate_parameters if self.selected_setting == 'automation' else should_show_view
		if really_show_view:
			if self.selected_mode == 'disabled':
				self.selected_mode = 'about_to_show'
		else:
			self._hide_settings()

	def _active_note_regions(self):
		all_active_regions = list(map(lambda e: e.active_note_regions, self._editors))
		return list(set(chain.from_iterable(all_active_regions)))

	def _active_note_regions_with_fill(self):
		all_active_regions = list(map(lambda e: e.active_note_regions_with_fill, self._editors))
		return list(set(chain.from_iterable(all_active_regions)))

	@listens_group('active_note_regions')
	def _on_active_note_regions_changed(self, _):
		if self.is_enabled():
			all_steps = self._active_note_regions()
			all_steps_with_fill = self._active_note_regions_with_fill()
			self.automation.selected_time = all_steps_with_fill
			self._update_note_infos()
			self._set_settings_view_enabled((len(all_steps) > 0) and (self.selected_setting != None) or (self.is_touched))

	@listens_group('modify_all_notes')
	def __on_modify_all_notes_changed(self, editor):
		self.selected_mode = 'about_to_show' if editor.modify_all_notes_enabled else 'disabled'

	@listens_group('notes_changed')
	def _on_notes_changed(self, editor):
		self._update_infos_task.restart()

	@listens('detail_clip')
	def _on_detail_clip_changed(self):
		# self.automation.clip = self.song.view.detail_clip if self.is_enabled() else None
		pass

	@listens('playing_clip')
	def _on_playing_clip_changed(self, clip):
		self.automation.clip = clip if self.is_enabled() else None

	@listens('selected_track')
	def _on_selected_track_changed(self):
		self.selected_mode = 'disabled'

	@initial_encoders.touched
	def initial_encoders(self, encoder):
		# debug('settings initial_encoders.touched')
		if self.selected_mode == 'about_to_show':
			self._show_settings()

	@initial_encoders.value
	def initial_encoders(self, encoder, value):
		# debug('settings initial_encoders.value', encoder, value)
		if self.selected_mode == 'about_to_show':
			self._show_settings()

	@buttons.pressed
	def buttons(self, button):
		debug('buttons.pressed')

	@buttons.released
	def buttons(self, button):
		debug('buttons.released')

	@encoders.touched
	def encoders(self, encoder):
		debug('settings encoders.touched')
		if self._can_notify_is_touched(encoder):
			self.notify_is_touched()

	@encoders.released
	def encoders(self, encoder):
		debug('settings encoders.released')
		if not self.is_touched:
			if not self._is_step_held():
				if not self._is_edit_all_notes_active():
					self._hide_settings()
		if self._can_notify_is_touched(encoder):
			self.notify_is_touched()

	@encoders.value
	def encoders(self, value, encoder):
		debug('settings encoders.value', value)
		self._notify_modification()

	def _can_notify_is_touched(self, encoder):
		if self.is_enabled():
			return self._settings_modes.selected_mode != 'note_settings' or encoder.index < self.settings.number_of_settings
		return False

	def _is_edit_all_notes_active(self):
		return find_if(lambda e: e.modify_all_notes_enabled, self._editors) != None

	def _notify_modification(self):
		for editor in self._editors:
			editor.notify_modification()

	def _update_note_infos(self):
		if self.settings.is_enabled():

			def min_max(l_min_max, r_min_max):
				l_min, l_max = l_min_max
				r_min, r_max = r_min_max
				return (
				 min(l_min, r_min), max(l_max, r_max))

			all_min_max_attributes = [_f for _f in map(lambda e: e.get_min_max_note_values(), self._editors) if _f]
			min_max_values = [(99999, -99999)] * self.settings.number_of_settings if len(all_min_max_attributes) > 0 else None
			for min_max_attribute in all_min_max_attributes:
				for i, attribute in enumerate(min_max_attribute[:self.settings.number_of_settings]):
					min_max_values[i] = min_max(min_max_values[i], attribute)

			for i in range(self.settings.number_of_settings):
				self.settings.set_min_max(i, min_max_values[i] if min_max_values else None)

			self.settings.set_info_message(min_max_values or 'Tweak to add note' if (not self._is_edit_all_notes_active()) else '')

	def _show_settings(self):
		if self.selected_mode != 'enabled':
			self.selected_mode = 'enabled'
			self._notify_modification()

	def _hide_settings(self):
		# self.selected_mode = 'disabled'
		pass

	def on_enabled_changed(self):
		super(SpecialNoteEditorSettingsComponent, self).on_enabled_changed()
		debug('settings.on_enabled_changed')
		# if not self.is_enabled():
		# 	self.selected_mode = 'disabled'

	def update(self):
		super(SpecialNoteEditorSettingsComponent, self).update()
		if self.is_enabled():
			self._on_detail_clip_changed()




def set_loop(clip, loop_start, loop_end):
	if loop_start >= clip.loop_end:
		clip.loop_end = loop_end
		if clip.loop_end == loop_end:
			clip.loop_start = loop_start
			clip.end_marker = loop_end
			clip.start_marker = loop_start
	else:
		clip.loop_start = loop_start
		if clip.loop_start == loop_start:
			clip.loop_end = loop_end
			clip.end_marker = loop_end
			clip.start_marker = loop_start

class SpecialLoopSelectorComponent(LoopSelectorComponent):
	loop_length_radio_buttons = control_list(RadioButtonControl, checked_color=u'SequenceSelector.Selected', unchecked_color=u'SequenceSelector.Unselected')

	def __init__(self, *a, **k):
		# self._playhead_page_index = 0
		super(SpecialLoopSelectorComponent, self).__init__(*a, **k)
		self._on_loop_changed()

	def _update_page_colors(self):
		pass

	def set_loop_length_radio_buttons(self, buttons):
		self.loop_length_radio_buttons.set_control_element(buttons)

	@listenable_property
	def loop_length(self):
		return self._loop_length

	def _on_loop_changed(self):
		super(SpecialLoopSelectorComponent, self)._on_loop_changed()
		if not liveobj_valid(self._sequencer_clip):
			self.loop_length_radio_buttons._checked_index = -1
		else:
			new_index = int(min(8, abs((self._loop_length/4)-8)))
			# debug('new_index:', new_index)
			# self.loop_length_radio_buttons.checked_index = new_index
			self.loop_length_radio_buttons._checked_index = new_index
			self.notify_loop_length(self._loop_length)
		self._update_loop_length_radio_buttons()

	def _update_loop_length_radio_buttons(self):
		debug('_update_loop_length_radio_buttons')
		if not self.loop_length_radio_buttons._checked_index == -1:
			# new_index = int(min(8, abs((self._loop_length/4)-8)))
			# # debug('new_index:', new_index)
			# # self.loop_length_radio_buttons.checked_index = new_index
			# self.loop_length_radio_buttons._checked_index =
			new_index = self.loop_length_radio_buttons._checked_index
			if(len(self.loop_length_radio_buttons._controls)>new_index):
				button = self.loop_length_radio_buttons[new_index]
				# debug('button is:', None)
				liveobj_valid(button) and self.loop_length_radio_buttons._on_checked(button)

	@loop_length_radio_buttons.checked
	def loop_length_radio_buttons(self, button):
		debug('loop_length_radio_buttons:', button.index)
		if liveobj_valid(self._sequencer_clip):
			end_loop = min(32, int(abs(button.index-8)*4))
			# debug('end_loop:', end_loop)
			self._duplicate_clip_contents(self._sequencer_clip, end_loop)
			set_loop(self._sequencer_clip, self._loop_start, end_loop)

	def _duplicate_clip_contents(self, clip, new_length):
		if liveobj_valid(clip):
			original_end = clip.loop_end
			debug('original_end', original_end, 'new_length', new_length)
			if new_length < original_end:
				# clip.get_notes(0, 0, original_end, 128)
				clip.remove_notes(new_length, 0, clip.length, 128)
			else:
				num_duplicates = math.floor(new_length/original_end)
				for x in range(num_duplicates):
					# clip.duplicate_loop()
					# debug('duplicating:', 0, original_end, original_end*(x+1), -1, 0)
					clip.duplicate_region(0, original_end, original_end*(x+1), -1, 0)
					self._duplicate_automation(clip, 0, original_end, original_end*(x+1))

	def _duplicate_automation(self, clip, origin_start, origin_end, destination_time):
		pass



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

	#
	# @listenable_property
	# def playhead_page_index(self):
	# 	return self._playhead_page_index



#This switches dynamically between the TrackStepSequencer instances.
class SequenceSelectorComponent(Component):

	selection_radio_buttons = new_control_list(CheckedRadioButtonControl, checked_color=u'SequenceSelector.Selected', unchecked_color=u'SequenceSelector.Unselected')
	length_page_button = ButtonControl()

	def __init__(self, matrix, length_matrix, sequencers, playheads, *a, **k):
		self._sequencers = sequencers
		for index, sequencer in enumerate(sequencers):
			key = u'NoteEditor'+str(index)
			sequencer._note_editor._skin_base_key = key
		self._pad_matrix = matrix
		self._length_matrix = length_matrix
		self._playheads = playheads
		super(SequenceSelectorComponent, self).__init__(*a, **k)
		self._active_sequencers = [0]
		# self.selection_radio_buttons.checked_indexes = [0]
		# self.build_sequencer_layers()



	@selection_radio_buttons.checked
	def selection_radio_buttons(self, state):
		# debug('SequenceSelectorComponent.selection_radio_buttons.checked:', state)
		pass

	@selection_radio_buttons.checked_indexes
	def selection_radio_buttons(self, state):
		# debug('SequenceSelectorComponent.selection_radio_buttons.checked_indexes:', state.checked_indexes)
		self._active_sequencers = state.checked_indexes
		self.build_sequencer_layers()

	def build_sequencer_layers(self):
		for playhead in self._playheads:
			playhead.set_buttons(None)
		if self.length_page_button.is_pressed:
			# debug('setting up length buttons')
			index = 0
			for sequencer in self._sequencers:
				sequencer.layer = Layer(priority=5, loop_length_buttons=self._length_matrix.submatrix[index,:])
				index+=1
		else:
			active_sequencers = [self._sequencers[index] for index in sorted(self._active_sequencers)]
			matrix_index = 0
			playhead_index = 0
			self._on_seq_length_changed.replace_subjects([None])

			for sequencer in self._sequencers:
				if not sequencer in active_sequencers:
					sequencer.layer = Layer(priority=5)

			for sequencer in active_sequencers:
				length = int(int(sequencer._note_sequencer._loop_selector.loop_length)/4)
				# debug('seq:', sequencer, 'length:', length, 'matrix_index:', matrix_index)
				if matrix_index+length <= 8:
					matrix = self._pad_matrix.submatrix[:, int(matrix_index):int(matrix_index+length)]
					sequencer._note_sequencer._playhead_component._notes = list(range(length*16))
					sequencer._note_sequencer._playhead_component._triplet_notes = list(range(length*24))
					sequencer.layer = Layer(priority = 5, playhead = self._playheads[playhead_index], sequencer_matrix = matrix)
					self._playheads[playhead_index].set_buttons(matrix)
					self._on_seq_length_changed.add_subject(sequencer._note_sequencer._loop_selector)
					matrix_index+=length
					playhead_index+=1
				else:
					break

	@listens_group('loop_length')
	def _on_seq_length_changed(self, *a, **k):
		# debug('_on_seq_length_changed')
		self.build_sequencer_layers()

	@length_page_button.pressed
	def length_page_button(self, button):
		# debug('length_page_button.pressed')
		self.build_sequencer_layers()

	@length_page_button.released
	def length_page_button(self, button):
		# debug('length_page_button.released')
		self.build_sequencer_layers()

	def update(self, *a, **k):
		super(SequenceSelectorComponent, self).update(*a, **k)
		self.build_sequencer_layers()
		self.selection_radio_buttons._update_controls()


class SpecialSessionRingComponent(SessionRingComponent):

	def __init__(self, *a, **k):
		super(SpecialSessionRingComponent, self).__init__(*a, **k)
		self._on_visible_tracks_name_changed.replace_subjects(self.song.visible_tracks)
		self._on_visible_tracks_changed.subject = self.song
		self._on_track_list_changed.subject = self.song

	@listens(u'tracks')
	def _on_track_list_changed(self):
		self._on_visible_tracks_name_changed.replace_subjects(self.song.visible_tracks)

	@listens(u'visible_tracks')
	def _on_visible_tracks_changed(self):
		self._on_visible_tracks_name_changed.replace_subjects(self.song.visible_tracks)

	@listens_group('name')
	def _on_visible_tracks_name_changed(self, *a, **k):
		debug('visible tracks name changed')
		self._update_track_list()

	def _update_highlight(self):
		self._session_ring.hide_highlight()


class STEPSEQ(ControlSurface):

	def __init__(self, *a, **k):
		super(STEPSEQ, self).__init__(*a, **k)
		self._skin = Skin(STEPSEQColors)
		with self._component_guard():
			self._setup_controls()
			self._setup_autoarm()
			self._setup_mixer_control()
			self._setup_session_control()
			# self._setup_device_control()
			self._setup_track_stepsequencers()
			self._setup_sequencer_selector()
			self._setup_background()
			self._setup_main_modes()
		self._main_modes.selected_mode = 'Main'


	def _setup_controls(self):
		is_momentary = True
		optimized = True
		resource = PrioritizedResource
		# self._encoder = [MonoEncoderElement(msg_type = MIDI_CC_TYPE, channel = ENCODER_CHANNEL, identifier = STEPSEQ_ENCODERS[index], name = 'Encoder_' + str(index), num = index, script = self, mapping_feedback_delay = -1, optimized_send_midi = optimized, resource_type = resource) for index in range(4)]
		self._encoder = [SpecialEncoderElement(msg_type = MIDI_CC_TYPE, channel = ENCODER_CHANNEL, identifier = STEPSEQ_ENCODERS[index], optimized_send_midi = optimized, resource_type = resource, map_mode = Live.MidiMap.MapMode.absolute) for index in range(4)]

		self._encoder_button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = ENCODER_CHANNEL, identifier = STEPSEQ_ENCODER_BUTTONS[index], name = 'Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(4)]

		self._encoder_matrix = ButtonMatrixElement(name = 'EncoderMatrix', rows = [self._encoder])
		self._encoder_button_matrix = ButtonMatrixElement(name = 'EncoderButtonMatrix', rows = [self._encoder_button[0:3]])

		self._button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = BUTTON_CHANNEL, identifier = STEPSEQ_BUTTONS[index], name = 'Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(8)]
		self._select_button_matrix = ButtonMatrixElement(name = 'SelectButtonMatrix', rows = [self._button])
		self._pad = [SpecialMonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = PAD_CHANNEL, identifier = STEPSEQ_PADS[index], name = 'Pad_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(128)]
		self._pad_matrix = ButtonMatrixElement(name = 'PadMatrix', rows = [self._pad[0:16],
																			self._pad[16:32],
																			self._pad[32:48],
																			self._pad[48:64],
																			self._pad[64:80],
																			self._pad[80:96],
																			self._pad[96:112],
																			self._pad[112:128]])

		self._mixer_button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = MIXER_SESSION_CHANNEL, identifier = STEPSEQ_MIXER_BUTTONS[index], name = 'Mixer_Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(8)]
		self._mixer_button_matrix = ButtonMatrixElement(name = 'MixerButtonMatrix', rows = [self._mixer_button])
		self._mixer_slider = [SliderElement(msg_type=MIDI_CC_TYPE, channel=MIXER_SESSION_CHANNEL, identifier=STEPSEQ_MIXER_SLIDERS[index]) for index in range(8)]
		self._mixer_slider_matrix = ButtonMatrixElement(name = 'MixerSliderMatrix', rows = [self._mixer_slider])
		self._session_button = [MonoButtonElement(is_momentary = is_momentary, msg_type = MIDI_NOTE_TYPE, channel = MIXER_SESSION_CHANNEL, identifier = STEPSEQ_SESSION_BUTTONS[index], name = 'Session_Button_' + str(index), script = self, skin = self._skin, color_map = COLOR_MAP, optimized_send_midi = optimized, resource_type = resource) for index in range(34)]
		self._session_button_matrix = ButtonMatrixElement(name = 'SessionButtonMatrix', rows = [self._session_button[0:8],
																								self._session_button[8:16],
																								self._session_button[16:24],
																								self._session_button[24:32]])

		# self._select_multi = MultiElement(self._button[0], self._button[1], self._button[2], self._button[3], self._button[4], self._button[5], self._button[6], self._button[7],)
		self._length_multis = [MultiElement(self._pad[index*2], self._pad[(index*2)+1]) for index in range(64)]
		self._length_matrix = ButtonMatrixElement(name = 'LengthMatrix', rows = [self._length_multis[0:8],
																			self._length_multis[8:16],
																			self._length_multis[16:24],
																			self._length_multis[24:32],
																			self._length_multis[32:40],
																			self._length_multis[40:48],
																			self._length_multis[48:56],
																			self._length_multis[56:64]])
		# debug('length_multis:', self._length_multis[0].owned_control_elements())

	def _setup_background(self):
		self._background = BackgroundComponent(name = 'Background')
		self._background.layer = Layer(priority = 0, matrix = self._pad_matrix,) # playhead = self._playhead_element)
		self._background.set_enabled(False)


	def _setup_autoarm(self):
		self._auto_arm = AutoArmComponent(name='Auto_Arm')
		self._auto_arm.can_auto_arm_track = self._can_auto_arm_track
		self._auto_arm._update_notification = lambda: None


	def _setup_mixer_control(self):

		self._session_ring = SpecialSessionRingComponent(name = 'Session_Ring', num_tracks = 8, num_scenes = 4, tracks_to_use=partial(tracks_to_use_from_song, self.song))
		# self._session_ring.tracks_to_use = lambda : tracks_to_use
		self._mixer = SpecialMonoMixerComponent(name = 'Mixer', num_returns = 4, tracks_provider = self._session_ring, track_assigner = SimpleTrackAssigner(), invert_mute_feedback = True, auto_name = True, enable_skinning = True, channel_strip_component_type=SpecialMonoChannelStripComponent)
		self._mixer.layer = Layer(priority = 5, volume_controls = self._mixer_slider_matrix, arm_buttons = self._mixer_button_matrix)
		# self._mixer.layer = Layer(priority = 5, track_select_buttons = self._select_button_matrix)
		self._mixer.set_enabled(False)


	def _setup_session_control(self):
		self._session = SessionComponent(session_ring = self._session_ring, auto_name = True)
		self._session.layer = Layer(priority = 5, clip_launch_buttons = self._session_button_matrix)
		self._session.set_enabled(False)

		self._session_navigation = SessionNavigationComponent(session_ring = self._session_ring)
		self._session_navigation.layer = Layer(priority = 5, up_button = self._session_button[32], down_button = self._session_button[33])
		self._session.set_enabled(False)


	# def _setup_device_control(self):
	# 	self._device_selection_follows_track_selection = True
	# 	self._device_bank_registry = DeviceBankRegistry()
	# 	self._banking_info = BankingInfo(BANK_DEFINITIONS)
	# 	self._device = SpecialDeviceComponent(name = 'Device_Component', device_bank_registry = DeviceBankRegistry(), banking_info=self._banking_info, device_provider = self._device_provider)
	# 	# self._device.layer = Layer(priority = 5, parameter_controls = self._encoder_matrix)
	# 	self._device.set_enabled(False)


	def _setup_track_stepsequencers(self):
		self._grid_resolution = GridResolution()

		# self._c_instance.playhead.enabled = True
		self._stepsequencers = [None for index in range(8)]
		for track in range(8):
			self._stepsequencers[track] = TrackStepSequencer(script=self, skin=self._skin, grid_resolution=self._grid_resolution, channel_strip=self._mixer.channel_strip(track), parent_task_group=self._task_group, buttons=self._encoder_button_matrix, encoders=self._encoder_matrix, track_index = track)
			# self._stepsequencers[track].layer = Layer(priority = 5, sequencer_matrix = self._pad_matrix.submatrix[:,track])


	def _setup_sequencer_selector(self):
		self._playhead_elements = [None for index in range(8)]
		for index in range(8):
			self._playhead_elements[index] = SpecialPlayheadElement(playhead = Playhead())   #(self._c_instance.playhead)

		self._sequence_selector = SequenceSelectorComponent(matrix = self._pad_matrix, length_matrix = self._length_matrix, sequencers = self._stepsequencers, playheads = self._playhead_elements)
		self._sequence_selector.layer = Layer(selection_radio_buttons=self._select_button_matrix, length_page_button=self._encoder_button[3])


	def _setup_main_modes(self):
		self._main_modes = ModesComponent(name = 'MainModes')
		self._main_modes.add_mode('disabled', [self._background])
		# self._main_modes.add_mode('Main', [self._mixer, self._device, self._instrument, self._stepsequencer])
		self._main_modes.add_mode('Main', [self._background, self._mixer, self._session, self._session_navigation, self._stepsequencers, self._sequence_selector])
		# self._main_modes.add_mode('Select', [self._device, self._instrument, tuple([self._send_instrument_shifted, self._send_instrument_unshifted])], behaviour = DelayedExcludingMomentaryBehaviour(excluded_groups = ['shifted']) )
		self._main_modes.selected_mode = 'disabled'
		# self._main_modes.layer = Layer(priority = 5, Select_button=self._select_multi)
		self._main_modes.set_enabled(True)
		debug('checked_indexes', self._sequence_selector.selection_radio_buttons.checked_indexes)


	"""general functionality"""
	def disconnect(self):
		super(STEPSEQ, self).disconnect()


	def _can_auto_arm_track(self, track):
		return False


	def touched(self):
		pass






#a
